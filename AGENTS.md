## Language
- Artifacts addressed to the user (chat, plans, plan-mode, interviews, validator summaries, user-spec, README): the language the user writes in.
- Technical docs, code, code comments, AI prompts, internal logs (tech-spec, tasks, AGENTS.md, skills): English.

## Behavior

- No "Great question!", no filler, no water.
- NEVER use plain chat question tool. Ask questions as plain text in chat instead.
- ALL deployments via GitHub CI/CD only. Direct server access (SSH, container restarts) only for emergency debugging of broken production.

## Task Planning
- Use update_plan for multi-step tasks (>1 step)
- When user asks for team/swarm of agents: use spawn_agent worker/explorer orchestration, not single-task spawn_agent

## Security

- NEVER ask user to write secrets in chat
- Instead: provide instructions where to store them securely
  - Local: `.env` files, config files
  - CI/CD: GitHub Actions secrets
- ALWAYS ask before Deploy/push to main/production
- ALWAYS add secrets to `.gitignore`: `.env`, `*.key`, `credentials.json`, `secrets/`
- Be cautious with external actions (push, deploy, send messages, create PRs). Ask before acting externally when uncertain.