# Skill + Agent Pattern

Subagents handle context-heavy subtasks for orchestrator skills. Each runs in isolated context, performs work, and returns results (or modifies files directly).

## Why Subagents

The orchestrator's context window is limited. Loading a skill, conversation history, and project context already consumes significant space. If the orchestrator opens many files, runs extensive analysis, or generates verbose output, context fills up and quality degrades.

**Solution:** Delegate heavy work to subagents. Each runs in isolated context, performs its task, and returns a structured result. The orchestrator receives only what it needs.

**Impact:** According to Anthropic research, multi-agent systems with Claude Opus orchestrator and Claude Sonnet subagents outperform single-agent Claude Opus by 90.2% on research tasks.

## Orchestration Rules

Subagents cannot call other subagents — Claude Code supports only one level of orchestration. Nested calls fail silently:

```
Orchestrator (main skill)
    ├── code-reviewer (subagent) ✓
    ├── security-auditor (subagent) ✓
    └── test-reviewer (subagent) ✓

code-reviewer
    └── another-agent ✗ FORBIDDEN
```

If subagent needs more work → return to orchestrator → orchestrator launches another subagent.

## When to Use Subagents

| Task Type | Why Subagent Helps | Example |
|-----------|-------------------|---------|
| Reviews | Fresh context for objective assessment | code-reviewer, security-auditor |
| Research | Extensive file reading stays isolated | Exploring codebase, reading docs |
| Debugging | Isolated diagnosis without polluting main context | Error analysis, root cause |
| Validation | Schema/format checking with clean slate | skill-checker, schema-validator |
| Parallel work | Multiple independent directions | Research 3 modules simultaneously |
| High-volume output | Tests, logs don't bloat main context | Running test suite, log analysis |

## Inline Agents (Ad-hoc Tasks)

For simple, one-off tasks — use Task tool with built-in subagent types:

```markdown
Use Explore subagent to find all files related to authentication
Use general-purpose subagent to analyze the error and suggest fixes
Use Plan subagent to design implementation approach for {feature}
```

The orchestrator calls Task tool with arbitrary prompt and `subagent_type`. No agent file needed.

**Built-in subagent types:**
- `Explore` — fast codebase exploration, file search, pattern matching
- `general-purpose` — flexible tasks, research, analysis
- `Plan` — designing implementation approaches

**When to use:**
- Simple research/exploration
- One-off file operations
- Tasks under 50 lines of instructions
- No reuse needed

## Dedicated Agents (Skill + Agent Pattern)

For complex, reusable tasks — create **Skill + Agent pair**:

1. **Skill** — holds methodology (WHAT to do, HOW to analyze)
   - Usable inline via `/skill-name`
   - Contains knowledge

2. **Agent** — adds isolation + output contract
   - Uses `skills:` to preload methodology
   - Defines output: JSON, file changes, or actions
   - Runs in isolated context

**Example:**

```yaml
# skills/code-reviewing/SKILL.md — methodology
---
name: code-reviewing
description: Code review methodology and quality standards.
---
## What to Check
- Architecture, error handling, edge cases...

## Severity Levels
- Critical, Major, Minor...
```

```yaml
# agents/code-reviewer.md — isolation + format
---
name: code-reviewer
description: Review code quality after implementation.
color: blue
skills:
  - code-reviewing    # Full SKILL.md content loaded
allowed-tools: Read, Glob, Grep
---
Follow code-reviewing methodology.

## Output
{ "findings": [...], "summary": {...} }
```

**Benefits:**
- Methodology usable inline (`/code-reviewing`) OR in isolation (via agent)
- Multiple agents can run in parallel
- No methodology duplication — skill is single source of truth
- Agent adds structure (output contract) without bloating skill

## Agent File Format

Agent files use YAML frontmatter + Markdown body. Store in `~/.claude/agents/{name}.md`.

