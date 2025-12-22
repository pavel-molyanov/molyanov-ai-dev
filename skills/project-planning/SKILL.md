---
name: project-planning
description: |
  Plan new projects: fills project.md + features.md + roadmap.md through interview.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "сделай описание проекта", "запиши описание проекта в документацию", "проведи со мной интервью для описания проекта"

  Do NOT use for: feature planning (use user-spec-planning), tech planning (use tech-spec-planning)
---

# Project Planning

## Overview

Conduct comprehensive adaptive interview that fills all three planning documents:
- **project.md** - High-level project overview, target audience, core problem, key features, scope boundaries
- **features.md** - Complete feature inventory with priorities and dependencies
- **roadmap.md** - Development phases, milestones, and timeline

## When to Use

Activate this skill when:
- Starting a new project from scratch
- Need to plan project comprehensively: what it is, what features it has, how to develop it
- User asks to plan or decompose a project

## Approach

### Your Role

You're conducting a planning interview to understand how to break down the project into manageable pieces. Be conversational, adaptive, and help the user think through unclear aspects.

**Communication style:** Разговорный (conversational Russian)

### Core Principles

1. **Adapt to the conversation**
   Every project is different. Let the conversation flow naturally based on what the user says.

2. **Build on previous answers**
   Each response reveals new context. Use what you learn to guide next questions.

3. **Help when stuck**
   If user doesn't know something, don't skip it. Offer examples, break down questions, suggest common patterns.

4. **Trust your judgment**
   You're an LLM, not a script. Think about what information is needed, don't follow mechanical rules.

5. **Confirm understanding**
   Periodically summarize to ensure you understood correctly.

## Process

### Phase 1: Gather Project Overview

**Verify environment:**
- Check if `.claude/skills/project-knowledge/guides/project.md` exists (template)
- If missing, tell user to run `/init-project` first

**Check for existing interview (Resume functionality):**

Before starting new interview, check if one is in progress:
```bash
ls .claude/tmp/interview-plan-*.yml 2>/dev/null
```

If file exists:
1. Read `interview_metadata`, `conversation_history`, and `phase4_documentation_review` sections
2. **Check if in review phase:** If `phase4_documentation_review.documentation_created.status` is "created":
   - Show user: "Нашёл интервью, ожидающее твоего подтверждения."
   - Jump directly to Phase 5 Step 2 (show files with links, ask for approval)
   - Resume review process from there
3. **If NOT in review phase:**
   - Show user: "Нашёл незавершённое интервью (начато: {started}, прогресс: {completion_estimate})"
   - Show brief recap: "Вот что мы уже обсудили:" + list topics from conversation_history
   - Ask: "Продолжить с того места, где остановились, или начать заново?"
   - If continue: Load interview plan, resume from current state
   - If restart: Archive old file (rename with .old suffix), create new one

**Start free-form conversation:**

Ask user to describe the project in free form. Guide them to cover:
- What the project is about
- Why it's needed (problem being solved)
- Who will use it (target audience)
- What main features/capabilities should be there

Let them describe as much or as little as they want - from one sentence to detailed spec.

**Create Interview Plan (if new interview):**

Copy interview plan template and initialize metadata:
```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp ~/.claude/shared/interview-plan-template.yml .claude/tmp/interview-plan-$TIMESTAMP.yml
```

Immediately update metadata after creating:
- Set `interview_metadata.started` to current timestamp
- Set `interview_metadata.last_updated` to current timestamp
- Save the file

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
   - Then optional items if user seems knowledgeable

2. **Ask ONE question:** Ask about that specific gap
   - Make it conversational in Russian
   - Don't batch multiple questions

3. **Listen to answer**

