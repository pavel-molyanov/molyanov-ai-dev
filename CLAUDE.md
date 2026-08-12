## Language
- Artifacts addressed to the user (chat, plans, plan-mode, interviews, validator summaries, user-spec, README): the language the user writes in. Declare your language here — e.g. "This user writes in English." Skills and agents read the user's language from this line.
- Technical docs, code, code comments, AI prompts, internal logs (tech-spec, tasks, CLAUDE.md, skills): English.

## Behavior

- No "Great question!", no filler, no water.
- NEVER use AskUserQuestion tool. Ask questions as plain text in chat instead.
- Never create Git worktrees or extra project copies unless the user explicitly asks.

## Task Scope

- The user's request and any explicitly approved plan define the authorized scope of work.
- Choose the minimal solution sufficient for the task. Do not add unrequested capabilities, files,
  rules, steps, or changes, and do not rework related materials "while you're there."
- Findings, ideas, and problems discovered during validation do not expand the authorized scope.
- Research, analysis, review, diagnosis, and planning do not by themselves authorize changes or
  external actions.

## Task Planning

- Use TodoWrite for multi-step tasks (>1 step).
- When the user asks for a team or swarm, orchestrate bounded subagent work with the runtime's team
  tools.

## Security

- NEVER ask user to write secrets in chat
- Instead: provide instructions where to store them securely
  - Local: `.env` files, config files
  - CI/CD: GitHub Actions secrets
- ALWAYS ask before pushing to main
- ALWAYS add secrets to `.gitignore`: `.env`, `*.key`, `credentials.json`, `secrets/`
- Be cautious with external actions (push, deploy, send messages, create PRs). Ask before acting externally when uncertain.
