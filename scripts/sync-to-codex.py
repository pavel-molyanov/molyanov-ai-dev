#!/usr/bin/env python3
"""Sync allowlisted Claude methodology files into Codex runtime files."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


VERSION = "1"
MANIFEST_REL = Path(".sync/claude-to-codex-manifest.json")
TEMPLATE_REL = Path("shared/templates/new-project")
SCRIPT_REL = Path("scripts/create-backlog.py")
LOCK_REL = Path(".sync/claude-to-codex.lock")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,80}$")

PROTECTED_PARTS = {
    "plugins",
    ".system",
    "cache",
    "log",
    "logs",
    "sessions",
    ".tmp",
    "tmp",
    "mcp-imported",
    "backups",
    "secrets",
    "history",
    "todos",
    "teams",
}
PROTECTED_NAMES = {
    "config.toml",
    "config.example.toml",
    "auth.json",
    "models_cache.json",
    "version.json",
    "credentials.json",
    "settings.json",
    "settings.local.json",
}
SECRET_LINE_RE = re.compile(
    r"(-----BEGIN .*PRIVATE KEY-----|(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9_]+|(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}|"
    r"\b[0-9]{8,10}:[A-Za-z0-9_-]{30,}\b|AKIA[0-9A-Z]{16}|"
    r"(password|secret|token|api[_-]?key)\s*=\s*[A-Za-z0-9_./+=:-]{8,})",
    re.IGNORECASE,
)
SECRET_PLACEHOLDER_RE = re.compile(r"(EXAMPLE|PLACEHOLDER|REDACTED|DUMMY|FAKE)", re.IGNORECASE)


@dataclass(frozen=True)
class SyncConfig:
    claude_root: Path = field(default_factory=lambda: Path.home() / ".claude")
    codex_root: Path = field(default_factory=lambda: Path.home() / ".codex")
    project_root: Path | None = None
    allow_project_outside_root: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "claude_root", self.claude_root.expanduser().resolve())
        object.__setattr__(self, "codex_root", self.codex_root.expanduser().resolve())
        if self.project_root is not None:
            object.__setattr__(self, "project_root", self.project_root.expanduser().resolve())


@dataclass
class PlanItem:
    action: str
    source: Path | None
    target: Path
    adapter: str
    content: str | None = None
    mode: int = 0o644
    reason: str = ""
    manifest_source: Path | None = None
    link_target: str | None = None


@dataclass
class SyncPlan:
    items: list[PlanItem]
    warnings: list[str] = field(default_factory=list)


class SyncError(Exception):
    exit_code = 2


class ProtectedPathError(SyncError):
    exit_code = 4


class ConflictError(SyncError):
    exit_code = 3


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def contains_secret_like_content(text: str) -> bool:
    for line in text.splitlines():
        if SECRET_LINE_RE.search(line) and not SECRET_PLACEHOLDER_RE.search(line):
            return True
    return False


def safe_relative(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ProtectedPathError(f"path outside allowed root: {resolved}") from exc
    if ".." in rel.parts:
        raise ProtectedPathError(f"path traversal rejected: {path}")
    return rel


def reject_protected_path(path: Path) -> None:
    if path.as_posix() in {
        "shared/templates/new-project/.mcp.bot.json",
        "shared/templates/new-project/.mcp.json",
    }:
        return
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & PROTECTED_PARTS:
        raise ProtectedPathError(f"protected path rejected: {path}")
    name = path.name.lower()
    if name in PROTECTED_NAMES:
        raise ProtectedPathError(f"protected filename rejected: {path}")
    if name.startswith(".env") and name != ".env.example":
        raise ProtectedPathError(f"env file rejected: {path}")
    if name.endswith((".key", ".pem", ".sqlite", ".db")):
        raise ProtectedPathError(f"protected extension rejected: {path}")
    if name.startswith(".mcp") or name in {"mcp.json", "mcp-config.json", "mcp-configs.json"}:
        raise ProtectedPathError(f"mcp-looking path rejected: {path}")


def validate_slug(slug: str) -> None:
    if not SLUG_RE.fullmatch(slug):
        raise ProtectedPathError(f"invalid generated path segment: {slug}")
    if slug.upper() in {"CON", "PRN", "AUX", "NUL"}:
        raise ProtectedPathError(f"reserved generated path segment: {slug}")


def reject_symlink(path: Path, allow_leaf: bool = False) -> None:
    current = Path(path.anchor) if path.is_absolute() else Path(".")
    parts = path.parts[1:] if path.is_absolute() else path.parts
    last_index = len(parts) - 1
    for index, part in enumerate(parts):
        current = current / part
        if allow_leaf and index == last_index:
            continue
        if current.exists() and current.is_symlink():
            raise ProtectedPathError(f"symlink rejected: {current}")


def is_agent_toml_rel(rel: Path) -> bool:
    """A managed agent .toml target where a mirrored symlink leaf is allowed."""
    if rel.suffix != ".toml":
        return False
    return (len(rel.parts) == 2 and rel.parts[0] == "agents") or (
        len(rel.parts) == 3 and rel.parts[:2] == (".codex", "agents")
    )


def is_command_skill_rel(rel: Path) -> bool:
    """A managed source-command skill dir where a mirrored symlink leaf is allowed."""
    leaf = rel.parts[-1] if rel.parts else ""
    if not leaf.startswith("source-command-"):
        return False
    return (len(rel.parts) == 2 and rel.parts[0] == "skills") or (
        len(rel.parts) == 3 and rel.parts[:2] == (".codex", "skills")
    )


def is_skill_dir_rel(rel: Path) -> bool:
    """A skills/<name> dir where a mirrored (nested-project) symlink leaf is allowed.

    Unlike command skills this matches any leaf name: shared skills live in
    nested-project and the parent project symlinks them (single source of truth).
    """
    return (len(rel.parts) == 2 and rel.parts[0] == "skills") or (
        len(rel.parts) == 3 and rel.parts[:2] == (".codex", "skills")
    )


def is_mirror_leaf_rel(rel: Path) -> bool:
    """Whether a managed target may carry a mirrored (nested-project) symlink leaf."""
    return is_agent_toml_rel(rel) or is_command_skill_rel(rel) or is_skill_dir_rel(rel)


def read_text_source(path: Path, root: Path) -> str:
    rel = safe_relative(path, root)
    reject_protected_path(rel)
    reject_symlink(path)
    text = path.read_text(encoding="utf-8")
    if contains_secret_like_content(text):
        raise ProtectedPathError(f"secret-looking source content rejected: {path}")
    return text


def lexical_relative(path: Path, root: Path) -> Path:
    """Relative path computed without following a symlink leaf.

    Resolves the parent directory only, so a managed symlink target (whose leaf
    points outside root) is still classified by its logical location under root.
    """
    resolved_parent = path.parent.resolve()
    try:
        rel_parent = resolved_parent.relative_to(root.resolve())
    except ValueError as exc:
        raise ProtectedPathError(f"path outside allowed root: {path}") from exc
    rel = rel_parent / path.name
    if ".." in rel.parts:
        raise ProtectedPathError(f"path traversal rejected: {path}")
    return rel


def validate_target(path: Path, root: Path, allow_template_stale: bool = False, symlink_leaf: bool = False) -> None:
    if symlink_leaf:
        rel = lexical_relative(path, root)
    else:
        safe_relative(path, root)
        rel = path.resolve().relative_to(root)
    reject_symlink(path, allow_leaf=symlink_leaf and is_mirror_leaf_rel(rel))
    allowed = (
        rel == Path("AGENTS.md")
        or rel.parts[:1] == ("skills",)
        or rel.parts[:1] == ("agents",)
        or rel.parts[:1] == ("commands",)
        or rel.parts[:3] == ("shared", "templates", "new-project")
        or rel == SCRIPT_REL
        or rel.parts[:1] == (".sync",)
    )
    if not allowed:
        raise ProtectedPathError(f"target outside allowlist: {path}")
    protected_check = rel
    if rel.parts[:1] == (".sync",):
        return
    if allow_template_stale and rel.parts[:3] == ("shared", "templates", "new-project"):
        return
    reject_protected_path(protected_check)


def validate_project_root(project_root: Path, allow_outside_root: bool = False) -> None:
    reject_symlink(project_root)
    if not project_root.is_dir():
        raise ProtectedPathError(f"project root is not a directory: {project_root}")
    if project_root.is_symlink():
        raise ProtectedPathError(f"project root symlink rejected: {project_root}")
    allowed_parent = Path.home() / "projects"
    if not allow_outside_root:
        try:
            project_root.relative_to(allowed_parent)
        except ValueError as exc:
            raise ProtectedPathError(f"project root outside {allowed_parent}: {project_root}") from exc
    for forbidden in (Path.home() / ".claude", Path.home() / ".codex"):
        try:
            project_root.relative_to(forbidden.resolve())
        except ValueError:
            pass
        else:
            raise ProtectedPathError(f"project root inside runtime directory rejected: {project_root}")


def validate_project_target(path: Path, project_root: Path, symlink_leaf: bool = False) -> None:
    if symlink_leaf:
        rel = lexical_relative(path, project_root)
    else:
        rel = safe_relative(path, project_root)
    reject_symlink(path, allow_leaf=symlink_leaf and is_mirror_leaf_rel(rel))
    allowed = (
        rel == Path("AGENTS.md")
        or rel.parts[:1] == (".codex",)
    )
    if not allowed:
        raise ProtectedPathError(f"project target outside allowlist: {path}")
    if rel.parts[:2] == (".codex", ".sync"):
        return
    reject_protected_path(rel)


def sync_root(config: SyncConfig) -> Path:
    return config.project_root if config.project_root is not None else config.codex_root


def manifest_path(config: SyncConfig) -> Path:
    if config.project_root is not None:
        return config.project_root / ".codex" / MANIFEST_REL
    return config.codex_root / MANIFEST_REL


def lock_path(config: SyncConfig) -> Path:
    if config.project_root is not None:
        return config.project_root / ".codex" / LOCK_REL
    return config.codex_root / LOCK_REL


def validate_any_target(path: Path, config: SyncConfig, allow_template_stale: bool = False, symlink_leaf: bool = False) -> None:
    if config.project_root is not None:
        validate_project_target(path, config.project_root, symlink_leaf=symlink_leaf)
    else:
        validate_target(path, config.codex_root, allow_template_stale=allow_template_stale, symlink_leaf=symlink_leaf)


def add_header(content: str, source: Path, comment: str) -> str:
    marker = f"Generated from {source} by sync-to-codex v{VERSION}. Do not edit directly."
    line = f"{comment[0]} {marker} {comment[1]}\n" if len(comment) == 2 else f"{comment}{marker}\n"
    if content.startswith(line):
        return content
    if comment == "# " and content.startswith("#!"):
        first_newline = content.find("\n") + 1
        return content[:first_newline] + line + content[first_newline:]
    return line + content


def add_generated_header(content: str, comment: str) -> str:
    marker = f"Generated by sync-to-codex v{VERSION}. Do not edit directly."
    if comment == "#":
        line = f"# {marker}\n"
        return content if content.startswith(line) else line + content
    line = f"{comment[0]} {marker} {comment[1]}\n" if len(comment) == 2 else f"{comment}{marker}\n"
    if content.startswith(line):
        return content
    if content.startswith("---\n"):
        end = content.find("\n---", 4)
        if end != -1:
            insert_at = content.find("\n", end + 4) + 1
            return content[:insert_at] + line + content[insert_at:]
    return line + content


def adapt_common_text(text: str) -> str:
    replacements = [
        ("CLAUDE.md", "AGENTS.md"),
        (".claude/", ".codex/"),
        (".claude", ".codex"),
        ("~/.claude", "~/.codex"),
        ("Claude Code", "Codex"),
        ("TodoWrite", "update_plan"),
        ("TaskCreate", "spawn_agent"),
        ("TeamCreate", "spawn_agent worker/explorer orchestration"),
        ("AskUserQuestion", "plain chat question"),
        ("Task tool", "spawn_agent"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def adapt_tool_terms(text: str) -> str:
    replacements = [
        ("TodoWrite", "update_plan"),
        ("TaskCreate", "spawn_agent"),
        ("TeamCreate", "spawn_agent worker/explorer orchestration"),
        ("AskUserQuestion", "plain chat question"),
        ("Task tool", "spawn_agent"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def strip_frontmatter(text: str) -> tuple[dict[str, str | list[str]], str]:
    """Parse a Markdown YAML frontmatter block.

    Handles the subset of YAML our agent/skill/command files actually use:
    - inline scalars (`key: value`),
    - block scalars (`key: |` / `key: >`, value collected from indented lines),
    - block sequences (`key:` then indented `- item` lines),
    - inline comma scalars stay raw strings; callers normalize via frontmatter_list.
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip("\n")
    body_start = text.find("\n", end + 4)
    body = text[body_start + 1 :] if body_start != -1 else ""
    meta: dict[str, str | list[str]] = {}
    lines = raw.splitlines()
    index = 0
    total = len(lines)
    while index < total:
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):(.*)$", line)
        if not match:
            index += 1
            continue
        key = match.group(1).strip()
        value = match.group(2).strip()
        if value and value[0] in "|>":
            index += 1
            collected: list[str] = []
            while index < total:
                nxt = lines[index]
                if nxt.strip() == "":
                    collected.append("")
                    index += 1
                elif nxt[0] in " \t":
                    collected.append(nxt.strip())
                    index += 1
                else:
                    break
            while collected and collected[-1] == "":
                collected.pop()
            meta[key] = "\n".join(collected)
        elif value == "":
            index += 1
            items: list[str] = []
            while index < total:
                nxt = lines[index]
                if nxt.strip() == "":
                    index += 1
                    continue
                item_match = re.match(r"^\s+-\s+(.*)$", nxt)
                if item_match:
                    items.append(item_match.group(1).strip())
                    index += 1
                elif nxt[0] in " \t":
                    # Indented but not a `- item`: nested mapping or unsupported
                    # YAML. Fail loud rather than silently yield an empty list,
                    # which could mis-map sandbox_mode/skills.
                    raise SyncError(f"unsupported frontmatter under {key!r}: {nxt!r}")
                else:
                    break
            meta[key] = items
        else:
            meta[key] = value
            index += 1
    return meta, body


