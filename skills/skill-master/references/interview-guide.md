# Skill Discovery Interview Guide

Run this interview when creating a NEW skill. Skip for editing existing skills.

## Process Overview

1. Check for existing interview (resume if found)
2. Phase 1: Skill Overview (name, purpose, triggers, NOT-for)
3. Phase 2: Usage Scenarios (examples, edge cases, errors)
4. Phase 3: Output & Resources (format, bundled resources)
5. Proceed to skill creation with gathered info

## Starting the Interview

### Check for Existing Interview

```bash
ls ~/.claude/tmp/interview-skill-*.yml 2>/dev/null
```

If found:
- Read file, show recap: "Found an unfinished interview for skill {name}"
- Ask: "Continue or start over?"
- If continue: resume from current state
- If restart: archive old file, create new

### Create New Interview

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp ~/.claude/shared/interview-templates/skill.yml ~/.claude/tmp/interview-skill-$TIMESTAMP.yml
```

Set `interview_metadata.started` to current timestamp.

## Iterative Interview Loop

**Repeat for each phase:**

1. **Find next gap:** Look at interview plan, find item with score < 70%
2. **Ask ONE question** about that gap
3. **Listen** to user's answer
4. **Update interview plan immediately:**
   - Add to `conversation_history`
   - Update `interview_metadata.last_updated`
   - Update score, value, gaps, status for the item
   - **SAVE the plan file**
5. **Check stop:** All required items >= 70%? → Move to next phase

## Example Questions

Ask these in the language the user writes in (examples below are in English).

### Phase 1: Skill Overview

- "What is the skill called? Suggest a descriptive name."
- "What problem does this skill solve? Why is it needed?"
- "Is it a step-by-step process with a clear sequence (procedural skill) or a body of knowledge/methodology without strict order (informational skill)?"
- "When should the skill activate? Which user phrases trigger it?"
- "What should the skill NOT do? What is out of scope?"

### Phase 2: Usage Scenarios

- "Give 2-3 concrete examples of using the skill."
- "What edge cases might occur? What if the user provides incomplete information?"
- "What could go wrong? How should the skill handle errors?"

### Phase 3: Output & Resources

- "What should the skill produce as a result? Files, messages, actions?"
- "Does the skill need supporting resources: scripts, references, assets?"
- "What external tools are needed? MCP servers, APIs, CLIs?"

## Handling "I don't know"

If user doesn't know:
1. Explain why this matters
2. Offer 2-3 examples from similar skills
3. Ask which is closer to their situation
4. If still uncertain and optional: mark as TBD, move on
5. If still uncertain and required: break down into simpler questions

## After Interview Complete

Proceed to Step 2 (Planning Reusable Skill Contents) with gathered information.

The interview plan file serves as the source of requirements for skill creation.

## Cleanup

After skill is created and user is satisfied:
- Delete interview file: `rm ~/.claude/tmp/interview-skill-*.yml`
- Or keep for audit trail (shows how requirements were gathered)
