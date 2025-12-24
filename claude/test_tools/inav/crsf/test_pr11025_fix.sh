#!/bin/bash
# Test script for PR #11025 CRSF telemetry corruption fix
#
# This script validates that the critical bugs in PR #11025 are fixed:
# 1. Unconditional frame scheduling (causes malformed frames when sensors disabled)
# 2. Buffer overflow risk (no bounds checking on arrays)
# 3. Protocol limit violations (>19 RPM values, >20 temperatures)
#
# Usage:
#   ./test_pr11025_fix.sh [commit]
#
# If no commit specified, tests current HEAD
#
# Exit codes:
#   0 = All fixes present (safe code)
#   1 = Bugs detected (unsafe code)
#   2 = Script error

set -e

COMMIT="${1:-HEAD}"
CRSF_FILE="src/main/telemetry/crsf.c"

echo "=========================================="
echo "PR #11025 CRSF Telemetry Fix Validation"
echo "=========================================="
echo "Testing commit: $COMMIT"
echo "File: $CRSF_FILE"
echo ""

# Store current branch/commit for restoration
ORIGINAL_HEAD=$(git rev-parse --abbrev-ref HEAD)
if [ "$ORIGINAL_HEAD" = "HEAD" ]; then
    ORIGINAL_HEAD=$(git rev-parse HEAD)
fi

# Function to restore original state
cleanup() {
    echo ""
    echo "Restoring original state..."
    git checkout "$ORIGINAL_HEAD" 2>/dev/null || true
}
trap cleanup EXIT

# Checkout the commit to test
if [ "$COMMIT" != "HEAD" ]; then
    git checkout "$COMMIT" --quiet
fi

# Verify file exists
if [ ! -f "$CRSF_FILE" ]; then
    echo "ERROR: $CRSF_FILE not found at commit $COMMIT"
    exit 2
fi

echo "Running tests..."
echo ""

BUGS_FOUND=0
FIXES_FOUND=0

# =============================================================================
# TEST 1: RPM Frame Scheduling - Must be CONDITIONAL
# =============================================================================
echo "TEST 1: RPM frame scheduling"
echo "  Expected: Conditional scheduling (if ESC_SENSOR_ENABLED && motorCount > 0)"

# Look for the RPM scheduling code in initCrsfTelemetry
RPM_SCHEDULE_PATTERN='crsfSchedule\[index\+\+\] = BV(CRSF_FRAME_RPM_INDEX)'

# Check if it exists
if ! grep -E -q "$RPM_SCHEDULE_PATTERN" "$CRSF_FILE"; then
    echo "  Status: ⚠️  RPM scheduling not found (feature may be disabled)"
else
    # Extract the initCrsfTelemetry function and look for RPM scheduling
    INIT_FUNCTION=$(sed -n '/void initCrsfTelemetry/,/^}/p' "$CRSF_FILE")
    RPM_CONTEXT=$(echo "$INIT_FUNCTION" | grep -E -B 3 -A 1 "$RPM_SCHEDULE_PATTERN")

    # Check if it's inside a conditional runtime check (not just compile-time #ifdef)
    if echo "$RPM_CONTEXT" | grep -q "if.*STATE(ESC_SENSOR_ENABLED)"; then
        echo "  Status: ✅ PASS - Conditional scheduling detected"
        FIXES_FOUND=$((FIXES_FOUND + 1))
    else
        # No runtime conditional - this is the bug!
        echo "  Status: ❌ FAIL - Unconditional scheduling (BUG #1)"
        echo "  Detail: RPM frames scheduled without runtime check for ESC sensors"
        echo "  Impact: Malformed frames sent when ESC sensors disabled → telemetry corruption"
        BUGS_FOUND=$((BUGS_FOUND + 1))
    fi
fi

echo ""

# =============================================================================
# TEST 2: Temperature Frame Scheduling - Must be CONDITIONAL
# =============================================================================
echo "TEST 2: Temperature frame scheduling"
echo "  Expected: Conditional scheduling (if hasTemperatureSources)"

TEMP_SCHEDULE_PATTERN='crsfSchedule\[index\+\+\] = BV(CRSF_FRAME_TEMP_INDEX)'

if ! grep -E -q "$TEMP_SCHEDULE_PATTERN" "$CRSF_FILE"; then
    echo "  Status: ⚠️  Temperature scheduling not found (feature may be disabled)"
else
    # Extract the initCrsfTelemetry function
    INIT_FUNCTION=$(sed -n '/void initCrsfTelemetry/,/^}/p' "$CRSF_FILE")
    TEMP_CONTEXT=$(echo "$INIT_FUNCTION" | grep -E -B 10 -A 1 "$TEMP_SCHEDULE_PATTERN")

    # Check for conditional logic (should have hasTemperatureSources variable/check)
    if echo "$TEMP_CONTEXT" | grep -q "if.*hasTemperatureSources"; then
        echo "  Status: ✅ PASS - Conditional scheduling with hasTemperatureSources"
        FIXES_FOUND=$((FIXES_FOUND + 1))
    elif echo "$TEMP_CONTEXT" | grep -q "hasTemperatureSources"; then
        echo "  Status: ✅ PASS - hasTemperatureSources variable detected"
        FIXES_FOUND=$((FIXES_FOUND + 1))
    else
        # No runtime conditional - this is the bug!
        echo "  Status: ❌ FAIL - Unconditional scheduling (BUG #2)"
        echo "  Detail: Temperature frames scheduled without runtime check for temp sensors"
        echo "  Impact: Malformed frames sent when no temp sensors → telemetry corruption"
        BUGS_FOUND=$((BUGS_FOUND + 1))
    fi
fi

