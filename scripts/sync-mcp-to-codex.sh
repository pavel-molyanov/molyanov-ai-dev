#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "${1:-}" = "--daemon" ]; then
  INTERVAL_SECONDS="${MCP_SYNC_INTERVAL_SECONDS:-600}"
  mkdir -p "$HOME/.claude/.sync" "$HOME/.claude/logs"
  while true; do
    flock -n "$HOME/.claude/.sync/sync-mcp-to-codex.lock" \
      "$SCRIPT_DIR/sync-mcp-to-codex.sh" --apply --prune --quiet \
      >> "$HOME/.claude/logs/sync-mcp-to-codex.log" 2>&1 || true
    sleep "$INTERVAL_SECONDS"
  done
fi

if [ "${1:-}" = "--install-daemon" ]; then
  mkdir -p "$HOME/.claude/.sync" "$HOME/.claude/logs"
  PID_FILE="$HOME/.claude/.sync/sync-mcp-to-codex.pid"
  TMUX_SESSION="claude-mcp-sync"
  if command -v tmux >/dev/null 2>&1; then
    if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
      echo "MCP sync daemon already running in tmux session: $TMUX_SESSION"
      exit 0
    fi
    tmux new-session -d -s "$TMUX_SESSION" "$SCRIPT_DIR/sync-mcp-to-codex.sh --daemon"
    tmux display-message -p -t "$TMUX_SESSION" '#{pane_pid}' > "$PID_FILE"
    echo "Installed MCP sync daemon in tmux session '$TMUX_SESSION': every 10 minutes."
    exit 0
  fi

  if [ -s "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "MCP sync daemon already running: $(cat "$PID_FILE")"
    exit 0
  fi
  setsid "$SCRIPT_DIR/sync-mcp-to-codex.sh" --daemon >/dev/null 2>&1 < /dev/null &
  echo "$!" > "$PID_FILE"
  echo "Installed MCP sync daemon: every 10 minutes."
  exit 0
fi

if [ "${1:-}" = "--install-cron" ]; then
  if ! command -v crontab >/dev/null 2>&1; then
    exec "$SCRIPT_DIR/sync-mcp-to-codex.sh" --install-daemon
  fi

  CRON_ID="# claude-to-codex-mcp-sync"
  CRON_LINE="*/10 * * * * mkdir -p \"\$HOME/.claude/.sync\" \"\$HOME/.claude/logs\" && flock -n \"\$HOME/.claude/.sync/sync-mcp-to-codex.lock\" \"$SCRIPT_DIR/sync-mcp-to-codex.sh\" --apply --prune --quiet >> \"\$HOME/.claude/logs/sync-mcp-to-codex.log\" 2>&1 $CRON_ID"
  TMP_CRON="$(mktemp)"
  trap 'rm -f "$TMP_CRON"' EXIT

  crontab -l 2>/dev/null | grep -vF "$CRON_ID" > "$TMP_CRON" || true
  printf '%s\n' "$CRON_LINE" >> "$TMP_CRON"
  if ! crontab "$TMP_CRON"; then
    echo "warning: cron install failed; falling back to background daemon" >&2
    exec "$SCRIPT_DIR/sync-mcp-to-codex.sh" --install-daemon
  fi
  echo "Installed MCP sync cron: every 10 minutes."
  exit 0
fi

exec python3 "$SCRIPT_DIR/sync-mcp-to-codex.py" "$@"
