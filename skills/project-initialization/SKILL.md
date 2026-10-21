---
name: project-initialization
description: |
  Initializes a project from the standard dual-runtime template, preserves existing files,
  configures Git hooks, and creates or connects a private GitHub repository: main and dev for
  software projects, main only for skills workspaces. Use whenever a new project is started or
  an existing folder needs the dual-runtime scaffold and Git setup.
---

# Project Initialization

Initialize the project in the current working directory. Existing project files are preserved in
an `old*` directory for later review; do not merge them into the new scaffold during this workflow.

## Dual-Runtime Project Generation

The bundled template contains Claude project sources under `.claude/**`. Its Git hooks use the
installed `~/.claude/scripts/codex-sync-git-guard.py`: pre-commit generates and stages `AGENTS.md`,
`.agents/skills/**`, and `.codex/agents/**` after the sources are staged; pre-push checks for drift.
Host-local `.codex/.sync/**` is ignored. A reported conflict or validation error stops the action.

## 1. Check the Current Directory

Work only in the current directory. If it is already a Git repository with uncommitted changes,
ask whether to commit them first, continue while preserving them in `old*`, or stop. Do not proceed
until the user chooses.

Resolve the directory of this loaded `project-initialization` skill and set `INIT_SKILL_DIR` to that
absolute path. Verify that its `assets/new-project/` directory exists before moving project files.

Determine whether this is a software project (`main` + `dev`) or a skills workspace (`main` only).
Use the request and existing project context; ask if the type is unclear.

## 2. Preserve Existing Files and Apply the Template

If the current directory contains anything other than `.git`, move all such entries into the first
available directory named `old`, `old2`, `old3`, and so on. Do not move `.git`.

```bash
OLD_DIR=""
if find . -mindepth 1 -maxdepth 1 ! -name '.git' -print -quit | grep -q .; then
  OLD_DIR="old"
  N=2
  while [ -e "$OLD_DIR" ]; do OLD_DIR="old${N}"; ((N++)); done
  mkdir "$OLD_DIR"
  find . -mindepth 1 -maxdepth 1 ! -name '.git' ! -name "$OLD_DIR" -exec mv -- {} "$OLD_DIR/" \;
fi

cp -rp "$INIT_SKILL_DIR/assets/new-project/." .
```

If `OLD_DIR` is non-empty, add its exact root-relative directory (for example `/old2/`) to the
new root `.gitignore`. Keep the archive local and untracked so Git hooks do not treat its saved
Claude configuration as another active project. Do not stage the archive.

Before staging, set **Default branch** in the copied `CLAUDE.md` to `dev` for software or `main`
for a skills workspace. For a skills workspace, also replace **Branch Structure** in
`.claude/skills/project-knowledge/references/patterns.md` with a single `main` branch for active
work and remove the merge-to-`dev` and merge-to-`main` testing requirements.

## 3. Initialize Git and Hooks

Initialize Git with `main` as the primary branch when needed. For an existing repository, preserve
its history and make the current primary branch `main`. Then:

1. Make `.githooks/pre-commit` and `.githooks/pre-push` executable.
2. Set `git config core.hooksPath .githooks`.
3. Stage the scaffold and tracked deletions caused by the move. Keep the ignored `old*` archive
   untracked.
4. Create the first initialization commit. The pre-commit hook generates and stages `AGENTS.md`
   alongside `.agents/skills/**` and `.codex/agents/**`; `.gitignore` excludes `.codex/.sync/**`.
   If generation reports a conflict or validation error, the commit stops. If the repository already
   has history, create a normal
   initialization commit instead of rewriting existing commits.

## 4. Connect GitHub and Create Branches

GitHub is required for this workflow. Verify that `gh` is installed and authenticated.

- If `origin` already exists, show its URL and ask whether it is the intended repository. Stop on
  a mismatch rather than replacing the remote. Confirm through `gh` that the repository is private;
  if it is public, stop and ask whether to make it private or use another repository.
- If `origin` does not exist, ask for the GitHub repository name unless already supplied. The
  supplied name authorizes creating the private repository. Create it with
  `gh repo create {name} --private --source=. --remote=origin`.

For software projects, before any push inspect whether a local or remote `dev` branch already
exists. If neither exists, create `dev` from `main`. If either exists, show its relationship to
`main` and ask whether to reuse it; never reset or recreate an existing `dev`, and stop if local
and remote histories conflict. For a skills workspace, use `main` without creating `dev`.

Ask explicitly before pushing `main`. After approval, push `main`; for software also push the
created or approved `dev` and leave `dev` checked out. For a skills workspace, leave `main` checked
out. Read the canonical repository URL through `gh`.

## 5. Report the Result

Report:

- the GitHub URL;
- the created or reused branches: `main` and `dev` for software, `main` for a skills workspace;
- the preserved local, Git-ignored `old*` directory, or that the directory was initially empty;
- the active branch: `dev` for software or `main` for a skills workspace;
- the next step: create the initial Project Knowledge with `documentation-writing`.

Do not review or merge files from `old*` during initialization.
