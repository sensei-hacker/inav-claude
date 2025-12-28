#!/bin/bash
#
# GPS Blackbox Test Wrapper
#
# Complete automated workflow for GPS altitude testing with blackbox logging.
# Combines SITL configuration, arming, and GPS injection into one command.
#
# USAGE:
#   ./run_gps_blackbox_test.sh <profile> <duration>
#
# ARGUMENTS:
#   profile   - Motion profile: climb, descent, hover, sine
#   duration  - Test duration in seconds (default: 60)
#
# EXAMPLES:
#   ./run_gps_blackbox_test.sh climb 60
#   ./run_gps_blackbox_test.sh hover 30
#
# WHAT IT DOES:
#   1. Checks if SITL is running (starts if needed)
#   2. Configures SITL for MSP receiver, blackbox, and ARM mode
#   3. Arms SITL and runs GPS altitude injection
#   4. Reports blackbox log location
#
# OUTPUT:
#   - GPS test log: /tmp/gps_test_<profile>.log
#   - Blackbox log: inav/build_sitl/YYYY_MM_DD_HHMMSS.TXT
#
# REQUIREMENTS:
#   - SITL built (inav/build_sitl/bin/SITL.elf)
#   - uNAVlib installed
#   - Python 3
#

set -e  # Exit on error

PROFILE="${1:-climb}"
DURATION="${2:-60}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SITL_DIR="$PROJECT_ROOT/inav/build_sitl"

echo "======================================================================"
echo "GPS Blackbox Test"
echo "======================================================================"
echo ""
echo "Profile:  $PROFILE"
echo "Duration: ${DURATION}s"
echo ""

# Check if SITL binary exists
if [ ! -f "$SITL_DIR/bin/SITL.elf" ]; then
    echo "✗ SITL not found at: $SITL_DIR/bin/SITL.elf"
    echo "  Build SITL first: cd inav/build_sitl && cmake -DSITL=ON .. && make -j4"
    exit 1
fi

# Check if SITL is running
if ! pgrep -x "SITL.elf" > /dev/null; then
    echo "SITL not running. Starting SITL..."
    cd "$SITL_DIR"
    ./bin/SITL.elf > /tmp/sitl.log 2>&1 &
    sleep 10
    echo "✓ SITL started"
else
    echo "✓ SITL already running"
fi

echo ""
echo "Step 1: Configuring SITL (MSP receiver, blackbox, ARM mode)..."
cd "$PROJECT_ROOT"

# Run configuration and arming test
if ! timeout 60 python3 claude/test_tools/inav/sitl/sitl_arm_test.py 5760 > /tmp/sitl_config.log 2>&1; then
    echo "✗ SITL configuration failed"
    echo "  See log: /tmp/sitl_config.log"
    exit 1
fi

echo "✓ SITL configured and armed"

# Enable blackbox (idempotent - safe to run multiple times)
python3 claude/test_tools/inav/gps/enable_blackbox.py > /dev/null 2>&1
python3 claude/test_tools/inav/gps/enable_blackbox_feature.py > /dev/null 2>&1

echo ""
echo "Step 2: Running GPS altitude injection ($PROFILE profile, ${DURATION}s)..."
echo ""

# Run GPS test immediately (must be within 200ms of arming or SITL disarms)
if ! timeout $((DURATION + 10)) python3 claude/test_tools/inav/gps/gps_with_rc_keeper.py \
    --profile "$PROFILE" \
    --duration "$DURATION" \
    2>&1 | tee "/tmp/gps_test_${PROFILE}.log"; then
    echo ""
    echo "✗ GPS test failed"
    echo "  See log: /tmp/gps_test_${PROFILE}.log"
    exit 1
fi

echo ""
echo "Step 3: Waiting for blackbox to flush..."
sleep 3

echo ""
echo "======================================================================"
echo "Test Complete"
echo "======================================================================"
echo ""

# Find blackbox log
cd "$SITL_DIR"
LATEST_LOG=$(ls -t 202*.TXT 2>/dev/null | head -1)

if [ -n "$LATEST_LOG" ]; then
    LOG_SIZE=$(ls -lh "$LATEST_LOG" | awk '{print $5}')
    echo "✓ Blackbox log created: $LATEST_LOG ($LOG_SIZE)"
    echo ""
    echo "To decode:"
    echo "  cd inav/build_sitl"
    echo "  blackbox_decode $LATEST_LOG"
    echo ""
    echo "To rename:"
    echo "  mv $LATEST_LOG ${PROFILE}_test.TXT"
else
    echo "⚠ No blackbox log found"
    echo "  Check if SITL actually armed (see GPS test log)"
    echo "  Check if BLACKBOX feature is enabled"
fi

echo ""
echo "Logs:"
echo "  GPS test:  /tmp/gps_test_${PROFILE}.log"
echo "  SITL:      /tmp/sitl.log"
echo "  Config:    /tmp/sitl_config.log"
echo ""
