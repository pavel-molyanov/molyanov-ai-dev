#!/bin/sh
# Gitleaks pre-commit hook for secret detection
# Blocks commits containing secrets (API keys, tokens, credentials)

# Check if gitleaks is installed
command -v gitleaks >/dev/null || {
  echo "❌ Install gitleaks: brew install gitleaks"
  exit 1
}

gitleaks detect --staged --verbose --no-banner || {
  echo ""
  echo "❌ Secrets detected in staged files!"
  echo ""
  echo "Remove secrets before committing:"
  echo "  - Use .env files for environment variables"
  echo "  - Use config files for API keys"
  echo "  - Never commit credentials directly"
  echo ""
  echo "If this is a false positive, update .gitleaksignore"
  exit 1
}
