---
name: skill-master
description: |
  Guides creating, editing, and reviewing skills in ~/.claude and project .claude/ for Claude
  Code and Codex: local form and routing standards, references, scripts, skill reviewers, and
  the required Claude-to-Codex sync after edits. Use whenever a skill is being changed or
  evaluated, including proposing a change, diagnosing why a skill did not trigger, and fixing
  its description or rules. Use instead of the generic skill-creator for these skills.
---

# Skill Creator

## Manual Claude-to-Codex Sync

Claude-side is the source of truth for the converter's allowlist: global `CLAUDE.md`, `skills/**`,
`agents/*.md`, and `commands/*.md`; or project `CLAUDE.md`, `.claude/skills/**`,
`.claude/agents/*.md`, and `.claude/commands/*.md`. Codex-side outputs are generated runtime. No
scheduled job performs this conversion. After editing an allowlisted source, the editing agent runs
the matching command immediately and reviews the generated result:

```bash
~/.claude/scripts/sync-to-codex.sh --apply                   # global ~/.claude/**
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply  # project .claude/**
```

Do not edit generated Codex files directly. If one was changed, move the intended content to its
Claude source, discard the direct generated edit, and run the matching command above to regenerate
Codex.

Git hooks are fallback checks: pre-commit repeats project sync, rejects partial staging, and stages
generated outputs; pre-push blocks remaining drift. For a project, commit generated
`.agents/skills/**`, `.codex/**`, and `AGENTS.md` changes with their Claude sources, except
host-local `.codex/.sync/**`. For global changes, commit and push generated outputs in the
separate `~/.codex` repository before pushing `~/.claude`; global pre-push enforces that ordering.

If sync reports a conflict or validation error, stop and report it. When an approved deletion or
rename produces an orphan, inspect every reported target and, only when all targets correspond to
the approved source change, run the matching reviewed prune command:

```bash
~/.claude/scripts/sync-to-codex.sh --apply --prune --confirm-delete
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply --prune --confirm-delete
```

Stop instead if the orphan list contains anything else.

**Bundled resources and the sync:** Markdown files (`SKILL.md`, `references/*.md`) are text-adapted
during sync (Claude tool names to Codex equivalents). Every other bundled file—`scripts/`,
`assets/`, images, and data—is copied byte-for-byte. Bundled executables must therefore remain
runtime-neutral: do not hardcode `.claude` paths or Claude-only tool names, resolve resources
relative to their own package, and keep runtime-specific instructions in Markdown that the
converter adapts.

## About Skills

Skills give the agent domain knowledge it does not have or a specific way of working needed by
the user.

Assume the agent can use ordinary tools, understand the current conversation, notice command
failures, and handle routine recoverable errors. Add an instruction only when the task, an
established contract, or a security, authorization, data-loss, or irreversible-action boundary
requires it. Do not add required actions, checks, state, or branches for behavior the agent can
already handle, and do not re-check immediately visible results.

Correct a local defect only when it restores agreed normal behavior. Treat a rare or unagreed
scenario, or a correction that adds behavior, state, entities, contracts, dependencies,
architecture, or material complexity, as a user decision; after the decision, encode the chosen
behavior or omit special handling.

## Skill Types

There are two types of skills based on how they guide Claude's work.

### Procedural Skills

Use when the skill defines a way of working or a sequence of actions. Describe it in the form and
detail the task requires. Phases, checkpoints, and explicit state are tools for real dependencies,
not required features of a procedural skill.

**Creating a procedural skill?** Read [procedural-skills.md](references/procedural-skills.md) — phase structure, checkpoints, verification patterns.

### Informational Skills

Use when providing methodology, knowledge, or guidelines without a required execution order.
Organize content by topic. Add decision guidance only where the task contains a real choice.

**Creating an informational skill?** Read [informational-skills.md](references/informational-skills.md) — section organization, knowledge structure.

## 1. Discovery

For a new skill or major change, reuse the request and project facts to establish purpose, routing,
scope, and required output. If a material design decision remains unresolved, run the adaptive
interview from [interview-guide.md](references/interview-guide.md) — question admission, stopping
rule, and handling decisions the user cannot answer. Otherwise proceed without an interview.

Before creating or materially changing a skill without an approved user-spec or user-approved
plan, briefly explain in simple user-facing language how the skill will behave from activation to
result, including any user checkpoints, and why this is the simplest sufficient design; then wait
for approval. Show the user the exact text of every skill change, however small, and edit only
after approval.

## 2. Skill Structure

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

