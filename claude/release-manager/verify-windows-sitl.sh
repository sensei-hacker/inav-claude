#!/bin/bash
#
# verify-windows-sitl.sh - Verify Windows configurator packages contain required SITL files
#
# Usage: ./verify-windows-sitl.sh <zip-file-or-directory>
#
# This script verifies that Windows INAV Configurator packages contain:
# - cygwin1.dll (required runtime for SITL)
# - inav_SITL.exe (the SITL binary)
#
# Both files must be present in resources/public/sitl/windows/ for SITL to work on Windows.
#
# Exit codes:
#   0 - All required files present
#   1 - Missing required files or error
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Required files - path in DISTRIBUTED packages (not source repo)
# Source repo: resources/public/sitl/windows/
# Packaged builds: resources/sitl/windows/ (per PR #2496 - extraResource copies without "public")
REQUIRED_FILES=(
    "resources/sitl/windows/cygwin1.dll"
    "resources/sitl/windows/inav_SITL.exe"
)

# Minimum expected file sizes (bytes) - sanity check
MIN_CYGWIN_SIZE=2000000   # ~2MB minimum for cygwin1.dll
MIN_SITL_SIZE=500000      # ~500KB minimum for inav_SITL.exe

usage() {
    echo "Usage: $0 <zip-file-or-directory>"
    echo ""
    echo "Verifies Windows INAV Configurator packages contain required SITL files."
    echo ""
    echo "Arguments:"
    echo "  zip-file-or-directory   Path to Windows configurator .zip file or extracted directory"
    echo ""
    echo "Examples:"
    echo "  $0 INAV-Configurator_win_x64_9.0.0.zip"
    echo "  $0 downloads/configurator-9.0.0-RC4/windows/INAV-Configurator_win_x64_9.0.0/"
    exit 1
}

verify_zip() {
    local zipfile="$1"
    local all_found=true
    local cygwin_size=0
    local sitl_size=0

    echo "Verifying zip file: $zipfile"
    echo ""

    # Get file listing
    local listing=$(unzip -l "$zipfile" 2>/dev/null)

    for file in "${REQUIRED_FILES[@]}"; do
        # Extract just the filename for matching (path may vary in zip)
        local filename=$(basename "$file")

        # Check if file exists in zip (match end of path)
        if echo "$listing" | grep -q "$filename"; then
            # Get file size from listing
            local size=$(echo "$listing" | grep "$filename" | awk '{print $1}')
            echo -e "${GREEN}[FOUND]${NC} $filename (${size} bytes)"

            # Store sizes for validation
            if [[ "$filename" == "cygwin1.dll" ]]; then
                cygwin_size=$size
            elif [[ "$filename" == "inav_SITL.exe" ]]; then
                sitl_size=$size
            fi
        else
            echo -e "${RED}[MISSING]${NC} $filename"
            all_found=false
        fi
    done

    echo ""

    # Size sanity checks
    if [[ $cygwin_size -gt 0 && $cygwin_size -lt $MIN_CYGWIN_SIZE ]]; then
        echo -e "${YELLOW}[WARNING]${NC} cygwin1.dll seems too small ($cygwin_size bytes)"
    fi

    if [[ $sitl_size -gt 0 && $sitl_size -lt $MIN_SITL_SIZE ]]; then
        echo -e "${YELLOW}[WARNING]${NC} inav_SITL.exe seems too small ($sitl_size bytes)"
    fi

    if $all_found; then
        echo -e "${GREEN}[PASS]${NC} All required Windows SITL files are present"
        return 0
    else
        echo -e "${RED}[FAIL]${NC} Missing required files - Windows SITL will not work!"
        return 1
    fi
}

verify_directory() {
    local dir="$1"
    local all_found=true

    echo "Verifying directory: $dir"
    echo ""

    for file in "${REQUIRED_FILES[@]}"; do
        local filepath="$dir/$file"
        local filename=$(basename "$file")

        if [[ -f "$filepath" ]]; then
            local size=$(stat -c%s "$filepath" 2>/dev/null || stat -f%z "$filepath" 2>/dev/null)
            echo -e "${GREEN}[FOUND]${NC} $filename (${size} bytes)"

            # Size sanity checks
            if [[ "$filename" == "cygwin1.dll" && $size -lt $MIN_CYGWIN_SIZE ]]; then
                echo -e "${YELLOW}[WARNING]${NC} cygwin1.dll seems too small"
            fi

            if [[ "$filename" == "inav_SITL.exe" && $size -lt $MIN_SITL_SIZE ]]; then
                echo -e "${YELLOW}[WARNING]${NC} inav_SITL.exe seems too small"
            fi
        else
            echo -e "${RED}[MISSING]${NC} $filename"
            all_found=false
        fi
    done

    echo ""

    if $all_found; then
        echo -e "${GREEN}[PASS]${NC} All required Windows SITL files are present"
        return 0
    else
        echo -e "${RED}[FAIL]${NC} Missing required files - Windows SITL will not work!"
        return 1
    fi
}

# Main
if [[ $# -ne 1 ]]; then
    usage
fi

TARGET="$1"

if [[ ! -e "$TARGET" ]]; then
    echo -e "${RED}Error:${NC} '$TARGET' does not exist"
    exit 1
fi

echo "========================================="
echo "Windows SITL Verification"
echo "========================================="
echo ""

if [[ -f "$TARGET" && "$TARGET" == *.zip ]]; then
    verify_zip "$TARGET"
elif [[ -d "$TARGET" ]]; then
    verify_directory "$TARGET"
else
    echo -e "${RED}Error:${NC} '$TARGET' is not a zip file or directory"
    exit 1
fi
