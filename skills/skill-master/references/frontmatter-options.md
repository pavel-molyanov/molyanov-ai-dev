# Optional Frontmatter Fields

Most skills need only `name` and `description`. Add another field only when the skill needs that
behavior. Codex reads only `name` and `description`; every field below works in Claude Code only.

| Field | Default | Effect in Claude Code |
|-------|---------|-----------------------|
| `argument-hint` | none | Autocomplete hint after `/skill-name`, e.g. `"[issue-number]"` |
| `disable-model-invocation` | `false` | `true`: only manual `/skill-name`; the description leaves the agent's context |
| `user-invocable` | `true` | `false`: hidden from the `/` menu; only the agent invokes it |
| `allowed-tools` | none | Pre-approves listed tools during the invoking turn; does not restrict other tools |
| `disallowed-tools` | none | Removes listed tools while the skill is active |
| `paths` | none | Auto-loads the skill only when working with files matching the globs |
| `context`, `agent` | inline | `context: fork` runs the skill as an isolated subagent of type `agent` |
| `background` | `true` | With `context: fork`, `false` waits for the result in the same turn and keeps the full tool set |
| `model`, `effort` | inherit | Model (`/model` values) or effort (`low`…`max`) while active; keep `inherit` unless the task clearly needs otherwise |

Do not use `when_to_use`. Codex ignores it, so routing text there is lost in Codex; keep all
routing in `description`.

## disable-model-invocation

Use for workflows with side effects or timing the user wants to control, such as deploys or
sending messages. The agent no longer sees the skill at all, so it never suggests it. Codex has
no equivalent in our sync, so the skill stays auto-invocable there.

## allowed-tools

Use to avoid permission prompts for the exact commands a skill always runs:

```yaml
allowed-tools: Bash(git status *) Bash(git diff *)
```

Deny rules still win. To make a skill read-only, use `disallowed-tools` instead.

## disallowed-tools

```yaml
disallowed-tools: Edit Write
```

Use for analysis or review skills that must not modify files.

## context and agent

```yaml
context: fork
agent: Explore
```

Use for a self-contained task whose result matters more than the conversation history. The
skill body becomes the subagent's task. By default it runs in the background with a narrower
tool set, and its edits are not covered by `/rewind`; set `background: false` when the result or
the full tool set is needed in the same turn.
