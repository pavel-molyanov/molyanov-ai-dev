---
name: user-spec-planning
description: |
  Create user-spec.md for features/bugs through interview.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "сделай юзер спек", "проведи интервью для юзер спека"

  Do NOT use for: tech planning (use tech-spec-planning), project planning (use project-planning)
---

# User Spec Planning

## Overview

Conduct comprehensive adaptive interview that creates detailed user-spec.md:
- Read project context (project.md, architecture.md)
- Deep Q&A to understand requirements and user value
- Explore user scenarios, edge cases, integration points
- Generate well-structured user specification (Russian)
- Get user approval before finalizing

## When to Use

Activate this skill when:
- Creating user specification for complex features/bugs/refactorings
- Need detailed business-level planning before technical implementation
- Requirements are unclear and need exploration through interview
- User says "создай юзерспек", "user spec", "detailed planning", "хочу продумать фичу"

**Do NOT use for:**
- Simple changes where requirements are already clear (use tech-spec-planning directly)
- Technical planning (that's tech-spec-planning skill)

## Approach

### Your Role

You're conducting a planning interview to create a comprehensive user specification. Be conversational, adaptive, and help the user think through all aspects of the feature.

**Communication style:** Разговорный (conversational Russian)

### Core Principles

1. **Understand the project first**
   Read project context before asking questions. Tailor questions to specific project architecture.

2. **Adaptive conversation**
   Every feature is different. Let the conversation flow naturally based on what the user says.

3. **Build on previous answers**
   Each response reveals new context. Use what you learn to guide next questions.

4. **Help when stuck**
   If user doesn't know something, don't skip it. Offer examples, break down questions, suggest common patterns.

5. **Validate understanding**
   Periodically summarize to ensure you understood correctly.

## Process

### Phase 1: Read Project Context

**Check for existing interview (Resume functionality):**

Before starting new interview, check if one is in progress:
```bash
ls .claude/tmp/interview-feature-*.yml 2>/dev/null
```

If file exists:
1. Read `interview_metadata`, `conversation_history`, and `phase4_userspec_review` sections
2. **Check if in review phase:** If `phase4_userspec_review.userspec_created.status` is "created":
   - Show user: "Нашёл интервью, ожидающее твоего подтверждения по user spec."
   - Jump directly to Phase 6 Step 2 (show file with link, ask for approval)
   - Resume review process from there
3. **If NOT in review phase:**
   - Show user: "Нашёл незавершённое интервью по фиче (начато: {started}, прогресс: {completion_estimate})"
   - Show brief recap: "Вот что мы уже обсудили:" + list topics from conversation_history
   - Ask: "Продолжить с того места, где остановились, или начать заново?"
   - If continue: Load interview plan, resume from current state
   - If restart: Archive old file (rename with .old suffix), create new one

**Read project context files:**

Before asking questions, understand the project:
```bash
Read: .claude/skills/project-knowledge/guides/project.md
Read: .claude/skills/project-knowledge/guides/architecture.md
```

**Do NOT read** patterns.md (that's for implementation, not planning).

**If context files missing:**
Tell user: "Похоже, проект ещё не настроен. Сначала нужно заполнить базовую информацию о проекте. Запустите `/init-context` или расскажите о проекте вручную."

Ask user if they want to continue without context or initialize project first.

### Phase 2: Gather High-Level Feature Understanding

**Start free-form conversation:**

Ask user to describe what they want to add/fix/refactor. Let them describe as much or as little as they want.

"Опиши подробно, что хочешь сделать. Какую фичу добавить или что исправить?"

**Create Interview Plan (if new interview):**

Copy interview plan template and initialize metadata:
```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp ~/.claude/shared/interview-templates/feature.yml .claude/tmp/interview-feature-$TIMESTAMP.yml
```

Immediately update metadata after creating:
- Set `interview_metadata.started` to current timestamp
- Set `interview_metadata.last_updated` to current timestamp
- Save the file

**Determine work type automatically:**

Based on user's description, determine:
- **feature**: New functionality being added
- **bug**: Fixing existing broken behavior
- **refactoring**: Improving existing code without changing behavior

Update interview plan `phase1_feature_overview.work_type` with determined type.

**Initial Scoring:**

Read the interview plan file and score Phase 1 items based on user's free-form description:
- If user mentioned something clearly: 80-95% (detailed) or 50-70% (brief)
- If user mentioned something vaguely: 20-40%
- If not mentioned at all: 0%

Update the plan file with:
- Scores for each item
- `value` field with what we learned
- `gaps` field with what's still missing
- Save the updated plan

**Iterative Interview Loop:**

Now enter iterative loop (ask → listen → update → decide → repeat):

1. **Find next gap:** Look at interview plan, find highest-priority gap:
   - Required items (score < 70%) first, lowest score first
   - Then optional items if relevant (user mentioned in context)

2. **Ask ONE question:** Ask about that specific gap
   - Make it conversational in Russian
   - Tailor to work_type (feature vs bug vs refactoring)
   - Don't batch multiple questions

3. **Listen to answer**

4. **IMMEDIATELY update interview plan (CRITICAL for session recovery):**

   a) **Add to conversation_history** (full preservation):
      ```yaml
      - question_num: [increment from current_question_num]
        timestamp: "[current timestamp]"
        topic: "[which item this addresses, e.g. 'user_problem']"
        agent_question: |
          [FULL TEXT of your question - preserve exactly]
        user_answer: |
          [FULL TEXT of user's answer - preserve EVERYTHING they said]
        summary: "[Brief one-line summary for quick reference]"
      ```

   b) **Update metadata:**
      - `interview_metadata.last_updated` = current timestamp
      - `interview_metadata.current_question_num` = increment by 1

   c) **Update scoring:**
      - Update score (based on how well answer fills the gap)
      - Update `value` field (what we learned - can be brief summary)
      - Update `gaps` field (what's still missing)
      - Update `status` (pending → partial → complete)
      - If answer reveals new gaps: add them
      - If feature understanding changed: update other scores

   d) **Update progress tracking:**
      - Recalculate `progress.total_required_score`
      - Recalculate `progress.completion_estimate`
      - Update `progress.questions_asked`
      - Update `progress.last_question`

   e) **SAVE the updated plan file** - don't batch, save NOW
      This is your backup. If session breaks, conversation_history will restore context.