4. **IMMEDIATELY update interview plan (CRITICAL for session recovery):**

   a) **Add to conversation_history** (full preservation):
      ```yaml
      - question_num: [increment from current_question_num]
        timestamp: "[current timestamp]"
        topic: "[which item this addresses, e.g. 'core_problem']"
        agent_question: |
          [FULL TEXT of your question - preserve exactly]
        user_answer: |
          [FULL TEXT of user's answer - preserve EVERYTHING they said]
        summary: "[Brief one-line summary for quick reference]"
      ```

   b) **Update metadata:**
      - `interview_metadata.last_updated` = current timestamp
      - `interview_metadata.current_question_num` = increment by 1

   c) **Update scoring as before:**
      - Update score (based on how well answer fills the gap)
      - Update `value` field (what we learned - can be brief summary)
      - Update `gaps` field (what's still missing)
      - Update `status` (pending → partial → complete)
      - If answer reveals new gaps: add them
      - If project understanding changed: update other scores

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
   - If YES: move to Phase 2
   - If NO: go back to step 1

**Example scoring:**
- User: "Todo app for myself" → target_audience: 70% (clear but brief)
- User: "Developers building CLI tools who need X because Y" → target_audience: 95%
- User: "Не знаю" → If required: help discover. If optional: mark TBD, score 50%

**Do NOT fill project.md yet** - just gather information in interview plan. User might change their mind during Phase 2-3.

### Phase 2: Gather Feature Information (Detailed Inventory)

**Start the conversation:**

Transition to features discussion. Briefly summarize what you understood from Phase 1, then ask about features in detail. Let user choose format: quick list or detailed descriptions.

**Update Interview Plan after response:**

Score Phase 2 items based on user's response:
- Did they list features? → `feature_list`: 50-90% depending on detail
- Did they mention priorities? → `feature_priorities`: score accordingly
- Did they explain WHY features needed? → `feature_user_value`: score accordingly

Save updated plan.

**Iterative Interview Loop (same structure as Phase 1):**

1. **Find next gap:** Look at interview plan Phase 2 section:
   - Required items (score < 70%) first
   - Optional items if relevant

2. **Ask ONE question:** About the specific gap
   - If they listed features but no priorities: Ask which are critical for MVP
   - If no user value explained: Ask why user needs this feature
   - If uncertain: Help break down by user journeys, suggest common features

3. **Listen to answer**

4. **IMMEDIATELY update interview plan (same as Phase 1):**
   - Add full Q&A to `conversation_history`
   - Update `interview_metadata` (last_updated, current_question_num)
   - Update scores, values, gaps, status
   - If they mention dependencies: update `dependencies` item
   - If they mention technical constraints: update `technical_constraints` item
   - Update progress tracking
   - **SAVE plan file NOW**

5. **Check stop criteria:**
   - All Phase 2 required items >= 70%?
   - OR user has no more info?
   - If YES: move to Phase 3
   - If NO: continue loop

**Gathering approach (choose based on context):**
- If user listed many features: Ask about all priorities together, then details one-by-one
- If user uncertain: One feature at a time, help discover
- If user detailed: Quick clarifying questions only

**Do NOT fill features.md yet** - just gather information in interview plan. User might refine understanding based on Phase 3.

### Phase 3: Determine Roadmap Needs

**Ask about development approach:**

Ask whether user plans phased development or building everything at once.

**Update Interview Plan after response:**

Score Phase 3 items based on answer:
- `development_approach`: 90-100% (should be clear yes/no)
- If phased: `phasing_strategy` and `milestones` become relevant
- If migration: `migration_context` becomes relevant

**Iterative Interview Loop:**

1. **Find next gap:** Look at Phase 3 section:
   - If phased development: need `phasing_strategy` and `milestones`
   - If migration project: need `migration_context` details

2. **Ask ONE question:**
   - If phased: Ask how to group features, what's MVP vs later phases
   - If phased: Ask about milestones and exit criteria for each phase
   - If migration: Ask about current system, data migration strategy, risks

3. **Listen to answer**

4. **IMMEDIATELY update interview plan (same as Phase 1 & 2):**
   - Add full Q&A to `conversation_history`
   - Update `interview_metadata` (last_updated, current_question_num)
   - Update scores, values, gaps for relevant items
   - Update progress tracking
   - **SAVE plan file NOW**

5. **Check stop criteria:**
   - All Phase 3 required items >= 70%?
   - OR user has no more info?
   - If YES: proceed to Phase 4 (Fill Documentation)
   - If NO: continue loop

**Important - NO time estimates:**
- Focus on: phases, milestones, exit criteria
- Do NOT ask about: weeks, months, deadlines
- AI-First development pace is unpredictable
- Roadmap is about WHAT and in WHAT ORDER, not WHEN

**Do NOT fill roadmap.md yet** - just gather information in interview plan. Now you have complete picture from all three phases.

### Phase 4: Fill All Three Documentation Files

**Now that you have complete picture from Phases 1-3, fill all three documentation files.**

**Read Interview Plan:**

Open the interview plan file from `.claude/tmp/interview-plan-*.yml` and use it as source:
- Phase 1 section → fills project.md
- Phase 2 section → fills features.md
- Phase 3 section → fills roadmap.md

**If documentation files don't exist** (old project):
Copy from template:
```bash
cp ~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/project.md .claude/skills/project-knowledge/guides/
cp ~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/features.md .claude/skills/project-knowledge/guides/
cp ~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/roadmap.md .claude/skills/project-knowledge/guides/
```

**Fill project.md:**
- File: `.claude/skills/project-knowledge/guides/project.md`
- Source: Interview plan Phase 1 (`value` fields)
- Keep it high-level (3-5 key features only from `key_features_highlevel`)
- Content in English (except Cyrillic project names)

**Fill features.md:**
- File: `.claude/skills/project-knowledge/guides/features.md`
- Source: Interview plan Phase 2 (`value` fields)
- List ALL features from `feature_list`
- Include priorities from `feature_priorities`
- Include user value from `feature_user_value`
- Include dependencies from `dependencies` if present
- Group features logically if many

**Fill roadmap.md:**
- File: `.claude/skills/project-knowledge/guides/roadmap.md`
- Source: Interview plan Phase 3 (`value` fields)
- If simple project (`development_approach` = all at once): minimal roadmap or mostly empty
- If phased: detailed phases from `phasing_strategy` and milestones from `milestones`
- If migration: detailed migration plan from `migration_context`
- **NO time estimates** - use milestones and exit criteria only

**Content language:** English (documentation is always in English)

**Cleanup Interview Plan (optional):**

After successfully filling all three files, you can either:

**Option A - Delete** (saves space):
```bash
rm .claude/tmp/interview-plan-*.yml
```

**Option B - Keep** (audit trail):
- Leave the file in `.claude/tmp/` for future reference
- Useful if user wants to see what questions were asked
- Can resume or review the interview process later
- Documentation is now the source of truth, but interview plan shows how we got there

Recommend: Keep the file (it's small, might be useful)

### Phase 5: Review and Iterate

**CRITICAL: This phase is mandatory. Do NOT skip user approval.**

After filling all three documentation files, you MUST get user approval before finishing.

**Step 1: Update Interview Plan (documentation created):**

```bash
# Update phase4_documentation_review section in interview plan
```

Update the interview plan file:
- Set `phase4_documentation_review.documentation_created.status`: "created"
- Set `phase4_documentation_review.documentation_created.files_created`: ["project.md", "features.md", "roadmap.md"]
- Set `phase4_documentation_review.documentation_created.timestamp_created`: current timestamp
- **SAVE the plan file**

**Step 2: Show Files to User (with clickable links):**

Tell user (in Russian):

"Готово! Я заполнил все три файла планирования:

- [project.md](.claude/skills/project-knowledge/guides/project.md) - Описание проекта
- [features.md](.claude/skills/project-knowledge/guides/features.md) - Список фич с приоритетами
- [roadmap.md](.claude/skills/project-knowledge/guides/roadmap.md) - План разработки

Посмотри, пожалуйста. Всё правильно? Есть что изменить?"

**Step 3: Update Interview Plan (awaiting feedback):**

Update the interview plan:
- Set `phase4_documentation_review.user_review.status`: "awaiting_feedback"
- Add to `phase4_documentation_review.user_review.review_requests`:
  ```yaml
  - iteration: 1
    timestamp: "[current timestamp]"
    files_shown: ["project.md", "features.md", "roadmap.md"]
    user_response: "pending"
    feedback: ""
    changes_made: ""
  ```
- **SAVE the plan file**

**Step 4: Wait for User Response (CRITICAL - don't proceed without approval!):**

User can respond in three ways:

**A) Changes requested:**
1. Make the requested edits to the files
2. Update interview plan:
   - Update last review_request: set `user_response`: "changes_requested", `feedback`: "[what user said]", `changes_made`: "[summary of changes]"
   - Add new review_request (increment iteration)
   - **SAVE plan**
3. Show updated files with links again
4. Return to Step 4 (wait for response again)

**B) Approved:**
1. Update interview plan:
   - Update last review_request: set `user_response`: "approved"
   - Set `phase4_documentation_review.user_review.status`: "approved"
   - **SAVE plan**
2. Tell user: "Отлично! Планирование завершено."
3. Suggest next step: "Следующий шаг: `/init-context` для технического планирования (архитектура, стек, паттерны)."
4. Skill work is DONE

**C) Questions/unclear:**
1. Answer questions
2. If questions lead to changes: follow path A
3. If just clarification: continue waiting for approval or change request

