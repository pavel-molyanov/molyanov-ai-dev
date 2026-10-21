---
name: methodology
description: |
  Explains the AI-First development methodology: which skill owns what, Project Knowledge,
  user-spec planning and implementation, reviewer agents, feature finalization, new projects, and
  the Claude/Codex dual runtime. Use whenever someone asks how the workflow, pipeline, or skill
  system works, or which path or skill fits a piece of work.
---

# AI-First Development Methodology

## Purpose

The methodology keeps project and feature work understandable across sessions while making the
process proportional to the task. Durable project facts live in Project Knowledge, an approved
user-spec is the contract for a planned feature, execution skills own their domain workflows, and
fresh reviewer agents diagnose completed work without taking decisions away from the orchestrator
or the user.

## Operating Model

Requests route directly to skills by intent. The global `commands/` source is currently empty;
feature planning, direct execution, initialization, documentation, and finalization do not depend
on command wrapper files. Request the workflow in plain language; historical shorthand such as
`/new-user-spec` or `/done` does not imply that an installed slash-command wrapper exists.

Choose the smallest path that fits the work:

| Need | Path |
|---|---|
| Small, well-defined change | Invoke the matching execution skill directly |
| Feature whose behavior or approach needs agreement | `user-spec-planning` → approval → execution → finalization |
| New repository | `project-initialization` → initial Project Knowledge → feature or ad-hoc work |
| Documentation-only work | `documentation-writing` with the evidence boundary named by the request |
| Review or audit only | Use the matching review skill or reviewer without modifying the artifact |

One request may activate several skills. For example, a UI feature with state changes uses both
`layout-writing` and `code-writing`; their verification and reviewers are coordinated in one
execution rather than treated as unrelated pipelines.

## Planned Feature Lifecycle

```text
user-spec-planning → explicit approval → new task: implement the approved spec
→ verified implementation commit → documentation-writing feature finalization
```

### Plan the Feature

`user-spec-planning` owns the complete planning contract:

1. Start or resume `work/{feature}/logs/userspec/interview.yml`. Ask 3–4 questions per batch and
   run as many batches as the actual gaps require; there is no fixed number of interview cycles.
2. Load the Project Knowledge router when it exists and follow only the routes relevant to the
   feature. Missing Project Knowledge does not block feature planning.
3. Once the intended outcome is clear enough, run `code-researcher`, write
   `work/{feature}/code-research.md`, and use code evidence in the remaining interview.
4. Run fresh `interview-completeness-checker` instances until the agreed scope has no substantive
   requirements gap. A finding that would expand the feature returns to the user for a decision.
5. Fill the bundled user-spec template in place. Keep its scaffold in English, write its content
   in the user's language, preserve the executor instruction, and commit the draft.
6. Validate every round in parallel with:
   - `userspec-quality-validator` for document quality, coverage, and testable criteria;
   - `userspec-adequacy-validator` for feasibility, proportionality, and architecture fit;
   - `skeptic` for factual claims about the current codebase.
7. Stop when all lanes are clean or after the third validation round. Obtain explicit user
   approval, set the spec and interview statuses, commit the approval, and return the absolute
   user-spec path for a new task.

If the request contains independently valuable outcomes, planning proposes a split and waits for
the user's choice. Different files, code layers, or execution skills alone do not require separate
specs.

### Implement the Feature

The implementation task reads the approved `user-spec.md`, its executor instruction,
`decisions.md` when present, and the relevant Project Knowledge routes. It then activates the
skills required by the agreed work:

- `code-writing` owns application behavior, data flow, APIs, state, validation, and code changes;
- `layout-writing` owns markup, styling, typography, assets, responsive behavior, and visual
  evidence;
- `infrastructure-setup` owns Docker, hooks, CI/CD, delivery, release artifacts, monitoring,
  recovery, and other operational changes;
- `prompt-master` owns LLM prompt creation and revision;
- `skill-master` owns skill creation and revision.

