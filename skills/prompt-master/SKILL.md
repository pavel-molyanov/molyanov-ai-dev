---
name: prompt-master
description: |
  Creates, improves, and reviews LLM prompts using concise, task-aware guidance.

  Use when: "напиши промпт", "улучши промпт", "prompt engineering", "проверь промпт"
---

# Prompt Master

Treat a prompt as a clear task contract. Add information that changes the result; do not add a
technique merely because it is common in prompt-engineering guides.

## Prompt Essentials

A prompt should communicate the applicable parts of:

- the task and required result;
- context the model cannot infer but needs to perform the task correctly;
- real constraints and the reasons behind non-obvious requirements;
- criteria that distinguish an acceptable result;
- the response format when it matters to the user or a downstream system.

Use a role only when it changes the required expertise, tone, or behavior. Decorative claims such
as "you are the best expert" do not replace relevant context or concrete requirements.

State each instruction once. Prefer direct positive guidance when it fully expresses the rule, and
keep explicit prohibitions for genuine boundaries or common failures that positive wording would
leave ambiguous. Explain why a non-obvious rule matters instead of relying on capitalization or
repeated emphasis.

## Conditional Techniques

- **Examples:** Start with a clear task description. Add examples when the required format, tone,
  or decision boundary is difficult to specify in words, or when observed outputs reveal a
  concrete failure that an example can correct. Use realistic examples without a fixed count.
- **Structure:** Use headings, XML, or other delimiters when they help distinguish instructions,
  context, examples, and input data. They improve readability and parsing; they do not create a
  security boundary by themselves.
- **Chaining:** Split work across model calls when an intermediate result must be inspected,
  evaluated, or kept separate by the application. A coherent task may remain in one prompt.
- **Structured output:** When software consumes the response, define the exact schema and use a
  structured-output feature when available rather than relying only on a request to return JSON.

## Agents and Tools

For an agent that can take actions, define the autonomy and approval boundary: what it may do on
its own and what requires confirmation. Distinguish privileged instructions from user-controlled
or external data.

Tool descriptions should tell the model when and why to use the tool, what relevant result it
returns, and how failures are represented when this is not already evident from the tool contract.
Expose only the tools and permissions needed for the task.

Do not place untrusted data in privileged instructions. Assess prompt-injection risk from the
agent's capabilities, the trust boundary, and the consequence of manipulated behavior. Delimiters
can help the model recognize data, but access control, least privilege, structured data flow, and
confirmations must be enforced by the surrounding system. These measures reduce prompt-injection
risk; prompt wording does not eliminate it.

## Quality

When a prompt needs empirical evaluation, especially for reusable or consequential use, define
what a correct result means and use representative normal, edge, and adversarial scenarios that
match the real task. Compare old and new versions on the same scenarios. Treat a metaprompt or
model self-critique as a source of hypotheses, not as proof that a revision is better.

Run no more than two review waves. After creating or changing a prompt, run wave 1 with a fresh
`prompt-reviewer`. Supply the prompt location, required result and output contract, input sources,
trust boundaries, model capabilities, and callers. Review findings are diagnoses, not a work queue.
Check the evidence and exact correction; apply only an authorized local correction to agreed normal
behavior. If the scenario is rare or unagreed, or the correction adds behavior, state, entities,
contracts, dependencies, architecture, or material complexity, reject it with a short reason or ask
the user before editing. `user_decision_required: false` does not replace this check. Include
reviewers required by other active skills in these same waves instead of starting a separate wave
sequence.

If an authorized fix changes the prompt, run wave 2 with a fresh reviewer against the revised
version. Stop after a clean wave or when no authorized correction changes the prompt. After wave 2,
do not launch another reviewer automatically; make only remaining local corrections within the
agreed prompt, perform applicable direct evaluation, and report any remaining findings or required
user decisions.
