#!/bin/bash
# Simple helper: Build and flash firmware

TARGET="${1:-JHEMCUF435}"

echo "Building $TARGET..."
cd build && make "$TARGET" || exit 1
cd ..

echo "Converting to bin..."
HEX=$(ls build/inav_*${TARGET}*.hex | head -1)
BIN="${HEX%.hex}.bin"
arm-none-eabi-objcopy -I ihex -O binary "$HEX" "$BIN"

echo "Flashing via DFU..."
cd build
dfu-util -d 2e3c:df11 --alt 0 -s 0x08000000:force:leave -D "$(basename $BIN)" | grep -E "Download|done"
cd ..

echo "Waiting for FC to reboot..."
sleep 5

if [ -e /dev/ttyACM0 ]; then
    echo "✓ Flash complete, FC ready"
else
    echo "⚠ FC not detected yet, may need more time"
fi
