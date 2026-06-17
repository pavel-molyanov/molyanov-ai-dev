#!/usr/bin/env bash
#
# init-feature-folder.sh — Create full feature folder structure
#
# Usage: ./init-feature-folder.sh <feature-name> [work-dir]
#   feature-name  — required, kebab-case slug (e.g., "add-auth", "fix-login-bug")
#   work-dir      — optional, path to work directory (default: ./work)
#
# Creates:
#   work/{feature-name}/
#     user-spec.md          (from template)
#     tech-spec.md          (from template, if available)
#     decisions.md          (from template or header)
#     tasks/
#     logs/userspec/
#       interview.yml       (from template)
#     logs/techspec/
#     logs/tasks/
#     logs/working/
#     logs/checkpoint.yml   (from template, for feature-execution recovery)

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
TEMPLATES_DIR="$HOME/.claude/shared/work-templates"
INTERVIEW_TEMPLATE="$HOME/.claude/shared/interview-templates/feature.yml"
FEATURE_DIR="$WORK_DIR/$FEATURE_NAME"
TODAY=$(date +%Y-%m-%d)

# --- Validation ---
if [[ ! -f "$TEMPLATES_DIR/user-spec.md.template" ]]; then
  echo "Error: template not found: $TEMPLATES_DIR/user-spec.md.template" >&2
  exit 1
fi

EXISTED=false
if [[ -d "$FEATURE_DIR" ]]; then
  EXISTED=true
fi

# --- Create directory structure (mkdir -p is safe for existing dirs) ---
mkdir -p "$FEATURE_DIR/tasks"
mkdir -p "$FEATURE_DIR/logs/userspec"
mkdir -p "$FEATURE_DIR/logs/techspec"
mkdir -p "$FEATURE_DIR/logs/tasks"
mkdir -p "$FEATURE_DIR/logs/working"

# --- Copy and fill templates (only if file doesn't already exist) ---

# user-spec.md
if [[ ! -f "$FEATURE_DIR/user-spec.md" ]]; then
  sed -e "s/\[DATE\]/$TODAY/g" \
      -e "s/\[feature\/fix name\]/$FEATURE_NAME/g" \
      "$TEMPLATES_DIR/user-spec.md.template" > "$FEATURE_DIR/user-spec.md"
fi

# tech-spec.md (optional — tech-spec-planning skill will create/overwrite if needed)
if [[ ! -f "$FEATURE_DIR/tech-spec.md" ]] && [[ -f "$TEMPLATES_DIR/tech-spec.md.template" ]]; then
  sed -e "s/\[DATE\]/$TODAY/g" \
      "$TEMPLATES_DIR/tech-spec.md.template" > "$FEATURE_DIR/tech-spec.md"
fi

# decisions.md
if [[ ! -f "$FEATURE_DIR/decisions.md" ]]; then
  if [[ -f "$TEMPLATES_DIR/decisions.md.template" ]]; then
    sed -e "s/{Feature Name}/$FEATURE_NAME/g" \
        "$TEMPLATES_DIR/decisions.md.template" > "$FEATURE_DIR/decisions.md"
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

# checkpoint.yml (for feature-execution recovery after context compaction)
if [[ ! -f "$FEATURE_DIR/logs/checkpoint.yml" ]]; then
  if [[ -f "$TEMPLATES_DIR/checkpoint.yml.template" ]]; then
    sed -e "s/{feature}/$FEATURE_NAME/g" \
        "$TEMPLATES_DIR/checkpoint.yml.template" > "$FEATURE_DIR/logs/checkpoint.yml"
  fi
fi

if [[ "$EXISTED" == true ]]; then
  echo "Updated feature folder: $FEATURE_DIR/ (added missing structure)"
else
  echo "Created feature folder: $FEATURE_DIR/"
fi
