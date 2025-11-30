#!/bin/bash
# Test MSP benchmark client against mock responder using virtual serial ports

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creating virtual serial port pair with socat..."
# Create virtual serial port pair
socat -d -d pty,raw,echo=0,link=/tmp/vserial1 pty,raw,echo=0,link=/tmp/vserial2 &
SOCAT_PID=$!

# Wait for ports to be created
sleep 2

if [ ! -e /tmp/vserial1 ] || [ ! -e /tmp/vserial2 ]; then
    echo "ERROR: Failed to create virtual serial ports"
    kill $SOCAT_PID 2>/dev/null
    exit 1
fi

echo "Virtual ports created: /tmp/vserial1 and /tmp/vserial2"
echo ""

# Start mock responder in background
echo "Starting mock responder on /tmp/vserial1..."
python3 "$SCRIPT_DIR/msp_mock_responder.py" /tmp/vserial1 115200 --verbose &
RESPONDER_PID=$!

# Give responder time to start
sleep 1

# Run benchmark test
echo ""
echo "Running benchmark test on /tmp/vserial2..."
echo ""
python3 "$SCRIPT_DIR/msp_benchmark_serial.py" /tmp/vserial2 115200

# Cleanup
echo ""
echo "Cleaning up..."
kill $RESPONDER_PID 2>/dev/null
kill $SOCAT_PID 2>/dev/null
rm -f /tmp/vserial1 /tmp/vserial2

echo "Test complete!"