### Frontmatter

**`name`** (required):
- kebab-case (lowercase, hyphens)
- ≤64 characters
- Exactly matches the skill directory name
- Unique identifier; must not contain "anthropic" or "claude"

**`description`** (required):
- Third person ("Analyzes code...", NOT "I analyze...")
- Include both WHAT the skill does AND WHEN to use it
- ≤1024 characters, no XML tags

#### Writing the Description

The agent sees only descriptions before loading a skill, matches them by meaning, and consults a
skill only when it believes it cannot handle the task well alone. Skills therefore tend to
under-trigger, especially when the need is one step of a larger task or looks simple.

- Put the key use case and terms first: Claude Code truncates long descriptions in the skill
  listing, and Codex shortens descriptions first when all skills exceed its shared budget.
- Describe WHEN as situations and topics, not as an inventory of user phrases; a few example
  requests are fine when they clarify the domain.
- Name what the agent lacks without the skill (data locations, conventions, a required
  workflow) and cover non-obvious cases with "including…": the skill as one step of another
  task, or a request that does not name the domain directly.

**Template:**
```yaml
description: |
  [What the skill does and what it knows that the agent does not; key terms first.]
  Use whenever [situations and topics], including [non-obvious cases].
```

**Bad:**
```yaml
description: |
  Helps with reports.

  Use when: "сделай отчёт", "создай отчёт", "сгенерируй отчёт", "подготовь отчёт"
```
**Good:**
```yaml
description: |
  Extracts text and tables from PDF files, fills forms, and merges documents. Use when working
  with PDF files or when the user mentions PDFs, forms, or document extraction.
```
#### Negative Triggers

Add an explicit "do not use for" line only when the skill genuinely overlaps a neighboring skill or has a plausible near-miss. Negative routing should resolve a real ambiguity, not pad the description.

```yaml
description: |
  Analyzes SQL query performance and suggests index changes. Use when a query is slow or may
  need an index.
  Do NOT use for: writing new queries from scratch, schema design, data migrations.
```

**Need invocation control, tool permissions, path scoping, forked execution, or a model or
effort override?** Read [frontmatter-options.md](references/frontmatter-options.md) — optional
fields, their Claude Code effect, and why routing stays in `description`.

### Body

Every SKILL.md body consists of:
- **Core workflow** — main instructions that are always needed
- **Links to references** — for optional/detailed information
- Keep under 500 lines (otherwise → split to references)

**When defining output format**, read [output-patterns.md](references/output-patterns.md) — template pattern, examples pattern.

### Bundled Resources

A skill contains only SKILL.md and these three optional directories — nothing else (no README, CHANGELOG, etc.).

#### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for **deterministic mechanical work** — the kind of thing a model should not be redoing by hand each run.

Use scripts for repeated deterministic work such as calculation, transformation, or scaffolding.
Do not use them to validate model judgment or police the skill's own output. A bundled script
should handle its mechanical errors and expose a clear invocation contract.

#### References (`references/`)

Content needed in some execution paths, not all. If the skill branches (multiple operations, domains, modes) — each branch's details go to a reference. Content needed on every execution stays in SKILL.md.

- **No duplication**: Content lives in either SKILL.md or references, not both

**How to link references in SKILL.md:**

Embed references where they are used:

**Pattern A: Action-embedded (strong)** — the workflow step's action IS applying the reference content. The agent cannot complete the step without loading the file.

```markdown
3. Write tests following patterns from [testing-guide.md](references/testing-guide.md)
   (test structure, naming, what to skip)

4. Apply audit criteria from [principles.md](references/principles.md) to each file
   (code examples, obvious content, generic explanations)
```

**Pattern B: Condition + contents (basic)** — for optional references needed only in specific scenarios. Each link explains WHEN to read and WHAT's inside.

```markdown
**For tracked changes**, see [REDLINING.md] — revision marks, accept/reject.
**First time with docx-js?** Read [DOCX-JS.md] — setup, examples, pitfalls.
```

Use Pattern A for required rules and Pattern B for conditional details. Do not put references in a
passive resource catalog separated from the workflow.

```markdown
❌ Bad — passive catalog (ignored):
## Resources
### references/structure.md
Complete description of all files...
### references/principles.md
Quality principles...

✅ Good — embed each reference into the workflow step where it's needed:
4. Apply audit criteria from [principles.md](references/principles.md) to each file
```

#### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

Use assets for templates, images, fonts, boilerplate, and other files copied or modified in the
output rather than read as instructions.

