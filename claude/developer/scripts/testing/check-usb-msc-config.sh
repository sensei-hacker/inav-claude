#!/bin/bash
# Check USB configuration when H743 board is in MSC mode
# Returns:
#   0 = MSC-only (GOOD - Windows compatible)
#   1 = MSC+CDC (BAD - breaks Windows)
#   2 = Error/not found

set -e

# STM32 vendor ID
VID="0483"

echo "=== Checking USB device configuration for STM32 in MSC mode ===" >&2

# Find STM32 devices
DEVICES=$(lsusb -d ${VID}: | grep -i "stm" || true)

if [ -z "$DEVICES" ]; then
    echo "ERROR: No STM32 devices found" >&2
    exit 2
fi

echo "Found STM32 devices:" >&2
echo "$DEVICES" >&2
echo "" >&2

# Get detailed info for all STM32 devices
HAS_MSC=false
HAS_CDC=false

while IFS= read -r line; do
    # Extract bus and device numbers
    BUS=$(echo "$line" | awk '{print $2}')
    DEV=$(echo "$line" | awk '{print $4}' | tr -d ':')

    echo "Checking Bus $BUS Device $DEV..." >&2

    # Get detailed USB descriptor
    USB_INFO=$(lsusb -v -s ${BUS}:${DEV} 2>/dev/null || true)

    # Check for Mass Storage interface (class 08)
    if echo "$USB_INFO" | grep -q "bInterfaceClass.*8 Mass Storage"; then
        echo "  ✓ Mass Storage interface found (class 08)" >&2
        HAS_MSC=true
    fi

    # Check for CDC/ACM interface (class 02)
    if echo "$USB_INFO" | grep -q "bInterfaceClass.*2 Communications"; then
        echo "  ✓ CDC/ACM Virtual COM Port interface found (class 02)" >&2
        HAS_CDC=true
    fi

done <<< "$DEVICES"

echo "" >&2
echo "=== RESULT ===" >&2

if [ "$HAS_MSC" = true ] && [ "$HAS_CDC" = false ]; then
    echo "MSC-ONLY mode detected (GOOD - Windows compatible)" >&2
    echo "GOOD"
    exit 0
elif [ "$HAS_MSC" = true ] && [ "$HAS_CDC" = true ]; then
    echo "MSC+CDC mode detected (BAD - breaks Windows)" >&2
    echo "BAD"
    exit 1
elif [ "$HAS_MSC" = false ]; then
    echo "ERROR: No Mass Storage interface found (device not in MSC mode?)" >&2
    exit 2
else
    echo "ERROR: Unknown configuration" >&2
    exit 2
fi
