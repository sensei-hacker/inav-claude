#!/bin/bash
# Build INAV SITL (Software In The Loop)
# Usage: ./build_sitl.sh [clean]
#
# This script builds SITL in a separate build_sitl directory to avoid
# conflicts with hardware target builds.

set -e

# Find inav directory - script is in claude/developer/scripts/build/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up 4 levels from scripts/build to inavflight, then into inav
PROJECT_ROOT="${SCRIPT_DIR}/../../../.."
INAV_DIR="${PROJECT_ROOT}/inav"

if [ ! -d "$INAV_DIR" ]; then
    echo "Error: Cannot find inav directory at $INAV_DIR"
    echo "Script dir: $SCRIPT_DIR"
    exit 1
fi

INAV_DIR="$(cd "$INAV_DIR" && pwd)"
BUILD_DIR="${INAV_DIR}/build_sitl"

echo "INAV directory: ${INAV_DIR}"
echo "Build directory: ${BUILD_DIR}"

# Check for clean option
if [ "$1" = "clean" ]; then
    echo "Cleaning SITL build directory..."
    rm -rf "${BUILD_DIR}"
fi

# Create build directory
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Function to check if ld supports --no-warn-rwx-segments
check_ld_rwx_support() {
    local tmpfile=$(mktemp /tmp/claude/test_ld_XXXXXX 2>/dev/null || echo "/tmp/claude/test_ld_$$")
    echo "int main(){return 0;}" | gcc -x c - -Wl,--no-warn-rwx-segments -o "$tmpfile" 2>/dev/null
    local result=$?
    rm -f "$tmpfile" 2>/dev/null
    return $result
}

# Patch cmake file if linker doesn't support rwx-segments flag
patch_cmake_if_needed() {
    local SITL_CMAKE="${INAV_DIR}/cmake/sitl.cmake"

    # Check if linker supports the flag
    if check_ld_rwx_support; then
        return 0  # No patching needed
    fi

    # Check if already patched (commented out)
    if grep -q '# .*no-warn-rwx-segments' "$SITL_CMAKE" 2>/dev/null; then
        echo "Note: cmake/sitl.cmake already patched for older ld"
        return 0
    fi

    # Check if the flag is present and needs patching
    if grep -q 'no-warn-rwx-segments' "$SITL_CMAKE" 2>/dev/null; then
        echo "Note: ld does not support --no-warn-rwx-segments (requires ld 2.39+)"
        echo "Patching cmake/sitl.cmake..."

        # Comment out just the rwx-segments line (the if/endif can stay)
        sed -i 's/\(.*SITL_LINK_OPTIONS.*no-warn-rwx-segments.*\)/# Disabled for ld <2.39: \1/' "$SITL_CMAKE"

        echo "Patched cmake/sitl.cmake for linker compatibility"
    fi
}

# Check if we need to run cmake
if [ ! -f "Makefile" ] || [ "$1" = "clean" ]; then
    echo "Configuring SITL build..."

    # Patch cmake if needed for older linkers
    patch_cmake_if_needed

    cmake -DSITL=ON ..
fi

echo "Building SITL..."
make SITL.elf -j$(nproc)

if [ -f "bin/SITL.elf" ]; then
    echo ""
    echo "========================================="
    echo "Build successful!"
    echo "Binary: ${BUILD_DIR}/bin/SITL.elf"
    echo "========================================="
    echo ""
    echo "To run: cd ${BUILD_DIR} && ./bin/SITL.elf"
else
    echo "Build failed - SITL.elf not found"
    exit 1
fi