## 3. Writing Guidelines

### Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Progressive Disclosure

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** — Always in context (~100 words)
2. **SKILL.md body** — When skill triggers (<5k words)
3. **Bundled resources** — As needed by Claude (unlimited, scripts execute without reading)

Keep SKILL.md body under 500 lines. Split content into separate files when approaching this limit. When splitting, reference them from SKILL.md and describe clearly when to read them.

Keep core workflow and selection guidance in SKILL.md. Move conditional or variant-specific
details into references, linked where the agent needs them.

```markdown
**For tracked changes**, read [redlining.md](references/redlining.md) — revision marks and
accept/reject behavior.
```

**Important guidelines:**
- Keep references one level deep from SKILL.md
- For large reference files (roughly over 300 lines), include a short table of contents when it
  materially improves navigation

### Generalize and Explain Why

Treat an incident as evidence, not as a rule template. Remove its names, artifacts, and exact
sequence; if no reusable decision remains across multiple realistic uses, fix the execution or
local artifact instead of changing the skill. Keep incident-specific guidance only for an
established contract or a security, authorization, data-loss, or irreversible-action boundary.

Refer to the person the skill serves as "the user" and keep their personal facts (name, accounts,
home-directory paths) in the project's documented context, such as Project Knowledge, not in skill
text: skills are reused across projects and people, and a hardcoded owner makes them wrong or
leaky elsewhere.

Prefer positive instructions when they fully convey the rule. Keep explicit negatives for
security, irreversible damage, disambiguation, and scope boundaries.

Explain why a non-obvious instruction matters so the agent can apply it correctly beyond the
example:

**Bad:** "Always return JSON format."
**Good:** "Return findings as JSON — orchestrator parses this automatically, invalid JSON crashes pipeline."

Words such as CRITICAL, MANDATORY, NEVER, IMPORTANT, and MUST do not replace a clear instruction
and its reason. Flag emphasis only when it creates noise, substitutes for motivation, or makes
priorities conflict.

### Delegating Heavy Work

Use subagents when fresh isolated context materially helps review, research, debugging, validation,
parallel work, or high-volume analysis. Use an inline prompt for a bounded one-off task and a
dedicated Skill + Agent only for substantial reusable methodology. Keep detailed agent contracts
out of SKILL.md. Apply [agents.md](references/agents.md) when delegating work or creating a
reviewer.

## 4. Validation

### Run Applicable Reviewers

Launch fresh skeptical reviewers according to what changed. Each applies the common contract from
[agents.md → Reviewer contract](references/agents.md):

- `skill-checker` — form, routing, package structure, and references;
- `skill-logic-reviewer` — executable logic on required paths and established contracts;
- `skill-simplicity-reviewer` — unnecessary rules, mechanisms, checks, and complexity.

Use `skill-checker` for form or routing changes, `skill-logic-reviewer` for workflow or branching
changes, and `skill-simplicity-reviewer` when changing rules, phases, checkpoints, scripts, options,
or references. Run all three in parallel for a new skill or a major rewrite. Do not run an
unaffected lane merely to satisfy ceremony.

Provide the user scope, touched artifacts, relevant references and contracts, validation evidence,
and a short explanation of what changed, how the skill will affect agent behavior, why this
approach was chosen, deliberate limits, and assumptions. Reviewers may challenge the chosen
approach or propose alternatives within their lane. After reviewers return, apply no finding and
do not repeat the review automatically. Explain what changed in the skill and how it will affect
agent behavior, then what reviewers found, what it can cause, whether you agree and why, and what
you recommend. Wait for the user's approval before editing.

All three are defined under `~/.claude/agents/` and have skill-master preloaded.

### Check Triggering

After applying a description change that affects routing, check it in fresh sessions; the
authoring session already holds the skill in context and hides gaps. From the directory where
each would normally be asked, run the request that exposed the miss, one or two realistic
requests (including one where the skill is a step of a larger task), and one near-miss that
belongs to a neighboring skill:

```bash
claude -p "<request>" --output-format stream-json --verbose --max-turns 4 \
  --permission-mode plan --no-session-persistence \
  | grep -oE '"skill":"[^"]*"|"terminal_reason":"[^"]*"'
```

Each run prints the skills it loaded and how it ended. A run that ended with an API or
authentication error (`"terminal_reason":"api_error"`) did not test routing: stop and tell the
user instead of counting it as a miss. Repeat the request that exposed the miss a few times.
Routing is probabilistic: report the results to the user as evidence, not as a guarantee.