```yaml
---
name: agent-name
description: |
  When Claude should delegate to this agent. Include:
  - Purpose and capabilities
  - Example triggers
  - What NOT to use it for
color: blue
skills:
  - methodology-skill
allowed-tools: Read, Glob, Grep
---

# Agent Instructions

## Input
[What the agent receives from the orchestrator]

## Process
[Step-by-step methodology — or reference preloaded skill]

## Output
[Output contract: JSON schema, file changes, or actions]
```

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Unique identifier (kebab-case) |
| `description` | When/why to use — Claude reads this to decide delegation |
| `color` | Badge color for visual identification (see below) |
| `skills` | Skill(s) to preload — agent must have methodology from skill |

### Color Recommendations

All agents must have a color for visual identification. Valid values: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`.

| Color | Agent Type |
|-------|------------|
| blue/cyan | Analysis, review (code-reviewer, test-reviewer) |
| red | Security, critical (security-auditor) |
| yellow | Validation, caution (skill-checker, schema-validator) |
| green | Success-oriented, exploration (Explore) |
| purple/pink | Creative, generation, research |
| orange | Infrastructure, deployment |

### Optional Fields

| Field | Default | Description |
|-------|---------|-------------|
| `model` | `inherit` | Always use `inherit` to match orchestrator's model |
| `allowed-tools` | All tools | Restrict to necessary tools (e.g., `Read, Glob, Grep`) |
| `permissionMode` | `default` | Permission handling: `default`, `acceptEdits`, `bypassPermissions`, `plan` |
| `hooks` | None | Lifecycle hooks for validation |

## Output Contracts

Agents always return JSON report — even if they modify files or execute commands. Work is the process, output is the report.

**Analysis agents** (reviewers, validators, critics) — findings and recommendations. These are hostile critics: they surface findings and do not gate. See [Reviewer Agents Are Hostile Critics](#reviewer-agents-are-hostile-critics) below — build every one of them that way.
```json
{
  "status": "clean" | "changes_required",
  "findings": [...],
  "clean_check": "when findings is empty: what you hunted for and why the artifact holds — a bare 'looks good' is not allowed",
  "summary": "..."
}
```

**Executor agents** — report of changes made:
```json
{
  "status": "success" | "partial" | "failed",
  "files_modified": ["path/to/file.ts", ...],
  "files_created": ["path/to/new.ts", ...],
  "summary": "Created 2 files, modified 3 files"
}
```

**Automation agents** — report of actions taken:
```json
{
  "status": "success" | "failed",
  "actions": ["ran tests", "deployed to staging"],
  "results": {...},
  "errors": []
}
```

## Reviewer Agents Are Hostile Critics

Any agent whose job is to **judge an artifact** — a reviewer, a validator, a checker, a critic — has one dominant failure mode: it rubber-stamps. Left neutral, a model reviewing work takes the safe path and says "looks good," because approving costs nothing and finding fault feels like conflict. A lenient reviewer is worse than no reviewer: it gives false confidence while the artifact stays flawed, and the holes surface later in a fresh session.

So every critic agent you create alongside a skill is built as a **hostile critic, not a gatekeeper**. This is not optional flavor — it is the contract that makes review actually work. (It applies only to *judging* agents. Executor agents that produce work, and automation agents that take actions, follow their own contracts above.)

### The six principles

**1. Adversarial stance, set in the opening line.** The first paragraph is the agent's identity and frames the whole run. Write it so the agent's job is to *build the case against* the artifact, not to bless it:

> You are a hostile {lane} critic, not a gatekeeper. Your job is to build the case that {artifact} {fails in your lane} — find every real {hole} and report it.

Then three explicit refusals: do not soften a finding, do not excuse a weak spot as "probably fine," do not stay silent to be safe. Close with the stake: *a critic who blesses flawed work has failed; a critic who finds nothing in a flawed artifact has failed.* **Why:** a neutral "review this" invites the safe "OK"; naming the agent a hostile critic in the first sentence flips its default from lenient to digging.

**2. The reviewer surfaces; the orchestrator decides.** State plainly that the agent does not gate — it does not decide whether the artifact ships. The orchestrator makes that call, weighing findings against its own copy of the standard. **Why:** the ship/no-ship decision is exactly what tempts a reviewer to be lenient. Remove it, and the agent's only job becomes producing the best possible list of real problems — no reason left to go easy.

**3. Read the whole artifact from scratch, not the diff.** The agent reads the entire artifact and every dependency it relies on, not just what changed. It understands what the change touches, but judges it in the context of the whole. **Why:** a diff shows what moved; a real hole usually lives where a change now contradicts an untouched part. Diff-only review is the single most common way holes slip through — the change looks fine in isolation and breaks something three sections away.

**4. Freshness is the orchestrator's job, not the agent's.** Keep round-awareness out of the agent entirely — it never needs to know which round it is or what a prior instance found. The orchestrator spawns a new instance each round (see [The orchestrator's half of the deal](#the-orchestrators-half-of-the-deal)), so every critic reads the artifact cold and structurally cannot anchor on "was my finding fixed?". The agent just gets a list of touched files, reads them whole (principle 3), and hunts. **Why:** a critic that tracks its own prior findings shrinks its scope each round and goes blind to holes a fix introduced; spawning fresh removes that failure at the source, and loading the agent with the round process is dead weight it never acts on.

**5. Every finding traces to a standard, with a location.** Each finding points to a concrete principle in the skill/spec/standard the agent checks against, and quotes the exact line or location. A finding without a location and a standard is noise. **Why:** taste-based findings can't be adjudicated and erode the orchestrator's trust in the whole report; anchored findings are actionable and let the orchestrator judge fast.

**6. Output discipline: no gate, worst-first, justified clean.** Findings are ranked worst-first — the highest-consequence problem at the top — with no severity threshold that hides "minor" issues. A clean verdict is allowed only when an honest full re-read genuinely finds nothing, and then the agent states what it hunted for and why the artifact holds. **A bare "approved" or "looks good" is not a review.** **Why:** worst-first lets the orchestrator triage at a glance; the justified-clean rule closes the rubber-stamp escape hatch — the agent can't pass by staying silent, it has to prove it looked.

### The orchestrator's half of the deal

Hostile reviewers surface findings even on a decent artifact — that is working as intended, not a bug. The orchestrator that calls them judges each finding on merit (severity is metadata, not a filter): a real hole → fix it; a finding you disagree with or aren't sure about → push back or discuss with the user. Without this judgment step, meaner reviewers just cause thrash — the orchestrator chases every nitpick. The two halves are a pair: aggressive reviewers *plus* an orchestrator that decides. See [Invoking from Skills](#invoking-from-skills) for the finding-processing pattern.

Three rules keep that judgment from snowballing one change into a rewrite of everything nearby:

**Scope discipline.** Fix unconditionally only what falls within the original scope of the work — the acceptance criteria of this task/change plus the files the change already touched. A finding that reaches outside that (new behavior beyond the criteria, a file the change never touched, a pre-existing defect unrelated to the change) is not fixed silently: surface it to the user for a scope decision. Reason: a hostile critic reading whole files will legitimately spot problems next door, and silently fixing them turns a scoped task into unbounded work the user never approved.

**Round cap.** Cap fix→re-review at two rounds per critic phase (e.g. tests, then code — each phase gets its own two rounds, not two shared across both). Reason: a fresh critic re-reads the whole artifact each round and can surface new holes indefinitely; two rounds catch what a fix regresses without looping forever. If in-scope findings remain after the second round, stop and bring them to the user instead of starting a third.

**A fresh critic each round is a new instance.** Spawn a new critic each round rather than handing the same one successive diffs. Reason: a critic that carries its previous context anchors on "was my finding fixed?" and stops hunting; a new instance reads the touched files from scratch, with no diff and no memory of the prior round, so it re-hunts the whole lane and catches holes a fix introduced.

### Skeleton to adapt

```markdown
You are a hostile {lane} critic, not a gatekeeper. Your job is to build the case
that {artifact} {fails in your lane} — find every {hole} and report it. You do
not decide whether {artifact} ships; the orchestrator does that, weighing your
findings against its own copy of {standard}. Do not soften a finding, do not
excuse a weak spot as "probably fine," and do not stay silent to be safe. A
critic who blesses flawed work has failed.

