#!/bin/bash
# Fully automated MSC configuration test using existing skills
# Usage: ./test-msc-config-auto.sh [path-to-firmware.bin]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="/home/raymorris/Documents/planes/inavflight"
SKILL_DIR="$REPO_ROOT/.claude/skills/flash-firmware-dfu"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default firmware path
if [ -z "$1" ]; then
    FIRMWARE="$REPO_ROOT/inav/build/inav_9.0.0_CORVON743V1.bin"
else
    FIRMWARE="$1"
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Automated MSC Configuration Test${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo "Firmware: $FIRMWARE"
echo ""

# Check firmware exists
if [ ! -f "$FIRMWARE" ]; then
    echo -e "${RED}ERROR: Firmware file not found: $FIRMWARE${NC}"
    exit 1
fi

# Step 1: Try to enter DFU mode
echo -e "${YELLOW}Step 1: Entering DFU mode...${NC}"

# Try software method first if serial port exists
if ls /dev/ttyACM* >/dev/null 2>&1; then
    SERIAL_PORT=$(ls /dev/ttyACM* | head -1)
    echo "Found serial port: $SERIAL_PORT"
    echo "Attempting software reboot to DFU mode..."

    if "$SKILL_DIR/reboot-to-dfu.py" "$SERIAL_PORT" 2>&1 | grep -q "device.*appeared"; then
        echo -e "${GREEN}✓ Software reboot successful${NC}"
    else
        echo -e "${YELLOW}Software reboot didn't work, trying manual method...${NC}"
    fi
fi

# Check if DFU device is present
if ! dfu-util -l 2>/dev/null | grep -q "0483:df11"; then
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Please put board in DFU mode manually:${NC}"
    echo -e "${YELLOW}1. Hold BOOT button${NC}"
    echo -e "${YELLOW}2. Press RESET (or unplug/replug USB)${NC}"
    echo -e "${YELLOW}3. Release BOOT button${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Waiting for DFU device..."

    # Wait up to 60 seconds for DFU device
    for i in {1..60}; do
        if dfu-util -l 2>/dev/null | grep -q "0483:df11"; then
            echo -e "${GREEN}✓ DFU device detected${NC}"
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
fi

# Verify DFU mode
if ! dfu-util -l 2>/dev/null | grep -q "0483:df11"; then
    echo -e "${RED}✗ DFU device not found${NC}"
    exit 1
fi
echo ""

# Step 2: Flash firmware
echo -e "${YELLOW}Step 2: Flashing firmware...${NC}"
echo ""

if dfu-util -d 0483:df11 --alt 0 -s 0x08000000:force:leave -D "$FIRMWARE" 2>&1 | tail -5; then
    echo ""
    echo -e "${GREEN}✓ Firmware flashed successfully${NC}"
else
    echo -e "${RED}✗ Flash failed${NC}"
    exit 1
fi
echo ""

# Step 3: Wait for board to reboot
echo -e "${YELLOW}Step 3: Waiting for board to reboot...${NC}"
sleep 3

SERIAL_PORT=""
for i in {1..10}; do
    if ls /dev/ttyACM* >/dev/null 2>&1; then
        SERIAL_PORT=$(ls /dev/ttyACM* | head -1)
        echo -e "${GREEN}✓ Serial port found: $SERIAL_PORT${NC}"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

if [ -z "$SERIAL_PORT" ]; then
    echo -e "${RED}ERROR: No serial port found after reboot${NC}"
    exit 1
fi

# Give the board time to fully initialize
sleep 2
echo ""

# Step 4: Enter MSC mode using skill
echo -e "${YELLOW}Step 4: Entering MSC mode...${NC}"
if "$SKILL_DIR/fc-cli.py" "msc" "$SERIAL_PORT"; then
    echo -e "${GREEN}✓ MSC command sent${NC}"
else
    echo -e "${RED}✗ Failed to send MSC command${NC}"
    exit 1
fi
echo ""

# Step 5: Wait for USB re-enumeration in MSC mode
echo -e "${YELLOW}Step 5: Waiting for USB re-enumeration...${NC}"
sleep 5

# Check for storage device
if ls /dev/sd* 2>/dev/null | grep -v sda | grep -q sd; then
    echo -e "${GREEN}✓ Storage device appeared:${NC}"
    ls /dev/sd* 2>/dev/null | grep -v "^/dev/sda"
else
    echo -e "${YELLOW}Note: No new storage device (may be normal on some systems)${NC}"
fi
echo ""

# Step 6: Check USB configuration
echo -e "${YELLOW}Step 6: Checking USB configuration...${NC}"
echo ""

if "$SCRIPT_DIR/check-usb-msc-config.sh"; then
    RESULT="MSC-ONLY (GOOD)"
    COLOR="$GREEN"
    EXIT_CODE=0
else
    TEST_EXIT=$?
    if [ $TEST_EXIT -eq 1 ]; then
        RESULT="MSC+CDC (BAD)"
        COLOR="$RED"
        EXIT_CODE=1
    else
        RESULT="ERROR/UNKNOWN"
        COLOR="$YELLOW"
        EXIT_CODE=2
    fi
fi

echo ""
echo -e "${COLOR}========================================${NC}"
echo -e "${COLOR}FINAL RESULT: $RESULT${NC}"
echo -e "${COLOR}========================================${NC}"
echo ""

# Show lsusb for reference
echo "USB devices:"
lsusb | grep -i stm || true
echo ""

exit $EXIT_CODE
