#!/bin/sh
# Pre-commit hook for Node.js projects using Husky
# Runs gitleaks to detect secrets before commit

# Run gitleaks on staged files
gitleaks detect --staged --verbose --no-banner

# If gitleaks finds secrets, commit will be blocked
# Exit code 1 = secrets found, commit blocked
# Exit code 0 = no secrets, commit proceeds