Each executor reads context in proportion to the change, implements only agreed behavior, runs the
smallest checks that establish the result, and coordinates every reviewer required by the active
skills. When observable behavior changes, `test-master` selects the smallest reliable boundary
that reproduces each meaningful risk; it does not create tests for artifacts with no contract to
protect.

The user-spec template requires the verified implementation to be committed separately before
feature finalization. `decisions.md` receives only material decisions or deviations that need to
survive the current context.

### Finalize the Feature

Feature finalization is an explicit mode of `documentation-writing`. The user identifies
`work/{feature}/` and asks to finish or finalize it; no wrapper command file is required.

The skill reads the spec, decisions, implementation, and relevant Git history; checks whether the
feature is evidently complete; updates only affected durable Project Knowledge; removes active
links that still treat the feature folder as current; moves it to
`work/completed/{feature}/`; and commits the documentation and archive change. If Project
Knowledge is missing, the documentation update is skipped but archival and finalization may still
continue.

This is the only documentation mode that reads feature artifacts by default, archives a feature,
or creates a finalization commit. A normal documentation update or audit does none of those.

## Ad-hoc Work

A small direct request does not require a user-spec. The matching execution skill derives done
from the request, reads only the needed project context, makes the focused change, and verifies it
at the smallest useful boundary. Broader or cross-cutting work loads the contracts and Project
Knowledge routes it actually affects.

A risk, idea, edge case, or improvement discovered during implementation or review is a proposal,
not new authorization. The executor may correct a local defect it finds during implementation or
direct checks before review; a change to behavior, scope, approach, state, fallback, validation, or
material complexity returns to the user for a decision. Reviewer findings also return to the user.

## New Projects and Project Knowledge

`project-initialization` creates a dual-runtime repository from its bundled template, preserves
pre-existing files in the next available `old*` directory,
configures Git hooks, creates the initialization commit, connects a private GitHub
repository, and creates `main`, plus an active `dev` for software development. Reviewing or
merging preserved `old*` files is separate work.

The next step is initial Project Knowledge through `documentation-writing`. Its adaptive interview
derives what it can from the repository, uses as many question batches as needed, obtains
checkpoint agreement for project definition, architecture, and operations/experience, proposes a
documentation topology when one is not already established, and writes durable facts in English.

Project Knowledge lives in `.claude/skills/project-knowledge/`, whose `SKILL.md` is always the
router. Use structure by context boundary rather than file size:

- compact projects may keep Project, Architecture, Patterns, Deployment, and applicable UX or
  domain facts in the router itself;
- standard projects use the router plus `project.md`, `architecture.md`, `patterns.md`, and
  `deployment.md`;
- `ux-guidelines.md` or domain references are added only when they form independently useful
  loading boundaries.

`CLAUDE.md` remains a compact entrypoint: project identity, Project Knowledge route, backlog path,
and default branch. It does not duplicate detailed project facts.

## Sources of Truth

### Approved User Spec

`work/{feature}/user-spec.md` owns the agreed feature outcome, behavior, acceptance criteria,
constraints, risks, accepted decisions, testing intent, and verification plan.

### Project Knowledge

Project Knowledge owns current durable project facts: purpose, architecture, project-specific
patterns and business rules, deployment and operations, and applicable UX or domain guidance.
Code owns implementation detail; configuration or registries own changing inventories; `work/`
artifacts are evidence rather than owners of current project state.

### Feature Folder

```text
work/{feature}/
├── user-spec.md
├── code-research.md
├── decisions.md
└── logs/
    ├── userspec/
    │   └── interview.yml
    └── working/
```

Completed features move to `work/completed/{feature}/`. Planning templates, interview state, and
the initializer script are bundled inside `user-spec-planning`; new-project templates are bundled
inside `project-initialization`. There is no shared resource directory between skills.

## Skill Responsibilities

