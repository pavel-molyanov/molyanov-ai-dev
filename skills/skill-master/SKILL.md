---
name: skill-master
description: |
  Guides skill creation and updates with specialized knowledge and workflows.

  Use when: "создай скилл", "измени скилл", "гайд по скиллам", "обнови скилл", "улучши скилл",
  "create skill", "update skill", "skill guide", "new skill", "how to write a skill"
---

# Skill Creator

## Manual Claude-to-Codex Sync

Claude-side is the source of truth for the converter's allowlist: global `skills/**`, `agents/*.md`,
and `commands/*.md`; or project `CLAUDE.md`, `.claude/skills/**`, `.claude/agents/*.md`, and
`.claude/commands/*.md`.
Codex-side outputs are generated runtime. No scheduled job performs this conversion. After editing
an allowlisted source, the editing agent runs the matching command and reviews the generated result
before finishing:

```bash
~/.claude/scripts/sync-to-codex.sh --apply                   # global ~/.claude/**
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply  # project .claude/**
```

For a project, commit generated `.codex/**` / `AGENTS.md` changes with their Claude sources, except host-local `.codex/.sync/**`. Global `~/.codex/**` is runtime state outside the `~/.claude` repository: run the global command explicitly on every affected host and do not add it to the Claude-source commit. If sync reports a conflict or validation error, stop and report it.

**Authoring a skill that edits `.claude/**`?** Paste the block above near the top of its `SKILL.md` so its changes reach Codex too. A skill that never touches `.claude/**` (pure analysis, code-writing in a project's own source tree) does not need it.

**Bundled resources and the sync:** Markdown files (`SKILL.md`, `references/*.md`) are text-adapted during sync (Claude tool names → Codex equivalents). Every other bundled file — `scripts/`, `assets/`, images, data — is copied **byte-for-byte, unmodified**. So a bundled script must be **runtime-agnostic**: don't hardcode `.claude` paths or Claude-only tool names, since neither is rewritten in the Codex copy. Reference files relative to the script's own location, and let the surrounding `SKILL.md` prose (which *is* adapted) carry any runtime-specific instructions.

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
- Unique identifier

**`description`** (required):
- Third person ("Analyzes code...", NOT "I analyze...")
- Include both WHAT the skill does AND WHEN to use it
- ≤1024 characters

#### Description Best Practices

Claude uses description to decide when to auto-invoke the skill. Be specific and include key terms.

**Template:**
```yaml
description: |
  [What the skill does — be specific, include key terms]

  Use when: [trigger conditions — specific phrases users say]
```

Use concrete positive routing: name the real intents and only the wording variations needed to
distinguish the skill's domain.

**Bad:**
```yaml
description: This skill helps with documents. Use when user wants to work with docs.
```
**Good:**
```yaml
description: |
  Manage .claude/skills/project-knowledge/ docs: create, check, update.

  Use when: "заполни документацию", "создай документацию", "проверь документацию", "обнови документацию"
```
#### Negative Triggers

Add an explicit "do not use for" line only when the skill genuinely overlaps a neighboring skill or has a plausible near-miss. Negative routing should resolve a real ambiguity, not pad the description.

```yaml
description: |
  Analyze SQL query performance and suggest index changes.

  Use when: "why is this query slow", "optimize this SELECT", "add an index"
  Do NOT use for: writing new queries from scratch, schema design, data migrations.
```

**Need argument-hint, disable-model-invocation, or model override?** Read [frontmatter-options.md](references/frontmatter-options.md) — optional fields and when to use each.

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

Write a draft, then remove instructions that do not change the outcome. Generalize from realistic
usage instead of adding branches for isolated examples or hypothetical future configurations.

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

Launch fresh skeptical reviewers according to what changed. Each applies the evidence gate and
common JSON contract from [agents.md → Reviewer contract](references/agents.md):

- `skill-checker` — form, routing, package structure, and references;
- `skill-logic-reviewer` — executable logic on required paths and established contracts;
- `skill-simplicity-reviewer` — unnecessary rules, mechanisms, checks, and complexity.

Use `skill-checker` for form or routing changes, `skill-logic-reviewer` for workflow or branching
changes, and `skill-simplicity-reviewer` when changing rules, phases, checkpoints, scripts, options,
or references. Run all three in parallel for a new skill or a major rewrite. Do not run an
unaffected lane merely to satisfy ceremony.

Provide the user scope, touched artifacts, relevant references and contracts, and validation
evidence. Review findings are diagnoses, not a work queue. Check the evidence and exact correction;
apply only an authorized local correction to agreed normal behavior. If the scenario is rare or
unagreed, or the correction adds behavior, state, entities, contracts, dependencies, architecture,
or material complexity, reject it with a short reason or ask the user before editing. A
`user_decision_required: false` value does not replace this check. Follow
[agents.md → Orchestrator responsibilities](references/agents.md).

All three are defined under `~/.claude/agents/` and have skill-master preloaded.