5. **Check stop criteria:**
   - All Phase 1 required items >= 70%?
   - OR user has no more info (all answered or marked TBD)?
   - If YES: move to Phase 3
   - If NO: go back to step 1

**Example questions for feature:**
- "Какую проблему решает эта фича?"
- "Кто будет это использовать?"
- "Как должно работать? Опиши сценарий использования."

**Example questions for bug:**
- "Как воспроизвести баг?"
- "Что ожидается vs что происходит сейчас?"
- "Насколько критично?"

**Example questions for refactoring:**
- "Что именно проблема в текущем коде?"
- "Какой результат хотим после рефакторинга?"
- "Есть ли тесты для этого кода?"

### Phase 3: Gather User Experience Details

**Start the conversation:**

Transition to user experience discussion. Briefly summarize what you understood from Phase 2, then ask about scenarios.

**Iterative Interview Loop (same structure as Phase 2):**

1. **Find next gap:** Look at interview plan Phase 2 section:
   - `user_stories`: How user will interact step-by-step
   - `acceptance_criteria`: What must work (testable checklist)
   - `edge_cases`: Unusual scenarios
   - `error_scenarios`: What can go wrong

2. **Ask ONE question:** About the specific gap
   - "Опиши пошагово: пользователь делает что → система отвечает как → результат?"
   - "Как понять, что фича готова? Какие критерии?"
   - "Какие граничные случаи могут быть?"

3. **Listen to answer**

4. **IMMEDIATELY update interview plan (same as Phase 2):**
   - Add full Q&A to `conversation_history`
   - Update `interview_metadata` (last_updated, current_question_num)
   - Update scores, values, gaps, status
   - Update progress tracking
   - **SAVE plan file NOW**

