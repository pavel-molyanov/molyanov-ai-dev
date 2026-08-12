**English** | [Русский](README.ru.md)

# AI-First Development Framework

A practical, intent-driven methodology for building software with
[Claude Code](https://docs.anthropic.com/en/docs/claude-code) and
[Codex](https://github.com/openai/codex). It combines proportional planning, durable Project
Knowledge, focused execution skills, and evidence-gated review without forcing every task through
the same heavyweight pipeline.

User-facing artifacts follow the user's language. Technical documentation, code, prompts, and
skill instructions stay in English so the same project remains portable across sessions and
runtimes.

## Two runtimes, one source

Claude files are the editable source of truth. Codex files are generated runtime artifacts.

| Claude source | Codex runtime |
|---|---|
| `~/.claude/skills/**` | `~/.codex/skills/**` |
| `~/.claude/agents/*.md` | `~/.codex/agents/*.toml` |
| `~/.claude/commands/*.md`, when present | `~/.codex/skills/source-command-*/**` |
| Project `CLAUDE.md` | Project `AGENTS.md` |
| Project `.claude/**` | Project `.codex/**` |

After editing Claude-side sources, regenerate and review the Codex runtime:

```bash
~/.claude/scripts/sync-to-codex.sh --apply
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

The conversion is manual and reports conflicts, validation failures, and managed orphans instead
of silently deleting ambiguous runtime output.

## Quick start

Clone the repository:

```bash
git clone https://github.com/pavel-molyanov/molyanov-ai-dev.git
cd molyanov-ai-dev
```

For a new or empty setup, copy the runtime you use:

```bash
mkdir -p ~/.claude/scripts ~/.codex
cp -R skills agents ~/.claude/
cp scripts/sync-*.py scripts/sync-*.sh ~/.claude/scripts/
cp -R .codex/skills .codex/agents ~/.codex/
```

If you already use Claude Code or Codex, do not overwrite your whole configuration. Compare this
repository's `CLAUDE.md` and `AGENTS.md` with your files and manually add the instructions you are
missing. Update framework skills and agents selectively, remove only obsolete framework packages,
and keep your personal packages and Codex-owned `.codex/skills/.system` unchanged.

Then describe the outcome in plain language. Skills route by intent; slash-command wrappers are
not required.

Typical starting points:

- New repository: “Initialize this project” → `project-initialization`
- Initial or updated project documentation: “Create Project Knowledge” → `documentation-writing`
- Feature that needs agreement first: “Let's plan this feature” → `user-spec-planning`
- Small implementation: “Implement/fix this” → the matching execution skill
- Review only: “Review this code/layout/security boundary” → the matching review skill

## How the methodology works

### Choose the smallest path that fits

| Need | Workflow |
|---|---|
| Small, well-defined change | Matching execution skill directly |
| Feature whose behavior or approach needs agreement | `user-spec-planning` → approval → implementation → finalization |
| New repository | `project-initialization` → initial Project Knowledge → feature or ad-hoc work |
| Documentation-only work | `documentation-writing` with an explicit evidence boundary |
| Review or audit only | Matching review skill or reviewer; no artifact modification |

One request may activate several skills. A UI feature with state changes, for example, can combine
`layout-writing` and `code-writing` while sharing one verification and review cycle.

### Planned feature lifecycle

1. **Plan.** `user-spec-planning` runs an adaptive interview, reads relevant Project Knowledge,
   researches the codebase, and writes `work/{feature}/user-spec.md` from bundled templates.
2. **Validate.** Fresh quality, adequacy, and factual-codebase reviewers check the same draft.
   Findings must identify concrete evidence, a violated requirement, realistic conditions, and
   impact.
3. **Approve.** The user explicitly approves the user spec before implementation begins.
4. **Implement.** The required execution skills make the scoped change and run the smallest checks
   that establish the result. Applicable reviewers inspect the completed revision.
5. **Finalize.** `documentation-writing` updates only affected durable Project Knowledge and moves
   the feature folder to `work/completed/{feature}/`.

A small direct request does not need a user spec. Risks or ideas found during execution are
reported as proposals; they do not silently expand the authorized scope.

### Project Knowledge

Durable project facts live in `.claude/skills/project-knowledge/`. Its `SKILL.md` is the router and
loads only the context needed for the current task. Standard projects may use references such as:

- `project.md` — purpose, audience, features, and scope
- `architecture.md` — stack, structure, integrations, and data boundaries
- `patterns.md` — project-specific conventions, testing, and business rules
- `deployment.md` — environments, delivery, operations, and recovery
- `ux-guidelines.md` — UX language and domain guidance when it forms a useful context boundary

`CLAUDE.md` stays a compact entry point rather than duplicating this documentation.

## Skills

### Planning and project context

| Skill | Purpose |
|---|---|
| `methodology` | Explains routing, lifecycle, sources of truth, and review model |
| `project-initialization` | Creates a dual-runtime project, preserves existing files, configures hooks, Git, and a private GitHub repository |
| `documentation-writing` | Creates, audits, updates, and finalizes Project Knowledge |
| `user-spec-planning` | Produces an approved user spec through adaptive interview, code research, and validation |

### Execution

| Skill | Purpose |
|---|---|
| `code-writing` | Application behavior, APIs, state, validation, and focused code changes |
| `layout-writing` | High-fidelity UI implementation, responsive behavior, and visual evidence |
| `infrastructure-setup` | Local setup, Docker, hooks, CI/CD, delivery, monitoring, backups, and operations |
| `prompt-master` | LLM prompt creation, improvement, and review |
| `skill-master` | Skill and reviewer-agent creation or revision |

### Testing and review

| Skill | Purpose |
|---|---|
| `test-master` | Selects the smallest reliable test boundary and reviews test quality |
| `code-reviewing` | Reviews code against scope, project contracts, and quality risks |
| `layout-reviewing` | Reviews visual fidelity, responsiveness, and evidence coverage |
| `security-auditor` | Reviews changed security boundaries against applicable OWASP risks |

## Agents

Agents provide fresh, bounded context for research and skeptical review. Reviewers diagnose only:
they do not edit artifacts or decide whether work ships.

| Group | Agents |
|---|---|
| Research and user-spec validation | `code-researcher`, `interview-completeness-checker`, `skeptic`, `userspec-quality-validator`, `userspec-adequacy-validator` |
| Implementation and documentation review | `code-reviewer`, `layout-reviewer`, `test-reviewer`, `security-auditor`, `documentation-reviewer`, `infrastructure-reviewer`, `prompt-reviewer` |
| Skill review | `skill-checker`, `skill-logic-reviewer`, `skill-simplicity-reviewer` |

Claude definitions live in `agents/*.md`; native Codex definitions live in
`.codex/agents/*.toml`.

## Bundled skill resources

Resources now live with the skill that owns them; the legacy shared resource tree has been
removed.

- `project-initialization/assets/new-project/` — dual-runtime project scaffold, Project Knowledge,
  hooks, secret-safe `.gitignore`, backlog, and work archive
- `user-spec-planning/assets/` and `scripts/` — user-spec, interview, decisions templates, and
  deterministic feature-folder initialization
- `documentation-writing/assets/` and `references/` — Project Knowledge interview and topology
  guidance
- `layout-writing/scripts/` — capture, overlay, and visual comparison utilities with tests
- `infrastructure-setup/references/` — deployment, release, monitoring, and alerting guidance
- `test-master/references/` — unit, integration, smoke, end-to-end, and test-review guidance
- `skill-master/references/` — skill forms, interviews, reviewer contracts, and output patterns

## Scripts and Codex support

- `scripts/sync-to-codex.py` / `.sh` convert Claude skills, agents, commands, and project
  instructions into Codex runtime artifacts.
- `scripts/sync-mcp-to-codex.py` / `.sh` preview and import MCP configuration separately from skill
  conversion.
- `.codex/skills/` and `.codex/agents/` provide a ready-made sanitized Codex runtime snapshot.
- Codex-owned `.system` skills and host-local `.codex/.sync/` state are intentionally excluded.

## Requirements

- Claude Code CLI and/or Codex CLI
- Python 3.11+
- Bash-compatible shell (macOS/Linux, WSL, or Git Bash on Windows)
- Git; GitHub CLI (`gh`) for `project-initialization`
- Context7 MCP configuration used by the bundled project template
- Node.js when using the bundled layout capture and comparison scripts

## License and author

[MIT](LICENSE) © [Pavel Molyanov](https://github.com/pavel-molyanov)
