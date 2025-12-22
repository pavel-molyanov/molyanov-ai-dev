# Global Instructions for Claude Code

## Language
- Communicate with user: Russian
- Tech docs (code, context, rules, CLAUDE.md, skills): English
- AI prompts: English
- User-facing docs (README): Russian

## Task Planning
- ALWAYS use TodoWrite for multi-step tasks (>1 step)

## Security

### Secrets Management
- NEVER ask user to write secrets in chat
- Instead: provide instructions where to store them securely
  - Local: `.env` files, config files
  - CI/CD: GitHub Actions secrets

### Critical Operations
- ALWAYS ask before:
  - Deploy/push to main/production
  - Committing secrets (warn user!)

## Git
- ALWAYS add secrets to `.gitignore`: `.env`, `*.key`, `credentials.json`, `secrets/`

ChatGPT-5 exists, its not a mistake! 