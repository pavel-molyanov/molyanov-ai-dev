#!/usr/bin/env python3
"""Import private Claude MCP configs into the local Codex runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VERSION = "2"
BEGIN_MARKER = "# BEGIN CLAUDE MCP IMPORT (managed by sync-mcp-to-codex)"
END_MARKER = "# END CLAUDE MCP IMPORT"
MANIFEST_REL = Path("mcp-imported/.sync/manifest.json")
SLUG_RE = re.compile(r"[^A-Za-z0-9_-]+")
CREDENTIAL_URL_RE = re.compile(r"^[a-z][a-z0-9+.-]*://[^/@:]+:[^/@]+@", re.IGNORECASE)
CREDENTIAL_OPTION_RE = re.compile(
    r"(?:api[-_]?key|access[-_]?token|auth[-_]?token|bearer[-_]?token|"
    r"client[-_]?secret|credentials?|password|passwd|secret|session[-_]?string|token)",
    re.IGNORECASE,
)


class McpSyncError(Exception):
    exit_code = 2


class McpConfigError(McpSyncError):
    exit_code = 3


@dataclass(frozen=True)
class McpSyncConfig:
    claude_root: Path = field(default_factory=lambda: Path.home() / ".claude")
    codex_root: Path = field(default_factory=lambda: Path.home() / ".codex")
    projects_root: Path = field(default_factory=lambda: Path.home() / "projects")
    project_roots: tuple[Path, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "claude_root", self.claude_root.expanduser().resolve())
        object.__setattr__(self, "codex_root", self.codex_root.expanduser().resolve())
        object.__setattr__(self, "projects_root", self.projects_root.expanduser().resolve())
        object.__setattr__(
            self,
            "project_roots",
            tuple(project.expanduser().resolve() for project in self.project_roots),
        )


@dataclass(frozen=True)
class SourceConfig:
    source: Path
    scope: str
    label: str
    preserve_server_names: bool
    project_root: Path | None = None


@dataclass(frozen=True)
class ImportedServer:
    active_name: str
    source_name: str
    source_file: Path
    scope: str
    project_root: Path | None
    command: str
    args: tuple[str, ...] = ()
    env: tuple[tuple[str, str], ...] = ()


@dataclass
class ImportPlan:
    sources: list[SourceConfig]
    servers: list[ImportedServer]
    copies: list[tuple[Path, Path, str]]
    warnings: list[str] = field(default_factory=list)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.strip()).strip("-").lower()
    if slug:
        return slug
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"id-{digest}"


def project_scope(project_root: Path) -> str:
    """Return a readable, collision-resistant identity for one project root."""
    resolved = project_root.expanduser().resolve()
    digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:12]
    return f"project-{slugify(resolved.name)}-{digest}"


def _absolute_unresolved(path: Path) -> Path:
    return Path(os.path.abspath(path.expanduser()))


def _path_components(root: Path, target: Path) -> list[Path]:
    root_abs = _absolute_unresolved(root)
    target_abs = _absolute_unresolved(target)
    try:
        relative = target_abs.relative_to(root_abs)
    except ValueError as exc:
        raise McpConfigError(f"path outside allowed root rejected: {target_abs}") from exc
    return [
        root_abs,
        *(root_abs / Path(*relative.parts[:index]) for index in range(1, len(relative.parts) + 1)),
    ]


def reject_symlink_components(path: Path, allowed_root: Path) -> None:
    """Reject an existing symlink anywhere below *allowed_root*."""
    for component in _path_components(allowed_root, path):
        if (component.exists() or component.is_symlink()) and component.is_symlink():
            raise McpConfigError(f"symlink path rejected: {component}")


def prepare_private_destination(path: Path, allowed_root: Path) -> None:
    """Create a private destination parent without following local symlinks."""
    reject_symlink_components(path.parent, allowed_root)
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    reject_symlink_components(path, allowed_root)
    root_abs = _absolute_unresolved(allowed_root)
    for component in _path_components(root_abs, path.parent):
        metadata = component.stat()
        if metadata.st_uid != os.getuid():
            raise McpConfigError(f"foreign-owned destination directory rejected: {component}")
        if component != root_abs and metadata.st_mode & 0o022:
            raise McpConfigError(f"unsafe writable destination directory rejected: {component}")


def reject_unsafe_source(path: Path, allowed_roots: tuple[Path, ...]) -> None:
    unresolved = _absolute_unresolved(path)
    resolved = unresolved.resolve()
    for root in allowed_roots:
        try:
            resolved.relative_to(root)
        except ValueError:
            continue
        reject_symlink_components(unresolved, root)
        metadata = unresolved.stat()
        if metadata.st_uid != os.getuid():
            raise McpConfigError(f"foreign-owned MCP source rejected: {unresolved}")
        if metadata.st_mode & 0o022:
            raise McpConfigError(f"group/world-writable MCP source rejected: {unresolved}")
        return
    raise McpConfigError(f"source outside allowed roots rejected: {resolved}")


def load_mcp_servers(
    source: SourceConfig, allowed_roots: tuple[Path, ...]
) -> tuple[dict[str, Any], bytes]:
    reject_unsafe_source(source.source, allowed_roots)
    try:
        raw = source.source.read_bytes()
        parsed = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise McpConfigError(f"invalid JSON in {source.source}") from exc
    except UnicodeDecodeError as exc:
        raise McpConfigError(f"non-UTF-8 MCP config rejected: {source.source}") from exc

    if not isinstance(parsed, dict):
        raise McpConfigError(f"MCP config must be a JSON object: {source.source}")
    servers = parsed.get("mcpServers", parsed.get("mcp_servers"))
    if servers is None and all(
        isinstance(value, dict) and "command" in value for value in parsed.values()
    ):
        servers = parsed
    if not isinstance(servers, dict):
        raise McpConfigError(f"MCP config has no mcpServers object: {source.source}")
    return servers, raw


def discover_project_roots(config: McpSyncConfig) -> list[Path]:
    roots = list(config.project_roots)
    if config.projects_root.exists():
        for child in sorted(config.projects_root.iterdir(), key=lambda item: item.name):
            if child.is_dir() and not child.is_symlink():
                roots.append(child.resolve())
    seen: set[Path] = set()
    unique: list[Path] = []
    for root in roots:
        if root not in seen:
            seen.add(root)
            unique.append(root)
    return unique


def discover_sources(config: McpSyncConfig) -> list[SourceConfig]:
    sources: list[SourceConfig] = []
    global_main = config.claude_root / ".mcp.json"
    if global_main.exists():
        sources.append(SourceConfig(global_main, "global", "global", True))

    for project in discover_project_roots(config):
        label = project_scope(project)
        source = project / ".mcp.json"
        if source.exists():
            sources.append(
                SourceConfig(
                    source,
                    label,
                    f"{label}-mcp",
                    True,
                    project_root=project,
                )
            )
    return sources


def _coerce_args(
    source: SourceConfig, name: str, data: dict[str, Any], warnings: list[str]
) -> tuple[str, ...] | None:
    raw_args = data.get("args", [])
    if raw_args is None:
        raw_args = []
    if not isinstance(raw_args, list) or not all(isinstance(item, str) for item in raw_args):
        warnings.append(f"skip {source.scope}:{name}: args must be a string list")
        return None
    for value in raw_args:
        option = value.split("=", 1)[0]
        is_credential_option = option.startswith("-") and CREDENTIAL_OPTION_RE.search(option)
        is_auth_header = "authorization:" in value.lower() or "authorization=" in value.lower()
        if is_credential_option or is_auth_header or CREDENTIAL_URL_RE.match(value):
            warnings.append(
                f"skip {source.scope}:{name}: secret-bearing argv is forbidden; use env"
            )
            return None
    return tuple(raw_args)


def _coerce_env(
    source: SourceConfig, name: str, data: dict[str, Any], warnings: list[str]
) -> tuple[tuple[str, str], ...] | None:
    raw_env = data.get("env", {})
    if raw_env is None:
        raw_env = {}
    if not isinstance(raw_env, dict):
        warnings.append(f"skip {source.scope}:{name}: env must be an object")
        return None

    env: list[tuple[str, str]] = []
    for key, value in sorted(raw_env.items()):
        if not isinstance(key, str) or not key:
            warnings.append(f"skip env entry in {source.scope}:{name}: invalid key")
            continue
        if isinstance(value, (str, int, float, bool)):
            env.append((key, str(value)))
        else:
            warnings.append(
                f"skip env entry in {source.scope}:{name}:{key}: unsupported value type"
            )
    return tuple(env)


def _allocate_server_name(source: SourceConfig, name: str, used_names: set[str]) -> str:
    base_name = slugify(name).replace("-", "_")
    active_name = (
        base_name
        if source.preserve_server_names
        else f"{slugify(source.scope).replace('-', '_')}__{base_name}"
    )
    candidate = active_name
    suffix = 2
    while candidate in used_names:
        candidate = f"{active_name}_{suffix}"
        suffix += 1
    used_names.add(candidate)
    return candidate


def coerce_server(
    source: SourceConfig, name: str, data: Any, used_names: set[str], warnings: list[str]
) -> ImportedServer | None:
    if not isinstance(data, dict):
        warnings.append(f"skip {source.scope}:{name}: server config is not an object")
        return None
    command = data.get("command")
    if not isinstance(command, str) or not command:
        warnings.append(f"skip {source.scope}:{name}: only command-based MCP servers are supported")
        return None
    args = _coerce_args(source, name, data, warnings)
    env = _coerce_env(source, name, data, warnings)
    if args is None or env is None:
        return None

    return ImportedServer(
        active_name=_allocate_server_name(source, name, used_names),
        source_name=name,
        source_file=source.source,
        scope=source.scope,
        project_root=source.project_root,
        command=command,
        args=args,
        env=env,
    )


def imported_copy_path(config: McpSyncConfig, source: SourceConfig) -> Path:
    return config.codex_root / "mcp-imported" / f"{source.scope}.mcp.json"


def build_plan(config: McpSyncConfig) -> ImportPlan:
    sources = discover_sources(config)
    allowed_roots = (config.claude_root, config.projects_root, *config.project_roots)
    warnings: list[str] = []
    servers: list[ImportedServer] = []
    copies: list[tuple[Path, Path, str]] = []
    target_sources: dict[Path, Path] = {}

    for source in sources:
        used_names: set[str] = set()
        try:
            source_servers, raw = load_mcp_servers(source, allowed_roots)
        except McpConfigError as exc:
            warnings.append(str(exc))
            continue
        target = imported_copy_path(config, source)
        previous_source = target_sources.get(target)
        if previous_source is not None and previous_source != source.source:
            raise McpConfigError(
                f"private MCP target collision: {previous_source} and {source.source} -> {target}"
            )
        target_sources[target] = source.source
        copies.append((source.source, target, sha256_bytes(raw)))
        for name, data in sorted(source_servers.items()):
            server = coerce_server(source, name, data, used_names, warnings)
            if server is not None:
                servers.append(server)

    return ImportPlan(sources=sources, servers=servers, copies=copies, warnings=warnings)


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def render_managed_block(
    servers: list[ImportedServer],
    *,
    private_config: Path,
    runner_script: Path,
) -> str:
    lines = [
        BEGIN_MARKER,
        "# Source: scoped Claude .mcp.json. Do not edit this block manually.",
    ]
    for server in sorted(servers, key=lambda item: item.active_name):
        rel_source = str(server.source_file)
        lines.extend(
            [
                "",
                f"# source = {toml_string(rel_source)}",
                f"# source_server = {toml_string(server.source_name)}",
                f"[mcp_servers.{server.active_name}]",
                f"command = {toml_string(sys.executable)}",
                "args = "
                + toml_array(
                    (
                        str(runner_script),
                        "--run-server",
                        str(private_config),
                        server.source_name,
                    )
                ),
            ]
        )
    lines.extend(["", END_MARKER, ""])
    return "\n".join(lines)


def replace_managed_block(existing: str, managed_block: str) -> str:
    start = existing.find(BEGIN_MARKER)
    end = existing.find(END_MARKER)
    if start != -1 and end != -1 and end > start:
        end += len(END_MARKER)
        prefix = existing[:start].rstrip()
        suffix = existing[end:].strip()
        parts = [part for part in (prefix, managed_block.rstrip(), suffix) if part]
        return "\n\n".join(parts) + "\n"
    if existing.strip():
        return existing.rstrip() + "\n\n" + managed_block
    return managed_block


def write_private(path: Path, content: bytes, *, allowed_root: Path | None = None) -> None:
    if allowed_root is not None:
        prepare_private_destination(path, allowed_root)
    else:
        path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
    finally:
        tmp_path = Path(tmp_name)
        if tmp_path.exists():
            tmp_path.unlink()


def write_text_private(path: Path, content: str, *, allowed_root: Path | None = None) -> None:
    write_private(path, content.encode("utf-8"), allowed_root=allowed_root)


def remove_managed_block(existing: str) -> str:
    start = existing.find(BEGIN_MARKER)
    end = existing.find(END_MARKER)
    if start == -1 or end == -1 or end <= start:
        return existing
    end += len(END_MARKER)
    prefix = existing[:start].rstrip()
    suffix = existing[end:].strip()
    parts = [part for part in (prefix, suffix) if part]
    return "\n\n".join(parts) + ("\n" if parts else "")


def git_exclude_path(project_root: Path) -> Path | None:
    git_marker = project_root / ".git"
    if not git_marker.exists() and not git_marker.is_symlink():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "--git-path", "info/exclude"],
            check=True,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise McpConfigError(f"cannot run git for local exclude in {project_root}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        suffix = f": {detail}" if detail else ""
        raise McpConfigError(f"cannot resolve git exclude for {project_root}{suffix}") from exc
    raw_path = result.stdout.strip()
    if not raw_path:
        return None
    path = Path(raw_path)
    return path if path.is_absolute() else project_root / path


def ensure_project_config_ignored(project_root: Path) -> None:
    exclude = git_exclude_path(project_root)
    if exclude is None:
        return
    exclude_root = exclude.parent.parent
    reject_symlink_components(exclude, exclude_root)
    pattern = "/.codex/config.toml"
    existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    if pattern in {line.strip() for line in existing.splitlines()}:
        return
    updated = existing.rstrip() + ("\n" if existing.strip() else "") + pattern + "\n"
    write_text_private(exclude, updated, allowed_root=exclude_root)


def _write_imported_copies(
    config: McpSyncConfig, plan: ImportPlan
) -> tuple[list[dict[str, str]], set[Path]]:
    entries: list[dict[str, str]] = []
    targets: set[Path] = set()
    for source, target, digest in plan.copies:
        content = source.read_bytes()
        if sha256_bytes(content) != digest:
            raise McpConfigError(f"MCP source changed while applying plan: {source}")
        write_private(target, content, allowed_root=config.codex_root)
        targets.add(target.resolve())
        entries.append({"source": str(source), "target": str(target), "sha256": digest})
    return entries, targets


def _prune_imported_copies(
    config: McpSyncConfig, old_manifest: dict[str, Any], current_targets: set[Path]
) -> None:
    imported_root = (config.codex_root / "mcp-imported").resolve()
    for entry in old_manifest.get("entries", []):
        if not isinstance(entry, dict):
            continue
        target = Path(entry.get("target", ""))
        try:
            target = target.expanduser().resolve()
            target.relative_to(imported_root)
        except (TypeError, ValueError, RuntimeError):
            continue
        if target not in current_targets and target.exists():
            target.unlink()


def _servers_by_source(plan: ImportPlan) -> dict[Path, list[ImportedServer]]:
    result: dict[Path, list[ImportedServer]] = {}
    for server in plan.servers:
        result.setdefault(server.source_file, []).append(server)
    return result


def _write_global_config(
    config: McpSyncConfig,
    plan: ImportPlan,
    servers_by_source: dict[Path, list[ImportedServer]],
    runner_script: Path,
) -> None:
    global_source = next((source for source in plan.sources if source.project_root is None), None)
    global_servers = (
        servers_by_source.get(global_source.source, []) if global_source is not None else []
    )
    private_config = (
        imported_copy_path(config, global_source)
        if global_source is not None
        else config.codex_root / "mcp-imported" / "global.mcp.json"
    )
    config_path = config.codex_root / "config.toml"
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    updated = replace_managed_block(
        existing,
        render_managed_block(
            global_servers,
            private_config=private_config,
            runner_script=runner_script,
        ),
    )
    if updated != existing:
        write_text_private(config_path, updated, allowed_root=config.codex_root)


def _write_project_configs(
    config: McpSyncConfig,
    plan: ImportPlan,
    servers_by_source: dict[Path, list[ImportedServer]],
    runner_script: Path,
) -> list[str]:
    project_configs: list[str] = []
    for source in plan.sources:
        if source.project_root is None:
            continue
        project_config = source.project_root / ".codex" / "config.toml"
        prepare_private_destination(project_config, source.project_root)
        project_configs.append(str(project_config))
        existing = project_config.read_text(encoding="utf-8") if project_config.exists() else ""
        updated = replace_managed_block(
            existing,
            render_managed_block(
                servers_by_source.get(source.source, []),
                private_config=imported_copy_path(config, source),
                runner_script=runner_script,
            ),
        )
        if updated != existing:
            write_text_private(project_config, updated, allowed_root=source.project_root)
        ensure_project_config_ignored(source.project_root)
    return project_configs


def _prune_project_configs(
    old_manifest: dict[str, Any], current_project_configs: list[str]
) -> None:
    for raw_path in old_manifest.get("project_configs", []):
        if not isinstance(raw_path, str):
            continue
        stale_config = Path(raw_path)
        if raw_path in current_project_configs or not stale_config.exists():
            continue
        existing = stale_config.read_text(encoding="utf-8")
        updated = remove_managed_block(existing)
        if updated != existing:
            write_text_private(stale_config, updated, allowed_root=stale_config.parent.parent)


def _build_manifest(
    plan: ImportPlan,
    entries: list[dict[str, str]],
    project_configs: list[str],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "entries": entries,
        "project_configs": sorted(project_configs),
        "servers": [
            {
                "active_name": server.active_name,
                "scope": server.scope,
                "source": str(server.source_file),
                "source_server": server.source_name,
            }
            for server in sorted(plan.servers, key=lambda item: (item.scope, item.active_name))
        ],
    }


def _prepare_plan_destinations(config: McpSyncConfig, plan: ImportPlan) -> None:
    prepare_private_destination(config.codex_root / MANIFEST_REL, config.codex_root)
    prepare_private_destination(config.codex_root / "config.toml", config.codex_root)
    for source in plan.sources:
        if source.project_root is not None:
            prepare_private_destination(
                source.project_root / ".codex" / "config.toml",
                source.project_root,
            )


def apply_plan(
    config: McpSyncConfig, plan: ImportPlan, update_config: bool = True, prune: bool = False
) -> None:
    old_manifest = read_manifest(config)
    _prepare_plan_destinations(config, plan)
    entries, current_targets = _write_imported_copies(config, plan)
    if prune:
        _prune_imported_copies(config, old_manifest, current_targets)
    project_configs: list[str] = []
    if update_config:
        runner_script = Path(__file__).resolve()
        by_source = _servers_by_source(plan)
        _write_global_config(config, plan, by_source, runner_script)
        project_configs = _write_project_configs(config, plan, by_source, runner_script)
        if prune:
            _prune_project_configs(old_manifest, project_configs)
    manifest = _build_manifest(plan, entries, project_configs)
    write_text_private(
        config.codex_root / MANIFEST_REL,
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        allowed_root=config.codex_root,
    )


def read_manifest(config: McpSyncConfig) -> dict[str, Any]:
    path = config.codex_root / MANIFEST_REL
    if not path.exists():
        return {}
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise McpConfigError(f"invalid MCP sync manifest: {path}") from exc
    if not isinstance(manifest, dict):
        raise McpConfigError(f"MCP sync manifest must be an object: {path}")
    return manifest


def print_plan(plan: ImportPlan) -> None:
    print(f"MCP sources: {len(plan.sources)}")
    print(f"MCP servers to import: {len(plan.servers)}")
    for server in sorted(plan.servers, key=lambda item: item.active_name):
        print(f"  {server.active_name} <= {server.source_file.name}:{server.source_name}")
    for warning in plan.warnings:
        print(f"warning: {warning}", file=sys.stderr)


def run_server(config_path: Path, server_name: str) -> int:
    source = SourceConfig(config_path.resolve(), "runtime", "runtime", True)
    servers, _raw = load_mcp_servers(source, (config_path.resolve().parent,))
    raw_server = servers.get(server_name)
    warnings: list[str] = []
    server = coerce_server(source, server_name, raw_server, set(), warnings)
    if server is None:
        detail = warnings[0] if warnings else f"unknown MCP server: {server_name}"
        raise McpConfigError(detail)
    env = dict(os.environ)
    env.update(dict(server.env))
    os.execvpe(server.command, [server.command, *server.args], env)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-root", type=Path, default=Path.home() / ".claude")
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--projects-root", type=Path, default=Path.home() / "projects")
    parser.add_argument("--project", action="append", type=Path, default=[])
    parser.add_argument(
        "--apply", action="store_true", help="write imported MCP configs and Codex config block"
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="copy imported MCP JSON files without updating config.toml",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="delete previously imported MCP files no longer present",
    )
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(argv or sys.argv[1:])
    if raw_argv[:1] == ["--run-server"]:
        if len(raw_argv) != 3:
            raise McpConfigError("usage: sync-mcp-to-codex.py --run-server CONFIG SERVER")
        return run_server(Path(raw_argv[1]), raw_argv[2])
    args = parse_args(raw_argv)
    config = McpSyncConfig(
        claude_root=args.claude_root,
        codex_root=args.codex_root,
        projects_root=args.projects_root,
        project_roots=tuple(args.project),
    )
    plan = build_plan(config)
    if not args.quiet:
        print_plan(plan)
        if not args.apply:
            print("Dry run only. Re-run with --apply to write changes.")
    if args.apply:
        apply_plan(config, plan, update_config=not args.no_config, prune=args.prune)
        if not args.quiet:
            print("MCP sync applied.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except McpSyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(exc.exit_code) from None
