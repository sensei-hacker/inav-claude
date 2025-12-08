#!/bin/bash
#
# Motion Simulator Test Wrapper
#
# This script orchestrates the motion simulation test by:
# 1. Starting the CRSF RC sender (keeps SITL active + receives telemetry)
# 2. Starting GPS altitude injection via MSP (separate script)
# 3. Waiting for both to complete
# 4. Displaying telemetry results
#

PROFILE="${1:-climb}"
DURATION="${2:-20}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================================================"
echo "CRSF Telemetry Motion Simulator Test"
echo "======================================================================"
echo ""
echo "Profile: $PROFILE"
echo "Duration: ${DURATION}s"
echo ""

# Start CRSF RC sender in background (handles telemetry)
echo "Starting CRSF RC sender (port 5761)..."
cd "$SCRIPT_DIR"
python3 crsf_rc_sender.py 2 --rate 50 --duration $DURATION --show-telemetry > /tmp/motion_test_telemetry.log 2>&1 &
RC_PID=$!

# Give RC sender time to connect and start receiving telemetry
echo "Waiting for CRSF connection to establish..."
sleep 3

if ! ps -p $RC_PID > /dev/null; then
    echo "✗ RC sender failed to start"
    exit 1
fi

echo "✓ RC sender started (PID: $RC_PID)"
echo ""

# Start GPS altitude injection in background (separate MSP connection)
echo "Starting GPS altitude injection..."
python3 "$SCRIPT_DIR/inject_gps_altitude.py" --profile "$PROFILE" --duration $DURATION > /tmp/motion_test_gps_injection.log 2>&1 &
GPS_PID=$!

echo "✓ GPS injection started (PID: $GPS_PID)"
echo ""
echo "Running motion simulation for ${DURATION}s..."
echo "(View live telemetry: tail -f /tmp/motion_test_telemetry.log)"
echo ""

# Wait for both processes to complete
wait $RC_PID
RC_STATUS=$?

wait $GPS_PID
GPS_STATUS=$?

echo ""
echo "======================================================================"
echo "Test Complete"
echo "======================================================================"
echo ""

if [ $RC_STATUS -eq 0 ]; then
    echo "✓ CRSF RC sender completed successfully"
else
    echo "✗ CRSF RC sender failed (exit code: $RC_STATUS)"
fi

if [ $GPS_STATUS -eq 0 ]; then
    echo "✓ GPS injection completed successfully"
else
    echo "✗ GPS injection failed (exit code: $GPS_STATUS)"
fi

echo ""
echo "======================================================================"
echo "Telemetry Results"
echo "======================================================================"
echo ""
tail -40 /tmp/motion_test_telemetry.log

echo ""
echo "======================================================================"
echo "GPS Injection Log"
echo "======================================================================"
echo ""
tail -20 /tmp/motion_test_gps_injection.log

echo ""
echo "Full logs saved to:"
echo "  Telemetry: /tmp/motion_test_telemetry.log"
echo "  GPS:       /tmp/motion_test_gps_injection.log"
echo ""
