#!/bin/bash
# Comprehensive USB device information gathering script
# Usage: ./gather-usb-info.sh output-file.txt

OUTPUT="${1:-usb-info.txt}"
VID="0483"

echo "USB Configuration Analysis - $(date)" > "$OUTPUT"
echo "==========================================" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Find STM32 device
DEVICE=$(lsusb -d ${VID}: | head -1)
if [ -z "$DEVICE" ]; then
    echo "ERROR: No STM32 device found" >> "$OUTPUT"
    exit 1
fi

BUS=$(echo "$DEVICE" | awk '{print $2}')
DEV=$(echo "$DEVICE" | awk '{print $4}' | tr -d ':')
PID=$(echo "$DEVICE" | grep -oP 'ID \K[0-9a-f]{4}:[0-9a-f]{4}' | cut -d: -f2)

echo "## Device Identification" >> "$OUTPUT"
echo "Vendor:Device ID: ${VID}:${PID}" >> "$OUTPUT"
echo "Bus: $BUS" >> "$OUTPUT"
echo "Device: $DEV" >> "$OUTPUT"
echo "$DEVICE" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# lsusb tree view
echo "## USB Tree" >> "$OUTPUT"
lsusb -t | grep -A5 -B5 "Dev $DEV" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# usb-devices output
echo "## USB Devices Detail" >> "$OUTPUT"
usb-devices | grep -A30 "Vendor=${VID} ProdID=${PID}" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Verbose lsusb output
echo "## Verbose USB Descriptor (lsusb -v)" >> "$OUTPUT"
lsusb -v -s ${BUS}:${DEV} 2>&1 >> "$OUTPUT"
echo "" >> "$OUTPUT"

# sysfs information
echo "## Sysfs Information" >> "$OUTPUT"
SYSPATH="/sys/bus/usb/devices/${BUS}-"
for path in ${SYSPATH}*; do
    if [ -d "$path" ] && [ -f "$path/idVendor" ]; then
        if [ "$(cat $path/idVendor 2>/dev/null)" = "$VID" ]; then
            echo "Device path: $path" >> "$OUTPUT"
            echo "  idVendor: $(cat $path/idVendor 2>/dev/null)" >> "$OUTPUT"
            echo "  idProduct: $(cat $path/idProduct 2>/dev/null)" >> "$OUTPUT"
            echo "  manufacturer: $(cat $path/manufacturer 2>/dev/null)" >> "$OUTPUT"
            echo "  product: $(cat $path/product 2>/dev/null)" >> "$OUTPUT"
            echo "  serial: $(cat $path/serial 2>/dev/null)" >> "$OUTPUT"
            echo "  bDeviceClass: $(cat $path/bDeviceClass 2>/dev/null)" >> "$OUTPUT"
            echo "  bDeviceSubClass: $(cat $path/bDeviceSubClass 2>/dev/null)" >> "$OUTPUT"
            echo "  bNumInterfaces: $(cat $path/bNumInterfaces 2>/dev/null)" >> "$OUTPUT"
            echo "  speed: $(cat $path/speed 2>/dev/null)" >> "$OUTPUT"

            echo "" >> "$OUTPUT"
            echo "  Interfaces:" >> "$OUTPUT"
            for iface in ${path}:*; do
                if [ -d "$iface" ]; then
                    IFACE_NUM=$(basename "$iface" | cut -d: -f2 | cut -d. -f1)
                    echo "    Interface $iface:" >> "$OUTPUT"
                    echo "      bInterfaceClass: $(cat $iface/bInterfaceClass 2>/dev/null)" >> "$OUTPUT"
                    echo "      bInterfaceSubClass: $(cat $iface/bInterfaceSubClass 2>/dev/null)" >> "$OUTPUT"
                    echo "      bInterfaceProtocol: $(cat $iface/bInterfaceProtocol 2>/dev/null)" >> "$OUTPUT"
                    echo "      bInterfaceNumber: $(cat $iface/bInterfaceNumber 2>/dev/null)" >> "$OUTPUT"
                    echo "      bNumEndpoints: $(cat $iface/bNumEndpoints 2>/dev/null)" >> "$OUTPUT"
                fi
            done
            echo "" >> "$OUTPUT"
        fi
    fi
done

# Storage devices
echo "## Storage Devices" >> "$OUTPUT"
echo "All /dev/sd* devices:" >> "$OUTPUT"
ls -la /dev/sd* 2>&1 >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Mounted filesystems:" >> "$OUTPUT"
mount | grep "^/dev/sd" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Serial/COM devices
echo "## Serial/COM Devices" >> "$OUTPUT"
ls -la /dev/ttyACM* /dev/ttyUSB* 2>&1 >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Kernel messages
echo "## Recent Kernel Messages (USB related)" >> "$OUTPUT"
sudo dmesg | grep -i "usb.*${BUS}-" | tail -30 >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Class code reference
echo "## USB Class Code Reference" >> "$OUTPUT"
echo "02h = CDC (Communications Device Class / Virtual COM Port)" >> "$OUTPUT"
echo "08h = MSC (Mass Storage Class)" >> "$OUTPUT"
echo "FFh = Vendor Specific" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "Analysis complete. Output saved to: $OUTPUT"
