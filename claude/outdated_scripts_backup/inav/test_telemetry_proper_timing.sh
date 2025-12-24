#!/bin/bash
# Test CRSF Telemetry with Proper Timing
# Start RC sender WHILE SITL is booting so RC frames are active during initialization

cd ~/Documents/planes/inavflight/inav/build_sitl_crsf

echo "========================================================================"
echo "CRSF TELEMETRY TEST - RC SENDER STARTS DURING SITL BOOT"
echo "========================================================================"
echo

# Step 1: Start SITL in background
echo "[1/3] Starting SITL..."
./bin/SITL.elf 2>&1 | tee /tmp/sitl_telemetry_test.log &
SITL_PID=$!
echo "  SITL PID: $SITL_PID"
echo

# Step 2: Wait 1 second for SITL to start binding ports
sleep 1

# Step 3: Start RC sender (it will retry connecting to port 5761)
echo "[2/3] Starting RC sender (will retry until port 5761 is ready)..."
cd ~/Documents/planes/inavflight/inav
python3 crsf_rc_sender.py 2 --rate 50 > /tmp/rc_sender_timing.log 2>&1 &
RC_PID=$!
echo "  RC sender PID: $RC_PID"
echo

# Step 4: Wait for SITL to complete initialization
echo "[3/3] Waiting 8 seconds for SITL to complete initialization..."
sleep 8
echo

echo "========================================================================"
echo "INITIALIZATION COMPLETE"
echo "========================================================================"
echo

# Check if both processes are running
echo "Process status:"
ps -p $SITL_PID > /dev/null && echo "  ✓ SITL running (PID: $SITL_PID)" || echo "  ✗ SITL died"
ps -p $RC_PID > /dev/null && echo "  ✓ RC sender running (PID: $RC_PID)" || echo "  ✗ RC sender died"
echo

# Check for telemetry initialization
echo "Telemetry initialization:"
grep "\[CRSF TELEM\]" /tmp/sitl_telemetry_test.log | head -10
echo

# Check ports
echo "Listening ports:"
ss -tlnp 2>/dev/null | grep -E "5760|5761"
echo

echo "========================================================================"
echo "Monitor telemetry frames:"
echo "  python3 crsf_stream_parser.py 2"
echo
echo "View SITL log:"
echo "  tail -f /tmp/sitl_telemetry_test.log"
echo
echo "View RC sender log:"
echo "  tail -f /tmp/rc_sender_timing.log"
echo "========================================================================"
