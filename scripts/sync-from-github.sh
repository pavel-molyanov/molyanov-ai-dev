#!/bin/bash

# Save working directory before any cd commands
WORKING_DIR="$PWD"

# Variables to collect status
META_STATUS=""
PROJECT_STATUS=""

# ============================================================================
# STEP 1: Sync ~/.claude meta-project
# ============================================================================

REPO_DIR="$HOME/.claude"
cd "$REPO_DIR"

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    META_STATUS="⚠️  ~/.claude has uncommitted changes (skipped sync)"
else
    # Check if we're behind remote
    git fetch origin main --quiet

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)

    if [ "$LOCAL" = "$REMOTE" ]; then
        META_STATUS="✓ ~/.claude is up to date"
    else
        # Check if we're behind, ahead, or diverged
        MERGE_BASE=$(git merge-base HEAD origin/main)

        if [ "$MERGE_BASE" = "$REMOTE" ]; then
            # We're ahead of remote (local has commits not pushed yet)
            META_STATUS="✓ ~/.claude is up to date"
        elif [ "$MERGE_BASE" = "$LOCAL" ]; then
            # We're behind remote (need to pull)
            if git pull origin main --quiet; then
                META_STATUS="✓ Synced ~/.claude from GitHub"
            else
                META_STATUS="✗ Failed to sync ~/.claude (run 'git pull' manually)"
            fi
        else
            # Branches have diverged (need merge)
            META_STATUS="⚠️  ~/.claude has diverged from GitHub (manual merge needed)"
        fi
    fi
fi

# ============================================================================
# STEP 2: Sync current project (if it's a git repository)
# ============================================================================

# Only sync if:
# 1. WORKING_DIR is not ~/.claude itself
# 2. WORKING_DIR is a git repository
if [ "$WORKING_DIR" != "$HOME/.claude" ] && [ -d "$WORKING_DIR/.git" ]; then
    cd "$WORKING_DIR"
    PROJECT_NAME=$(basename "$WORKING_DIR")

    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        PROJECT_STATUS="⚠️  $PROJECT_NAME has uncommitted changes (skipped sync)"
    else
        # Get current branch
        CURRENT_BRANCH=$(git branch --show-current)

        if [ -n "$CURRENT_BRANCH" ]; then
            # Check if we're behind remote
            if git fetch origin "$CURRENT_BRANCH" --quiet 2>/dev/null; then
                LOCAL=$(git rev-parse HEAD)
                REMOTE=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null)

                if [ -n "$REMOTE" ]; then
                    if [ "$LOCAL" = "$REMOTE" ]; then
                        PROJECT_STATUS="✓ $PROJECT_NAME is up to date"
                    else
                        # Check if we're behind, ahead, or diverged
                        MERGE_BASE=$(git merge-base HEAD "origin/$CURRENT_BRANCH" 2>/dev/null)

                        if [ -n "$MERGE_BASE" ]; then
                            if [ "$MERGE_BASE" = "$REMOTE" ]; then
                                # We're ahead of remote
                                PROJECT_STATUS="✓ $PROJECT_NAME is up to date"
                            elif [ "$MERGE_BASE" = "$LOCAL" ]; then
                                # We're behind remote (need to pull)
                                if git pull origin "$CURRENT_BRANCH" --quiet; then
                                    PROJECT_STATUS="✓ Synced $PROJECT_NAME from GitHub"
                                else
                                    PROJECT_STATUS="✗ Failed to sync $PROJECT_NAME (run 'git pull' manually)"
                                fi
                            else
                                # Branches have diverged
                                PROJECT_STATUS="⚠️  $PROJECT_NAME has diverged from GitHub (manual merge needed)"
                            fi
                        fi
                    fi
                fi
            fi
        fi
    fi
fi

# ============================================================================
# Output final message as JSON
# ============================================================================

# Build final message
if [ -n "$PROJECT_STATUS" ]; then
    FINAL_MESSAGE="$META_STATUS\n$PROJECT_STATUS"
else
    FINAL_MESSAGE="$META_STATUS"
fi

# Output JSON with systemMessage
cat <<EOF
{
  "systemMessage": "$FINAL_MESSAGE"
}
EOF

exit 0
