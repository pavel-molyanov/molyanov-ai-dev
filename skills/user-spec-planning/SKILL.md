---
name: user-spec-planning
description: |
  Creates user-spec.md through adaptive interview, codebase research, and three-lane validation.

  Use when: "сделай юзер спек", "проведи интервью для юзер спека",
  "создай юзерспек", "user spec", "detailed planning", "хочу продумать фичу",
  "опиши требования к фиче", "сделай описание фичи", "/new-user-spec"
---

# User Spec Planning

Thorough adaptive interview → codebase research → completeness review → user-spec.md → three-lane
validation → user approval. Output: `work/{feature}/user-spec.md` with status `approved`.

## Interview Style

Conduct the interview in the language the user writes in. Be an engaged co-thinker: propose
solutions, challenge weak answers with concrete examples or code evidence, and keep interviewing
until the applicable requirements are understood.

- Ask 3–4 questions per batch and run as many batches as needed.
- Save every question and answer verbatim after each user response.
- Give one substantive challenge to a weak or unclear answer, then accept a supported answer and
  move to the next gap.
- When the user does not know, offer concrete options or break a required question down. An
  optional detail may remain an acknowledged limitation; a required detail may not remain TBD.
- Record material choices, rejected alternatives, and reasons in the relevant topic summary so
  they survive into `Accepted Decisions`.

When Project Knowledge exists, read its `SKILL.md` as the router and load only the references
relevant to the task. Missing Project Knowledge does not block planning.

## Workflow

### 1. Start or Resume

If the user explicitly asks to continue an existing user spec and provides its feature folder or
slug:

1. Use that exact `work/{feature}` directory. Do not search for other interviews.
2. Read `logs/userspec/interview.yml` and the existing feature artifacts. Treat any additions or
   changes in the current request as interview input.
3. Derive the next action from the interview and artifacts:

   - continue with the earliest required topic below 85% or with an unresolved gap;
   - once the general task is understood, create `code-research.md` if it does not exist, then use
     it for the remaining questions;
   - when all required topics are complete and no substantive draft exists, run the completeness
     review;
   - when a filled draft already exists, validate it again with fresh reviewers rather than trying
     to restore old reviewer responses.

Otherwise start a new spec:

1. Use the current request as the initial task description. If the intended work is not described,
   ask the user what they want to plan. Infer `feature`, `bug`, or `refactoring`.
2. Choose a kebab-case slug and tell the user which `work/{slug}` folder will be used. Do not pause
   only to confirm the slug.
3. If that exact folder already contains prior user-spec work, ask whether to continue that work in
   the same folder or create the new spec under another slug. If the user chooses the existing
   folder, follow the resume path above. Never overwrite prior work implicitly.
4. Resolve the directory of this loaded `user-spec-planning` skill, then from the target project
   root run its `scripts/init-feature-folder.sh` with `{slug}`. Initialize the interview metadata
   with the start time, last-update time, and `in_progress` status, then begin the interview.

If at any point the request appears to contain several independently valuable outcomes, explain
the proposed split and ask the user whether to separate them. Only after the user agrees, read and
apply [splitting-user-specs.md](references/splitting-user-specs.md). Otherwise do not read that
reference and continue the normal workflow.

### 2. Interview and Research

1. Score the initial description against every interview topic.
2. Complete the general-understanding topics using the interview loop below.
3. Once the intended outcome is clear enough to research, launch `code-researcher` with the
   feature path and description. Read `code-research.md` and use its evidence in later questions.
4. Complete user-flow and integration topics, including applicable failures, edge cases,
   constraints, deployment, manual user actions, and verification.
5. Make a final pass over every remaining required gap. If a later answer exposes a factual code
   gap, run focused code research again.

Testing depth follows behavior and risk. Record concrete observable checks and the smallest
reliable unit, integration, E2E, build, lint, render, smoke, or manual boundary that can reproduce
each applicable risk.

### 3. Check Interview Completeness

Launch a fresh `interview-completeness-checker` with the feature path and intended scope. It reads
the interview, code research, and relevant Project Knowledge and returns the common reviewer JSON
directly.

Before acting on any reviewer finding, evaluate the specific intended response, not
only the finding. Apply it automatically only when that exact response is authorized by the user
request or agreed feature scope. A valid finding does not authorize additional work. If the response
has no clear authorization anchor or expands the agreed task, show the user the finding and proposed
response, then wait before changing artifacts or adding requirements.

Use supported findings to ask targeted questions for gaps inside the agreed task. Run a fresh
checker after the answers are recorded, and draft only after it returns `clean`.

### 4. Draft the User Spec

Fill the initialized `work/{feature}/user-spec.md` in place without replacing a substantive
existing document. Preserve its executor instruction and replace every placeholder.
Keep the template-provided scaffold in English; write the specification content in the user's
language.

- `What We Are Building` is self-contained without the interview.
- `Why` states concrete user value.
- Acceptance criteria describe observable, testable results.
- Include agreed outcomes, constraints, material decisions, testing, and acknowledged
  limitations; omit exploratory tangents that do not clarify a decision.

Commit: `draft(userspec): create user-spec for {feature}`.

### 5. Validate the User Spec

For every validation round, launch all three fresh reviewers in parallel:

- `userspec-quality-validator` — document completeness, clarity, acceptance criteria,
  contradictions, and template compliance;
- `userspec-adequacy-validator` — feasibility, proportionality, architecture fit, insufficient or
  unnecessary complexity, and demonstrably simpler existing approaches;
- `skeptic` — factual claims about current files, symbols, dependencies, integrations, and
  behavior.

Supply the complete inputs required by each agent. All reviewers may inspect code; overlap is
acceptable when independently supported evidence falls within more than one lane.

Deduplicate overlapping supported findings and apply accepted corrections. User-spec decisions
remain with the user.

- If all three results are `clean`, validation ends immediately.
- If accepted findings were fixed after rounds 1 or 2, commit
  `chore(userspec): validation round {N} — {summary}` and launch the next full round.
- After round 3, stop and show any remaining findings. Do not launch round 4 without a new explicit
  user request.

If a session ends after drafting, a later run starts a new validation from round 1; old reviewer
responses are not persisted or reconstructed.

### 6. Obtain Approval

Show the user the spec path and validation summary. A requested content change returns the document
to validation; immediate approval is valid only when the validated content did not change.

After explicit approval:

1. Set the user-spec frontmatter status to `approved`.
2. Set `interview_metadata.status` to `completed`.
3. Commit `chore(userspec): approve user-spec for {feature}`.
4. Return the absolute user-spec path and tell the user it can be implemented in a new chat.

## Interview Loop

Repeat inside the current topic group:

1. Find required topics below 85% or with a missing substantive answer or unresolved gap.
2. Ask 3–4 questions about different gaps, using Project Knowledge and code evidence when
   available.
3. After the user responds, append the full question batch and answer to `conversation_history`.
4. Update each affected topic's `score`, `value`, and `gaps`, plus
   `interview_metadata.last_updated`, and save immediately.
5. Continue until every required topic in scope has score ≥85%, a substantive value, no TBD, and
   no unresolved gap except an explicitly accepted limitation.

Use scores as a compact completeness signal: detailed 80–95%, brief 50–70%, vague 20–40%, and not
mentioned 0%. Optional topics are covered when the task makes them relevant.

For bugs, emphasize reproduction, expected versus actual behavior, severity, root cause, and
regression risk. For refactoring, emphasize the current problem, target structure, compatibility,
migration, and stability guarantees.
