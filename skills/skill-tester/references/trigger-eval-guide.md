# Trigger Eval Guide

How to design queries that test whether a skill's description triggers correctly.

## Why This Matters

The description field in SKILL.md frontmatter is the primary mechanism that
determines whether Claude invokes a skill. Claude sees the skill's name +
description in its available_skills list and decides whether to consult it.

Claude tends to **undertrigger** skills — not use them when they'd be useful.
This means false negatives (skill should trigger but doesn't) are the most
costly failure mode: users won't discover the skill exists.

## Designing Trigger Eval Queries

### Should-Trigger Queries (8-10)

Think about **coverage** — different phrasings of the same intent:
- Some formal, some casual
- Cases where user doesn't explicitly name the skill or file type but
  clearly needs it
- Uncommon use cases that still fall within the skill's domain
- Cases where this skill competes with another but should win
- Different levels of detail (brief request vs. detailed backstory)
- Different languages if applicable (English + the user's own language)

### Should-NOT-Trigger Queries (8-10)

The most valuable are **near-misses** — queries that share keywords or
concepts with the skill but actually need something different:
- Adjacent domains
- Ambiguous phrasing where naive keyword match would trigger but shouldn't
- Cases touching on something the skill does but in a context where another
  tool/skill is more appropriate

Avoid obviously irrelevant queries — "Write a fibonacci function" as a
negative test for a PDF skill is too easy. It doesn't test anything. The
negative cases should be genuinely tricky.

### Query Quality

Queries must be realistic — something a real user would actually type:
- File paths, personal context, column names, company names, URLs
- Some backstory
- Mix of lowercase, abbreviations, typos, casual speech
- Different lengths
- Concrete and specific, not abstract

**Bad query:**
```
"Format this data"
```

**Good query:**
```
"ok so my boss just sent me this xlsx file (its in my downloads, called
something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add
a column that shows the profit margin as a percentage"
```

### Substantive Queries

Skills trigger for tasks Claude can't easily handle on its own. Simple,
one-step queries like "read this PDF" may not trigger a skill even if the
description matches perfectly — Claude handles them directly with basic tools.

Complex, multi-step, or specialized queries reliably trigger skills when the
description matches. So eval queries should be substantive enough that Claude
would actually benefit from consulting a skill.

## trigger-evals.json Format

```json
[
  {
    "id": 1,
    "query": "the user prompt — realistic, detailed",
    "should_trigger": true,
    "rationale": "Why this should/shouldn't trigger the skill"
  }
]
```

## Evaluating Trigger Accuracy

### Assessment Method

For each query, assess whether the skill's current description would cause
Claude to invoke it. Consider:
- Does the query's intent match the description's keywords?
- Would Claude see this as the skill's domain based on description alone?
- Is the query substantive enough to warrant a skill consultation?

### Metrics

```
Trigger accuracy = (true positives + true negatives) / total queries
False negative rate = false negatives / should-trigger queries
False positive rate = false positives / should-not-trigger queries
```

**Target: ≥85% trigger accuracy, ≤20% false negative rate.**

### Improving the Description

When accuracy is below target, analyze failure patterns:

1. **False negatives cluster** — missing keywords? Add them.
   The description should explicitly list contexts that activate the skill.
2. **False positives cluster** — description too broad? Add scope limits.
   "This skill does NOT handle X" can help disambiguate.
3. **Mixed failures** — description may need restructuring. Try the
   "pushy" approach: list specific scenarios explicitly rather than
   relying on general terms.

### Before/After Format

When suggesting an improved description, show:

```
BEFORE:
description: |
  [current description]

AFTER:
description: |
  [improved description]

Changes:
- Added: [keywords/contexts added]
- Removed: [overly broad terms removed]
- Clarified: [disambiguations added]

Expected impact:
- False negatives fixed: queries #3, #7, #9
- False positives fixed: query #14
- New accuracy: ~95% (was 70%)
```
