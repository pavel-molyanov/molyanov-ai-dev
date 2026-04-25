## Language
- Communicate with user, plans, plan-mode: Russian
- Tech docs (code, context, rules, AGENTS.md, skills): English
- AI prompts: English
- User-facing docs (README): Russian

## Behavior

- No "Great question!", no filler, no water.
- Do not use special question tools for ordinary clarification. Ask questions as plain text in chat instead.
- ALL deployments via GitHub CI/CD only. Direct server access (SSH, container restarts) only for emergency debugging of broken production.

## Task Planning
- Use update_plan for multi-step tasks (>1 step)
- When user asks for team/swarm of agents: orchestrate Codex `worker`/`explorer` subagents with `spawn_agent`.

## Security

- NEVER ask user to write secrets in chat
- Instead: provide instructions where to store them securely
  - Local: `.env` files, config files
  - CI/CD: GitHub Actions secrets
- ALWAYS ask before Deploy/push to main/production
- ALWAYS add secrets to `.gitignore`: `.env`, `*.key`, `credentials.json`, `secrets/`
- Be cautious with external actions (push, deploy, send messages, create PRs). Ask before acting externally when uncertain.