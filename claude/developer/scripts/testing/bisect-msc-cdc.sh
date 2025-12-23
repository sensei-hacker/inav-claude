#!/bin/bash
# Automated bisect script for H743 MSC+CDC issue
# Finds the commit where CDC interface was added to MSC mode
#
# Usage: ./bisect-msc-cdc.sh
#
# This script:
# 1. Builds firmware for current commit
# 2. Waits for user to flash it (DFU mode)
# 3. Tests USB configuration when in MSC mode
# 4. Marks commit as good/bad based on result

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="/home/raymorris/Documents/planes/inavflight"
TARGET="CORVON743V1"
TARGET_BACKUP="/tmp/${TARGET}_backup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "H743 MSC+CDC Bisect Automation Script"
echo "============================================"
echo ""

# Show current commit
cd "$REPO_ROOT/inav"
CURRENT_COMMIT=$(git log -1 --oneline)
echo -e "${YELLOW}Current commit:${NC} $CURRENT_COMMIT"
echo ""

# Check if target backup exists
if [ ! -d "$TARGET_BACKUP" ]; then
    echo -e "${RED}ERROR: Target backup not found at $TARGET_BACKUP${NC}"
    echo "Please create target backup first:"
    echo "  cp -r inav/src/main/target/$TARGET /tmp/${TARGET}_backup"
    exit 1
fi

# Step 1: Restore target files (in case they don't exist in this commit)
echo "Step 1: Restoring target files..."
mkdir -p "src/main/target/$TARGET"
cp -r "$TARGET_BACKUP"/* "src/main/target/$TARGET/"
echo -e "${GREEN}✓ Target files restored${NC}"
echo ""

# Step 2: Build firmware
echo "Step 2: Building firmware for $TARGET..."
cd build
make clean_${TARGET} >/dev/null 2>&1 || true
if make ${TARGET}; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    echo ""
    echo "This commit cannot be built. Mark as 'skip'?"
    read -p "Skip this commit? [y/N]: " SKIP
    if [ "$SKIP" = "y" ] || [ "$SKIP" = "Y" ]; then
        cd "$REPO_ROOT/inav"
        git bisect skip
        exit 0
    else
        exit 1
    fi
fi
echo ""

# Step 3: Convert to binary for flashing
echo "Step 3: Converting to binary..."
HEX_FILE=$(ls inav_*_${TARGET}.hex 2>/dev/null | head -1)
if [ -z "$HEX_FILE" ]; then
    echo -e "${RED}ERROR: No hex file found${NC}"
    exit 1
fi
BIN_FILE="${HEX_FILE%.hex}.bin"
objcopy -I ihex "$HEX_FILE" -O binary "$BIN_FILE"
echo -e "${GREEN}✓ Binary ready: $BIN_FILE${NC}"
echo ""

# Step 4: Wait for user to flash
echo "========================================"
echo "Step 4: FLASH THE FIRMWARE"
echo "========================================"
echo ""
echo "Binary location: $REPO_ROOT/inav/build/$BIN_FILE"
echo ""
echo "Instructions:"
echo "  1. Put board in DFU mode (hold BOOT button, plug USB)"
echo "  2. Verify DFU: dfu-util -l | grep '0483:df11'"
echo "  3. Flash: dfu-util -d 0483:df11 --alt 0 -s 0x08000000:force:leave -D $BIN_FILE"
echo "  4. Wait for board to reboot (LED should blink)"
echo ""
read -p "Press ENTER when flashing is complete..."
echo ""

# Step 5: Enter MSC mode
echo "Step 5: Entering MSC mode..."
echo ""
echo "Instructions:"
echo "  1. Connect to FC via serial (e.g., minicom -D /dev/ttyACM0)"
echo "  2. Type 'msc' and press ENTER"
echo "  3. Board should disconnect and reconnect in MSC mode"
echo ""
read -p "Press ENTER when board is in MSC mode..."
echo ""

# Wait a bit for USB enumeration
echo "Waiting 3 seconds for USB enumeration..."
sleep 3
echo ""

# Step 6: Check USB configuration
echo "Step 6: Checking USB configuration..."
echo ""

if "$SCRIPT_DIR/check-usb-msc-config.sh"; then
    RESULT="GOOD"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}RESULT: MSC-ONLY (GOOD)${NC}"
    echo -e "${GREEN}This commit shows only mass storage${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 1 ]; then
        RESULT="BAD"
        echo ""
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}RESULT: MSC+CDC (BAD)${NC}"
        echo -e "${RED}This commit shows MSC + Virtual COM${NC}"
        echo -e "${RED}========================================${NC}"
    else
        RESULT="ERROR"
        echo ""
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}RESULT: ERROR${NC}"
        echo -e "${YELLOW}Could not determine USB configuration${NC}"
        echo -e "${YELLOW}========================================${NC}"
    fi
fi
echo ""

# Step 7: Mark commit
echo "Step 7: Marking commit..."
echo ""
echo "Current commit: $CURRENT_COMMIT"
echo "Result: $RESULT"
echo ""

if [ "$RESULT" = "GOOD" ]; then
    echo "Marking as GOOD (MSC-only, works on Windows)"
    cd "$REPO_ROOT/inav"
    git bisect good
elif [ "$RESULT" = "BAD" ]; then
    echo "Marking as BAD (MSC+CDC, breaks Windows)"
    cd "$REPO_ROOT/inav"
    git bisect bad
else
    echo "Manual decision required."
    echo ""
    echo "What should we do?"
    echo "  g) Mark as good"
    echo "  b) Mark as bad"
    echo "  s) Skip this commit"
    echo "  q) Quit bisect"
    read -p "Choice [g/b/s/q]: " CHOICE

    cd "$REPO_ROOT/inav"
    case "$CHOICE" in
        g|G) git bisect good ;;
        b|B) git bisect bad ;;
        s|S) git bisect skip ;;
        q|Q) echo "Bisect not marked. Exiting."; exit 0 ;;
        *) echo "Invalid choice. Exiting."; exit 1 ;;
    esac
fi

echo ""
echo "========================================"
echo "Next commit ready for testing"
echo "========================================"
echo ""
git log -1 --oneline
echo ""
echo "Run this script again to test the next commit."