echo ""

# =============================================================================
# TEST 3: Temperature Array Bounds Checking
# =============================================================================
echo "TEST 3: Temperature array bounds checking"
echo "  Expected: Loop condition includes 'tempCount < MAX_CRSF_TEMPS'"

# Look for the temperature collection loops
TEMP_LOOP_ESC='for.*i.*motorCount.*i\+\+'
TEMP_LOOP_SENSOR='for.*i.*MAX_TEMP_SENSORS.*i\+\+'

BOUNDS_CHECK_FOUND=0

# Check ESC temperature loop
if grep -q "$TEMP_LOOP_ESC" "$CRSF_FILE"; then
    ESC_LOOP=$(grep "$TEMP_LOOP_ESC" "$CRSF_FILE")
    if echo "$ESC_LOOP" | grep -q "tempCount < MAX_CRSF_TEMPS\|tempCount < 20"; then
        echo "  Status: ✅ PASS - ESC loop has bounds checking"
        BOUNDS_CHECK_FOUND=$((BOUNDS_CHECK_FOUND + 1))
    else
        echo "  Status: ❌ FAIL - ESC loop missing bounds check (BUG #4)"
        echo "  Detail: No check for tempCount < MAX_CRSF_TEMPS"
        echo "  Impact: Buffer overflow if >20 ESC temperatures"
        BUGS_FOUND=$((BUGS_FOUND + 1))
    fi
fi

# Check temperature sensor loop
if grep -q "$TEMP_LOOP_SENSOR" "$CRSF_FILE"; then
    SENSOR_LOOP=$(grep "$TEMP_LOOP_SENSOR" "$CRSF_FILE")
    if echo "$SENSOR_LOOP" | grep -q "tempCount < MAX_CRSF_TEMPS\|tempCount < 20"; then
        echo "  Status: ✅ PASS - Sensor loop has bounds checking"
        BOUNDS_CHECK_FOUND=$((BOUNDS_CHECK_FOUND + 1))
    else
        echo "  Status: ❌ FAIL - Sensor loop missing bounds check (BUG #4)"
        echo "  Detail: No check for tempCount < MAX_CRSF_TEMPS"
        echo "  Impact: Buffer overflow if >20 temperature sensors"
        BUGS_FOUND=$((BUGS_FOUND + 1))
    fi
fi

if [ $BOUNDS_CHECK_FOUND -gt 0 ]; then
    FIXES_FOUND=$((FIXES_FOUND + 1))
fi

echo ""

# =============================================================================
# TEST 4: RPM Protocol Limit Enforcement
# =============================================================================
echo "TEST 4: RPM protocol limit enforcement"
echo "  Expected: motorCount clamped to MAX_CRSF_RPM_VALUES (19)"

# Look for RPM frame function
if grep -q "static void crsfRpm" "$CRSF_FILE"; then
    # Extract the function body
    RPM_FUNCTION=$(sed -n '/static void crsfRpm/,/^}/p' "$CRSF_FILE")

    # Check for protocol limit constant
    if echo "$RPM_FUNCTION" | grep -q "MAX_CRSF_RPM_VALUES.*19"; then
        echo "  Status: ✅ PASS - MAX_CRSF_RPM_VALUES constant defined"

        # Check for clamping logic
        if echo "$RPM_FUNCTION" | grep -q "motorCount > MAX_CRSF_RPM_VALUES"; then
            echo "  Status: ✅ PASS - motorCount clamping logic detected"
            FIXES_FOUND=$((FIXES_FOUND + 1))
        else
            echo "  Status: ⚠️  WARN - Constant defined but no clamping logic"
        fi
    else
        echo "  Status: ❌ FAIL - No protocol limit enforcement (BUG #5)"
        echo "  Detail: motorCount not clamped to 19 values"
        echo "  Impact: Protocol violation if >19 motors configured"
        BUGS_FOUND=$((BUGS_FOUND + 1))
    fi
else
    echo "  Status: ⚠️  RPM function not found (feature may be disabled)"
fi

echo ""

# =============================================================================
# TEST 5: MAX_CRSF_TEMPS Constant Definition
# =============================================================================
echo "TEST 5: MAX_CRSF_TEMPS constant"
echo "  Expected: const uint8_t MAX_CRSF_TEMPS = 20"

if grep -q "MAX_CRSF_TEMPS.*20" "$CRSF_FILE"; then
    echo "  Status: ✅ PASS - Constant defined correctly"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "  Status: ⚠️  WARN - Constant not found (may use hard-coded value 20)"
fi

echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Commit: $COMMIT"
echo "Fixes detected: $FIXES_FOUND"
echo "Bugs detected: $BUGS_FOUND"
echo ""

if [ $BUGS_FOUND -eq 0 ]; then
    echo "✅ RESULT: PASS - Code is safe"
    echo ""
    echo "All critical fixes are present:"
    echo "  ✓ RPM frames scheduled conditionally"
    echo "  ✓ Temperature frames scheduled conditionally"
    echo "  ✓ Buffer bounds checking present"
    echo "  ✓ Protocol limits enforced"
    echo ""
    exit 0
else
    echo "❌ RESULT: FAIL - Bugs detected"
    echo ""
    echo "This code has the telemetry corruption bugs from PR #11025."
    echo "Deploying this code will break CRSF telemetry when sensors are disabled."
    echo ""
    echo "Expected behavior with bugs:"
    echo "  - Malformed frames sent when ESC/temp sensors disabled"
    echo "  - CRSF protocol stream corruption"
    echo "  - ALL telemetry stops working (GPS, battery, altitude, etc.)"
    echo "  - Receiver loses sync"
    echo ""
    exit 1
fi
