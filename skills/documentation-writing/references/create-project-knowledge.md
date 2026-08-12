# Create Project Knowledge

Use this workflow when the user wants to create or finish initial Project Knowledge and the
current documentation is missing, still a template, or only partially filled. The interview is
stored at `work/project-knowledge/interview.yml`; it is working evidence, while Project Knowledge
remains the owner of approved current facts.

## Phase 0: Start or Resume

1. Inspect the repository, configuration, `CLAUDE.md`, and current Project Knowledge.
2. If an in-progress interview exists, summarize its recorded topics and decisions, then resume
   from the earliest incomplete topic or unrecorded approval. If no interview exists, create
   `work/project-knowledge/` and copy the bundled `../assets/project-knowledge-interview.yml`
   (relative to this reference) there as `interview.yml` without overwriting other work. A completed
   interview may be reused when initial documentation is still incomplete; reopen only contradicted
   or missing topics.
3. For a fresh interview when the triggering message has no substantive project description, first
   ask the user to describe the project freely in their own words and record that exchange in
   `conversation_history`.
4. Set the session timestamps and status, then pre-fill every topic from the user's description and
   repository evidence. Store source paths in the affected topic's `evidence`. Mark topics whose
   irrelevance is already established as `not_applicable` with a concise evidence-backed reason;
   do not ask the user to confirm them. When a cycle has no unresolved applicable topics, skip its
   question batches but still show its summary and obtain its checkpoint approval. Skip the whole
   cycle only when all its topics are not applicable; always show the Cycle 3 final summary.

## Interview Loop

Run the loop separately for each cycle:

1. Find required applicable topics below 85% or structurally incomplete, starting with the lowest
   scores and open gaps.
2. Ask 3-4 questions about different material gaps, or all remaining questions when only 1-2 gaps
   remain. Use repository evidence, propose concrete options, and challenge a weak choice once with
   a consequence or counterexample.
3. If the user does not know, offer 2-3 options or split a required question. An optional unknown
   may remain TBD; an inapplicable topic is complete only when its `value` explains why.
4. After every response, append the full Q&A to `conversation_history`; update each affected
   topic's `score`, `value`, `gaps`, `status`, and `evidence`; record substantive choices and rejected
   alternatives in `decisions`; advance `current_question_num` by the number of questions in the
   batch; update timestamps; save immediately.
5. Finish the cycle only when every required applicable topic is at least 85% and structurally
   complete: non-empty `value`, no unresolved TBD, and no gaps except consciously accepted
   limitations. Detailed answers score 80-95%, brief 50-70%, vague 20-40%, and absent 0%.

Use as many batches as needed. When scope changes materially, record the change, lower affected
scores, add the new gaps, and continue from the earliest affected cycle.

The same persistence rule applies outside question batches: append cycle-summary responses,
structure choices, documentation corrections, and final approval to `conversation_history`, and
record each approved checkpoint or topology choice in `decisions` before continuing. These records
determine the resume point without separate progress or approval fields.

## Cycle 1: Project Definition

1. Cover project identity, purpose and problem, audience and use cases, capabilities, scope
   boundaries, priorities, MVP, phased or all-at-once development, feature grouping, order after
   MVP, and post-launch ideas.
2. Summarize the resulting project definition and resolve corrections before technical decisions.

**Checkpoint:** the user agrees with the project scope, MVP, priorities, and development approach.

## Cycle 2: Architecture and Technical Decisions

1. Cover project type and artifacts, stack and rationale, structure and components, dependencies
   and integrations, data flow and model, technical constraints, and sensitive-data boundaries.
2. For an existing project, derive facts from manifests, configuration, source, and deployment
   files. When the repository is too large for proportionate direct inspection, launch bounded
   research subagents for specific questions and record their source-backed findings in the log.
3. For a new coding project, propose applicable choices, verify unstable libraries or platforms
   against current official documentation, and iterate until substantive decisions are approved.
   For a non-coding project, document its artifacts and working process and mark irrelevant
   technical topics not applicable with a reason.

**Checkpoint:** applicable architecture and technical decisions are evidence-backed and approved.

## Cycle 3: Operations, Experience, and Remaining Gaps

1. Cover project-specific patterns and workflow, testing and quality gates, deployment and
   operations, migration, UX/design/accessibility, and independently useful domain areas. Mark a
   topic not applicable rather than inventing requirements for it.
2. Revisit every required topic across all cycles that still fails the score or structural stop
   condition. Then show one final summary of the complete project understanding.

**Checkpoint:** all required applicable topics satisfy the interview stop condition and the user
has corrected the final summary.

## Write the Documentation

1. Apply [project-knowledge-structures.md](project-knowledge-structures.md). Preserve an existing
   suitable topology without asking for it again; when a new topology or explicit reorganization is
   needed, obtain the user's choice before writing it.
2. Write durable project facts in English. Replace template placeholders and keep `CLAUDE.md` as a
   compact entrypoint.
3. If post-launch ideas were discussed, offer to add them to the existing backlog. When the project
   has no backlog convention, ask where to put them instead of inventing a second convention.
4. Return to Documentation Review in the main skill, using `interview.yml`, its recorded decisions,
   the final corrected summary, and relevant repository sources as the selected evidence boundary.
   Show the reviewed files, apply the user's corrections, and re-review when warranted.
   When a correction changes a substantive fact or decision, update its topic state, decision
   record, conversation history, and final summary before continuing. If that correction opens a
   required gap or invalidates an approved checkpoint, return to the earliest affected cycle.
5. After the user approves the documentation, record that approval and set
   `interview_metadata.status` to `completed`, then offer a commit.
