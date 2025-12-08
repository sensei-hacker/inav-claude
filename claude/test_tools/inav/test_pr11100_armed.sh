#!/bin/bash
# Test PR#11100 CRSF BARO_ALT frames with arming and GPS altitude motion
#
# Run from the project root (inavflight directory)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "=== PR#11100 Armed Test ==="
echo

# Enable telemetry
echo "Enabling TELEMETRY feature..."
python3 "$PROJECT_ROOT/claude/developer/test_tools/enable_telemetry_feature.py" || exit 1

sleep 2

# Arm via MSP using arm_sitl.py script
echo
echo "Arming SITL..."
python3 "$SCRIPT_DIR/arm_sitl.py" || exit 1

sleep 2

# Start GPS injection in background
echo
echo "Starting GPS altitude injection (climb 0-100m over 60s)..."
python3 "$SCRIPT_DIR/gps/inject_gps_altitude.py" --profile climb --duration 60 > /tmp/pr11100_gps_armed.log 2>&1 &
GPS_PID=$!

sleep 2

# Start CRSF telemetry monitoring
echo "Starting CRSF telemetry monitoring..."
python3 "$SCRIPT_DIR/crsf/crsf_rc_sender.py" 2 --rate 50 --duration 60 --show-telemetry > /tmp/pr11100_crsf_armed.log 2>&1

# Wait for GPS to finish
wait $GPS_PID

echo
echo "=== Test Complete ==="
echo "GPS log: /tmp/pr11100_gps_armed.log"
echo "CRSF log: /tmp/pr11100_crsf_armed.log"