def frontmatter_list(value: str | list[str] | None) -> list[str]:
    """Normalize a frontmatter field to a list of tokens.

    Accepts YAML block sequences (already a list) and inline comma strings
    (`Read, Glob, Edit`), so allowed-tools/skills detection is format-agnostic.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [token.strip() for token in value if token.strip()]
    return [token.strip() for token in value.split(",") if token.strip()]


TOML_AGENT_KEYS = ("name", "description", "developer_instructions", "sandbox_mode")
WRITE_TOOLS = {"write", "edit", "multiedit", "bash", "notebookedit"}


def toml_basic_string(value: str) -> str:
    """Serialize a Python string as a single-line TOML basic string.

    Single-line (newlines escaped as \\n) avoids the multi-line `\"\"\"` delimiter
    edge cases entirely, so arbitrary agent bodies — including quotes, backslashes
    and `sandbox_mode = "danger-full-access"`-looking text — cannot break out of the
    string value. Round-trip validation in serialize_agent_toml is the safety net.
    """
    out: list[str] = []
    for char in value:
        code = ord(char)
        if char == "\\":
            out.append("\\\\")
        elif char == '"':
            out.append('\\"')
        elif char == "\n":
            out.append("\\n")
        elif char == "\t":
            out.append("\\t")
        elif char == "\r":
            out.append("\\r")
        elif char == "\b":
            out.append("\\b")
        elif char == "\f":
            out.append("\\f")
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\u{code:04X}")
        else:
            out.append(char)
    return '"' + "".join(out) + '"'


def serialize_agent_toml(fields: dict[str, str]) -> str:
    """Emit a Codex agent TOML from string fields, validating by round-trip parse.

    Only keys from TOML_AGENT_KEYS are allowed (Codex uses deny_unknown_fields).
    After serialization we parse it back with tomllib and assert keys and values
    match exactly — any escaping defect or injected key fails loudly instead of
    silently producing a malicious file.
    """
    unknown = set(fields) - set(TOML_AGENT_KEYS)
    if unknown:
        raise SyncError(f"unexpected agent TOML keys: {sorted(unknown)}")
    lines = [f"{key} = {toml_basic_string(fields[key])}" for key in TOML_AGENT_KEYS if key in fields]
    content = "\n".join(lines) + "\n"
    parsed = tomllib.loads(content)
    if set(parsed) != set(fields):
        raise SyncError(f"agent TOML key mismatch after round-trip: {sorted(parsed)} != {sorted(fields)}")
    for key, value in fields.items():
        if parsed[key] != value:
            raise SyncError(f"agent TOML round-trip mismatch for key {key!r}")
    return content


def sandbox_mode_for_tools(allowed_tools: list[str]) -> str:
    """Map Claude allowed-tools to a Codex sandbox_mode.

    Write-capable tools (Write/Edit/Bash/...) -> workspace-write. Anything else,
    including an empty/missing list, defaults to the strictest read-only so a
    missing field never silently grants write access.
    """
    for tool in allowed_tools:
        if tool.strip().lower() in WRITE_TOOLS:
            return "workspace-write"
    return "read-only"


def build_agent_toml(source: Path, source_root: Path) -> str | None:
    """Generate a Codex agent .toml from a Claude agent .md, or None to skip.

    Skips like the official migrator: missing name/description or empty body.
    """
    text = read_text_source(source, source_root)
    meta, body = strip_frontmatter(text)
    name = meta.get("name")
    description = meta.get("description")
    instructions = adapt_tool_terms(body).strip()
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(description, str) or not description.strip():
        return None
    if not instructions:
        return None
    validate_slug(name.strip())
    skills = frontmatter_list(meta.get("skills"))
    if skills:
        pointers = "\n".join(
            f"- Before starting, load the methodology from `.codex/skills/{skill}/SKILL.md`."
            for skill in skills
        )
        instructions = f"{instructions}\n\n## Required methodology\n\n{pointers}"
    assert_no_operational_leftovers(instructions, source)
    fields = {
        "name": name.strip(),
        "description": description.strip(),
        "developer_instructions": instructions,
        "sandbox_mode": sandbox_mode_for_tools(frontmatter_list(meta.get("allowed-tools"))),
    }
    content = serialize_agent_toml(fields)
    return add_generated_header(content, "#")


def validate_skill_frontmatter(content: str, source: Path) -> None:
    meta, _ = strip_frontmatter(content)
    if not meta.get("name"):
        raise SyncError(f"skill frontmatter missing name: {source}")
    if not meta.get("description"):
        raise SyncError(f"skill frontmatter missing description: {source}")
    validate_slug(meta["name"])


def assert_no_operational_leftovers(content: str, target: Path) -> None:
    blocked = [
        "TodoWrite",
        "TaskCreate",
        "TeamCreate",
        "AskUserQuestion",
        "Task tool",
        "Read .claude/",
        "Use .claude/",
    ]
    for token in blocked:
        if token in content:
            raise SyncError(f"operational Claude leftover {token!r} in {target}")


def template_target_rel(source_rel: Path) -> Path | None:
    parts = list(source_rel.parts)
    if parts == ["CLAUDE.md"]:
        return Path("AGENTS.md")
    if parts[:1] == [".claude"]:
        if source_rel.name.startswith("settings") and source_rel.suffix == ".json":
            return None
        parts[0] = ".codex"
    return Path(*parts)


def template_codex_target_rel(source_rel: Path) -> Path | None:
    parts = list(source_rel.parts)
    if parts == ["CLAUDE.md"]:
        return Path("AGENTS.md")
    if parts[:1] == [".claude"]:
        if source_rel.name.startswith("settings") and source_rel.suffix == ".json":
            return None
        parts[0] = ".codex"
        return Path(*parts)
    return None


def adapt_template_file(source: Path, source_root: Path) -> str:
    text = adapt_common_text(read_text_source(source, source_root))
    if source.suffix == ".md":
        return add_generated_header(text, ("<!--", "-->"))
    return text


def adapt_skill_file(source: Path, source_root: Path) -> str:
    text = adapt_tool_terms(read_text_source(source, source_root))
    if source.name == "SKILL.md":
        validate_skill_frontmatter(text, source)
    if source.suffix == ".md":
        text = add_generated_header(text, ("<!--", "-->"))
    return text


def adapt_create_backlog(source: Path, source_root: Path) -> str:
    original = read_text_source(source, source_root)
    text = adapt_common_text(original)
    text = text.replace("Create a vault backlog for a new project.", "Create a vault backlog for a new project instructions file.")
    text = text.replace("Adds Backlog: line to the project's AGENTS.md", "Adds Backlog: line to the project's instructions file")
    text = text.replace("--claude-md ./AGENTS.md", "--instructions-md ./AGENTS.md")
    text = text.replace(
        'def update_claude_md(claude_md_path: str, slug: str) -> None:\n    """Add Backlog: line to the project\'s AGENTS.md."""\n    path = Path(claude_md_path).resolve()\n    if not path.exists():\n        print(f"AGENTS.md not found: {path}")\n        return',
        'def update_instructions_md(instructions_md_path: str, slug: str) -> None:\n    """Add Backlog: line to the project\'s instructions file."""\n    path = Path(instructions_md_path).resolve()\n    if not path.exists():\n        print(f"Instructions file not found: {path}")\n        return',
    )
    text = text.replace("update_claude_md", "update_instructions_md")
    text = text.replace(
        '    parser.add_argument("--claude-md", required=True, help="Path to project\'s AGENTS.md")\n    args = parser.parse_args()',
        '    parser.add_argument("--instructions-md", help="Path to project instructions file, usually AGENTS.md")\n'
        '    parser.add_argument("--claude-md", dest="claude_md", help="Deprecated alias for --instructions-md")\n'
        "    args = parser.parse_args()\n"
        "    if not args.instructions_md:\n"
        "        args.instructions_md = args.claude_md\n"
        "        if args.instructions_md:\n"
        '            print("Warning: --claude-md is deprecated; use --instructions-md.", file=sys.stderr)\n'
        "    if not args.instructions_md:\n"
        '        parser.error("--instructions-md is required (or deprecated --claude-md)")',
    )
    text = text.replace("update_instructions_md(args.codex_md, args.slug)", "update_instructions_md(args.instructions_md, args.slug)")
    text = text.replace("update_instructions_md(args.claude_md, args.slug)", "update_instructions_md(args.instructions_md, args.slug)")
    return add_header(text, source, "# ")


