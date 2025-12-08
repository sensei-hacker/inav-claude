#!/bin/bash
#
# Quick CRSF Telemetry Test - Build and Test Cycle
#
# This script automates the common build-test workflow for CRSF telemetry development.
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
INAV_ROOT="$PROJECT_ROOT/inav"
BUILD_DIR="build_sitl_crsf"
SITL_LOG="/tmp/sitl_debug.log"

echo "======================================================================"
echo "Quick CRSF Telemetry Build & Test"
echo "======================================================================"
echo ""

# Parse command line arguments
REBUILD=0
CLEAN=0
SKIP_TEST=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--rebuild)
            REBUILD=1
            shift
            ;;
        -c|--clean)
            CLEAN=1
            REBUILD=1
            shift
            ;;
        -s|--skip-test)
            SKIP_TEST=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -r, --rebuild     Rebuild SITL without cleaning"
            echo "  -c, --clean       Clean rebuild SITL"
            echo "  -s, --skip-test   Build only, don't run test"
            echo "  -h, --help        Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                # Just run test (no rebuild)"
            echo "  $0 -r             # Rebuild and test"
            echo "  $0 -c             # Clean rebuild and test"
            echo "  $0 -r -s          # Rebuild but don't test"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h for help"
            exit 1
            ;;
    esac
done

# Step 1: Build if requested
if [ $REBUILD -eq 1 ]; then
    echo "[1/3] Building SITL..."
    cd "$INAV_ROOT/$BUILD_DIR"

    if [ $CLEAN -eq 1 ]; then
        echo "  Clean build..."
        make clean > /dev/null 2>&1
    fi

    if make -j4 2>&1 | tail -3 | grep -q "Built target SITL"; then
        echo "  ✓ Build successful"
    else
        echo "  ✗ Build failed"
        exit 1
    fi
else
    echo "[1/3] Skipping build (use -r to rebuild)"
fi

# Step 2: Kill existing processes
echo ""
echo "[2/3] Cleaning up processes..."
pkill -9 SITL.elf 2>/dev/null || true
pkill -9 -f crsf_rc_sender 2>/dev/null || true
sleep 1
echo "  ✓ Cleanup complete"

# Step 3: Run test if not skipped
if [ $SKIP_TEST -eq 1 ]; then
    echo ""
    echo "[3/3] Test skipped (use without -s to run test)"
    echo ""
    echo "To run manually:"
    echo "  cd $INAV_ROOT/$BUILD_DIR"
    echo "  rm -f eeprom.bin"
    echo "  ./bin/SITL.elf | egrep -v 'Program word' > $SITL_LOG 2>&1 &"
    echo "  # Then check log: tail -f $SITL_LOG"
    exit 0
fi

echo ""
echo "[3/3] Running CRSF telemetry test..."
echo ""

# Run the full test
cd "$INAV_ROOT"
exec "$SCRIPT_DIR/test_crsf_telemetry.sh" "$BUILD_DIR"