| Area | Owning skills |
|---|---|
| Feature requirements | `user-spec-planning` |
| Project documentation and finalization | `documentation-writing` |
| Application implementation | `code-writing` |
| UI implementation and visual evidence | `layout-writing` |
| Infrastructure and operations | `infrastructure-setup` |
| Project creation | `project-initialization` |
| Prompt authoring | `prompt-master` |
| Skill authoring | `skill-master` |
| Test selection and quality | `test-master` |
| Code, layout, and security review criteria | `code-reviewing`, `layout-reviewing`, `security-auditor` |

A skill package owns its optional `references/`, deterministic `scripts/`, and output
`assets/`. This keeps dependencies portable through Claude-to-Codex conversion and public
publication instead of relying on unrelated global directories.

## Review Model

Reusable methodology lives in skills. Dedicated reviewer agents add fresh isolated context, a
bounded skeptical role, the minimum tools needed to inspect evidence, and a structured diagnostic
result. They inherit the orchestrator's model without a caller override. They do not edit
artifacts or decide whether work ships. Within their lane they may challenge the chosen approach,
complexity, or missing possibilities and propose alternatives. A clean result is valid.

The orchestrator supplies the requirements, relevant artifacts and contracts, validation evidence,
and a short explanation of the implementation. Reviewers verify that explanation as a claim rather
than treating it as authority. The shared reviewer and orchestrator contract is owned by
`skill-master/references/agents.md`.

Before the first review, the orchestrator selects the complete reviewer set required by all active
skills. The set reviews the same artifact revision in parallel as one review stage. After the
reviewers return, the orchestrator explains their findings, its assessment, and its recommendation
to the user without applying findings or automatically repeating the stage. Only explicit approval
of specific changes starts a correction cycle. The separate user-spec validation process still
allows at most three rounds.

Common reviewer ownership is:

- every completed code implementation: `code-reviewer`;
- layout implementation: `layout-reviewer` with prepared source and rendered evidence;
- meaningful test-code changes: `test-reviewer` through `test-master`;
- changed security boundaries or an explicit security request: `security-auditor`;
- documentation edits: `documentation-reviewer`;
- material infrastructure work or an explicit infrastructure review: `infrastructure-reviewer`;
- prompt edits: `prompt-reviewer`;
- skill changes: the applicable `skill-checker`, `skill-logic-reviewer`, and
  `skill-simplicity-reviewer` lanes;

Distinct stages that examine different artifacts or boundaries remain separate, such as the source
and destination scans in public publication.

## Working Principles

- **Simplest sufficient process:** add a document, abstraction, rule, fallback, or coordination
  layer only for a current requirement or demonstrated failure.
- **Proportional context:** load the smallest context that preserves the affected contracts.
- **One outcome, one user-facing specification:** split only independently valuable outcomes and
  let the user decide.
- **Evidence before action:** reviewer identity or severity never substitutes for evidence, and a
  finding never expands authorization.
- **Stable commits:** commit meaningful states such as a draft spec, approved spec, verified
  implementation, or finalized documentation; do not force incidental state into a commit.

## Claude and Codex Dual Runtime

Claude-side instructions, skills, agents, and commands are the source of truth. The editing agent
runs Claude-to-Codex sync during its work and reviews the generated runtime; no background timer
does this. Repository hooks are safety checks: pre-commit repeats sync and stages generated
outputs, while pre-push blocks drift. Commit project outputs with their sources, and deliver global
outputs through the separate `~/.codex` repository first. Project Codex skills are generated into
`<project>/.agents/skills`, where Codex discovers them; agents, `config.toml`, and the sync manifest
stay in `.codex/`.

### MCP Import

MCP import is separate from skill conversion. The importer scans the global Claude MCP source and
immediate projects under `~/projects`; `--project` adds roots rather than narrowing that host-wide
scope. Preview changes on every host whose Codex runtime must change:

```bash
~/.claude/scripts/sync-mcp-to-codex.sh
```

Review sources, servers, and warnings; stop on any warning or validation error. Then apply with
`--apply` and inspect every changed Codex configuration. The dry run does not report deletions
performed by `--prune`, so normal changes do not use it. Treat removal or relocation as a separate
maintenance operation: inspect the import manifest and every target before an explicit prune.
Credentials never belong in commits.