def source_name(path: Path) -> str:
    validate_slug(path.stem)
    return path.stem


def is_syncable_file(rel: Path) -> bool:
    """Whether a skill/template file should be synced.

    Compiled Python bytecode under `__pycache__` is regenerable build output, not
    source, and is binary so it cannot be read as UTF-8 text. Skipping it keeps the
    sync from crashing on projects whose skills ship helper scripts (e.g. SEO tools).
    """
    if "__pycache__" in rel.parts:
        return False
    return rel.suffix not in (".pyc", ".pyo")


def mirror_agent_link(link: str) -> str:
    """Mirror a Claude agent symlink string into its Codex equivalent.

    Rewrites each `.claude` path component to `.codex` and the `.md` leaf suffix
    to `.toml`, preserving the relative shape (e.g.
    `../../nested-project/.claude/agents/x.md` -> `../../nested-project/.codex/agents/x.toml`).
    """
    parts = link.split("/")
    mirrored: list[str] = []
    for index, part in enumerate(parts):
        if part == ".claude":
            mirrored.append(".codex")
        elif index == len(parts) - 1 and part.endswith(".md"):
            mirrored.append(part[:-3] + ".toml")
        else:
            mirrored.append(part)
    return "/".join(mirrored)


def mirror_skill_link(link: str) -> str:
    """Mirror a Claude skill-dir symlink into its Codex equivalent.

    Only rewrites `.claude` path components to `.codex`; the `skills/<name>` dir
    shape is preserved (e.g. `../../nested-project/.claude/skills/task-manager`
    -> `../../nested-project/.codex/skills/task-manager`).
    """
    return "/".join(".codex" if part == ".claude" else part for part in link.split("/"))


