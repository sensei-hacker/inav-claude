#!/bin/bash
# Test script to interact with SITL CLI and test align_mag_roll

cd /home/raymorris/Documents/planes/inavflight/build_sitl/bin

# Kill any existing SITL instances
pkill -9 SITL.elf 2>/dev/null

# Start SITL in background
./SITL.elf > /tmp/sitl_output.txt 2>&1 &
SITL_PID=$!

echo "SITL started with PID $SITL_PID"
sleep 2

# Send CLI commands via echo and nc (if websocket is available)
# Or we can use a file-based approach

# Try sending commands directly to stdin
{
    sleep 1
    echo "#"
    sleep 1
    echo "get align_mag_roll"
    sleep 1
    echo "set align_mag_roll=900"
    sleep 1
    echo "set align_mag_roll = 1800"
    sleep 1
    echo "get align_mag_roll"
    sleep 1
    echo "exit"
    sleep 2
} | nc localhost 5761 > /tmp/cli_output.txt 2>&1 &

sleep 5

# Kill SITL
kill $SITL_PID 2>/dev/null

# Show results
echo "=== SITL Output ==="
cat /tmp/sitl_output.txt

echo ""
echo "=== CLI Output ==="
cat /tmp/cli_output.txt

echo ""
echo "=== Analysis ==="
if grep -q "Invalid name" /tmp/cli_output.txt /tmp/sitl_output.txt; then
    echo "❌ FOUND 'Invalid name' error!"
    grep -n "Invalid name" /tmp/cli_output.txt /tmp/sitl_output.txt
else
    echo "✓ No 'Invalid name' error found"
fi

if grep -q "align_mag_roll" /tmp/cli_output.txt /tmp/sitl_output.txt; then
    echo "✓ Setting 'align_mag_roll' found"
    grep -n "align_mag_roll" /tmp/cli_output.txt /tmp/sitl_output.txt
else
    echo "⚠ Setting 'align_mag_roll' NOT found"
fi
