# Skill + Agent Pattern

Subagents isolate context-heavy work from the orchestrator. A skill holds reusable methodology;
an agent adds a bounded role, necessary tools, and a result contract.

## Contents

- [Runtime-neutral orchestration](#runtime-neutral-orchestration)
- [When to delegate](#when-to-delegate)
- [Inline and dedicated agents](#inline-and-dedicated-agents)
- [Agent file format](#agent-file-format)
- [Reviewer contract](#reviewer-contract)
- [Other agent contracts](#other-agent-contracts)
- [Orchestrator responsibilities](#orchestrator-responsibilities)
- [Invoking agents from skills](#invoking-agents-from-skills)

## Runtime-neutral orchestration

Use the subagent mechanism available in the current runtime. Describe the role and required
result without assuming a particular Team, Task, transcript, or transport API.

Nested delegation is allowed when the runtime supports it and the subtask genuinely benefits
from another isolated context. The delegating agent remains responsible for its own bounded
result. If nested delegation is unavailable or unnecessary, it returns the need to the
orchestrator instead.

Agents inherit the orchestrator's model. Do not set a different model in callers; agent
definitions use `model: inherit` where the runtime supports that field.

## When to delegate

| Task type | Why isolation helps | Example |
|---|---|---|
| Review | Fresh context reduces anchoring on the implementation | Code or security review |
| Research | Extensive file reading stays outside the main context | Codebase exploration |
| Debugging | A focused trace keeps logs and hypotheses bounded | Root-cause analysis |
| Validation | A clean context can simulate or verify independently | Schema or skill review |
| Parallel work | Independent questions can run concurrently | Researching separate modules |
| High-volume work | Large logs and test output stay isolated | Test-suite analysis |

Delegate a concrete, bounded task. Keep decisions that combine findings, user scope, and the
overall solution with the orchestrator.

## Inline and dedicated agents

Use an inline subagent for a short, one-off task whose prompt can state the scope and result
directly. Use the runtime's suitable exploration, analysis, or execution role; role names differ
between runtimes.

Create a dedicated Skill + Agent pair for a reusable task with substantial methodology:

1. The skill contains the domain methodology and remains usable without an agent.
2. The agent preloads that skill, receives a bounded input, and defines the result contract.

This keeps methodology in one source while giving repeated reviews fresh context.

### Responsibility split for reviewers

- The skill owns reusable domain criteria, checklists, decision rules, and defect examples.
- The reviewer agent owns the fresh skeptical stance, bounded input, evidence to read,
  reviewer-specific investigation, direct JSON response, and the freedom to challenge the chosen
  approach or describe a useful alternative within its lane. It does not edit or make the release
  decision.
- The caller owns supplying complete context and explaining the review to the user. It applies no
  reviewer finding until the user explicitly approves the specific change.

Do not repeat the preloaded skill's reusable domain rules in the agent. When a necessary reusable
rule exists only in an agent, move it into the preloaded skill before removing the agent copy;
this preserves behavior while restoring one canonical owner. Mechanics used only to investigate
the reviewer agent's bounded lane may remain in that agent.

## Agent file format

Store source definitions in `~/.claude/agents/{name}.md`. Generated runtimes may adapt the
frontmatter and tool names during synchronization.

```yaml
---
name: agent-name
description: |
  Explains the bounded purpose, when to delegate, and important exclusions.
model: inherit
color: blue
skills:
  - methodology-skill
allowed-tools: Read, Glob, Grep
---

## Input

State the paths, requirements, scope, and evidence the orchestrator supplies.

## Process

Apply the preloaded methodology to the complete relevant artifact and its contracts.

## Output

Return the role's structured result directly to the orchestrator.
```

Required frontmatter fields are `name`, `description`, `color`, and `skills` when methodology is
preloaded. Use only the tools needed for the task. Analysis agents normally need read/search
tools; add shell access only for relevant read-only checks. Do not grant write access to a
reviewer merely to persist its report.

## Reviewer contract

A reviewer, validator, checker, scanner, or critic reviews the supplied artifact within its
defined lane. It does not modify the artifact or decide whether the result may ship.

### Stance and scope

The reviewer starts from fresh context, reads the complete artifact, and follows relevant
callers, dependencies, standards, and contracts. Apply the preloaded lane rather than a generic
preference. The reviewer may report defects, unnecessary complexity, a simpler approach, a
different design, an improvement, or an additional scenario when relevant to that lane. Explain
what was observed and why it matters; unsupported preference is not useful. Accuracy matters more
than finding count, and a clean result is complete.

The orchestrator also supplies a short implementation explanation when reviewing completed work:
what changed, how the result works, why this approach was chosen, deliberate limits, and
assumptions. Treat this explanation as a claim to verify against the request, project evidence, and
artifact, not as authority. For a review of existing material, use the review goal and known usage
instead of inventing an implementation rationale.

A finding gives the caller enough context to explain the relevant behavior, what is wrong or
proposed, when it matters, and the consequence.

### Required JSON shape

Return the JSON directly as the subagent result. Every shown top-level key is required:

```json
{
  "status": "findings_present",
  "findings": [
    {
      "location": "string",
      "finding": "what the reviewer found or proposes",
      "reasoning": "why it matters within this review lane",
      "alternative": "optional simpler or stronger approach, or null"
    }
  ],
  "clean_check": null,
  "summary": "string"
}
```

`status` is exactly `clean` or `findings_present`. With `clean`, `findings` is empty and
`clean_check` briefly states what was checked. With `findings_present`, `findings` is non-empty and
`clean_check` is `null`. Domain agents may add evidence, conditions, impact, severity, category, or
other useful fields. Order findings by importance.

### Reviewer skeleton

```markdown
You are a fresh skeptical {lane} reviewer. Review the complete supplied {artifact} and relevant
context within that lane. You may challenge correctness, complexity, the chosen approach, or
missing possibilities and describe a useful alternative. Explain what you found and why it matters;
do not edit or decide whether the result ships. Treat the implementer's explanation as a claim to
verify, not as authority. Return the common reviewer JSON directly. A clean result is valid.
```

## Other agent contracts

Executor and automation agents are not reviewers and use role-specific results. Keep their
contracts separate from the reviewer contract.

An executor reports changed artifacts and incomplete work:

```json
{
  "status": "success",
  "files_modified": ["path/to/file.ts"],
  "files_created": [],
  "summary": "Implemented the bounded task."
}
```

An automation agent reports actions and observable results:

```json
{
  "status": "success",
  "actions": ["ran tests"],
  "results": {},
  "errors": []
}
```

## Orchestrator responsibilities

The orchestrator launches a fresh reviewer instance with the touched artifacts, deleted or
renamed-file evidence, generated or mechanical evidence, relevant requirements, related contracts
or callers, validation evidence, and the short implementation explanation described above. Select
the complete reviewer set required by the active skills and launch it in parallel against one
artifact revision.

After reviewers return, apply no finding and do not repeat the review automatically. Explain what
you changed and how it works, then what reviewers found, what it can cause, whether you agree and
why, and what you recommend. Group related points, avoid internal process terms, and wait for the
user's approval before editing.

One review wave applies to one review stage. Preserve distinct stages that examine different
artifacts or boundaries, such as a source scan followed by a destination scan. The orchestrator may
still correct problems it finds through implementation, direct checks, or diff inspection before
review begins.

If a durable log is needed, the orchestrator stores the returned JSON. The reviewer does not need
a report path or write permission.

## Invoking agents from skills

Reference a dedicated agent by its role and provide complete input without prescribing a
runtime-specific transport:

```markdown
Run a fresh `code-reviewer` with:
- touched, deleted, renamed, generated, and mechanical artifacts;
- the user request or user-spec;
- applicable repository instructions and project contracts;
- relevant callers, dependencies, and validation evidence;
- a short explanation of what changed, how the result works, why this approach was chosen,
  deliberate limits, and assumptions.

After the reviewer returns, do not edit. Explain what you changed and how it works, then what the
reviewer found, what it can cause, whether you agree and why, and what you recommend. Wait for the
user's approval.
```

Dedicated agent descriptions should state purpose, trigger, and exclusions concretely. Keep
large domain prompts in the preloaded skill rather than duplicating them in every caller.