def assert_mirror_source_shape(link: str, kind: str, *, leaf_is_dir: bool = False) -> None:
    """Reject a symlink whose target is not a genuine Claude `kind` artifact.

    Only `<ascent>.../<dirs>/.claude/<kind>/<name>`-shaped destinations are
    mirrored. The check is *positional*, not membership-based: the final three
    components must be exactly `.claude`, `<kind>`, `<name>`, and `..` is only
    permitted as a contiguous leading prefix. Otherwise a link like
    `../.claude/agents/../../secrets/x.md` (tokens present, but `..` re-escapes
    into another in-root file) would slip past, letting Codex load an arbitrary
    file as an agent/command definition. `leaf_is_dir` accepts a skill directory
    leaf (`.claude/skills/<name>`) instead of an `.md` file leaf.
    """
    if link.startswith("/"):
        raise ProtectedPathError(f"mirrored {kind} symlink must be relative: {link}")
    parts = link.split("/")
    seen_non_ascent = False
    for part in parts:
        if part == "..":
            if seen_non_ascent:
                raise ProtectedPathError(f"mirrored {kind} symlink has non-leading '..': {link}")
            continue
        if part in ("", "."):
            raise ProtectedPathError(f"mirrored {kind} symlink has empty/'.' segment: {link}")
        seen_non_ascent = True
    tail = parts[-3:]
    leaf_ok = bool(tail[2]) and not tail[2].endswith(".md") if leaf_is_dir else tail[2].endswith(".md")
    if len(tail) != 3 or tail[0] != ".claude" or tail[1] != kind or not leaf_ok:
        suffix = "<name>" if leaf_is_dir else "<name>.md"
        raise ProtectedPathError(f"mirrored {kind} symlink must end .claude/{kind}/{suffix}: {link}")


