#!/bin/bash
# Build, run, and wait for SITL to be ready
# Usage: build_run_sitl.sh [timeout_seconds] [port]
#
# This script:
# 1. Builds SITL (if needed)
# 2. Kills any existing SITL process
# 3. Starts SITL in background
# 4. Waits for it to be ready on the specified port
#
# Default timeout: 30 seconds (includes build time)
# Default port: 5761 (UART2, commonly used for MSP)

set -e

TIMEOUT=${1:-30}
PORT=${2:-5761}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INAV_DIR="${SCRIPT_DIR}/../../../../inav"
BUILD_DIR="${INAV_DIR}/build_sitl"

echo "=== SITL Build & Run Script ==="

# Step 1: Build SITL
echo "[1/4] Building SITL..."
cd "$BUILD_DIR"

# Check if cmake has been run
if [ ! -f CMakeCache.txt ]; then
    echo "  Running cmake..."
    cmake -DSITL=ON ..
fi

# Build
make -j$(nproc) 2>&1 | tail -5
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi
echo "  Build complete."

# Step 2: Kill existing SITL
echo "[2/4] Stopping any existing SITL..."
pkill -f "SITL.elf" 2>/dev/null || true
sleep 1

# Step 3: Start SITL
echo "[3/4] Starting SITL..."
./bin/SITL.elf > /tmp/claude/sitl.log 2>&1 &
SITL_PID=$!
echo "  SITL PID: $SITL_PID"

# Step 4: Wait for SITL to be ready
echo "[4/4] Waiting for SITL on port $PORT (timeout: ${TIMEOUT}s)..."
for i in $(seq 1 $TIMEOUT); do
    if ss -tln | grep -q ":$PORT "; then
        echo "  SITL ready on port $PORT after ${i}s"
        echo ""
        echo "=== SITL is running ==="
        echo "PID: $SITL_PID"
        echo "Log: /tmp/claude/sitl.log"
        echo "Connect via: tcp://127.0.0.1:5760"
        exit 0
    fi

    # Check if process died
    if ! kill -0 $SITL_PID 2>/dev/null; then
        echo "ERROR: SITL process died"
        echo "Log output:"
        cat /tmp/claude/sitl.log
        exit 1
    fi

    sleep 1
done

echo "ERROR: Timeout waiting for SITL on port $PORT"
echo "Log output:"
tail -20 /tmp/claude/sitl.log
exit 1
