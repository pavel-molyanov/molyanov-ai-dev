# AI-First Development Framework

**English** | [Русский](README.ru.md)

A framework for AI-First development with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://github.com/openai/codex). One methodology, two compatible runtimes.

At its core is a spec-driven pipeline: first we plan the work in detail through an interview with the user and research of the codebase, agree on the specifications, and only then write code. Every stage is checked by specialized validator agents. Code is written via TDD.

The framework is multilingual: it talks to you, runs interviews, and writes user-facing specs in the language you write in, while keeping technical documents (tech-spec, tasks, code) in English.

You set your language in one place — the instruction file: `~/.claude/CLAUDE.md` for Claude and `~/.codex/AGENTS.md` for Codex (or a project's `CLAUDE.md` / `AGENTS.md`). In the `## Language` section, declare your language, e.g. `This user writes in English.` Skills and agents read the language from there, so even subagents that never see the chat produce output in your language.

## Two runtimes: Claude and Codex

The methodology supports both agents at once.

- **Claude is the source of truth.** You edit files in `~/.claude/`, `CLAUDE.md`, and projects' `.claude/**`.
- **Codex is the generated runtime.** `~/.codex/`, `AGENTS.md`, and `.codex/**` are created from the Claude sources by `scripts/sync-to-codex.py`. Do not edit them by hand.

The commands (`/new-user-spec`, `/do-task`, `/done`, etc.), skills, and agents are the same. Only the interpreter changes.

### Installation

Copy the framework files into your runtime folders:

```bash
# Claude (source):
mkdir -p ~/.claude
cp -r skills agents commands shared hooks ~/.claude/

# Codex (ready-made snapshot):
mkdir -p ~/.codex
cp -r .codex/skills .codex/commands .codex/agents ~/.codex/

# Or drop in the script and regenerate Codex from your own ~/.claude/**:
mkdir -p ~/.claude/scripts
cp scripts/sync-to-codex.py scripts/sync-to-codex.sh ~/.claude/scripts/
~/.claude/scripts/sync-to-codex.sh --apply
```

### After any change to the methodology

If you edit `~/.claude/**` locally — regenerate Codex:

```bash
~/.claude/scripts/sync-to-codex.sh --apply                   # global changes
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply  # per-project .claude/**
```

Alternative without copying the script: run it from a clone of the repo — `python3 scripts/sync-to-codex.py --apply`.

## Quick Start

**New project:**

`/init-project` → `/init-project-knowledge` → start building features

**New feature:**

`/new-user-spec` → `/new-tech-spec` → `/decompose-tech-spec` → `/do-feature` (or `/do-task`) → `/done`

**Quick task without a spec:**

`/write-code`

---

## How the methodology works

### Project documentation — Project Knowledge

All project documentation lives not in CLAUDE.md but in a dedicated skill, **Project Knowledge** — a set of files in `.claude/skills/project-knowledge/references/`:

| File | What's inside |
|---|---|
| `project.md` | Project purpose, audience, key features, scope |
| `architecture.md` | Tech stack, project structure, dependencies, data model |
| `patterns.md` | Code conventions, git workflow, testing strategy, business rules |
| `deployment.md` | Platform, environment variables, CI/CD pipeline, monitoring |
| `ux-guidelines.md` | UI language, tone of voice, domain glossary (optional) |

CLAUDE.md stays minimal — project name, a link to Project Knowledge, the default branch. The agent loads only the Project Knowledge files it needs for the current task (just-in-time context) rather than the entire context at once.

To create Project Knowledge in a new project, use the **`project-planning`** skill (the `/init-project-knowledge` command) — it interviews the user, fills in all Project Knowledge files, and creates a project backlog (features + roadmap). To keep documentation up to date during development, use the **`documentation-writing`** skill.

---

### Feature development pipeline

The full path from idea to production. Automatic validators run at every step, and a git commit is made after each validation round (you can roll back to any intermediate state).

#### Step 1. User Spec — what we're building (`/new-user-spec`)

The agent loads the **`user-spec-planning`** skill, reads Project Knowledge, scans the codebase, and runs a structured interview with the user in 3 cycles:

1. **General questions** — what we want to build, why, for whom
2. **Code-informed** — the agent has already studied the project and asks clarifying questions about integration, existing patterns, dependencies
3. **Edge cases** — boundary conditions, errors, what-ifs

After the interview, the `interview-completeness-checker` agent checks for any remaining gaps. Then the agent writes user-spec.md — a requirements spec in the user's language, understandable by a person without a technical background.

Two validators check the result (up to 3 fix iterations):
- **`userspec-quality-validator`** — document structure, testability of acceptance criteria
- **`userspec-adequacy-validator`** — feasibility of the solution, no over/underengineering

The user reads and approves the spec.

**Result:** `work/{feature}/user-spec.md` (status: approved)

#### Step 2. Tech Spec — how we're building it (`/new-tech-spec`)

The agent loads the **`tech-spec-planning`** skill, takes the approved user-spec, and turns it into a technical specification: architecture, key decisions, testing strategy, and an implementation plan broken down into tasks.

It's written in English — this is a document for the agent, not for a human. If you're not into development, you won't follow much here — and that's fine, that's what the previous step was for.

At this stage the agent researches the codebase (via the `code-researcher` agent), checks dependencies, and uses the Context7 MCP to fetch up-to-date documentation for external libraries.

5 validators run in parallel (up to 3 fix iterations):
- **`skeptic`** — hunts for mirages: references to non-existent files, functions, APIs
- **`completeness-validator`** — bidirectional traceability: are all user-spec requirements covered, is there anything extra
- **`security-auditor`** — review of architectural decisions against OWASP Top 10
- **`test-reviewer`** — adequacy of the testing strategy
- **`tech-spec-validator`** — template compliance, task quality, dependency conflicts

The user approves the tech-spec.

**Result:** `work/{feature}/tech-spec.md` (status: approved)

#### Step 3. Decomposition into tasks (`/decompose-tech-spec`)

The agent loads the **`task-decomposition`** skill, takes the approved tech-spec, and creates a separate file for each task in the implementation plan. Tasks are created in parallel by the `task-creator` agent.

Each task file contains: acceptance criteria, a TDD anchor (which tests to write first), a list of context files, the required skills, reviewers, the execution wave, and dependencies on other tasks.

2 validators check the result (up to 3 iterations):
- **`task-validator`** — template compliance, description quality
- **`reality-checker`** — whether the referenced files, functions, and dependencies exist in the real codebase

**Result:** `work/{feature}/tasks/*.md`

#### Step 4. Development and QA

Two modes to choose from:

**`/do-task`** — one task at a time, manual control. The agent reads the task file, loads the specified skills (usually `code-writing`), writes tests, then code, and goes through review. After each review round — a commit with fixes. Good for debugging, complex tasks, iterative work.

**`/do-feature`** — parallel execution of all tasks by a team of agents. The **`feature-execution`** skill spins up a team lead who creates a team via TeamCreate and distributes tasks across waves. Within each wave tasks run in parallel: one agent = one task. Each agent commits its own code, goes through review (up to 3 rounds), and fixes findings. The team lead coordinates and commits statuses.

Both modes use TDD: tests first, then code. After the code — automatic code review and security audit.

The final part of any feature's development is QA. QA tasks are added automatically at the end of the tech-spec:
- **Pre-deploy QA** — running tests, checking acceptance criteria from user-spec and tech-spec
- **Post-deploy QA** — verification on the live environment via MCP tools (Playwright, curl, Telegram MCP, etc.)

There's also **`/write-code`** — for writing code without a spec. A quick task, a bug fix, an experiment. It uses the `code-writing` skill directly: plan → tests → code → code review + security audit. No upfront planning through user-spec/tech-spec.

#### Step 5. Finalization (`/done`)

Closes out the feature: reads user-spec, tech-spec, and decisions.md (decisions made during development), updates the affected Project Knowledge files (architecture.md, patterns.md, etc.), and archives `work/{feature}/` into `work/completed/{feature}/`.

---

### Structure of the work directory

```
work/{feature}/
├── user-spec.md       # What we're building (user's language, for a human)
├── tech-spec.md       # How we're building it (English, for the agent)
├── decisions.md       # Decisions made during development
├── tasks/
│   ├── 1.md           # Atomic tasks
│   ├── 2.md
│   └── 3.md
└── logs/              # Working logs (interviews, research, reviews)
```

Completed features are archived in `work/completed/{feature}/`.

---

## Project initialization

For a new project:

1. **`/init-project`** — creates the project structure from a template: a `.claude/` folder with Project Knowledge files, `CLAUDE.md`, a `.gitignore` with rules for secrets and dependencies. Initializes a git repository, creates a private GitHub repository via the `gh` CLI, makes the initial commit, and creates the `main` and `dev` branches. If the folder already has files — it offers to move them into `old/`.

2. **`/init-project-knowledge`** — runs the `project-planning` skill, which conducts a detailed interview about the project and fills in all Project Knowledge files (`project.md`, `architecture.md`, `patterns.md`, `deployment.md`), and also creates a project backlog with features and a roadmap.

After that you can start developing features with `/new-user-spec`.

---

## Creating new skills

The framework is extended by creating new skills in the same style:

- **`skill-master`** — a guide and rules for creating skills: structure, patterns, types (procedural and informational), templates
- **`skill-tester`** — the full skill-testing cycle: designing scenarios, running with parallel runners, evaluation, report

---

## Reference

### All commands

| Command | What it does |
|---|---|
| `/init-project` | Creates the project structure from a template, initializes git, creates a private GitHub repo, sets up branches (main + dev) |
| `/init-project-knowledge` | Interviews about the project, fills in all Project Knowledge files, and creates the backlog (features + roadmap) |
| `/new-user-spec` | Interviews the user, researches the code, creates a requirements spec with validation (2 validators, up to 3 iterations) |
| `/new-tech-spec` | Researches the codebase, creates a technical spec with architecture, decisions, testing strategy, and implementation plan (5 validators) |
| `/decompose-tech-spec` | Breaks the tech-spec into atomic tasks with acceptance criteria, TDD anchors, and dependencies (2 validators) |
| `/do-task` | Executes one task: TDD (tests → code), code review, security audit. Commits after implementation and after each review round |
| `/do-feature` | Creates a team of agents, distributes tasks across waves, each agent executes its task in parallel with TDD and review |
| `/write-code` | Writes code without a spec: plan → tests → code → code review + security audit |
| `/done` | Reads the specs and decisions.md, updates Project Knowledge, archives the feature into `work/completed/` |

### All agents

Agents are isolated subprocesses with their own context. They receive a task, do one job, and return a structured result.

#### Validators and creators
| Agent | What it does |
|---|---|
| `userspec-quality-validator` | Checks user-spec structure, coverage, testability of acceptance criteria |
| `userspec-adequacy-validator` | Checks feasibility of the solution, scope, no over/underengineering |
| `interview-completeness-checker` | Looks for gaps in the user-spec interview |
| `tech-spec-validator` | Checks tech-spec structure, template compliance, task quality |
| `skeptic` | Hunts for mirages — references to non-existent files, functions, APIs |
| `completeness-validator` | Bidirectional requirement traceability user-spec ↔ tech-spec, over/underengineering detection |
| `task-creator` | Creates task files from the tech-spec implementation plan |
| `task-validator` | Checks task files for template compliance and description quality |
| `reality-checker` | Checks whether the files, functions, and dependencies referenced in tasks exist |
| `skill-checker` | Checks skills against skill-master standards |

#### Reviewers
| Agent | What it checks |
|---|---|
| `code-reviewer` | Code quality: architecture, readability, error handling, tests |
| `code-researcher` | Researches the codebase: files, patterns, tests, integrations, risks |
| `documentation-reviewer` | Project Knowledge quality: completeness, accuracy, no bloat |
| `test-reviewer` | Test quality: finds problems and proposes concrete fixes |
| `security-auditor` | Security against OWASP Top 10: SQL injection, XSS, auth, cryptography |
| `deploy-reviewer` | CI/CD pipeline: GitHub Actions, secrets management, deploy configuration |
| `infrastructure-reviewer` | Infrastructure: project structure, Docker, pre-commit hooks, .gitignore |
| `prompt-reviewer` | LLM prompt quality against prompt-master principles |

#### QA
| Agent | What it does |
|---|---|
| `pre-deploy-qa` | Runs tests, checks acceptance criteria from user-spec and tech-spec |
| `post-deploy-qa` | Verification on the live environment via MCP tools (Playwright, curl, Telegram MCP) |

### All skills

#### Planning
| Skill | Purpose |
|---|---|
| `methodology` | Description of the whole methodology: pipeline, structure, principles |
| `project-planning` | Interview about a new project → fills Project Knowledge + backlog (features, roadmap) |
| `user-spec-planning` | Interview with the user → user-spec.md with requirements |
| `tech-spec-planning` | Code research → tech-spec.md with architecture and implementation plan |
| `task-decomposition` | Tech-spec → atomic task files with TDD anchors |

#### Development
| Skill | Purpose |
|---|---|
| `code-writing` | The code-writing process: plan → tests → code → review |
| `feature-execution` | Feature orchestration: a team lead creates a team of agents and distributes tasks across waves |
| `prompt-master` | Writing, improving, and reviewing prompts for LLMs |

#### Quality
| Skill | Purpose |
|---|---|
| `code-reviewing` | Code review methodology across 11 dimensions: architecture, security, performance, etc. |
| `test-master` | Testing strategy: the test pyramid, when to use unit/integration/e2e, how to ensure test quality |
| `security-auditor` | Security audit against OWASP Top 10: injections, authentication, cryptography |
| `pre-deploy-qa` | Acceptance testing: running tests, checking acceptance criteria without a live environment |
| `post-deploy-qa` | Post-deploy verification on the live environment via MCP tools |

#### Infrastructure and documentation
| Skill | Purpose |
|---|---|
| `infrastructure-setup` | Setting up a new project's infrastructure: framework, Docker, pre-commit hooks (gitleaks), tests |
| `deploy-pipeline` | Setting up CI/CD: GitHub Actions, deploy (Vercel, Railway, Fly.io, AWS, VPS), secrets management |
| `documentation-writing` | Managing Project Knowledge: audit, update, consistency check |

#### Meta
| Skill | Purpose |
|---|---|
| `skill-master` | Creating and updating skills: structure, patterns, rules |
| `skill-tester` | The full skill-testing cycle: scenario design, runs, evaluation, report |

---

## Shared — templates and scripts

The `shared/` folder contains source materials used by skills and commands:

| Folder | What's inside |
|---|---|
| `templates/new-project/` | New-project template: `.claude/` structure, Project Knowledge files, CLAUDE.md, .gitignore. Used by `/init-project` |
| `templates/infrastructure/` | Infrastructure templates (Docker, CI/CD configs). Used by the `infrastructure-setup` skill |
| `work-templates/` | Working-document templates: `user-spec.md.template`, `tech-spec.md.template`, `task.md.template`, `decisions.md.template`, `checkpoint.yml.template`, `execution-plan.md.template`. Skills copy them when creating new specs and tasks |
| `interview-templates/` | Interview structures for the planning skills: `feature.yml` (for user-spec), `skill.yml` (for skill-tester) |
| `scripts/` | Helper scripts: `init-feature-folder.sh` — creates the work directory for a new feature |

---

## Hooks — automation

The `hooks/` folder contains Claude Code hooks that fire automatically on certain events:

| Hook | Event | What it does |
|---|---|---|
| `post-compact-restore.sh` | SessionStart (compact) | Restores feature-execution context after compaction: finds the checkpoint, verifies the current session is the team lead, prints instructions to resume work |

---

## Scripts and .codex — Codex runtime support

The `scripts/` folder:

| File | What it does |
|---|---|
| `sync-to-codex.py` + `sync-to-codex.sh` | Generates Codex-compatible skills/commands/agents and `AGENTS.md` from the Claude sources. The CLI supports `--dry-run`, `--apply`, `--project`. |
| `sync-mcp-to-codex.py` + `sync-mcp-to-codex.sh` | Imports MCP configs from `~/.claude/.mcp*.json` and projects into the local private Codex config (`~/.codex/mcp-imported/` and a block in `~/.codex/config.toml`). MCP secrets never go to the public repo. |

The `.codex/` folder is a pre-generated snapshot of the Codex runtime: `skills/`, `commands/`, `agents/`. You can copy it into `~/.codex/` as-is, or regenerate it locally (see the "Two runtimes" section above).

More on the dual runtime — the `methodology` skill.

---

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) and/or [Codex CLI](https://github.com/openai/codex) — the framework supports both runtimes
- [Context7 MCP server](https://github.com/upstash/context7) — the agent uses it to fetch up-to-date library documentation instead of relying on training data
- Python 3.10+ — needed for `scripts/sync-to-codex.py` if you use the Codex runtime

---

## License

MIT License — use freely.

## Author

Pavel Molyanov — [molyanov.ru](https://molyanov.ru)