def assert_mirror_link_contained(target: Path, link: str, root: Path) -> None:
    """Reject a mirrored symlink whose destination lexically escapes the sync root.

    Purely lexical (no resolve), so a still-uncreated nested-project target is fine,
    while an absolute or `../`-escaping link that could point Codex at a file
    outside the repo is rejected — parity with the old containment guard.
    """
    destination = Path(os.path.normpath(os.path.join(str(target.parent), link)))
    try:
        destination.relative_to(root.resolve())
    except ValueError as exc:
        raise ProtectedPathError(f"mirrored symlink escapes root: {target} -> {link}") from exc
    # When the destination already exists, an intermediate directory in the link
    # could itself be a symlink pointing outside root; the lexical check above
    # cannot see that, so confirm the real path stays contained.
    if destination.exists():
        real = Path(os.path.realpath(destination))
        try:
            real.relative_to(root.resolve())
        except ValueError as exc:
            raise ProtectedPathError(f"mirrored symlink resolves outside root: {target} -> {link}") from exc


def classify_symlink(target: Path, link_target: str, manifest_links: dict[str, str]) -> str:
    """Classify a managed symlink without ever resolving its (possibly dangling) target."""
    if not target.is_symlink():
        if target.exists():
            return "conflict target edited"
        return "create"
    current = os.readlink(target)
    if current == link_target:
        return "skip unchanged"
    previous = manifest_links.get(str(target))
    if previous is not None and current == previous:
        return "update"
    return "conflict target edited"


def make_agent_item(
    source: Path,
    read_root: Path,
    target_dir: Path,
    adapter: str,
    config: SyncConfig,
    manifest_targets: dict[str, str],
    manifest_links: dict[str, str],
) -> PlanItem | None:
    """Build a plan item for one Claude agent source.

    Real files become a generated `.toml`; symlinks are mirrored as symlinks so
    the single-source-of-truth layout (nested-project) is preserved in Codex too.
    Returns None when the agent has no name/description/body (skipped like the
    official migrator), or when the slug collides with config.toml.
    """
    name = source_name(source)
    if name == "config":
        return None
    target = target_dir / f"{name}.toml"
    if source.is_symlink():
        raw_link = os.readlink(source)
        assert_mirror_source_shape(raw_link, "agents")
        link = mirror_agent_link(raw_link)
        assert_mirror_link_contained(target, link, sync_root(config))
        validate_any_target(target, config, symlink_leaf=True)
        return PlanItem(
            action=classify_symlink(target, link, manifest_links),
            source=source,
            target=target,
            adapter=adapter,
            content=None,
            link_target=link,
            manifest_source=source,
        )
    content = build_agent_toml(source, read_root)
    if content is None:
        return None
    validate_any_target(target, config)
    return PlanItem(
        action=classify_managed_write(target, content, manifest_targets),
        source=source,
        target=target,
        adapter=adapter,
        content=content,
        manifest_source=source,
    )


def inject_init_project_asserts(text: str) -> str:
    old_codex = "After copy:\n- Verify `.codex/skills/project-knowledge/` exists"
    old_claude = "After copy:\n- Verify `.claude/skills/project-knowledge/` exists"
    new = """After copy:
- Generate Codex runtime files from Claude source:

```bash
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

- Verify required dual-runtime files exist before any registry, backlog, git, or GitHub step:

```bash
REQUIRED_PATHS=(
  "CLAUDE.md"
  ".claude/skills/project-knowledge/SKILL.md"
  ".claude/skills/project-knowledge/references/project.md"
  "AGENTS.md"
  ".codex/skills/project-knowledge/SKILL.md"
  ".codex/skills/project-knowledge/references/project.md"
  "README.md"
  ".env.example"
  ".gitignore"
  "work/completed/.gitkeep"
)

for path in "${REQUIRED_PATHS[@]}"; do
  if [ ! -e "$path" ]; then
    echo "Dual-runtime template assertion failed: missing $path" >&2
    exit 1
  fi
done
```"""
    if old_codex in text:
        text = text.replace(old_codex, new)
    if old_claude in text:
        text = text.replace(old_claude, new)
    return text


def adapt_command_body(source: Path, source_root: Path) -> str:
    _, body = strip_frontmatter(read_text_source(source, source_root))
    body = adapt_tool_terms(body).lstrip()
    if source.stem == "init-project":
        body = inject_init_project_asserts(body)
    policy = (
        "## Codex Policy Gates\n\n"
        "- Ask before external actions such as GitHub repository creation, `git push`, deploys, or sending messages unless the user explicitly requested that exact action.\n"
        "- Deployments must go through GitHub CI/CD; direct server access is only for emergency debugging of broken production.\n"
        "- Never ask the user to paste secrets in chat. Direct them to `.env` files or GitHub Actions secrets.\n\n"
    )
    if "## Codex Policy Gates" not in body:
        body = policy + body
    return body


def command_skill_slug(name: str) -> str:
    """Codex skill slug for a Claude command, matching the official migrator prefix."""
    slug = f"source-command-{name}"[:64]
    validate_slug(slug)
    return slug


def build_command_skill(source: Path, source_root: Path) -> tuple[str, str]:
    """Return (slug, SKILL.md content) for a Claude command rendered as a Codex skill."""
    name = source_name(source)
    slug = command_skill_slug(name)
    body = adapt_command_body(source, source_root)
    content = (
        "---\n"
        f"name: {slug}\n"
        f"description: Converted Codex workflow from Claude slash command `{name}`. Use when the user asks to run the equivalent command or describes this workflow.\n"
        "---\n\n"
        f"# Command Workflow: {name}\n\n"
        "Treat Claude-only tool names as conceptual workflow steps and use available Codex tools/policies.\n\n"
        f"{body}"
    )
    content = add_generated_header(content, ("<!--", "-->"))
    assert_no_operational_leftovers(content, source)
    return slug, content


