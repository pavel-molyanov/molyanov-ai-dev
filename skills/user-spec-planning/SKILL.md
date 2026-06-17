---
name: user-spec-planning
description: |
  Creates user-spec.md through adaptive interview with codebase scanning and dual validation.

  Use when: "сделай юзер спек", "проведи интервью для юзер спека",
  "создай юзерспек", "user spec", "detailed planning", "хочу продумать фичу",
  "опиши требования к фиче", "сделай описание фичи", "/new-user-spec"

  For tech planning use tech-spec-planning. For project planning use project-planning.
---

# User Spec Planning

Thorough adaptive interview → codebase scan → user-spec.md → dual validation → user approval.
Output: `work/{feature}/user-spec.md` with status `approved`.

## Interview Style

Conduct the interview in the language the user writes in. Be thorough and opinionated — an engaged co-thinker who actively proposes solutions and challenges weak answers.

**How to interview:**
- 3-4 questions per batch. Run as many batches as needed until the cycle's items are fully covered.
- Propose solutions based on Project Knowledge (example in English): "architecture.md describes pattern X — I think we need Y here. Agree?"
- Challenge with substance — concrete counterexamples, code references, unexplored scenarios: "What if the user does Z? In the code, module Q doesn't handle this case."
- Accept the answer after one substantive challenge and move on to the next gap.
- When the user says "I don't know": help think through it (examples, common patterns). Optional item → mark TBD. Required item → break into simpler questions.

**Interview depth** depends on feature size (S/M/L in interview metadata):
- S (1-3 files, local fix): focused interview, core behavior
- M (several components): moderate depth, integration questions
- L (new architecture): deep interview, thorough edge cases and risk analysis

## Process

### Phase 0: Init

