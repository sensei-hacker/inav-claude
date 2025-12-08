#!/bin/bash
#
# CRSF Telemetry Test Script for INAV SITL
#
# This script automates the complete workflow for testing CRSF telemetry frames.
#
# Usage:
#   ./test_crsf_telemetry.sh [build_dir] [test_mode]
#
# Parameters:
#   build_dir  - SITL build directory (default: build_sitl)
#   test_mode  - Test mode: pr11025, pr11100, merged, or baseline (default: baseline)
#
# Examples:
#   ./test_crsf_telemetry.sh build_sitl_pr11025 pr11025
#   ./test_crsf_telemetry.sh build_sitl_pr11100 pr11100
#   ./test_crsf_telemetry.sh build_sitl_merged merged    # Tests all 4 new frames
#   ./test_crsf_telemetry.sh build_sitl baseline
#
# Prerequisite: Enable telemetry using claude/test_tools/inav/crsf/configure_sitl_crsf.py

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
BUILD_DIR="${1:-build_sitl}"
TEST_MODE="${2:-baseline}"
INAV_ROOT="$PROJECT_ROOT/inav"
SITL_BIN="$INAV_ROOT/$BUILD_DIR/bin/SITL.elf"
SITL_LOG="/tmp/sitl_crsf_${TEST_MODE}.log"
RC_SENDER_SCRIPT="$SCRIPT_DIR/crsf_rc_sender.py"
TEST_DURATION="${3:-10}"  # seconds (can be overridden by 3rd argument)

echo "======================================================================"
echo "CRSF Telemetry Test Script"
echo "======================================================================"
echo ""
echo "Configuration:"
echo "  INAV Root:   $INAV_ROOT"
echo "  Build Dir:   $BUILD_DIR"
echo "  Test Mode:   $TEST_MODE"
echo "  SITL Binary: $SITL_BIN"
echo ""

# Step 1: Verify SITL binary exists
echo "[1/7] Verifying SITL binary..."
if [ ! -f "$SITL_BIN" ]; then
    echo "✗ SITL binary not found: $SITL_BIN"
    echo "  Please build SITL first with CRSF enabled:"
    echo "    cd $INAV_ROOT"
    echo "    mkdir -p $BUILD_DIR && cd $BUILD_DIR"
    echo "    # Edit src/main/target/SITL/target.h line ~97:"
    echo "    # Comment out: // #undef USE_TELEMETRY_CRSF"
    echo "    cmake -DSITL=ON .."
    echo "    make -j4"
    exit 1
fi

# Verify CRSF telemetry symbols in binary
if ! nm "$SITL_BIN" | grep -q "crsfRxSendTelemetryData"; then
    echo "✗ CRSF telemetry not compiled into SITL"
    echo "  Please rebuild with CRSF enabled (see above)"
    exit 1
fi
echo "✓ SITL binary found with CRSF telemetry support"

# Step 2: Kill existing SITL instances
echo ""
echo "[2/7] Cleaning up existing processes..."
pkill -9 SITL.elf 2>/dev/null || true
pkill -9 -f crsf_rc_sender 2>/dev/null || true
sleep 1
echo "✓ Cleanup complete"

# Step 3: Start SITL
echo ""
echo "[3/7] Starting SITL..."
cd "$INAV_ROOT/$BUILD_DIR"
# rm -f eeprom.bin  # Start fresh
rm -f "$SITL_LOG"
# ./bin/SITL.elf | egrep -v 'Program word' > "$SITL_LOG" 2>&1 &
( ./bin/SITL.elf 2>&1 | egrep -v 'Program word' > $SITL_LOG ) &
# SITL_PID=$!
# echo "  SITL PID: $SITL_PID"
sleep 3

# Verify SITL is running
if ! pgrep -x SITL.elf > /dev/null; then
    echo "✗ SITL failed to start"
    echo "  Log output:"
    tail -20 "$SITL_LOG"
    exit 1
fi

# Check for UART1 binding (MSP port 5760) using ss instead of log parsing
if ! ss -tlnp 2>/dev/null | grep -q ":5760"; then
    echo "✗ SITL didn't bind UART1 (port 5760 not listening)"
    tail -20 "$SITL_LOG"
    exit 1
fi
echo "✓ SITL started (UART1 on port 5760)"

# Step 4: Configure CRSF and TELEMETRY (without auto-reboot)
echo ""
echo "[4/7] Configuring CRSF and TELEMETRY..."
python3 "$SCRIPT_DIR/configure_sitl_crsf.py" --no-reboot
if [ $? -ne 0 ]; then
    echo "✗ CRSF/TELEMETRY configuration failed"
    pkill -9 SITL.elf
    exit 1
fi

# Start RC sender BEFORE reboot so crsfRxIsActive() sees it during init
echo ""
echo "[5/7] Starting RC sender (before reboot)..."
python3 "$RC_SENDER_SCRIPT" 2 --rate 50 --show-telemetry > /tmp/rc_sender.log 2>&1 &
RC_PID=$!
sleep 2

if ! pgrep -f crsf_rc_sender > /dev/null; then
    echo "✗ RC sender failed to start"
    cat /tmp/rc_sender.log
    pkill -9 SITL.elf
    exit 1
fi
echo "✓ RC sender running (PID $RC_PID)"

# Now reboot SITL (which will call initCrsfTelemetry with RC active)
echo ""
echo "[6/7] Rebooting SITL..."
python3 "$SCRIPT_DIR/reboot_sitl.py"

# Wait for SITL to reboot and apply configuration
sleep 8

# Verify SITL is still running after reboot
if ! pgrep -x SITL.elf > /dev/null; then
    echo "✗ SITL died after reboot"
    tail -20 "$SITL_LOG"
    pkill -9 SITL.elf
    exit 1
fi

# Verify UART2 is bound (CRSF config was saved before reboot) using ss
if ! ss -tlnp 2>/dev/null | grep -q ":5761"; then
    echo "✗ UART2 not bound (port 5761 not listening)"
    echo "  This means CRSF configuration didn't work"
    echo "  Log output:"
    tail -30 "$SITL_LOG"
    pkill -9 SITL.elf
    exit 1
fi
echo "✓ SITL rebooted (UART2 on port 5761)"

# Step 7: Test telemetry using the library (RC sender already running from before reboot)
echo ""
echo "[7/7] Testing CRSF telemetry..."
echo "  Test mode: $TEST_MODE"
echo "  Duration: ${TEST_DURATION}s"
echo "  (using test_crsf_frames.py with arming + error checking)"
echo ""

# Use the Python test library (imports from crsf_rc_sender.py for validation)
python3 "$SCRIPT_DIR/test_crsf_frames.py" --port 5761 --duration "$TEST_DURATION" --mode "$TEST_MODE"

TEST_RESULT=$?

# Step 7: Cleanup
echo ""
echo "[7/7] Cleanup..."
pkill -9 -f crsf_rc_sender 2>/dev/null || true
pkill -9 SITL.elf 2>/dev/null || true
echo "✓ Processes stopped"

echo ""
echo "======================================================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo "TEST PASSED: All CRSF telemetry frames verified!"
else
    echo "TEST FAILED: Some frames missing or invalid"
    echo "  Check logs:"
    echo "    SITL: $SITL_LOG"
    echo "    RC:   /tmp/rc_sender.log"
fi
echo "======================================================================"

exit $TEST_RESULT
