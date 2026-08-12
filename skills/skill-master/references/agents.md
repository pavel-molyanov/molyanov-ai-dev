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
  reviewer-specific hunt or investigation mechanics, evidence gate, diagnostic result fields,
  direct JSON response, and the exclusions against editing, designing remediation, or making a
  release decision.
- The caller owns launching a fresh reviewer, supplying complete context, evaluating returned
  findings, and deciding whether an authorized correction is warranted.

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

A reviewer, validator, checker, scanner, or critic diagnoses the supplied artifact. It does not
modify the artifact, design remediation, or decide whether the result may ship.

### Stance and scope

The reviewer starts from fresh context, reads the complete artifact, and follows relevant
callers, dependencies, standards, and contracts. It actively tries to disprove correctness but
does not assume a defect must exist. Accuracy matters more than the number of findings, and a
clean result is a complete valid outcome.

Review the current change or other scope supplied by the orchestrator. An unrelated pre-existing
problem is not a finding unless the supplied scope includes it or the current change creates a
demonstrable path to it.

### Evidence gate

Create a finding only when all five facts are established:

1. `location` identifies the concrete artifact location.
2. `evidence` states the observed fact, not a suspicion.
3. `violated_requirement` names the requirement, standard, or contract that the fact violates.
4. `conditions` describes a realistic path that triggers the problem in the current project.
5. `impact` states the concrete consequence under those conditions.

If any fact is missing, continue investigating or omit the finding. A personal preference, a
possible improvement, a best practice without demonstrated consequence, hypothetical future
expansion, a scenario without an established trigger path, or defensive machinery proposed
"just in case" does not pass the gate. A false finding is a reviewer error.

### No solution or release verdict

Findings describe the violated property, not how to fix it. Reviewer output contains no fix,
recommendation, patch, remediation plan, replacement architecture, new dependency, fallback,
corrected code example, or release verdict. Severity and other domain fields are diagnostic
metadata only; they do not decide the orchestrator's action.

### Required JSON shape

Return the JSON directly as the subagent result. Every shown top-level key is required:

```json
{
  "status": "findings_present",
  "findings": [
    {
      "location": "string",
      "evidence": "string",
      "violated_requirement": "string",
      "conditions": "string",
      "impact": "string"
    }
  ],
  "clean_check": null,
  "scope_reminder": "Before making any change because of this review, check whether that specific change is authorized by the user's request or approved plan. If it would go beyond them, stop and ask the user.",
  "summary": "string"
}
```

`status` is exactly `clean` or `findings_present`. With `clean`, `findings` is empty and
`clean_check` briefly lists the checked risks, related locations, and why no demonstrated
violation exists. With `findings_present`, `findings` is non-empty and `clean_check` is `null`.
Every result, including `clean`, returns `scope_reminder` exactly as shown in the JSON contract.
Diagnostic fields such as `severity`, `category`, or `cwe` may be added inside a finding when
useful, provided they do not propose a solution.

Order findings by consequence so the orchestrator can triage efficiently. A bare assertion that
the artifact is fine is not an adequate clean check.

### Reviewer skeleton

```markdown
You are a fresh skeptical {lane} reviewer. Try to disprove that the supplied {artifact}
satisfies {standard}, while treating accuracy rather than finding count as the goal. Read the
whole artifact and its relevant callers, dependencies, and contracts. Diagnose only: do not edit,
design remediation, or decide whether it ships.

Create a finding only after establishing its location, observed evidence, violated requirement,
realistic trigger conditions, and concrete impact. Return the common reviewer JSON directly to
the orchestrator. A clean result explains what was checked and why no violation was proved.
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
renamed-file evidence, generated or mechanical evidence, relevant requirements, and complete
related contracts or callers. Freshness is an orchestration property; the reviewer does not need
round history.

For every returned finding, the orchestrator checks the evidence gate and chooses the simplest
sufficient response. Evaluate the specific intended correction, not only the finding. Apply it
automatically only when that exact correction is authorized by the user's request or approved
plan. A valid finding and its severity do not authorize additional work.

If the correction has no clear authorization anchor, or it adds or expands behavior, tests,
validation, files, workflow steps, state, fallbacks, abstractions, or material complexity beyond
the agreed work, show the user the finding and proposed correction, then wait for a decision before
changing artifacts. Surface unsupported or unrelated findings without acting on them.

Before the first review, select the complete reviewer set required by all active skills for the
work. Launch that complete set in parallel against the same artifact revision as one review wave;
active skills do not start independent wave sequences. After a correction, use a fresh wave when
another review is warranted so every included reviewer re-reads the whole artifact without
anchoring on prior findings. A workflow may set a stricter limit, but it must not require more than
three automatic review waves. Stop earlier when a wave is clean or no authorized correction changes
the reviewed result.

After the final permitted wave, do not launch another reviewer automatically. Correct remaining
local defects only within the agreed behavior, run the applicable direct checks, and return any
remaining findings or required scope and design decisions to the user. A new explicit user request
may start another review cycle; do not persist or reconstruct wave counts across separate runs.

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
- relevant callers, dependencies, and validation evidence.

Evaluate the returned findings against their evidence and the approved scope. Choose the
simplest sufficient response; discuss scope, behavior, approach, or material-complexity changes
with the user before acting.
```

Dedicated agent descriptions should state purpose, trigger, and exclusions concretely. Keep
large domain prompts in the preloaded skill rather than duplicating them in every caller.