1. Check for existing interview: look in `work/*/logs/userspec/interview.yml` for `metadata.status: in_progress`. If found — load, show discussed topics summary, resume. If multiple found — show list, let user choose.
2. Get task description (ask in the user's language): "Describe what you want to do."
3. Determine work_type (feature / bug / refactoring) from description.
4. Propose feature name (kebab-case), get user confirmation.
5. Run `~/.claude/shared/scripts/init-feature-folder.sh {name}` — creates folder structure with interview.yml.
6. Update interview.yml: set metadata.started, metadata.status: in_progress, phase1_feature_overview.feature_name, phase1_feature_overview.work_type.

**Checkpoint:** interview.yml exists with status in_progress, feature name confirmed.

### Phase 1: Study Project Knowledge

Read ALL files from `.claude/skills/project-knowledge/references/`. If directory missing or empty — warn user, suggest running project-planning skill (or `/init-project-knowledge` command).

These files are your context for the entire interview. Reference them when asking questions and proposing solutions.

### Phase 2: Cycle 1 — General Understanding

**Scope:** `phase1_feature_overview` items in interview.yml.

1. Score user's initial description against all items (detailed 80-95%, brief 50-70%, vague 20-40%, not mentioned 0%).
2. Run interview loop (see below) on phase1_feature_overview items.
3. During this cycle — determine feature size S/M/L and agree on testing strategy:
   - S: integration/E2E usually not needed — state why
   - M: propose whether integration tests make sense, explain reasoning
   - L: propose specific integration and E2E scope with justification

### Phase 3: Code Scanning

Launch `code-researcher` subagent (Task tool, opus) with feature path and feature description from Cycle 1.

After subagent completes — read `{feature_path}/code-research.md`. Use findings in Cycle 2 questions.

If during later phases a gap is discovered — launch `code-researcher` again with the specific question to investigate.

### Phase 4: Cycle 2 — Code-Informed Refinement

**Scope:** `phase2_user_experience` + `phase3_integration` items.

1. Summarize understanding (examples in English; ask in the user's language): "I understand the task as: [X]. I plan to do it like: [Y, based on code]."
2. Questions based on code findings: "Found module X that does Y — reuse it?"
3. Cover deploy and user actions (items `deploy_approach`, `manual_user_actions`):
   - "Are manual steps needed to launch? (create a bot, get API keys, set up a service, register somewhere)"
   - "How to deploy? What needs configuring? (CI/CD already exists, needs setup, manual deploy)"
   - "How to verify it works after deploy? (MCP tools, curl, manual check)"
   - "What can be checked during development, without deploy? (call an external API, run locally, check config, poke the UI on localhost, test a prompt)"
4. Run interview loop on phase2 + phase3 items.

### Phase 5: Cycle 3 — Review & Finalize

**Scope:** ALL items across all phases still below threshold.

Cleanup pass: revisit anything not fully covered in Cycles 1-2. Deepen edge cases and error scenarios — probe for scenarios user hasn't considered, even if items formally passed threshold.

Run interview loop on remaining gaps.

### Phase 6: Completeness Check

Launch `interview-completeness-checker` subagent (Task tool, sonnet) with feature path. It reviews interview.yml against PK files and code-research.md.

- `needs_more` → ask the suggested questions, re-run checker
- `complete` → proceed to Phase 7

### Phase 7: Create User Spec

1. Copy template to working file:
   - Copy `~/.claude/shared/work-templates/user-spec.md.template` → `work/{feature}/user-spec.md`
   - Edit sections one by one using Edit tool, replacing placeholders with interview data
   Reason: agent sees template structure and comments while editing each section, preventing drift from template format.
2. Content rules (section headers stay as in the template — English; fill content in the language the user writes in):
   - "What we're building" — self-contained, understandable without the interview
   - "Why" — concrete user value, not vague claims like "improve UX"
   - Acceptance criteria — testable, no vague "works correctly"
   - Every discussed topic from interview must appear in the spec
3. If feature seems large (>10 criteria, >3 user flows, >5 integrations) — suggest splitting.

Git commit: `draft(userspec): create user-spec for {feature}`

### Phase 8: Validation

Run 2 validators in parallel (Task tool):
- `userspec-quality-validator` (sonnet) — document structure, template compliance, formal completeness. Returns JSON with per-check pass/fail and findings list.
- `userspec-adequacy-validator` (opus) — feasibility, over/underengineering, better alternatives. Returns JSON with findings by category and severity.

**Handling findings:**
- Obvious issue → fix silently
- Borderline → discuss with user
- Disagree with finding → reject with reasoning
- Conflict between validators → userspec-adequacy-validator takes priority (substance over form)

After each validation round (validators wrote reports + you applied fixes), git commit: `chore(userspec): validation round {N} — {summary of fixes}`. Re-run validators. Max 3 iterations, then show remaining issues to user.

### Phase 9: User Approval

Show user-spec.md link + validation summary. If changes requested — edit and show again.

When approved:
1. Set user-spec.md frontmatter `status: approved`
2. Set interview.yml `metadata.status: completed`
3. Git commit: `chore(userspec): approve user-spec for {feature}`
4. Suggest `/new-tech-spec {feature-name}`

## Interview Loop

Runs inside each cycle. Repeats until the cycle's scope is fully covered.

```
1. Find gaps: required items in current scope with score < 85%. Lowest first.
2. Ask 3-4 questions about different gaps. Reference PK and code findings.
3. User responds.
4. Update interview.yml:
   - conversation_history: add full Q&A entry
   - Item: score, value, gaps, status
   - metadata: last_updated, current_question_num
   - Save immediately
5. Check stop criteria (BOTH must be true):
   a) All required items in scope score >= 85%
   b) Structural: every required item has non-empty value,
      no TBD in value, gaps empty or only conscious limitations
6. Not done → step 1. Done → exit cycle.
```

Scoring: detailed answer 80-95%, brief 50-70%, vague 20-40%, not mentioned 0%.

Optional items: cover when user mentions relevant context or when naturally connected to required items.

## Work Type Adaptations

All three cycles apply to any work_type, but focus shifts:

**Bug:** Cycle 1 → reproduction steps, expected vs actual, severity, when it broke. Code scanning → find bug location and root cause. Cycle 2 → fix approach, regression risks.

**Refactoring:** Cycle 1 → current problems, target architecture, stability guarantees. Code scanning → current structure, dependencies, test coverage. Cycle 2 → migration path, backward compatibility.

## Scope Changes

If understanding changes significantly during interview:
- Update affected scores downward, add new gaps
- Reassess feature size (S/M/L)
- If work_type changes (was feature, actually bug) — pivot items accordingly
- Note the change in interview.yml notes section

## Self-Verification

- [ ] All cycles completed, completeness checker passed
- [ ] user-spec.md filled with real content (no placeholders)
- [ ] Both validators passed (or issues resolved with user)
- [ ] User approved, frontmatter status: approved
- [ ] interview.yml metadata.status: completed
- [ ] Suggested `/new-tech-spec` as next step
