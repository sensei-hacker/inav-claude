#!/bin/bash
#
# CRSF Telemetry Test with GPS Altitude Motion
#
# This script tests the BAROMETER_ALT_VARIO frame (0x09) from PR #11100
# with simulated GPS altitude changes to verify altitude tracking.
#
# Usage:
#   ./test_crsf_telemetry_with_gps.sh [build_directory] [gps_profile]
#
# Parameters:
#   gps_profile  - GPS motion profile: climb, descent, hover, sine (default: climb)

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
GPS_SCRIPT="$SCRIPT_DIR/../gps/inject_gps_altitude.py"
BUILD_DIR="${1:-build_sitl_pr11100}"
INAV_ROOT="$PROJECT_ROOT/inav"
SITL_BIN="$INAV_ROOT/$BUILD_DIR/bin/SITL.elf"
SITL_LOG="/tmp/sitl_pr11100_gps.log"
RC_SENDER_SCRIPT="$SCRIPT_DIR/crsf_rc_sender.py"
GPS_PROFILE="${2:-climb}"
TEST_DURATION=30

echo "======================================================================"
echo "PR #11100 CRSF Telemetry Test with GPS Motion"
echo "======================================================================"
echo ""
echo "Configuration:"
echo "  Build Dir:   $BUILD_DIR"
echo "  GPS Profile: $GPS_PROFILE"
echo "  Duration:    ${TEST_DURATION}s"
echo ""

# Step 1: Verify binaries exist
echo "[1/8] Verifying prerequisites..."
if [ ! -f "$SITL_BIN" ]; then
    echo "ERROR: SITL binary not found: $SITL_BIN"
    exit 1
fi
if [ ! -f "$GPS_SCRIPT" ]; then
    echo "ERROR: GPS injection script not found: $GPS_SCRIPT"
    exit 1
fi
echo "OK SITL binary and GPS script found"

# Step 2: Cleanup
echo ""
echo "[2/8] Cleaning up existing processes..."
pkill -9 SITL.elf 2>/dev/null || true
pkill -9 -f crsf_rc_sender 2>/dev/null || true
pkill -9 -f inject_gps 2>/dev/null || true
sleep 2
echo "OK Cleanup complete"

# Step 3: Start SITL
echo ""
echo "[3/8] Starting SITL..."
cd "$INAV_ROOT/$BUILD_DIR"
# rm -f eeprom.bin
./bin/SITL.elf > "$SITL_LOG" 2>&1 &
# ( ./bin/SITL.elf 2>&1 | egrep -v 'Program word' > $SITL_LOG ) &
SITL_PID=$!
sleep 4

if ! pgrep -x SITL.elf > /dev/null; then
    echo "ERROR: SITL failed to start"
    tail -20 "$SITL_LOG"
    exit 1
fi
echo "OK SITL started"

# Step 4: Configure CRSF and TELEMETRY
echo ""
echo "[4/8] Configuring CRSF and TELEMETRY..."
python3 "$SCRIPT_DIR/configure_sitl_crsf.py" --no-reboot
if [ $? -ne 0 ]; then
    echo "ERROR: Configuration failed"
    pkill -9 SITL.elf
    exit 1
fi

# Step 5: Start RC sender BEFORE reboot (brief, just for init)
echo ""
echo "[5/8] Starting RC sender briefly for CRSF init..."
python3 "$RC_SENDER_SCRIPT" 2 --rate 50 --duration 3 > /tmp/rc_sender_gps_test.log 2>&1 &
RC_PID=$!
sleep 2

if ! pgrep -f crsf_rc_sender > /dev/null; then
    echo "WARNING: RC sender may have already completed"
fi
echo "OK RC sender started (PID: $RC_PID)"

# Step 6: Reboot SITL
echo ""
echo "[6/8] Rebooting SITL..."
python3 "$SCRIPT_DIR/reboot_sitl.py"
sleep 8

if ! pgrep -x SITL.elf > /dev/null; then
    echo "ERROR: SITL died after reboot"
    pkill -9 SITL.elf
    exit 1
fi

# Verify UART2 is bound
if ! grep -q "Bind TCP.*5761" "$SITL_LOG"; then
    echo "ERROR: UART2 not bound"
    tail -30 "$SITL_LOG"
    pkill -9 SITL.elf
    exit 1
fi
echo "OK SITL rebooted (UART2 on port 5761)"

# Step 6b: Enable HITL mode (must be done after every boot)
echo ""
echo "[6b/8] Enabling HITL mode for arming..."
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from configure_sitl_crsf import enable_hitl_mode
enable_hitl_mode(5760)
"
if [ $? -ne 0 ]; then
    echo "WARNING: HITL mode may not have been enabled"
fi

# Step 7: Start GPS altitude injection
echo ""
echo "[7/8] Starting GPS altitude injection ($GPS_PROFILE profile)..."
python3 "$GPS_SCRIPT" --profile "$GPS_PROFILE" --duration "$TEST_DURATION" > /tmp/gps_injection.log 2>&1 &
GPS_PID=$!
sleep 2

if ! pgrep -f inject_gps > /dev/null; then
    echo "WARNING: GPS injection may have failed"
    cat /tmp/gps_injection.log
fi
echo "OK GPS injection running (PID: $GPS_PID)"

# Step 8: Capture and analyze telemetry using the library
echo ""
echo "[8/8] Capturing CRSF telemetry for ${TEST_DURATION}s..."
echo "      (using test_pr11100_telemetry.py with arming + error checking)"
echo ""

# Use the Python test library (imports from crsf_rc_sender.py for validation)
python3 "$SCRIPT_DIR/test_pr11100_telemetry.py" --port 5761 --duration "$TEST_DURATION"

TEST_RESULT=$?

# Cleanup
echo ""
echo "Cleanup..."
pkill -9 -f crsf_rc_sender 2>/dev/null || true
pkill -9 -f inject_gps 2>/dev/null || true
pkill -9 SITL.elf 2>/dev/null || true
echo "OK Processes stopped"

# Show GPS injection log
echo ""
echo "GPS Injection Log:"
cat /tmp/gps_injection.log 2>/dev/null | head -20

echo ""
echo "======================================================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo "TEST PASSED: PR #11100 altitude tracking verified!"
else
    echo "TEST INCOMPLETE: Altitude tracking needs verification"
fi
echo "======================================================================"

exit $TEST_RESULT