def make_command_item(
    source: Path,
    read_root: Path,
    skills_dir: Path,
    adapter: str,
    config: SyncConfig,
    manifest_targets: dict[str, str],
    manifest_links: dict[str, str],
) -> PlanItem | None:
    """Build a plan item for one Claude command as a Codex source-command skill.

    Symlinked command sources are mirrored as symlinks (parity with agents);
    real files generate the SKILL.md. config-named commands are skipped.
    """
    name = source_name(source)
    if name == "config":
        return None
    slug = command_skill_slug(name)
    if source.is_symlink():
        target = skills_dir / slug
        raw_link = os.readlink(source)
        assert_mirror_source_shape(raw_link, "commands")
        link = mirror_command_link(raw_link, slug)
        assert_mirror_link_contained(target, link, sync_root(config))
        validate_any_target(target, config, symlink_leaf=True)
        return PlanItem(
            action=classify_symlink(target, link, manifest_links),
            source=source,
            target=target,
            adapter=adapter,
            content=None,
            link_target=link,
            manifest_source=source,
        )
    slug, content = build_command_skill(source, read_root)
    target = skills_dir / slug / "SKILL.md"
    validate_any_target(target, config)
    return PlanItem(
        action=classify_managed_write(target, content, manifest_targets),
        source=source,
        target=target,
        adapter=adapter,
        content=content,
        manifest_source=source,
    )


def mirror_command_link(link: str, slug: str) -> str:
    """Mirror a Claude command symlink into a Codex source-command skill-dir symlink."""
    parts = link.split("/")
    mirrored: list[str] = []
    for index, part in enumerate(parts):
        if part == ".claude":
            mirrored.append(".codex")
        elif part == "commands":
            mirrored.append("skills")
        elif index == len(parts) - 1 and part.endswith(".md"):
            mirrored.append(slug)
        else:
            mirrored.append(part)
    return "/".join(mirrored)


def make_skill_symlink_item(
    source: Path,
    skills_dir: Path,
    adapter: str,
    config: SyncConfig,
    manifest_links: dict[str, str],
) -> PlanItem:
    """Mirror a symlinked skill directory (shared from nested-project) as a symlink.

    Keeps the single-source-of-truth layout in Codex too: the parent project
    points at nested-project's `.codex/skills/<name>` rather than duplicating files.
    """
    name = source.name
    validate_slug(name)
    target = skills_dir / name
    raw_link = os.readlink(source)
    assert_mirror_source_shape(raw_link, "skills", leaf_is_dir=True)
    link = mirror_skill_link(raw_link)
    assert_mirror_link_contained(target, link, sync_root(config))
    validate_any_target(target, config, symlink_leaf=True)
    return PlanItem(
        action=classify_symlink(target, link, manifest_links),
        source=source,
        target=target,
        adapter=adapter,
        content=None,
        link_target=link,
        manifest_source=source,
    )


def build_template_items(config: SyncConfig) -> list[PlanItem]:
    source_root = config.claude_root / TEMPLATE_REL
    target_root = config.codex_root / TEMPLATE_REL
    if not source_root.is_dir():
        raise SyncError(f"missing source template: {source_root}")
    items: list[PlanItem] = []
    for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
        source_rel = source.relative_to(source_root)
        if not is_syncable_file(source_rel):
            continue
        if source_rel.parts[:1] == (".claude",) and source.name.startswith("settings") and source.suffix == ".json":
            continue
        source_content = read_text_source(source, config.claude_root)
        source_target = target_root / source_rel
        validate_target(source_target, config.codex_root)
        items.append(
            PlanItem(
                action=classify_write(source_target, source_content),
                source=source,
                target=source_target,
                adapter="new-project-template",
                content=source_content,
            )
        )
        codex_rel = template_codex_target_rel(source_rel)
        if codex_rel is None:
            continue
        content = adapt_template_file(source, config.claude_root)
        target = target_root / codex_rel
        validate_target(target, config.codex_root)
        action = classify_write(target, content)
        items.append(PlanItem(action=action, source=source, target=target, adapter="new-project-template", content=content))
    return items


def build_script_item(config: SyncConfig) -> PlanItem:
    source = config.claude_root / SCRIPT_REL
    target = config.codex_root / SCRIPT_REL
    content = adapt_create_backlog(source, config.claude_root)
    validate_target(target, config.codex_root)
    return PlanItem(action=classify_write(target, content), source=source, target=target, adapter="script", content=content, mode=0o755)


def build_skill_items(config: SyncConfig) -> list[PlanItem]:
    source_root = config.claude_root / "skills"
    target_root = config.codex_root / "skills"
    if not source_root.is_dir():
        return []
    items: list[PlanItem] = []
    skill_names: set[str] = set()
    for skill_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        validate_slug(skill_dir.name)
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = read_text_source(skill_md, config.claude_root)
            meta, _ = strip_frontmatter(content)
            if meta.get("name"):
                if meta["name"] in skill_names:
                    raise SyncError(f"duplicate skill name: {meta['name']}")
                skill_names.add(meta["name"])
        for source in sorted(path for path in skill_dir.rglob("*") if path.is_file()):
            source_rel = source.relative_to(source_root)
            if not is_syncable_file(source_rel):
                continue
            target = target_root / source_rel
            content = adapt_skill_file(source, config.claude_root)
            validate_target(target, config.codex_root)
            items.append(PlanItem(action=classify_write(target, content), source=source, target=target, adapter="skill", content=content))
    return items


def build_agent_items(
    config: SyncConfig,
    manifest_targets: dict[str, str],
    manifest_links: dict[str, str],
) -> list[PlanItem]:
    source_root = config.claude_root / "agents"
    if not source_root.is_dir():
        return []
    target_dir = config.codex_root / "agents"
    items: list[PlanItem] = []
    for source in sorted(source_root.glob("*.md")):
        item = make_agent_item(source, config.claude_root, target_dir, "agent", config, manifest_targets, manifest_links)
        if item is not None:
            items.append(item)
    return items


def build_command_items(
    config: SyncConfig,
    manifest_targets: dict[str, str],
    manifest_links: dict[str, str],
) -> list[PlanItem]:
    source_root = config.claude_root / "commands"
    if not source_root.is_dir():
        return []
    skills_dir = config.codex_root / "skills"
    items: list[PlanItem] = []
    for source in sorted(source_root.glob("*.md")):
        item = make_command_item(source, config.claude_root, skills_dir, "command", config, manifest_targets, manifest_links)
        if item is not None:
            items.append(item)
    return items


def classify_write(target: Path, content: str) -> str:
    if not target.exists():
        return "create"
    if target.read_text(encoding="utf-8") == content:
        return "skip unchanged"
    return "update"


STALE_GLOBS = ("skills/claude-agent-*", "skills/claude-command-*", "agents/*.md", "commands/*")


def build_stale_items(base: Path, prune: bool, reason: str) -> list[PlanItem]:
    """Collect legacy wrapper artifacts under a Codex base dir for pruning.

    Old layout used `skills/claude-agent-*`, `skills/claude-command-*`,
    markdown `agents/*.md` references, and a dead `commands/*` mirror; the new
    layout emits `agents/*.toml` and `skills/source-command-*` instead.
    """
    stale_paths: list[Path] = []
    for pattern in STALE_GLOBS:
        for path in sorted(base.glob(pattern)):
            stale_paths.append(path)
    action = "delete" if prune else "stale managed"
    return [
        PlanItem(action=action, source=None, target=path, adapter="stale", reason=reason)
        for path in stale_paths
    ]