## Process
1. Read the whole {artifact} from scratch — and every {dependency} — not just the
   diff. Judge what changed in the context of the whole.
2. {lane-specific hunt method: simulate execution / walk each element / trace each claim}

## Output
No gate. Findings worst-first, each with a quoted location and the {standard} it
breaks. Report clean only on an honest full re-read that finds nothing — then say
what you hunted for and why it holds. A bare "approved" is not a review.
```

Fill `{lane}`, `{artifact}`, `{hole}`, and `{standard}` for the specific critic; the three skill-master reviewers (`skill-checker`, `skill-logic-reviewer`, `skill-simplicity-reviewer`) are worked examples of this skeleton.

## Resuming Agents

After agent completes, orchestrator receives `agentId`. Use it to continue work with same context:

```
Resume agent {agentId} to ask follow-up question about findings
```

**When to resume:**
- Need clarification on agent's findings
- Iterative refinement (agent found X, now do Y based on X)

**When NOT to resume (start fresh):**
- Different task, unrelated to previous
- Context would confuse agent
- Previous work is complete, new work begins

## Writing Effective Descriptions

The `description` field is critical — Claude uses it to decide when to delegate. Include:

1. **Purpose** — what the agent does
2. **Triggers** — when to use (with examples)
3. **Exclusions** — what NOT to use it for

Example from `code-reviewer`:
```yaml
description: |
  Use this agent when code has been written or modified and needs quality assessment.

  **Examples of when to use:**
  - After implementing a feature
  - After refactoring code
  - Before committing changes

  **Proactive usage**: Invoke automatically after any code implementation task.
