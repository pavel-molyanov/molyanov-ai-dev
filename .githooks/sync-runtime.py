#!/usr/bin/env python3
"""Regenerate the public snapshot with global-install agent pointers."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import replace
from pathlib import Path

# Check mode must not create import caches inside the repository.
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("public_codex_converter", ROOT / "scripts/sync-to-codex.py")
assert SPEC is not None and SPEC.loader is not None
CONVERTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CONVERTER
SPEC.loader.exec_module(CONVERTER)


def generated(path: Path) -> bool:
    if CONVERTER.has_generation_marker(path):
        return True
    try:
        skill = path.relative_to(ROOT / ".agents/skills").parts[0]
    except (ValueError, IndexError):
        return False
    return CONVERTER.has_generation_marker(ROOT / ".agents/skills" / skill)


def validate_snapshot_target(path: Path, *, symlink_leaf: bool = False) -> None:
    if path.is_relative_to(ROOT / ".agents/skills"):
        # Preserve the converter's exact skills/... template exceptions.
        CONVERTER.validate_target(path, ROOT / ".agents", symlink_leaf=symlink_leaf)
    else:
        CONVERTER.validate_project_target(path, ROOT, symlink_leaf=symlink_leaf)


def plan():
    legacy = ROOT / ".codex/skills"
    if legacy.is_symlink() or (legacy.exists() and any(legacy.iterdir())):
        raise CONVERTER.SyncError("legacy .codex/skills snapshot remains; run the publication mirror first")
    config = CONVERTER.SyncConfig(claude_root=ROOT, codex_root=ROOT / ".codex")
    warnings = []
    # Keep global conversion semantics; only the distribution destinations differ.
    items = CONVERTER.build_global_instruction_items(config, {})
    items += CONVERTER.build_skill_items(config, {}, {}, warnings)
    items += CONVERTER.build_agent_items(config, {}, {})
    items += CONVERTER.build_command_items(config, {}, {})
    if warnings:
        raise CONVERTER.SyncError("; ".join(warnings))
    mapped = []
    for item in items:
        relative = item.target.relative_to(config.codex_root)
        if relative.parts[0] == "skills":
            target = ROOT / ".agents" / relative
        elif relative == Path("AGENTS.md"):
            target = ROOT / "AGENTS.md"
        else:
            target = item.target
        validate_snapshot_target(target, symlink_leaf=item.link_target is not None)
        if item.content and CONVERTER.contains_secret_like_content(item.content):
            raise CONVERTER.ProtectedPathError(f"secret-looking output rejected: {target}")
        if item.raw_bytes is not None and CONVERTER.opaque_bytes_look_secret(item.raw_bytes):
            raise CONVERTER.ProtectedPathError(f"secret-looking output rejected: {target}")
        if item.link_target is not None:
            CONVERTER.assert_mirror_link_contained(target, item.link_target, ROOT)
            action = CONVERTER.classify_symlink(target, item.link_target, {})
        elif item.raw_bytes is not None:
            action = CONVERTER.classify_managed_write_bytes(target, item.raw_bytes, {})
            if action == "skip unchanged" and bool(target.stat().st_mode & 0o111) != bool(item.mode & 0o111):
                action = "update"
        else:
            action = CONVERTER.classify_managed_write(target, item.content, {})
        if action == "update" and not (generated(target) or CONVERTER.is_clean_tracked_file(target)):
            action = "conflict target edited"
        mapped.append(replace(item, target=target, action=action))
    expected = {item.target for item in mapped}
    for directory in (ROOT / ".agents/skills", ROOT / ".codex/agents"):
        CONVERTER.reject_symlink(directory)
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path in expected or (path.is_dir() and not path.is_symlink()):
                continue
            validate_snapshot_target(path, symlink_leaf=path.is_symlink())
            # A package marker does not make a user's extra files generated.
            # Never follow a symlink when inferring ownership from its contents.
            owned = not path.is_symlink() and (
                CONVERTER.has_generation_marker(path)
                or (generated(path) and CONVERTER.is_clean_tracked_file(path))
            )
            action = "delete" if owned else "conflict unexpected file"
            mapped.append(CONVERTER.PlanItem(action, None, path, "snapshot"))
    return mapped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        items = plan()
        conflicts = [item for item in items if item.action.startswith("conflict")]
        if conflicts:
            raise CONVERTER.ConflictError("refusing to overwrite: " + ", ".join(str(item.target.relative_to(ROOT)) for item in conflicts))
        changes = [item for item in items if item.action != "skip unchanged"]
        if not args.apply:
            for item in changes:
                print(f"{item.action}: {item.target.relative_to(ROOT)}")
            return int(bool(changes))
        for item in changes:
            if item.action == "delete":
                CONVERTER.remove_target(item.target)
                CONVERTER.cleanup_empty_dirs(item.target.parent, ROOT)
            elif item.link_target is not None:
                CONVERTER.write_symlink(item.target, item.link_target)
            elif item.raw_bytes is not None:
                CONVERTER.atomic_write_bytes(item.target, item.raw_bytes, item.mode)
            else:
                CONVERTER.atomic_write_text(item.target, item.content, item.mode)
        print(f"public snapshot: {len(changes)} generated files updated")
        return 0
    except (CONVERTER.SyncError, OSError, ValueError) as exc:
        print(f"public snapshot: {exc}", file=sys.stderr)
        return getattr(exc, "exit_code", 2)


if __name__ == "__main__":
    raise SystemExit(main())