def build_template_stale_items(config: SyncConfig, prune: bool) -> list[PlanItem]:
    template_root = config.codex_root / TEMPLATE_REL
    stale_settings = template_root / ".claude" / "settings.json"
    if not stale_settings.exists():
        return []
    action = "delete" if prune else "stale managed"
    return [PlanItem(action=action, source=None, target=stale_settings, adapter="new-project-template", reason="Claude-shaped template leftover")]


def build_project_items(
    config: SyncConfig,
    manifest_targets: dict[str, str],
    manifest_links: dict[str, str],
    prune: bool,
) -> list[PlanItem]:
    if config.project_root is None:
        return []
    project = config.project_root
    validate_project_root(project, config.allow_project_outside_root)
    items: list[PlanItem] = []
    claude_md = project / "CLAUDE.md"
    if claude_md.exists():
        content = adapt_common_text(read_text_source(claude_md, project))
        target = project / "AGENTS.md"
        validate_project_target(target, project)
        items.append(
            PlanItem(
                action=classify_managed_write(target, content, manifest_targets),
                source=claude_md,
                target=target,
                adapter="project-instructions",
                content=content,
            )
        )
    skills_root = project / ".claude" / "skills"
    if skills_root.exists():
        codex_skills_dir = project / ".codex" / "skills"
        for child in sorted(skills_root.iterdir()):
            # A skill dir that is itself a symlink (shared from nested-project) is
            # mirrored as a symlink, never walked/copied file-by-file.
            if child.is_symlink():
                items.append(
                    make_skill_symlink_item(child, codex_skills_dir, "project-skill", config, manifest_links)
                )
                continue
            file_sources = sorted(p for p in child.rglob("*") if p.is_file()) if child.is_dir() else [child]
            for source in file_sources:
                source_rel = source.relative_to(skills_root)
                if not is_syncable_file(source_rel):
                    continue
                if source.name.startswith("settings") and source.suffix == ".json":
                    continue
                content = adapt_skill_file(source, project)
                target = codex_skills_dir / source_rel
                validate_project_target(target, project)
                items.append(
                    PlanItem(
                        action=classify_managed_write(target, content, manifest_targets),
                        source=source,
                        target=target,
                        adapter="project-skill",
                        content=content,
                    )
                )
    agents_dir = project / ".claude" / "agents"
    if agents_dir.is_dir():
        for source in sorted(agents_dir.glob("*.md")):
            item = make_agent_item(
                source, project, project / ".codex" / "agents", "project-agent", config, manifest_targets, manifest_links
            )
            if item is not None:
                items.append(item)
    commands_dir = project / ".claude" / "commands"
    if commands_dir.is_dir():
        for source in sorted(commands_dir.glob("*.md")):
            item = make_command_item(
                source, project, project / ".codex" / "skills", "project-command", config, manifest_targets, manifest_links
            )
            if item is not None:
                items.append(item)
    items.extend(build_stale_items(project / ".codex", prune, "Claude-shaped Codex wrapper leftover"))
    return items


def manifest_target_hashes(config: SyncConfig) -> dict[str, str]:
    manifest = load_manifest(config)
    hashes: dict[str, str] = {}
    for entry in manifest.get("entries", []):
        for output in entry.get("outputs", []):
            target = output.get("target")
            output_sha = output.get("output_sha256")
            if target and output_sha:
                hashes[str(Path(target).resolve())] = output_sha
    return hashes


def manifest_target_links(config: SyncConfig) -> dict[str, str]:
    """Map of managed-symlink target -> recorded link string (lexical key, never resolved)."""
    manifest = load_manifest(config)
    links: dict[str, str] = {}
    for entry in manifest.get("entries", []):
        for output in entry.get("outputs", []):
            target = output.get("target")
            link_target = output.get("link_target")
            if target and link_target:
                links[str(target)] = link_target
    return links


def classify_managed_write(target: Path, content: str, manifest_targets: dict[str, str]) -> str:
    if not target.exists():
        return "create"
    current = target.read_text(encoding="utf-8")
    if current == content:
        return "skip unchanged"
    previous_hash = manifest_targets.get(str(target.resolve()))
    if previous_hash and sha256_text(current) != previous_hash:
        return "conflict target edited"
    return "update"


def build_plan(config: SyncConfig, prune: bool) -> SyncPlan:
    manifest_targets = manifest_target_hashes(config)
    manifest_links = manifest_target_links(config)
    if config.project_root is not None:
        items = build_project_items(config, manifest_targets, manifest_links, prune)
        for item in items:
            validate_any_target(item.target, config, symlink_leaf=item.link_target is not None)
            if item.content and contains_secret_like_content(item.content):
                raise ProtectedPathError(f"secret-looking output rejected: {item.target}")
        return SyncPlan(items=items)
    items = build_template_items(config)
    items.append(build_script_item(config))
    items.extend(build_skill_items(config))
    items.extend(build_agent_items(config, manifest_targets, manifest_links))
    items.extend(build_command_items(config, manifest_targets, manifest_links))
    items.extend(build_template_stale_items(config, prune))
    items.extend(build_stale_items(config.codex_root, prune, "Claude-shaped Codex wrapper leftover"))
    for item in items:
        validate_any_target(
            item.target,
            config,
            allow_template_stale=item.action in {"delete", "stale managed"},
            symlink_leaf=item.link_target is not None,
        )
        if item.content and contains_secret_like_content(item.content):
            raise ProtectedPathError(f"secret-looking output rejected: {item.target}")
    return SyncPlan(items=items)


def manifest_output(item: PlanItem, source_text: str) -> dict:
    if item.link_target is not None:
        # Lexical target (never resolve a symlink leaf) + recorded link string.
        return {
            "target": str(item.target),
            "source_sha256": sha256_text(source_text),
            "link_target": item.link_target,
            "sync_owned": True,
        }
    return {
        "target": str(item.target.resolve()),
        "source_sha256": sha256_text(source_text),
        "output_sha256": sha256_text(item.content or ""),
        "sync_owned": True,
    }