```

## Invoking from Skills

Reference agents by name in skill workflow:

```markdown
## Post-work

1. **Run Reviews** (launch in parallel)
   - `code-reviewer` — quality, architecture, patterns
   - `security-auditor` — OWASP Top 10, vulnerabilities

2. **Process Findings** (see [The orchestrator's half of the deal](#the-orchestrators-half-of-the-deal))
   Evaluate each finding on merit — severity is metadata, not a filter.
   - Valid, in-scope, agree → apply (any severity)
   - In-scope but you disagree or are uncertain → discuss with user
   - Out of scope (new behavior, untouched files, unrelated pre-existing defect) → surface to user, don't fix silently
   Log each finding with action taken.

3. **Re-review** — spawn a fresh critic instance (not the same one); it re-reads the
   touched files from scratch. Cap at two rounds per critic phase; if in-scope
   findings remain, ask the user.
```

For agents needing specific input:

```markdown
Use `code-reviewer` subagent with:
- files: {list of modified files}
- userspec: {user requirements document}
- techspec: {technical specifications}
```

## Best Practices

1. **Define clear output contract** — JSON for analysis, file changes for executors
2. **Restrict tools** — Most agents only need `Read, Glob, Grep`
3. **Use `model: inherit`** — Ensures maximum quality from orchestrator's model
4. **Always preload skill** — Agent must have methodology, not just output format
5. **Include examples in description** — Helps Claude know when to invoke
6. **One level of orchestration** — Subagents cannot call other subagents

## Example Agents

See existing agents for full examples:
- `~/.claude/agents/code-reviewer.md` — Detailed methodology with review dimensions
- `~/.claude/agents/security-auditor.md` — OWASP-based security analysis
- `~/.claude/agents/skill-checker.md` — Skill validation against standards

## References

- [Create custom subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Multi-agent research system - Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)
