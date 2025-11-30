#!/bin/bash
# Automated comparison test for MSP optimization

set -e

# Get script directory and infer project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
FIRMWARE_DIR="$PROJECT_ROOT/inav"

echo "========================================="
echo "MSP Optimization Comparison Test"
echo "========================================="
echo ""

# Test baseline
echo "Testing BASELINE binary..."
echo "Start SITL baseline in another terminal:"
echo "  cd $FIRMWARE_DIR && ./inav_SITL_baseline"
echo ""
read -p "Press Enter when SITL baseline is running..."

python3 "$SCRIPT_DIR/msp_benchmark.py" localhost 5761 > /tmp/baseline_results.txt
cat /tmp/baseline_results.txt
BASELINE_TIME=$(grep "Average time:" /tmp/baseline_results.txt | awk '{print $3}' | tr -d 's')

echo ""
echo "Stop baseline SITL and start optimized version."
echo "  Ctrl+C baseline, then: ./inav_SITL_optimized"
echo ""
read -p "Press Enter when SITL optimized is running..."

# Test optimized
echo ""
echo "Testing OPTIMIZED binary..."
python3 "$SCRIPT_DIR/msp_benchmark.py" localhost 5761 > /tmp/optimized_results.txt
cat /tmp/optimized_results.txt
OPTIMIZED_TIME=$(grep "Average time:" /tmp/optimized_results.txt | awk '{print $3}' | tr -d 's')

# Compare
echo ""
echo "========================================="
echo "COMPARISON"
echo "========================================="
echo "Baseline time:  ${BASELINE_TIME}s"
echo "Optimized time: ${OPTIMIZED_TIME}s"

# Calculate improvement using bc
IMPROVEMENT=$(echo "scale=2; (($BASELINE_TIME - $OPTIMIZED_TIME) / $BASELINE_TIME) * 100" | bc)
echo "Improvement:    ${IMPROVEMENT}%"
echo "========================================="