**Important:**
- Do NOT suggest `/init-context` until user approves
- Do NOT end the skill until user explicitly approves or asks to stop
- If session breaks during review, next session will resume from review state (thanks to interview plan tracking)

## Handling Special Cases

### User Says "Не знаю"

Don't skip the question. Help them think through it:
- Say you understand
- Explain common approaches for this type of project (2-3 variants with examples)
- Ask which is closer to their situation
- If still uncertain and it's optional: mark as TBD and move on
- If still uncertain and it's required: help break down into simpler questions

### Project Turns Out More Complex

If initial understanding was wrong, adapt:
- Acknowledge the complexity increased
- Explain what you initially thought vs what you now understand
- Update interview plan: lower affected scores, add new gaps
- Ask more detailed questions about newly discovered areas

### Unclear Requirements

If you can't understand something after multiple attempts:
- Suggest marking it as TBD
- Explain it can be revisited later when more clear
- Note it in documentation as something to resolve
- Move to next gap rather than getting stuck

## Resources

This skill includes reference documentation:

### references/conversation-examples.md
Real examples of good planning conversations:
- Simple project (3 features)
- Complex project (15+ features)
- Migration project
- Uncertain/exploratory project

Shows full conversations with thinking process.

### references/documentation-guide.md
Guidance on filling project.md, features.md, and roadmap.md:
- project.md structure and principles (high-level vs detailed)
- When to make roadmap detailed vs minimal
- How to structure features
- How to group and prioritize
- Migration-specific patterns

