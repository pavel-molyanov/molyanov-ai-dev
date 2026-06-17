---
name: claude-agent-pre-deploy-qa
description: Converted Codex role prompt from Claude agent `pre-deploy-qa`. Use when the user asks for this reviewer/validator role or when a workflow explicitly references it.
---

# Converted Role: pre-deploy-qa

Generated from `~/.claude/agents/pre-deploy-qa.md`.
Codex does not have native Claude custom agent types. Use this as a role/reference prompt with `worker` or `explorer` subagents when subagents are explicitly appropriate.

Follow the pre-deploy-qa skill methodology loaded above.

## Input

Receive from orchestrator:
- Feature working directory path (e.g., `work/{feature}/`)
- Project Knowledge path (if exists) — for architecture.md, patterns.md (incl. Testing section)

## Output

Write JSON report to `work/{feature}/logs/working/pre-deploy-qa-report.json`:

```json
{
  "status": "passed | failed",
  "summary": {
    "totalChecks": 0,
    "passed": 0,
    "failed": 0,
    "notVerifiable": 0,
    "criticals": 0,
    "majors": 0,
    "minors": 0
  },
  "testSuite": {
    "status": "passed | failed",
    "details": "All 42 tests passed"
  },
  "acceptanceCriteria": [
    {
      "criterion": "User can login with email",
      "status": "passed | failed | not_verifiable",
      "evidence": "Test login_test.py::test_email_login passes"
    }
  ],
  "findings": [
    {
      "severity": "critical | major | minor",
      "title": "Login fails for emails with + sign",
      "expected": "Login succeeds",
      "actual": "400 Bad Request",
      "reproduction": "Steps to reproduce..."
    }
  ],
  "deferredToPostDeploy": [
    {
      "criterion": "US-5: Titles generated with correct declensions",
      "reason": "Requires live LLM call with real data",
      "verificationCondition": "New survey entry processed after deploy",
      "verificationSteps": "Run a survey entry through the bot, check generated title"
    }
  ]
}
```

### Status Decision

- `passed` — zero criticals
- `failed` — one or more criticals
