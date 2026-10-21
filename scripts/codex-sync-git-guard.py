#!/usr/bin/env python3
"""Git guard for keeping Claude sources and generated Codex files together."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


ZERO_OID = "0" * 40
MANIFEST = Path(".sync/claude-to-codex-manifest.json")
# Project skills are generated into .agents/skills; .codex/skills is the legacy location.
PROJECT_SKILLS = ".agents/skills"
LEGACY_PROJECT_SKILLS = ".codex/skills"
# Git exports these to hooks, and a pathspec commit (`git commit -- path`) points
# GIT_INDEX_FILE at a temporary index. Git commands for another repository must
# not inherit them, or they read and write the hook repository's index.
HOOK_REPO_ENV = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_PREFIX",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)
HOOK_REPO: Path | None = None


class GuardError(RuntimeError):
    pass


def foreign_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in HOOK_REPO_ENV}


def run(
    args: list[str],
    *,
    cwd: Path,
    check: bool = True,
    capture: bool = True,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if env is None and HOOK_REPO is not None and not Path(cwd).resolve().is_relative_to(HOOK_REPO):
        env = foreign_env()
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        input=stdin,
        capture_output=capture,
        env=env,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise GuardError(detail or f"command failed ({result.returncode}): {' '.join(args)}")
    return result


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=repo, check=check)


def repo_root(path: Path) -> Path:
    result = git(path, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def rel_to_repo(path: Path, repo: Path) -> str:
    return Path(os.path.abspath(path)).relative_to(repo).as_posix()


def staged_paths(repo: Path) -> list[str]:
    result = git(repo, "diff", "--cached", "--no-renames", "--name-only", "--diff-filter=ACMRD", "-z")
    return [part for part in result.stdout.split("\0") if part]


def worktree_paths(repo: Path) -> list[str]:
    result = git(repo, "status", "--porcelain=v1", "--no-renames", "--untracked-files=all", "-z")
    return [entry[3:] for entry in result.stdout.split("\0") if len(entry) >= 4]


def is_global_source(path: str) -> bool:
    parts = Path(path).parts
    if path == "CLAUDE.md":
        return True
    if not parts:
        return False
    if parts[0] == "skills":
        # claude.ai rewrites skills/synced in the background; sync-to-codex skips it.
        return len(parts) >= 2 and parts[1] != "synced"
    if parts[0] in {"agents", "commands"}:
        return len(parts) == 2 and path.endswith(".md")
    return False


def project_source_root(path: str) -> str | None:
    parts = Path(path).parts
    if not parts:
        return None
    for index, part in enumerate(parts):
        if part != ".claude" or index + 2 > len(parts):
            continue
        if index + 1 < len(parts) and parts[index + 1] in {"skills", "agents", "commands"}:
            return Path(*parts[:index]).as_posix() if index else "."
    if parts[-1] == "CLAUDE.md":
        return Path(*parts[:-1]).as_posix() if len(parts) > 1 else "."
    return None


def project_target_root(path: str) -> str | None:
    parts = Path(path).parts
    if not parts:
        return None
    if parts[-1] == "AGENTS.md":
        return Path(*parts[:-1]).as_posix() if len(parts) > 1 else "."
    for index, part in enumerate(parts):
        if part == ".agents" and parts[index + 1 : index + 2] == ("skills",) and index + 2 < len(parts):
            return Path(*parts[:index]).as_posix() if index else "."
        if part != ".codex" or index + 1 >= len(parts):
            continue
        if parts[index + 1] == ".sync":
            return None
        return Path(*parts[:index]).as_posix() if index else "."
    return None


def project_managed_root(path: str) -> str | None:
    return project_source_root(path) or project_target_root(path)


def is_global_target(path: str) -> bool:
    parts = Path(path).parts
    if path == "AGENTS.md":
        return True
    if not parts:
        return False
    if parts[0] == "agents":
        return len(parts) == 2 and path.endswith(".toml")
    if parts[0] == "skills":
        return len(parts) >= 2 and parts[1] != ".system"
    return False


def source_pathspecs(root: str, *, global_scope: bool) -> list[str]:
    if global_scope:
        return ["CLAUDE.md", "skills", ":(exclude)skills/synced", "agents/*.md", "commands/*.md"]
    prefix = "" if root == "." else f"{root}/"
    return [
        f"{prefix}CLAUDE.md",
        f"{prefix}.claude/skills",
        f"{prefix}.claude/agents/*.md",
        f"{prefix}.claude/commands/*.md",
    ]


def dirty_source_paths(repo: Path, pathspecs: list[str]) -> list[str]:
    unstaged = git(repo, "diff", "--name-only", "-z", "--", *pathspecs).stdout.split("\0")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z", "--", *pathspecs).stdout.split("\0")
    return sorted({path for path in [*unstaged, *untracked] if path})


def changed_paths(repo: Path, pathspecs: list[str]) -> list[str]:
    output = git(repo, "status", "--porcelain=v1", "-z", "--", *pathspecs).stdout
    return [entry for entry in output.split("\0") if entry]


def load_manifest_targets(path: Path) -> set[Path]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GuardError(f"cannot read sync manifest {path}: {exc}") from exc
    targets: set[Path] = set()
    for entry in data.get("entries", []):
        for output in entry.get("outputs", []):
            target = output.get("target")
            if isinstance(target, str):
                targets.add(Path(target))
    return targets


def sync_command(sync_script: Path, *, project: Path | None, apply: bool) -> list[str]:
    command = [str(sync_script)]
    if project is not None:
        command.extend(["--project", str(project), "--allow-project-outside-root"])
    command.append("--apply" if apply else "--check-drift")
    command.append("--no-diff")
    return command


def recovery_command(sync_script: Path, project: Path | None, *, prune: bool = False) -> str:
    command = [str(sync_script)]
    if project is not None:
        command.extend(["--project", str(project)])
    command.append("--apply")
    if project is not None:
        try:
            project.relative_to(Path.home() / "projects")
        except ValueError:
            command.append("--allow-project-outside-root")
    if prune:
        command.extend(["--prune", "--confirm-delete"])
    return shlex.join(command)


def regeneration_guidance(sync_script: Path, project: Path | None) -> str:
    return (
        "Claude is the source of truth. Do not edit generated Codex files directly. "
        "Move any intended direct Codex change to the matching Claude source and discard the "
        "direct generated edit. Then regenerate Codex with:\n"
        + recovery_command(sync_script, project)
    )


def sync_failure_guidance(sync_script: Path, project: Path | None, detail: str) -> str:
    if "orphaned managed" in detail:
        return (
            "Claude is the source of truth. For an approved Claude source deletion or rename, "
            "review the reported generated orphans, then prune them with:\n"
            + recovery_command(sync_script, project, prune=True)
        )
    return regeneration_guidance(sync_script, project)


def invoke_sync(
    sync_script: Path,
    *,
    cwd: Path,
    project: Path | None,
    apply: bool,
    foreign_targets: bool = False,
) -> None:
    # The converter runs git in the repository that holds its outputs; from the
    # ~/.claude hook that is ~/.codex, so it must not see the hook's git variables.
    env = foreign_env() if foreign_targets else None
    result = run(sync_command(sync_script, project=project, apply=apply), cwd=cwd, check=False, env=env)
    if result.returncode != 0:
        detail = (result.stderr + result.stdout).strip()
        action = "sync" if apply else "drift check"
        raise GuardError(
            f"Codex {action} failed:\n{detail}\n\n{sync_failure_guidance(sync_script, project, detail)}"
        )


def stage_targets(repo: Path, targets: set[Path]) -> None:
    relative: list[str] = []
    for target in sorted(targets):
        try:
            candidate = rel_to_repo(target, repo)
        except ValueError:
            raise GuardError(f"manifest target escapes repository: {target}")
        if os.path.lexists(target) or git(repo, "ls-files", "--", candidate).stdout.strip():
            relative.append(candidate)
    if relative:
        git(repo, "add", "-A", "--", *relative)


def status_for_targets(repo: Path, targets: set[Path]) -> list[str]:
    relative: list[str] = []
    for target in sorted(targets):
        try:
            relative.append(rel_to_repo(target, repo))
        except ValueError:
            raise GuardError(f"manifest target escapes repository: {target}")
    if not relative:
        return []
    output = git(repo, "status", "--porcelain=v1", "-z", "--", *relative).stdout
    return [entry for entry in output.split("\0") if entry]


def legacy_skills_path(root: str) -> str:
    return LEGACY_PROJECT_SKILLS if root == "." else f"{root}/{LEGACY_PROJECT_SKILLS}"


def stage_removed_legacy_skills(repo: Path, root: str) -> None:
    """Stage deletions the converter made while moving skills out of .codex/skills.

    The manifest of this host may not record every legacy file (another host or
    branch generated it), so the deletions are taken from Git, not the manifest.
    """
    output = git(repo, "ls-files", "--deleted", "-z", "--", legacy_skills_path(root)).stdout
    deleted = [path for path in output.split("\0") if path]
    if deleted:
        git(repo, "add", "-A", "--", *deleted)


def project_roots(paths: list[str]) -> list[str]:
    roots = {root for path in paths if (root := project_managed_root(path)) is not None}
    return sorted(roots, key=lambda value: (len(Path(value).parts), value), reverse=True)


def project_has_managed_sources(project: Path) -> bool:
    return (project / "CLAUDE.md").is_file() or any(
        (project / ".claude" / family).exists()
        for family in ("skills", "agents", "commands")
    )


def mapped_targets(
    repo: Path,
    root: str,
    paths: list[str],
    *,
    global_scope: bool,
    source_repo: Path | None = None,
) -> set[Path]:
    base = repo if root == "." else repo / root
    source_repo = source_repo or repo
    targets: set[Path] = set()
    prefix = "" if root == "." else f"{root}/"
    for path in paths:
        if not path.startswith(prefix):
            continue
        relative = path[len(prefix) :]
        if relative == "CLAUDE.md":
            targets.add(base / "AGENTS.md")
            continue
        source_prefix = "" if global_scope else ".claude/"
        if not relative.startswith(source_prefix):
            continue
        source_relative = relative[len(source_prefix) :]
        parts = Path(source_relative).parts
        if len(parts) < 2:
            continue
        family, remainder = parts[0], Path(*parts[1:])
        if family == "skills":
            targets.add(base / ("skills" if global_scope else PROJECT_SKILLS) / remainder)
        elif family == "agents" and remainder.suffix == ".md":
            targets.add(base / ("agents" if global_scope else ".codex/agents") / remainder.with_suffix(".toml"))
        elif family == "commands" and remainder.suffix == ".md":
            command_root = base / ("skills" if global_scope else PROJECT_SKILLS)
            command_target = command_root / f"source-command-{remainder.stem}"
            source_staged = git(source_repo, "ls-files", "--stage", "--", path).stdout.splitlines()
            source_head = git(source_repo, "ls-tree", "HEAD", "--", path, check=False).stdout.splitlines()
            source_is_symlink = os.path.islink(source_repo / path) or any(
                line.startswith("120000 ") and line.rsplit("\t", 1)[-1] == path for line in source_staged
            ) or any(
                line.startswith("120000 ") and line.rsplit("\t", 1)[-1] == path for line in source_head
            )
            if source_is_symlink:
                targets.add(command_target)
            else:
                targets.add(command_target / "SKILL.md")
    return targets


def require_owned_deleted_targets(
    target_repo: Path,
    staged_sources: list[str],
    source_repo: Path,
    root: str,
    manifest_targets: set[Path],
    *,
    global_scope: bool,
) -> None:
    deleted_sources = [path for path in staged_sources if not os.path.lexists(source_repo / path)]
    if not deleted_sources:
        return
    deleted_targets = mapped_targets(
        target_repo,
        root,
        deleted_sources,
        global_scope=global_scope,
        source_repo=source_repo,
    )
    owned = {Path(os.path.abspath(path)) for path in manifest_targets}
    unresolved: list[str] = []
    for target in deleted_targets:
        absolute = Path(os.path.abspath(target))
        if absolute in owned:
            continue
        relative = rel_to_repo(target, target_repo)
        staged_delete = git(
            target_repo,
            "diff",
            "--cached",
            "--no-renames",
            "--diff-filter=D",
            "--name-only",
            "--",
            relative,
        ).stdout.strip()
        if os.path.lexists(target) and not staged_delete:
            unresolved.append(relative)
    if unresolved:
        raise GuardError(
            "the host-local manifest has no ownership record for generated outputs of deleted or renamed sources; "
            "review and remove these generated paths explicitly, then retry:\n- " + "\n- ".join(unresolved)
        )


def project_pre_commit(repo: Path, sync_script: Path) -> None:
    staged = staged_paths(repo)
    roots = project_roots(staged)
    if not roots:
        return
    for root in roots:
        project = repo if root == "." else (repo / root).resolve()
        if not project_has_managed_sources(project):
            continue
        source_staged = any(project_source_root(path) == root for path in staged)
        if not source_staged:
            invoke_sync(sync_script, cwd=repo, project=project, apply=False)
            continue
        dirty = dirty_source_paths(repo, source_pathspecs(root, global_scope=False))
        if dirty:
            raise GuardError(
                "managed Claude sources are only partially staged. Keep intended changes in "
                "Claude, discard unintended Claude changes, and include every remaining managed "
                "Claude change in this commit. The hook will regenerate and stage Codex outputs.\n\n"
                + regeneration_guidance(sync_script, project)
                + "\n\nManaged Claude changes not included in the commit:\n- "
                + "\n- ".join(dirty)
            )
        manifest = project / ".codex" / MANIFEST
        targets = load_manifest_targets(manifest)
        require_owned_deleted_targets(
            repo,
            staged,
            repo,
            root,
            targets,
            global_scope=False,
        )
        targets.update(mapped_targets(repo, root, staged, global_scope=False, source_repo=repo))
        invoke_sync(sync_script, cwd=repo, project=project, apply=True)
        targets.update(load_manifest_targets(manifest))
        stage_targets(repo, targets)
        stage_removed_legacy_skills(repo, root)
        invoke_sync(sync_script, cwd=repo, project=project, apply=False)
    print("Claude sources and generated Codex files are staged together.")


def global_codex_pre_commit(repo: Path, sync_script: Path) -> None:
    if not any(is_global_target(path) for path in staged_paths(repo)):
        return
    invoke_sync(sync_script, cwd=repo, project=None, apply=False)
    print("Managed global Codex files match their Claude sources.")


def global_pre_commit(repo: Path, sync_script: Path, codex_root: Path) -> None:
    staged = staged_paths(repo)
    relevant = [path for path in staged if is_global_source(path)]
    if not relevant:
        return
    dirty = dirty_source_paths(repo, source_pathspecs(".", global_scope=True))
    if dirty:
        raise GuardError(
            "managed global Claude sources are only partially staged. Keep intended changes in "
            "Claude, discard unintended Claude changes, and include every remaining managed "
            "Claude change in this commit. The hook will regenerate and stage Codex outputs.\n\n"
            + regeneration_guidance(sync_script, None)
            + "\n\nManaged global Claude changes not included in the commit:\n- "
            + "\n- ".join(dirty)
        )
    manifest = codex_root / MANIFEST
    targets = load_manifest_targets(manifest)
    require_owned_deleted_targets(
        codex_root,
        relevant,
        repo,
        ".",
        targets,
        global_scope=True,
    )
    targets.update(mapped_targets(codex_root, ".", relevant, global_scope=True, source_repo=repo))
    invoke_sync(sync_script, cwd=repo, project=None, apply=True, foreign_targets=True)
    targets.update(load_manifest_targets(manifest))
    stage_targets(codex_root, targets)
    invoke_sync(sync_script, cwd=repo, project=None, apply=False, foreign_targets=True)
    print(
        "Global Codex outputs are staged in ~/.codex. Commit and push that repository before pushing ~/.claude."
    )


def outgoing_paths(repo: Path, stdin_text: str) -> list[str]:
    paths: set[str] = set()
    lines = [line.split() for line in stdin_text.splitlines() if line.strip()]
    if not lines:
        upstream = git(repo, "rev-parse", "--verify", "@{upstream}", check=False)
        if upstream.returncode != 0:
            return []
        lines = [["HEAD", git(repo, "rev-parse", "HEAD").stdout.strip(), "upstream", upstream.stdout.strip()]]
    for fields in lines:
        if len(fields) != 4:
            continue
        _local_ref, local_oid, _remote_ref, remote_oid = fields
        if local_oid == ZERO_OID:
            continue
        if remote_oid == ZERO_OID:
            revs = git(repo, "rev-list", local_oid, "--not", "--remotes").stdout.splitlines()
            if not revs:
                revs = [local_oid]
        else:
            revs = git(repo, "rev-list", f"{remote_oid}..{local_oid}").stdout.splitlines()
        for commit in revs:
            output = git(
                repo,
                "diff-tree",
                "--root",
                "--no-renames",
                "--no-commit-id",
                "--name-only",
                "-r",
                commit,
            ).stdout
            paths.update(path for path in output.splitlines() if path)
    return sorted(paths)


def require_relevant_refs_at_head(repo: Path, stdin_text: str, predicate) -> None:
    if not stdin_text.strip():
        return
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    for line in stdin_text.splitlines():
        fields = line.split()
        if len(fields) != 4 or fields[1] == ZERO_OID:
            continue
        local_oid = fields[1]
        if local_oid != head and any(predicate(path) for path in outgoing_paths(repo, line + "\n")):
            raise GuardError(
                "a managed ref being pushed is not the checked-out HEAD; check out that branch and push it separately"
            )


def require_clean_sources(
    repo: Path,
    roots: list[str],
    *,
    global_scope: bool,
    sync_script: Path,
) -> None:
    for root in roots:
        dirty = changed_paths(repo, source_pathspecs(root, global_scope=global_scope))
        if dirty:
            project = None if global_scope else (repo if root == "." else (repo / root).resolve())
            raise GuardError(
                "managed Claude sources have uncommitted changes. Include all intended managed "
                "Claude changes in a commit with their regenerated Codex outputs before pushing.\n\n"
                + regeneration_guidance(sync_script, project)
                + "\n\nUncommitted managed Claude changes:\n- "
                + "\n- ".join(dirty)
            )


def project_pre_push(repo: Path, sync_script: Path, stdin_text: str) -> None:
    require_relevant_refs_at_head(repo, stdin_text, lambda path: project_managed_root(path) is not None)
    outgoing = outgoing_paths(repo, stdin_text)
    roots = [
        root
        for root in project_roots(outgoing)
        if project_has_managed_sources(repo if root == "." else (repo / root).resolve())
        or any(project_source_root(path) == root for path in outgoing)
    ]
    if not roots:
        return
    require_clean_sources(repo, roots, global_scope=False, sync_script=sync_script)
    for root in roots:
        project = repo if root == "." else (repo / root).resolve()
        invoke_sync(sync_script, cwd=repo, project=project, apply=False)
        manifest = project / ".codex" / MANIFEST
        targets = load_manifest_targets(manifest)
        if not targets:
            raise GuardError(
                f"missing local sync manifest for {project}.\n\n"
                + regeneration_guidance(sync_script, project)
                + "\nThen commit the regenerated Codex outputs before pushing."
            )
        targets.update(mapped_targets(repo, root, outgoing, global_scope=False, source_repo=repo))
        # A half-committed move would leave both copies of a skill in the pushed tree.
        targets.add(repo / legacy_skills_path(root))
        dirty = status_for_targets(repo, targets)
        if dirty:
            raise GuardError(
                "generated Codex files are not fully committed. Regenerate them from Claude, "
                "commit them with their Claude sources, and retry the push.\n\n"
                + regeneration_guidance(sync_script, project)
                + "\n\nUncommitted generated Codex files:\n- "
                + "\n- ".join(dirty)
            )


def global_codex_pre_push(repo: Path, sync_script: Path, stdin_text: str) -> None:
    require_relevant_refs_at_head(repo, stdin_text, is_global_target)
    claude_repo = repo_root(sync_script.parent.parent)
    require_clean_sources(claude_repo, ["."], global_scope=True, sync_script=sync_script)
    current = [path for path in worktree_paths(repo) if is_global_target(path)]
    if not any(is_global_target(path) for path in outgoing_paths(repo, stdin_text)) and not current:
        return
    invoke_sync(sync_script, cwd=repo, project=None, apply=False)
    targets = load_manifest_targets(repo / MANIFEST)
    targets.update(repo / path for path in current)
    dirty = status_for_targets(repo, targets)
    if dirty:
        raise GuardError(
            "managed global Codex files have uncommitted changes. Commit them before pushing.\n\n"
            + regeneration_guidance(sync_script, None)
            + "\n\nUncommitted global Codex files:\n- "
            + "\n- ".join(dirty)
        )


def global_pre_push(repo: Path, sync_script: Path, codex_root: Path, stdin_text: str) -> None:
    require_relevant_refs_at_head(repo, stdin_text, is_global_source)
    outgoing = outgoing_paths(repo, stdin_text)
    relevant = [path for path in outgoing if is_global_source(path)]
    require_clean_sources(repo, ["."], global_scope=True, sync_script=sync_script)
    invoke_sync(sync_script, cwd=repo, project=None, apply=False, foreign_targets=True)
    targets = load_manifest_targets(codex_root / MANIFEST)
    if not targets:
        raise GuardError(
            "missing global sync manifest.\n\n"
            + regeneration_guidance(sync_script, None)
            + "\nThen commit and push ~/.codex before pushing ~/.claude."
        )
    targets.update(mapped_targets(codex_root, ".", relevant, global_scope=True, source_repo=repo))
    dirty = status_for_targets(codex_root, targets)
    if dirty:
        raise GuardError(
            "global Codex outputs are not fully committed. Regenerate them from Claude, commit "
            "them in ~/.codex, and retry the push.\n\n"
            + regeneration_guidance(sync_script, None)
            + "\n\nUncommitted global Codex outputs:\n- "
            + "\n- ".join(dirty)
        )
    upstream = git(codex_root, "rev-parse", "--verify", "@{upstream}", check=False)
    if upstream.returncode != 0:
        raise GuardError("~/.codex has no upstream; configure and push it before pushing global Claude changes")
    head = git(codex_root, "rev-parse", "HEAD").stdout.strip()
    if head != upstream.stdout.strip():
        raise GuardError("~/.codex has unpushed commits; push it before pushing global Claude changes")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("pre-commit", "pre-push"))
    parser.add_argument("--scope", choices=("global", "global-codex", "project"), required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--sync-script", type=Path)
    parser.add_argument("--codex-root", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    global HOOK_REPO
    args = parse_args(argv or sys.argv[1:])
    try:
        repo = repo_root(args.repo)
        HOOK_REPO = repo
        sync_script = (args.sync_script or Path.home() / ".claude/scripts/sync-to-codex.sh").expanduser().resolve()
        codex_root = (args.codex_root or Path.home() / ".codex").expanduser().resolve()
        if not sync_script.is_file():
            raise GuardError(f"sync script not found: {sync_script}")
        stdin_text = sys.stdin.read() if args.phase == "pre-push" else ""
        if args.scope == "global" and args.phase == "pre-commit":
            global_pre_commit(repo, sync_script, codex_root)
        elif args.scope == "global":
            global_pre_push(repo, sync_script, codex_root, stdin_text)
        elif args.scope == "global-codex" and args.phase == "pre-commit":
            global_codex_pre_commit(repo, sync_script)
        elif args.scope == "global-codex":
            global_codex_pre_push(repo, sync_script, stdin_text)
        elif args.phase == "pre-commit":
            project_pre_commit(repo, sync_script)
        else:
            project_pre_push(repo, sync_script, stdin_text)
        return 0
    except GuardError as exc:
        print(f"Codex sync guard: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