Read this reference when you need detailed guidance on documentation structure and content decisions.

## Quality Guidelines

**Good project.md:**
- ✅ Clear, specific one-line description (not vague)
- ✅ Specific target audience (not "everyone")
- ✅ Core problem clearly articulated (why this matters)
- ✅ Key features = only 3-5 most important (high-level)
- ✅ Out of scope section (prevents scope creep)
- ✅ Concise and high-level (details belong in features.md)

**Good features.md:**
- ✅ Every feature has clear user value
- ✅ Priorities are justified
- ✅ Dependencies are explicit
- ✅ Grouped logically if many features
- ✅ Concise but complete descriptions

**Good roadmap.md:**
- ✅ Realistic phases
- ✅ Clear milestones
- ✅ Considers dependencies
- ✅ For migrations: detailed risk mitigation
- ✅ Minimal if project is simple (not bloated)

**Bad practices:**
- ❌ **project.md:** Vague description ("a platform for everything")
- ❌ **project.md:** Too broad target audience or unclear
- ❌ **project.md:** Key features list is exhaustive (should be in features.md)
- ❌ **project.md:** Too detailed (belongs in features.md/architecture.md)
- ❌ **project.md:** Missing out of scope section
- ❌ **features.md:** Features too granular (tasks, not features)
- ❌ **features.md:** No priorities ("everything is important")
- ❌ **features.md:** No user value explained
- ❌ **roadmap.md:** Timeline estimates (weeks/months/dates) - AI-First development uses milestones instead
- ❌ **roadmap.md:** Bloated roadmap for simple project
