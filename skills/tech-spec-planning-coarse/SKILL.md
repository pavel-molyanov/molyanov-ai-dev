---
name: tech-spec-planning-coarse
description: |
  Creates tech-spec.md with architecture, decisions, testing strategy, and coarse implementation plan.
  Coarse variant: groups related work into skill-scoped tasks instead of atomic ones.
  Fewer tasks, each covers one skill's cohesive scope in the feature.

  Use when: "сделай техспек coarse", "составь техспек крупно", "техспек крупными задачами",
  "подготовь техспек крупно", "группировка задач по скиллам", "tech spec coarse",
  "new-tech-spec-coarse", "/new-tech-spec-coarse", "крупная декомпозиция",
  "one task per skill", "skill-scoped tasks", "group related work"

  Requires existing user-spec.md as input (create with user-spec-planning skill first if missing).
---

# Tech Spec Planning (Coarse Variant)

Create technical specification with coarse implementation plan: one task per skill's cohesive scope, not atomic units.

**Input:** `work/{feature}/user-spec.md` + Project Knowledge
**Output:** `work/{feature}/tech-spec.md` (approved)
**Language:** Technical documentation in English; communication with the user in the language the user writes in

## Phase 1: Load Context

1. Ask user for feature name if not provided. Check `work/{feature}/` exists, create if needed.

2. Read `work/{feature}/user-spec.md`. If missing — ask user to describe the task or create user-spec first.
   Extract `size: S|M|L` from user-spec frontmatter — it determines testing strategy depth.

3. Read all files in `.claude/skills/project-knowledge/references/` (project.md, architecture.md, patterns.md, deployment.md, ux-guidelines.md, and any custom domain files). Missing files are fine.

4. user-spec.md is the single input source — all information from interview.yml and code research is already consolidated there.

**Checkpoint:**
- [ ] Feature folder exists
- [ ] user-spec.md read, size extracted
- [ ] Project Knowledge read

## Phase 2: Code Research

Launch `code-researcher` subagent (Task tool, opus) with feature path and user-spec path. The agent reads existing `code-research.md` (from user-spec phase if available) and deepens analysis for implementation.

After subagent completes — read `{feature_path}/code-research.md`. Use in Phase 3 clarification and Phase 4 spec writing.

If during later phases a gap is discovered — launch `code-researcher` again with the specific question.

**Checkpoint:**
- [ ] code-research.md created/updated with implementation-level analysis
- [ ] Research file read by orchestrator

## Phase 3: Clarification (Adaptive)

Analyze if additional information is needed based on user-spec and code research.

- Ask technical questions if gaps exist.
- Focus: technical constraints, integration points, data sources, external dependencies.
- If gaps found in user-spec requirements — discuss with user and update user-spec too.
- If requirements are fundamentally unclear — suggest creating user-spec first.

**Checkpoint:**
- [ ] All technical gaps clarified (or none existed)

## Phase 4: Create tech-spec

1. Copy template to feature folder:
   ```bash
   cp ~/.claude/shared/work-templates/tech-spec.md.template work/{feature}/tech-spec.md
   ```
   Then edit sections one by one using Edit tool.

2. Fill frontmatter:
   - `created`: today's date
   - `status`: draft
   - `size`: copy from user-spec (S|M|L)
   - `branch`: `dev`

3. Fill all template sections. The template defines section structure — follow it directly.
   In Architecture → Shared Resources: list heavy resources (ML models, DB pools, browser instances, API clients) shared across components. Specify owner, consumers, instance count. If none — write "None".

   **User-spec anchoring:** Every decision in the Decisions section must reference a user-spec requirement it serves. If a decision is purely technical — mark it `[TECHNICAL]`. If a decision contradicts user-spec — document it in User-Spec Deviations as `[PENDING USER APPROVAL]`.

4. **Coarse decomposition rule:** fill Implementation Tasks by grouping related work into skill-scoped tasks.

   **How to decompose:**
   - Start from the list of execution skills needed (from [skills-and-reviewers.md](~/.claude/skills/tech-spec-planning/references/skills-and-reviewers.md)): `code-writing`, `prompt-master`, `skill-master`, `infrastructure-setup`, `deploy-pipeline`.
   - **Group into one task:** work that shares a skill AND (same module OR shared files OR logical dependency). All ingestion code → one `code-writing` task. All system prompts for one pipeline → one `prompt-master` task.
   - **Split into separate tasks:** independent modules within the same skill (enables parallel execution in the same wave). Backend ingest + frontend dashboard → two `code-writing` tasks when each owns a separate set of files and can proceed in parallel.
   - **Different implementation skills → usually different tasks.** Code and prompts never mix in one task unless the prompt text has already been explicitly agreed in the tech-spec/user discussion and the remaining work is only ordinary code assembly of fixed prompt strings.
   - **Do not create a standalone Project Knowledge / documentation-writing implementation task.** Project documentation is updated later by the feature-closing documentation command after implementation, audits, deploy, and verification are complete. If documentation is relevant, mention it in release/final notes, not as an implementation task.
   - Aim for 3-7 implementation tasks (plus final audit/QA/deploy waves).

   **Per task fill:** Description (scope of the skill's role — may be several sentences), Skill (one skill per task), Reviewers, Verify-smoke (optional), Verify-user (optional), Files to modify (list of all files within the skill's scope), Files to read. Select skill and reviewers from [skills-and-reviewers.md](~/.claude/skills/tech-spec-planning/references/skills-and-reviewers.md).

   For each task, write `Verify-smoke:` when the task involves:
   - External API integration → curl/httpie command to real endpoint with expected response
   - Library/model initialization → `python -c` or import check
   - Docker/infrastructure → `docker compose build`, `docker run` commands
   - LLM/prompt work → spawn agent with prompt + test question, check response
   - External service API → test API call with expected response
   - MCP-verifiable UI/frontend → use Playwright MCP or similar
   Write `Verify-user:` when user should check something: UI on localhost, behavior, UX.
   Omit both if task is purely internal logic covered by unit tests.

   **Task content rules:**
   - Description describes scope of the role — what this skill accomplishes in the feature. Length matches scope (1-5 sentences typical). Longer is fine for complex coarse tasks.
   - Description answers WHAT and WHY, not HOW. No line numbers, no pseudocode, no step-by-step implementation details (those go into task files during decomposition).
   - All technical decisions belong in the Decisions section, not in task descriptions.