def manifest_entry(source: Path, adapter: str, items: list[PlanItem]) -> dict:
    # A mirrored symlink source may point at a directory (shared skill); hash the
    # link string, which is what actually determines the mirrored output.
    source_text = os.readlink(source) if source.is_symlink() else source.read_text(encoding="utf-8")
    return {
        "source": str(source.resolve()),
        "adapter": adapter,
        "adapter_version": VERSION,
        "transformer_version": VERSION,
        "input_set_hash": sha256_text(source_text),
        "outputs": [
            manifest_output(item, source_text)
            for item in sorted(items, key=lambda planned: str(planned.target))
        ],
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def manifest_groups(plan: SyncPlan) -> dict[tuple[str, str], tuple[Path, str, list[PlanItem]]]:
    groups: dict[tuple[str, str], tuple[Path, str, list[PlanItem]]] = {}
    for item in plan.items:
        if item.action not in {"create", "update", "skip unchanged"} or not item.source:
            continue
        if item.content is None and item.link_target is None:
            continue
        source = item.manifest_source or item.source
        key = (str(source.resolve()), item.adapter)
        if key not in groups:
            groups[key] = (source, item.adapter, [])
        groups[key][2].append(item)
    return groups


def load_manifest(config: SyncConfig) -> dict:
    path = manifest_path(config)
    if not path.exists():
        return {"version": VERSION, "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(config: SyncConfig, plan: SyncPlan) -> None:
    existing = load_manifest(config)
    old_by_key = {(entry["source"], entry["adapter"]): entry for entry in existing.get("entries", [])}
    new_by_key: dict[tuple[str, str], dict] = {}
    # Rebuild from the current plan only, so entries for sources that no longer
    # exist are garbage-collected. Preserve the prior entry (and timestamp) when
    # outputs are unchanged to keep repeated syncs idempotent.
    for key, (source, adapter, grouped_items) in manifest_groups(plan).items():
        entry = manifest_entry(source, adapter, grouped_items)
        old_entry = old_by_key.get(key)
        if old_entry and old_entry.get("outputs") == entry.get("outputs"):
            new_by_key[key] = old_entry
        else:
            new_by_key[key] = entry
    manifest = {"version": VERSION, "entries": list(new_by_key.values())}
    path = manifest_path(config)
    validate_any_target(path, config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    content = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    atomic_write_text(path, content, 0o600)


def atomic_write_text(path: Path, content: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_name, mode)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def write_symlink(target: Path, link_target: str) -> None:
    """Atomically create/replace a symlink leaf with the given (unresolved) link string."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.parent / f".{target.name}.{os.getpid()}.tmp"
    if tmp.is_symlink() or tmp.exists():
        tmp.unlink()
    os.symlink(link_target, tmp)
    os.replace(tmp, target)


def remove_target(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def acquire_lock(config: SyncConfig) -> Path:
    lock = lock_path(config)
    validate_any_target(lock, config)
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.parent.chmod(0o700)
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(f"{os.getpid()}\n")
    return lock


def apply_plan(config: SyncConfig, plan: SyncPlan) -> None:
    conflicts = [item for item in plan.items if item.action.startswith("conflict")]
    if conflicts:
        paths = ", ".join(str(item.target) for item in conflicts)
        raise ConflictError(f"conflicts detected; refusing to apply: {paths}")
    lock = acquire_lock(config)
    stop = sync_root(config)
    try:
        for item in plan.items:
            if item.action in {"create", "update"}:
                if item.link_target is not None:
                    write_symlink(item.target, item.link_target)
                else:
                    assert item.content is not None
                    atomic_write_text(item.target, item.content, item.mode)
            elif item.action == "delete":
                if item.target.is_symlink() or item.target.exists():
                    remove_target(item.target)
                    cleanup_empty_dirs(item.target.parent, stop)
        write_manifest(config, plan)
    finally:
        lock.unlink(missing_ok=True)


def cleanup_empty_dirs(start: Path, stop: Path) -> None:
    current = start
    while current != stop and current.exists():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def redacted_diff(target: Path, content: str) -> str:
    before = target.read_text(encoding="utf-8").splitlines(keepends=True) if target.exists() else []
    after = content.splitlines(keepends=True)
    diff = difflib.unified_diff(before, after, fromfile=str(target), tofile=str(target), lineterm="")
    lines = []
    for line in diff:
        if SECRET_LINE_RE.search(line):
            lines.append("[REDACTED secret-looking diff line]\n")
        else:
            lines.append(line)
    return "".join(lines)


def print_report(plan: SyncPlan, show_diff: bool) -> None:
    counts: dict[str, int] = {}
    for item in plan.items:
        counts[item.action] = counts.get(item.action, 0) + 1
    print("sync-to-codex report")
    for action in sorted(counts):
        print(f"{action}: {counts[action]}")
    for item in plan.items:
        print(f"- {item.action}: {item.target}")
        if show_diff and item.content is not None and item.action in {"create", "update"}:
            print(redacted_diff(item.target, item.content))
    for warning in plan.warnings:
        print(f"warning: {warning}", file=sys.stderr)


def exit_code_for_plan(plan: SyncPlan) -> int:
    if any(item.action.startswith("conflict") for item in plan.items):
        return 3
    if any(item.action in {"create", "update", "delete", "stale managed"} for item in plan.items):
        return 1
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync allowlisted Claude files into Codex runtime files.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Show planned changes without writing. Default.")
    mode.add_argument("--apply", action="store_true", help="Apply planned changes.")
    mode.add_argument("--check-drift", action="store_true", help="Alias for dry-run drift-oriented report in this skeleton.")
    parser.add_argument("--prune", action="store_true", help="Delete stale managed template leftovers.")
    parser.add_argument("--confirm-delete", action="store_true", help="Required with --apply --prune.")
    parser.add_argument("--claude-root", type=Path, default=Path.home() / ".claude")
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--project", type=Path, help="Sync one project: CLAUDE.md/.claude -> AGENTS.md/.codex.")
    parser.add_argument("--allow-project-outside-root", action="store_true", help="Allow --project outside ~/projects.")
    parser.add_argument("--no-diff", action="store_true", help="Do not print unified diffs.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = SyncConfig(
        claude_root=args.claude_root,
        codex_root=args.codex_root,
        project_root=args.project,
        allow_project_outside_root=args.allow_project_outside_root,
    )
    if args.apply and args.prune and not args.confirm_delete:
        print("--prune during --apply requires --confirm-delete", file=sys.stderr)
        return 2
    try:
        plan = build_plan(config, prune=args.prune and args.confirm_delete)
        print_report(plan, show_diff=not args.no_diff)
        if args.apply:
            apply_plan(config, plan)
            print("applied")
            return 0
        return exit_code_for_plan(plan)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return getattr(exc, "exit_code", 2)


if __name__ == "__main__":
    sys.exit(main())