5. **Check stop criteria:**
   - All Phase 2 required items >= 70%?
   - OR user has no more info?
   - If YES: move to Phase 4
   - If NO: continue loop

### Phase 4: Gather Integration Context

**Ask about integration:**

How does this fit into existing system?

**Iterative Interview Loop:**

1. **Find next gap:** Look at Phase 3 section:
   - `integration_points`: Where this fits in existing codebase
   - `dependencies`: What existing features/services needed
   - `technical_constraints`: Performance, security requirements
   - `data_requirements`: What data needed, where from

2. **Ask ONE question:**
   - "Где эта фича встраивается? Какие компоненты затрагивает?"
   - "От каких существующих сервисов зависит?"
   - "Какие данные нужны? Откуда берём?"

3. **Listen to answer**

4. **IMMEDIATELY update interview plan:**
   - Add to conversation_history
   - Update metadata, scores, progress
   - **SAVE plan file NOW**

5. **Check stop criteria:**
   - All Phase 3 required items >= 70%?
   - OR user has no more info?
   - If YES: proceed to Phase 5 (Fill User Spec)
   - If NO: continue loop

### Phase 5: Fill User Spec

**Now that you have complete picture from all phases, create user-spec.md.**

**Propose feature name:**

Based on feature description, propose a folder name:
- lowercase
- words separated by dashes
- descriptive and concise
- Example: "stripe-payments", "fix-drag-drop", "refactor-auth"

Ask user: "Предлагаю название: `{proposed-name}`. Подходит или хотите изменить?"

Wait for confirmation or alternative name.

**Create feature folder:**
```bash
mkdir -p work/{feature-name}
```

**Read template:**
```bash
Read: ~/.claude/shared/work-templates/user-spec.md.template
```

**Fill user-spec.md:**

File: `work/{feature-name}/user-spec.md`

Source: Interview plan (`value` fields from all phases)

Content (in Russian):
- **Frontmatter:**
  - `created`: Today's date (YYYY-MM-DD)
  - `status`: draft
  - `type`: feature|bug|refactoring (from Phase 1)

- **Что делаем:** From `phase1_feature_overview.feature_description`
- **Зачем:** From `phase1_feature_overview.user_problem`
- **Как должно работать:** From `phase2_user_experience.user_stories`
- **Критерии готовности:** From `phase2_user_experience.acceptance_criteria`
- **Что НЕ делаем:** From `phase1_feature_overview.out_of_scope`

Additional sections if relevant:
- **Граничные случаи:** From `phase2_user_experience.edge_cases` (if scored > 50%)
- **Обработка ошибок:** From `phase2_user_experience.error_scenarios` (if scored > 50%)
- **Интеграция:** From `phase3_integration.integration_points` (if scored > 50%)
- **Зависимости:** From `phase3_integration.dependencies` (if scored > 50%)

**Write the file.**

### Phase 6: Review and Approve

**CRITICAL: This phase is mandatory. Do NOT skip user approval.**

After filling user-spec.md, you MUST get user approval before finishing.

**Step 1: Update Interview Plan (userspec created):**

Update the interview plan file:
- Set `phase4_userspec_review.userspec_created.status`: "created"
- Set `phase4_userspec_review.userspec_created.file_created`: "work/{feature-name}/user-spec.md"
- Set `phase4_userspec_review.userspec_created.feature_name`: "{feature-name}"
- Set `phase4_userspec_review.userspec_created.timestamp_created`: current timestamp
- **SAVE the plan file**

**Step 2: Show File to User (with clickable link):**

Tell user (in Russian):

"Готово! Я подготовил user spec:

[work/{feature-name}/user-spec.md](work/{feature-name}/user-spec.md)

Посмотри, пожалуйста. Всё правильно? Нужны ли изменения?"

**Step 3: Update Interview Plan (awaiting feedback):**

Update the interview plan:
- Set `phase4_userspec_review.user_review.status`: "awaiting_feedback"
- Add to `phase4_userspec_review.user_review.review_requests`:
  ```yaml
  - iteration: 1
    timestamp: "[current timestamp]"
    file_shown: "work/{feature-name}/user-spec.md"
    user_response: "pending"
    feedback: ""
    changes_made: ""
  ```
