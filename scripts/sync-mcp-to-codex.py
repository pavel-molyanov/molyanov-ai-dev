#!/usr/bin/env python3
"""Import private Claude MCP configs into the local Codex runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "1"
BEGIN_MARKER = "# BEGIN CLAUDE MCP IMPORT (managed by sync-mcp-to-codex)"
END_MARKER = "# END CLAUDE MCP IMPORT"
MANIFEST_REL = Path("mcp-imported/.sync/manifest.json")
SLUG_RE = re.compile(r"[^A-Za-z0-9_-]+")


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


@dataclass(frozen=True)
class ImportedServer:
    active_name: str
    source_name: str
    source_file: Path
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


def reject_unsafe_source(path: Path, allowed_roots: tuple[Path, ...]) -> None:
    resolved = path.resolve()
    if path.is_symlink() or any(parent.is_symlink() for parent in resolved.parents if parent.exists()):
        raise McpConfigError(f"symlink source rejected: {resolved}")
    for root in allowed_roots:
        try:
            resolved.relative_to(root)
        except ValueError:
            continue
        return
    raise McpConfigError(f"source outside allowed roots rejected: {resolved}")


def load_mcp_servers(source: SourceConfig, allowed_roots: tuple[Path, ...]) -> tuple[dict[str, Any], bytes]:
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
    if servers is None and all(isinstance(value, dict) and "command" in value for value in parsed.values()):
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
    global_bot = config.claude_root / ".mcp.bot.json"
    if global_main.exists():
        sources.append(SourceConfig(global_main, "global", "global", True))
    if global_bot.exists():
        sources.append(SourceConfig(global_bot, "global-bot", "global-bot", False))

    for project in discover_project_roots(config):
        label = f"project-{slugify(project.name)}"
        for name in (".mcp.json", ".mcp.bot.json"):
            source = project / name
            if source.exists():
                file_label = "mcp" if name == ".mcp.json" else "mcp-bot"
                sources.append(SourceConfig(source, label, f"{label}-{file_label}", False))
    return sources


def coerce_server(source: SourceConfig, name: str, data: Any, used_names: set[str], warnings: list[str]) -> ImportedServer | None:
    if not isinstance(data, dict):
        warnings.append(f"skip {source.scope}:{name}: server config is not an object")
        return None
    command = data.get("command")
    if not isinstance(command, str) or not command:
        warnings.append(f"skip {source.scope}:{name}: only command-based MCP servers are supported")
        return None

    raw_args = data.get("args", [])
    if raw_args is None:
        raw_args = []
    if not isinstance(raw_args, list) or not all(isinstance(item, str) for item in raw_args):
        warnings.append(f"skip {source.scope}:{name}: args must be a string list")
        return None

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
            warnings.append(f"skip env entry in {source.scope}:{name}:{key}: unsupported value type")

    base_name = slugify(name).replace("-", "_")
    if source.preserve_server_names:
        active_name = base_name
    else:
        active_name = f"{slugify(source.scope).replace('-', '_')}__{base_name}"
    candidate = active_name
    suffix = 2
    while candidate in used_names:
        candidate = f"{active_name}_{suffix}"
        suffix += 1
    used_names.add(candidate)

    return ImportedServer(
        active_name=candidate,
        source_name=name,
        source_file=source.source,
        command=command,
        args=tuple(raw_args),
        env=tuple(env),
    )


def imported_copy_path(config: McpSyncConfig, source: SourceConfig) -> Path:
    suffix = "mcp.bot.json" if source.source.name == ".mcp.bot.json" else "mcp.json"
    return config.codex_root / "mcp-imported" / f"{source.scope}.{suffix}"


def build_plan(config: McpSyncConfig) -> ImportPlan:
    sources = discover_sources(config)
    allowed_roots = (config.claude_root, config.projects_root, *config.project_roots)
    warnings: list[str] = []
    servers: list[ImportedServer] = []
    copies: list[tuple[Path, Path, str]] = []
    used_names: set[str] = set()

    for source in sources:
        try:
            source_servers, raw = load_mcp_servers(source, allowed_roots)
        except McpConfigError as exc:
            warnings.append(str(exc))
            continue
        copies.append((source.source, imported_copy_path(config, source), sha256_bytes(raw)))
        for name, data in sorted(source_servers.items()):
            server = coerce_server(source, name, data, used_names, warnings)
            if server is not None:
                servers.append(server)

    return ImportPlan(sources=sources, servers=servers, copies=copies, warnings=warnings)


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def render_managed_block(plan: ImportPlan) -> str:
    lines = [
        BEGIN_MARKER,
        f"# Generated at {datetime.now(timezone.utc).isoformat()}",
        "# Source: Claude .mcp*.json files. Do not edit this block manually.",
    ]
    for server in sorted(plan.servers, key=lambda item: item.active_name):
        rel_source = str(server.source_file)
        lines.extend(
            [
                "",
                f"# source = {toml_string(rel_source)}",
                f"# source_server = {toml_string(server.source_name)}",
                f"[mcp_servers.{server.active_name}]",
                f"command = {toml_string(server.command)}",
                f"args = {toml_array(server.args)}",
            ]
        )
        if server.env:
            lines.append("")
            lines.append(f"[mcp_servers.{server.active_name}.env]")
            for key, value in server.env:
                lines.append(f"{key} = {toml_string(value)}")
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


def write_private(path: Path, content: bytes) -> None:
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


def write_text_private(path: Path, content: str) -> None:
    write_private(path, content.encode("utf-8"))


def apply_plan(config: McpSyncConfig, plan: ImportPlan, update_config: bool = True, prune: bool = False) -> None:
    config.codex_root.mkdir(parents=True, exist_ok=True)
    imported_root = config.codex_root / "mcp-imported"
    imported_root.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(imported_root, 0o700)

    manifest_entries = []
    current_targets: set[Path] = set()
    for source, target, digest in plan.copies:
        content = source.read_bytes()
        write_private(target, content)
        current_targets.add(target.resolve())
        manifest_entries.append(
            {
                "source": str(source),
                "target": str(target),
                "sha256": digest,
            }
        )

    if prune:
        old_manifest = read_manifest(config)
        for entry in old_manifest.get("entries", []):
            target = Path(entry.get("target", ""))
            try:
                target = target.expanduser().resolve()
                target.relative_to(imported_root.resolve())
            except (ValueError, RuntimeError):
                continue
            if target not in current_targets and target.exists():
                target.unlink()

    if update_config:
        config_path = config.codex_root / "config.toml"
        existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
        updated = replace_managed_block(existing, render_managed_block(plan))
        if updated != existing:
            write_text_private(config_path, updated)

    manifest = {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": manifest_entries,
        "servers": [
            {
                "active_name": server.active_name,
                "source": str(server.source_file),
                "source_server": server.source_name,
            }
            for server in sorted(plan.servers, key=lambda item: item.active_name)
        ],
    }
    write_text_private(config.codex_root / MANIFEST_REL, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def read_manifest(config: McpSyncConfig) -> dict[str, Any]:
    path = config.codex_root / MANIFEST_REL
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def print_plan(plan: ImportPlan) -> None:
    print(f"MCP sources: {len(plan.sources)}")
    print(f"MCP servers to import: {len(plan.servers)}")
    for server in sorted(plan.servers, key=lambda item: item.active_name):
        print(f"  {server.active_name} <= {server.source_file.name}:{server.source_name}")
    for warning in plan.warnings:
        print(f"warning: {warning}", file=sys.stderr)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-root", type=Path, default=Path.home() / ".claude")
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--projects-root", type=Path, default=Path.home() / "projects")
    parser.add_argument("--project", action="append", type=Path, default=[])
    parser.add_argument("--apply", action="store_true", help="write imported MCP configs and Codex config block")
    parser.add_argument("--no-config", action="store_true", help="copy imported MCP JSON files without updating config.toml")
    parser.add_argument("--prune", action="store_true", help="delete previously imported MCP files no longer present")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
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
        raise SystemExit(exc.exit_code)
