#!/usr/bin/env bash
#
# init-feature-folder.sh — Create a user-spec feature folder
#
# Usage: ./init-feature-folder.sh <feature-name> [work-dir]
#   feature-name  — required, kebab-case slug (e.g., "add-auth", "fix-login-bug")
#   work-dir      — optional, path to work directory (default: ./work)
#
# Creates:
#   work/{feature-name}/
#     user-spec.md          (from template)
#     decisions.md          (from template or header)
#     logs/userspec/
#       interview.yml       (from template)
#     logs/working/

set -euo pipefail

# --- Arguments ---
FEATURE_NAME="${1:-}"
WORK_DIR="${2:-./work}"

if [[ -z "$FEATURE_NAME" ]]; then
  echo "Error: feature-name is required" >&2
  echo "Usage: $0 <feature-name> [work-dir]" >&2
  exit 1
fi

# --- Paths ---
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ASSETS_DIR="$SKILL_DIR/assets"
INTERVIEW_TEMPLATE="$ASSETS_DIR/interview.yml.template"
DECISIONS_TEMPLATE="$ASSETS_DIR/decisions.md.template"
USER_SPEC_TEMPLATE="$ASSETS_DIR/user-spec.md.template"
FEATURE_DIR="$WORK_DIR/$FEATURE_NAME"
TODAY=$(date +%Y-%m-%d)

# --- Validation ---
if [[ ! -f "$USER_SPEC_TEMPLATE" ]]; then
  echo "Error: template not found: $USER_SPEC_TEMPLATE" >&2
  exit 1
fi

EXISTED=false
if [[ -d "$FEATURE_DIR" ]]; then
  EXISTED=true
fi

# --- Create directory structure (mkdir -p is safe for existing dirs) ---
mkdir -p "$FEATURE_DIR/logs/userspec"
mkdir -p "$FEATURE_DIR/logs/working"

# --- Copy and fill templates (only if file doesn't already exist) ---

# user-spec.md
if [[ ! -f "$FEATURE_DIR/user-spec.md" ]]; then
  sed -e "s/\[DATE\]/$TODAY/g" \
      -e "s/\[feature\/fix name\]/$FEATURE_NAME/g" \
      "$USER_SPEC_TEMPLATE" > "$FEATURE_DIR/user-spec.md"
fi

# decisions.md
if [[ ! -f "$FEATURE_DIR/decisions.md" ]]; then
  if [[ -f "$DECISIONS_TEMPLATE" ]]; then
    sed -e "s/{Feature Name}/$FEATURE_NAME/g" \
        "$DECISIONS_TEMPLATE" > "$FEATURE_DIR/decisions.md"
  else
    echo "# Decisions: $FEATURE_NAME" > "$FEATURE_DIR/decisions.md"
  fi
fi

# interview.yml (from template)
if [[ ! -f "$FEATURE_DIR/logs/userspec/interview.yml" ]]; then
  if [[ -f "$INTERVIEW_TEMPLATE" ]]; then
    cp "$INTERVIEW_TEMPLATE" "$FEATURE_DIR/logs/userspec/interview.yml"
  else
    echo "Warning: interview template not found: $INTERVIEW_TEMPLATE" >&2
  fi
fi

if [[ "$EXISTED" == true ]]; then
  echo "Updated feature folder: $FEATURE_DIR/ (added missing structure)"
else
  echo "Created feature folder: $FEATURE_DIR/"
fi
