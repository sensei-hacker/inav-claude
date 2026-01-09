#!/bin/bash
# Start SITL or connect to existing instance
# Usage: start_sitl.sh [timeout_seconds]
#
# IMPORTANT: This script must run WITHOUT sandbox to connect to localhost.
# Claude Code sandbox blocks localhost network by default.
# Either run with dangerouslyDisableSandbox or add localhost to allowed hosts.

set -e

TIMEOUT=${1:-15}
PORT=5760
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITL_DIR="${SCRIPT_DIR}/../../../../inav/build_sitl"
SITL_BIN="${SITL_DIR}/bin/SITL.elf"
PID_FILE="/tmp/claude/sitl.pid"
LOG_FILE="/tmp/claude/sitl.log"

mkdir -p /tmp/claude

# Check if SITL binary exists
if [ ! -x "$SITL_BIN" ]; then
    echo "ERROR: SITL binary not found at $SITL_BIN"
    echo "Run: build-sitl skill or cd inav/build_sitl && cmake -DSITL=ON .. && make SITL.elf -j4"
    exit 1
fi

# Check if SITL is already running and accessible
if nc -z localhost $PORT 2>/dev/null; then
    echo "========================================="
    echo "SITL already running on port $PORT"
    echo "Connect: tcp://localhost:$PORT"
    echo "========================================="
    exit 0
fi

# Check if port is in use but not responding (zombie process?)
if ss -tln 2>/dev/null | grep -qE ":${PORT}\b"; then
    echo "Port $PORT is bound but not responding."
    echo ""

    # Try to find and kill SITL
    SITL_PIDS=$(pgrep -x "SITL.elf" 2>/dev/null || true)
    if [ -n "$SITL_PIDS" ]; then
        echo "Found SITL process(es): $SITL_PIDS"
        for pid in $SITL_PIDS; do
            echo "  Killing PID $pid..."
            kill -9 "$pid" 2>/dev/null || true
        done
        sleep 2
    else
        echo "========================================="
        echo "ERROR: Cannot find process holding port $PORT"
        echo ""
        echo "This may mean SITL is running outside this environment."
        echo ""
        echo "To fix, run in your terminal:"
        echo "    pkill -9 SITL.elf"
        echo ""
        echo "Or find and kill manually:"
        echo "    ps aux | grep SITL"
        echo "    kill -9 <PID>"
        echo "========================================="
        exit 1
    fi
fi

# Kill any previous SITL we started (from PID file)
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Killing previous SITL (PID $OLD_PID)..."
        kill -9 "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

# Start SITL
echo "Starting SITL from $SITL_DIR..."
cd "$SITL_DIR"
./bin/SITL.elf > "$LOG_FILE" 2>&1 &
SITL_PID=$!
echo "$SITL_PID" > "$PID_FILE"

# Wait for SITL to be ready
echo "Waiting for port $PORT (timeout: ${TIMEOUT}s)..."
for i in $(seq 1 $TIMEOUT); do
    # Check process is alive
    if ! kill -0 "$SITL_PID" 2>/dev/null; then
        echo ""
        echo "ERROR: SITL process died (was PID $SITL_PID)"
        echo ""
        echo "If running in sandbox, start SITL manually instead:"
        echo "    cd $SITL_DIR && ./bin/SITL.elf"
        echo ""
        echo "Log output:"
        cat "$LOG_FILE" 2>/dev/null
        rm -f "$PID_FILE"
        exit 1
    fi

    # Check port is listening AND responding
    if nc -z localhost $PORT 2>/dev/null; then
        echo ""
        echo "========================================="
        echo "SITL ready (PID: $SITL_PID, port: $PORT)"
        echo "Connect: tcp://localhost:$PORT"
        echo "Log: $LOG_FILE"
        echo "========================================="
        exit 0
    fi

    printf "."
    sleep 1
done

echo ""
echo "ERROR: Timeout waiting for SITL"
cat "$LOG_FILE" 2>/dev/null
exit 1
