#!/bin/bash

# Hook: Kill old Next.js dev servers before starting a new one
# Purpose: Prevent multiple Next.js servers running simultaneously on port 3000

# Read the command that's about to be executed from stdin
read -r COMMAND

# Check if the command contains npm run dev or next dev
if echo "$COMMAND" | grep -qE "(npm run dev|next dev|pnpm dev|yarn dev)"; then
    echo "🔄 [Hook] Detected dev server start command"
    echo "🔄 [Hook] Checking for existing Next.js processes and port 3000..."

    # First, aggressively kill anything on port 3000
    if ss -tlnp 2>/dev/null | grep -q ":3000 "; then
        echo "⚠️  [Hook] Port 3000 is occupied, force killing..."

        # Try multiple methods to kill port 3000
        lsof -ti:3000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
        fuser -k 3000/tcp 2>/dev/null || true

        # Also kill by process name pattern
        pkill -9 -f "next-server.*3000" 2>/dev/null || true

        sleep 1
        echo "   Killed processes on port 3000"
    fi

    # Find and kill all Next.js dev server processes
    echo "🔄 [Hook] Killing all Next.js processes..."

    # Kill all Next.js related processes with force
    pkill -9 -f "next-dev" 2>/dev/null || true
    pkill -9 -f "npm.*run dev" 2>/dev/null || true
    pkill -9 -f "pnpm.*dev" 2>/dev/null || true
    pkill -9 -f "yarn.*dev" 2>/dev/null || true
    pkill -9 -f "node.*next" 2>/dev/null || true
    pkill -9 -f "next-server" 2>/dev/null || true

    # Wait for processes to fully terminate
    sleep 1.5

    # Final check - if port 3000 is STILL occupied, kill it again
    if ss -tlnp 2>/dev/null | grep -q ":3000 "; then
        echo "⚠️  [Hook] Port 3000 STILL occupied after cleanup, trying harder..."
        lsof -ti:3000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
        fuser -k -9 3000/tcp 2>/dev/null || true
        sleep 1
    fi

    # Verify port 3000 is free
    if ss -tlnp 2>/dev/null | grep -q ":3000 "; then
        echo "❌ [Hook] ERROR: Failed to free port 3000!"
        echo "   Manual intervention required: sudo lsof -ti:3000 | xargs kill -9"
    else
        echo "✅ [Hook] Port 3000 is free, all old dev servers stopped"
    fi

    # Force PORT=3000 if not already set in the command
    if ! echo "$COMMAND" | grep -q "PORT=3000"; then
        echo "🔧 [Hook] Setting PORT=3000 for dev server"
        export PORT=3000
    fi

    echo "🚀 [Hook] Ready to start new dev server on port 3000"
fi

# Always allow the command to proceed
exit 0