- **SAVE the plan file**

**Step 4: Wait for User Response (CRITICAL - don't proceed without approval!):**

User can respond in three ways:

**A) Changes requested:**
1. Make the requested edits to user-spec.md
2. Update interview plan:
   - Update last review_request: set `user_response`: "changes_requested", `feedback`: "[what user said]", `changes_made`: "[summary of changes]"
   - Add new review_request (increment iteration)
   - **SAVE plan**
3. Show updated file with link again
4. Return to Step 4 (wait for response again)

**B) Approved:**
1. Update user-spec.md frontmatter: `status: draft` → `status: approved`
2. Update interview plan:
   - Update last review_request: set `user_response`: "approved"
   - Set `phase4_userspec_review.user_review.status`: "approved"
   - **SAVE plan**
3. Tell user: "Отлично! User spec готов."
4. Suggest next step: "Следующий шаг: `/create-tech-spec {feature-name}` для создания технической спецификации."
5. Skill work is DONE

**C) Questions/unclear:**
1. Answer questions
2. If questions lead to changes: follow path A
3. If just clarification: continue waiting for approval or change request

**Important:**
- Do NOT suggest `/create-tech-spec` until user approves
- Do NOT end the skill until user explicitly approves or asks to stop
- If session breaks during review, next session will resume from review state (thanks to interview plan tracking)

**Cleanup Interview Plan (optional):**

After user approval (Step 4B completed), you can either:

**Option A - Delete** (saves space):
```bash
rm .claude/tmp/interview-feature-*.yml
```

**Option B - Keep** (audit trail):
- Leave the file in `.claude/tmp/` for future reference
- Shows how user spec was created
- Can review interview questions later
- User spec is now the source of truth, but interview plan shows how we got there

Recommend: Keep the file (it's small, might be useful)

## Handling Special Cases

### User Says "Не знаю"

Don't skip the question. Help them think through it:
- Say you understand
- Explain common approaches (2-3 examples)
- Ask which is closer to their situation
- If still uncertain and it's optional: mark as TBD and move on
- If still uncertain and it's required: break down into simpler questions

### Feature Turns Out More Complex

If initial understanding was wrong, adapt:
- Acknowledge the complexity increased
- Explain what you initially thought vs what you now understand
- Update interview plan: lower affected scores, add new gaps
- Ask more detailed questions about newly discovered areas

### Unclear Requirements

If you can't understand something after multiple attempts:
- Suggest marking it as TBD
- Explain it can be detailed in tech-spec phase
- Note it in user spec as something to resolve
- Move to next gap rather than getting stuck

### No Project Context Available

If project.md and architecture.md are missing:
- Ask user if they want to initialize project first (`/init-context`)
- OR continue without context (generic questions, not tailored to project)
- Warn: "Без контекста проекта я буду задавать общие вопросы. Лучше сначала настроить проект."

## Quality Guidelines

**Good user-spec.md:**
- ✅ Clear problem statement (why we're building this)
- ✅ Specific target users (not "everyone")
- ✅ Step-by-step user scenarios
- ✅ Testable acceptance criteria (concrete checklist)
- ✅ Clear out-of-scope section (prevents scope creep)
- ✅ Considers edge cases and error handling
- ✅ Integration points identified

**Bad practices:**
- ❌ Vague description ("make it better")
- ❌ No user value explained ("just add X")
- ❌ Missing acceptance criteria
- ❌ No edge cases considered
- ❌ Unclear scope boundaries
- ❌ Technical implementation details in user spec (belongs in tech-spec)

## Resources

This skill uses shared templates:
- `~/.claude/shared/interview-templates/feature.yml` - Interview tracking structure
- `~/.claude/shared/work-templates/user-spec.md.template` - Output template

Interview plan enables:
- Session recovery (resume after interruption)
- Progress tracking (completion estimate)
- Full conversation history (what was discussed)
- Adaptive scoring (know what gaps remain)
- User approval tracking (review iterations and feedback)