5. The final waves are always **Final Wave 1** then deploy/post-deploy waves as needed:

   **Final Wave 1: Audit and Pre-deploy QA** (always present) — one driver task with skill `pre-deploy-qa`, `reviewers: none`.
   The task description must say that the driver:
   - runs the full test suite and acceptance checks;
   - launches three parallel audit subagents: `code-reviewing`, `security-auditor`, and `test-master`;
   - fixes actionable audit findings;
   - reruns targeted checks;
   - records code/security/test audit reports plus the pre-deploy QA report.

   **Final Wave 2: Deploy** — one `deploy-pipeline` task only if deploy is needed.

   **Final Wave 3: Post-deploy verification** — one `post-deploy-qa` task only if live-environment checks are needed.

6. Fill User-Spec Deviations section. Each deviation has: requirement ID, what user-spec says, what tech-spec does differently, why. Mark each `[PENDING USER APPROVAL]`. If no deviations — write "None".

7. Task Count Check: typical coarse decomposition produces 3-7 implementation tasks. If >7 → review for merge candidates (two tasks with same skill on related work), or propose splitting into MVP + Extension phases.

8. Git commit: `draft(techspec): create coarse tech-spec for {feature}`

**Checkpoint:**
- [ ] tech-spec.md created with all sections
- [ ] Implementation Tasks are coarse (3-7 tasks): one skill per task, related work grouped, independent work split
- [ ] No AC or TDD anchors in tasks (those come from task-decomposition-coarse phase)
- [ ] Technical decisions in Decisions section, not in task descriptions
- [ ] User-Spec Deviations section filled (or "None")
- [ ] Final Wave present with QA (mandatory) + Deploy/Post-deploy (if applicable)

## Phase 5: Validation

### Run 5 validators in parallel

Launch all as subagents, each writes JSON report to `logs/techspec/{name}-review.json`:

| Validator | Agent | Checks |
|-----------|-------|--------|
| Mirage detector | `skeptic` | Non-existent files, APIs, functions, dependencies |
| Completeness + adequacy | `completeness-validator` | Bidirectional traceability, scope creep, overengineering, underengineering, solution depth |
| Security | `security-auditor` | OWASP, input validation, auth, sensitive data |
| Testing strategy | `test-reviewer` | Test plan adequacy for feature size S/M/L |
| Template + wave conflicts | `tech-spec-validator-coarse` | All sections filled, frontmatter, format, skills/reviewers, wave conflict detection, one-skill-per-task |

Pass to each validator: `work/{feature}/tech-spec.md` + `work/{feature}/user-spec.md`.

### Process findings

Read all 5 reports. For each finding:
- Fix if clearly valid (typos, missing sections, structural issues)
- Reject with reasoning if disagree — only for findings unrelated to user-spec alignment

**User-spec alignment findings require user decision.** When completeness-validator reports `gap`, `scope_creep`, `overengineering`, or `shallow_solution` — present each finding to the user with your recommendation.

### Iterate if needed (up to 3 iterations)

If fixes were made:
1. Apply targeted fixes directly in `work/{feature}/tech-spec.md`.
2. Git commit: `chore(techspec): validation round {N} — {summary of fixes}`
3. Re-run validators on updated tech-spec.
4. Repeat up to 3 iterations.

If problems remain after 3 iterations — show user: "Validation didn't pass in 3 iterations. Here's what remains — let's resolve together."

**Checkpoint:**
- [ ] All 5 validators ran
- [ ] Findings processed (fixed / rejected / discussed)
- [ ] Final tech-spec.md placed in work/{feature}/

## Phase 6: User Approval

1. Show user the full tech-spec.md.
2. Show validation summary: iterations count, issues found and resolved.
3. Wait for explicit approval.
4. If user has comments — fix, re-validate, show again.
5. After approval: update `status: draft` → `status: approved` in tech-spec frontmatter.
6. Git commit: `chore(techspec): approve coarse tech-spec for {feature}`
7. Tell user next step: run `/decompose-tech-spec-coarse` to create task files.

**Checkpoint:**
- [ ] User explicitly approved tech-spec
- [ ] status = approved

## Final Check

- [ ] tech-spec.md created with all sections (Implementation Tasks are coarse scope descriptions)
- [ ] Validation passed (5 validators)
- [ ] User approved tech-spec
- [ ] status = approved in frontmatter
