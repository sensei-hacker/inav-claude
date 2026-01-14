#!/usr/bin/env python3
"""
DFU Flash with Settings Preservation - Direct Translation from Configurator

This is a direct translation of inav-configurator/js/protocols/stm32usbdfu.js
"""

import usb.core
import usb.util
import sys
import time

# DFU Protocol Constants (from configurator)
DFU_REQUEST = {
    'DNLOAD': 0x01,
    'GETSTATUS': 0x03,
    'CLRSTATUS': 0x04,
}

DFU_STATE = {
    'dfuIDLE': 2,
    'dfuDNLOAD_SYNC': 3,
    'dfuDNBUSY': 4,
    'dfuDNLOAD_IDLE': 5,
    'dfuERROR': 10
}

# STM32 DFU Device IDs
STM32_DFU_VID = 0x0483
STM32_DFU_PID = 0xdf11

# Flash layouts for different MCU families
# Based on inav-configurator/js/protocols/stm32usbdfu.js

# Flash layout for STM32F4 (F405/F407)
# F40x: "@Internal Flash  /0x08000000/04*016Kg,01*064Kg,07*128Kg"
FLASH_LAYOUT_F4 = {
    'start_address': 0x08000000,
    'sectors': [
        {'start_address': 0x08000000, 'page_size': 16384, 'num_pages': 4},   # 4x 16KB
        {'start_address': 0x08010000, 'page_size': 65536, 'num_pages': 1},   # 1x 64KB
        {'start_address': 0x08020000, 'page_size': 131072, 'num_pages': 7}   # 7x 128KB
    ]
}

# Flash layout for STM32F7 (F722/F745)
# F72x: "@Internal Flash  /0x08000000/04*016Kg,01*64Kg,03*128Kg"
# F74x: "@Internal Flash  /0x08000000/04*032Kg,01*128Kg,03*256Kg"
FLASH_LAYOUT_F7 = {
    'start_address': 0x08000000,
    'sectors': [
        {'start_address': 0x08000000, 'page_size': 16384, 'num_pages': 4},   # 4x 16KB
        {'start_address': 0x08010000, 'page_size': 65536, 'num_pages': 1},   # 1x 64KB
        {'start_address': 0x08020000, 'page_size': 131072, 'num_pages': 3}   # 3x 128KB
    ]
}

# Flash layout for STM32H7 (H743/H750)
# H7 has uniform 128KB sectors
FLASH_LAYOUT_H7 = {
    'start_address': 0x08000000,
    'sectors': [
        {'start_address': 0x08000000, 'page_size': 131072, 'num_pages': 16}  # 16x 128KB (2MB)
    ]
}

# Flash layout for AT32F435
# AT32F435: "@Internal Flash   /0x08000000/512*002Kg"
FLASH_LAYOUT_AT32F435 = {
    'start_address': 0x08000000,
    'sectors': [
        {'start_address': 0x08000000, 'page_size': 2048, 'num_pages': 512}   # 512x 2KB (1MB)
    ]
}

# Map MCU type to flash layout
FLASH_LAYOUTS = {
    'F4': FLASH_LAYOUT_F4,
    'F7': FLASH_LAYOUT_F7,
    'H7': FLASH_LAYOUT_H7,
    'AT32F435': FLASH_LAYOUT_AT32F435,
}

def get_string_descriptor(dev, index):
    """Get USB string descriptor - direct translation from configurator"""
    if index == 0:
        return ""

    try:
        # Request string descriptor
        # requestType: standard, recipient: device, request: GET_DESCRIPTOR (6)
        # wValue: 0x0300 | index (string descriptor type 3)
        result = dev.ctrl_transfer(0x80, 6, 0x0300 | index, 0, 255, 5000)

        if len(result) < 2:
            return ""

        length = result[0]
        # Decode UTF-16LE (skip first 2 bytes: length and descriptor type)
        descriptor = ""
        for i in range(2, min(length, len(result)), 2):
            if i + 1 < len(result):
                char_code = result[i] | (result[i + 1] << 8)
                descriptor += chr(char_code)

        return descriptor
    except Exception as e:
        print(f"  Warning: Failed to get string descriptor {index}: {e}")
        return ""

def get_interface_descriptors(dev):
    """Get interface descriptor strings - direct translation from configurator"""
    descriptors = []

    try:
        # Get device configuration
        config = dev.get_active_configuration()

        # DFU devices have multiple alternate settings on interface 0
        # Try to access alt settings 0-7 (DFU devices typically have 4)
        for alt_setting in range(8):
            try:
                # Access interface 0, alternate setting N
                alt_intf = config[(0, alt_setting)]
                iface_string_idx = alt_intf.iInterface

                if iface_string_idx > 0:
                    descriptor_string = get_string_descriptor(dev, iface_string_idx)
                    if descriptor_string:
                        descriptors.append(descriptor_string)
            except (usb.core.USBError, IndexError):
                # No more alternate settings
                break

    except Exception as e:
        print(f"  Warning: Failed to get interface descriptors: {e}")

    return descriptors

def parse_flash_descriptor(descriptor_str):
    """Parse DFU flash descriptor string - direct translation from configurator

    Examples:
        F303: "@Internal Flash  /0x08000000/128*0002Kg"
        F40x: "@Internal Flash  /0x08000000/04*016Kg,01*064Kg,07*128Kg"
        F72x: "@Internal Flash  /0x08000000/04*016Kg,01*64Kg,03*128Kg"
        F74x: "@Internal Flash  /0x08000000/04*032Kg,01*128Kg,03*256Kg"
        H743: "@Internal Flash  /0x08000000/16*128Kg"
        AT32F435: "@Internal Flash   /0x08000000/512*002Kg"
    """
    try:
        # Clean non-printable characters
        descriptor_str = ''.join(c for c in descriptor_str if 32 <= ord(c) <= 126)

        # Handle known quirks (H750 early bootloader)
        if descriptor_str == "@External Flash /0x90000000/1001*128Kg,3*128Kg,20*128Ka":
            descriptor_str = "@External Flash /0x90000000/998*128Kg,1*128Kg,4*128Kg,21*128Ka"

        # Split into [location, start_addr, sectors]
        parts = descriptor_str.split('/')

        # Handle multi-part descriptors (e.g., AT32 with option bytes)
        if len(parts) > 3:
            parts = parts[:3]

        if len(parts) < 3 or not parts[0].startswith('@'):
            return None

        memory_type = parts[0].strip().replace('@', '')
        start_address = int(parts[1], 16)

        # Parse sectors: "04*016Kg,01*064Kg,07*128Kg"
        sectors = []
        total_size = 0
        sector_parts = parts[2].split(',')

        for sector_str in sector_parts:
            # Split "04*016Kg" into ["04", "016Kg"]
            if '*' not in sector_str:
                continue

            num_str, size_str = sector_str.split('*')
            num_pages = int(num_str)

            # Parse size with unit: "016Kg" -> 16KB
            # Extract numeric part and unit
            size_numeric = ''.join(c for c in size_str if c.isdigit())
            if not size_numeric:
                continue

            page_size = int(size_numeric)

            # Get unit (K or M) - it's the second-to-last character
            if len(size_str) >= 2:
                unit = size_str[-2:-1]
                if unit == 'M':
                    page_size *= 1024 * 1024
                elif unit == 'K':
                    page_size *= 1024

            sectors.append({
                'start_address': start_address + total_size,
                'page_size': page_size,
                'num_pages': num_pages,
                'total_size': num_pages * page_size
            })

            total_size += num_pages * page_size

        if not sectors:
            return None

        return {
            'type': memory_type,
            'start_address': start_address,
            'sectors': sectors,
            'total_size': total_size
        }

    except Exception as e:
        print(f"  Warning: Failed to parse descriptor '{descriptor_str}': {e}")
        return None

def infer_mcu_family_from_layout(flash_layout):
    """Infer MCU family from detected flash layout characteristics"""
    if not flash_layout or 'sectors' not in flash_layout:
        return None

    sectors = flash_layout['sectors']
    total_size = flash_layout.get('total_size', sum(s.get('total_size', s['page_size'] * s['num_pages']) for s in sectors))

    # Check for AT32F435 signature: 512x2KB
    if len(sectors) == 1 and sectors[0]['page_size'] == 2048 and sectors[0]['num_pages'] == 512:
        return 'AT32F435'

    # Check for H7 signature: uniform 128KB sectors
    if len(sectors) == 1 and sectors[0]['page_size'] == 131072:
        return 'H7'

    # Check for F4 signature: 4x16KB + 1x64KB + 7x128KB (or similar)
    if len(sectors) >= 3 and sectors[0]['page_size'] == 16384 and sectors[1]['page_size'] == 65536:
        if len(sectors) > 2 and sectors[2]['page_size'] == 131072 and sectors[2]['num_pages'] >= 7:
            return 'F4'
        # F7 signature: 4x16KB + 1x64KB + 3x128KB
        elif len(sectors) > 2 and sectors[2]['page_size'] == 131072 and sectors[2]['num_pages'] == 3:
            return 'F7'

    return None

def extract_target_from_filename(hex_file):
    """Extract target name from hex filename (e.g., 'MATEKF405' from 'inav_9.0.0_MATEKF405.hex')"""
    import os
    basename = os.path.basename(hex_file)
    # Remove .hex extension
    name = basename.replace('.hex', '').replace('.HEX', '')

    # Common patterns: inav_X.X.X_TARGET or just TARGET
    parts = name.split('_')
    if len(parts) > 1:
        # Last part is usually the target
        return parts[-1].upper()

    return name.upper()

def infer_mcu_family_from_target(target_name):
    """Infer expected MCU family from target name"""
    target_upper = target_name.upper()

    # F4 patterns
    if any(pattern in target_upper for pattern in ['F405', 'F411', 'F40', 'F4']):
        return 'F4'

    # F7 patterns
    if any(pattern in target_upper for pattern in ['F722', 'F745', 'F765', 'F72', 'F74', 'F7']):
        return 'F7'

    # H7 patterns
    if any(pattern in target_upper for pattern in ['H743', 'H750', 'H7']):
        return 'H7'

    # AT32 patterns
    if any(pattern in target_upper for pattern in ['AT32F435', 'AT32']):
        return 'AT32F435'

    return None

def check_firmware_hardware_match(hex_file, flash_layout):
    """Check if firmware filename matches detected hardware and warn if mismatch"""
    target_name = extract_target_from_filename(hex_file)
    expected_family = infer_mcu_family_from_target(target_name)
    detected_family = infer_mcu_family_from_layout(flash_layout)

    if not expected_family:
        print(f"  ℹ️  Target: {target_name} (MCU family unknown from filename)")
        return True

    if not detected_family:
        print(f"  ℹ️  Target: {target_name} (expected {expected_family}, but could not infer from detected layout)")
        return True

    if expected_family != detected_family:
        print()
        print("=" * 60)
        print("⚠️  WARNING: FIRMWARE/HARDWARE MISMATCH DETECTED!")
        print("=" * 60)
        print(f"Firmware target: {target_name} (implies {expected_family})")
        print(f"Detected hardware: {detected_family} flash layout")
        print()
        print("Flashing wrong firmware to wrong hardware can BRICK your FC!")
        print()
        print("If you are CERTAIN this is correct, you can:")
        print("  1. Press Ctrl+C to abort")
        print("  2. Or continue at your own risk")
        print("=" * 60)

        try:
            response = input("\nType 'YES' to continue anyway: ")
            if response.strip().upper() != 'YES':
                print("Aborted by user.")
                return False
        except KeyboardInterrupt:
            print("\nAborted by user.")
            return False

        print()
        return True

    print(f"  ✓ Firmware/hardware match: {target_name} ({expected_family})")
    return True

def detect_flash_layout(dev):
    """Detect flash layout from DFU device descriptors - like configurator does"""
    print("Detecting flash layout from device...")

    # Get interface descriptors
    descriptors = get_interface_descriptors(dev)

    if not descriptors:
        print("  Warning: No interface descriptors found")
        return None

    print(f"  Found {len(descriptors)} interface descriptor(s)")

    # Parse each descriptor and look for internal flash
    for desc_str in descriptors:
        print(f"  Descriptor: {desc_str}")
        parsed = parse_flash_descriptor(desc_str)

        if parsed and 'internal flash' in parsed['type'].lower():
            print(f"  ✓ Detected {parsed['type']}: {parsed['total_size'] / 1024:.0f}KB")
            print(f"    {len(parsed['sectors'])} sector(s)")
            for i, sector in enumerate(parsed['sectors']):
                print(f"    Sector {i}: {sector['num_pages']} x {sector['page_size'] / 1024:.0f}KB")
            return parsed

    print("  Warning: No internal flash descriptor found")
    return None

def parse_intel_hex(filename):
    """Parse Intel HEX file"""
    blocks = []
    current_block = None
    extended_address = 0

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] != ':':
                continue

            byte_count = int(line[1:3], 16)
            address = int(line[3:7], 16)
            record_type = int(line[7:9], 16)
            data = line[9:9+byte_count*2]

            if record_type == 0x00:  # Data record
                full_address = extended_address + address
                data_bytes = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]

                if current_block and current_block['address'] + current_block['bytes'] == full_address:
                    current_block['data'].extend(data_bytes)
                    current_block['bytes'] += byte_count
                else:
                    if current_block:
                        blocks.append(current_block)
                    current_block = {
                        'address': full_address,
                        'bytes': byte_count,
                        'data': data_bytes
                    }

            elif record_type == 0x01:  # End of file
                if current_block:
                    blocks.append(current_block)
                break

            elif record_type == 0x04:  # Extended linear address
                extended_address = int(data, 16) << 16

    total_bytes = sum(block['bytes'] for block in blocks)
    return {'data': blocks, 'bytes_total': total_bytes}

def calculate_pages_to_erase(hex_data, flash_layout):
    """Calculate which flash pages need to be erased"""
    pages = []

    for sector_idx, sector in enumerate(flash_layout['sectors']):
        for page_idx in range(sector['num_pages']):
            page_start = sector['start_address'] + page_idx * sector['page_size']
            page_end = page_start + sector['page_size'] - 1

            for block in hex_data['data']:
                block_start = block['address']
                block_end = block['address'] + block['bytes'] - 1

                starts_in_page = page_start <= block_start <= page_end
                ends_in_page = page_start <= block_end <= page_end
                spans_page = block_start < page_start and block_end > page_end

                if starts_in_page or ends_in_page or spans_page:
                    pages.append({'sector': sector_idx, 'page': page_idx})
                    break

    return pages

def control_transfer_out(dev, request, value, data):
    """OUT control transfer"""
    return dev.ctrl_transfer(0x21, request, value, 0, data, 5000)

def control_transfer_in(dev, request, length):
    """IN control transfer"""
    return dev.ctrl_transfer(0xA1, request, 0, 0, length, 5000)

def get_status(dev):
    """Get DFU status"""
    data = control_transfer_in(dev, DFU_REQUEST['GETSTATUS'], 6)
    return {
        'status': data[0],
        'poll_timeout': data[1] | (data[2] << 8) | (data[3] << 16),
        'state': data[4]
    }

def clear_status(dev):
    """Clear DFU status - loops until device reaches dfuIDLE"""
    # Check status first
    status = get_status(dev)

    while status['state'] != DFU_STATE['dfuIDLE']:
        # Clear status
        control_transfer_out(dev, DFU_REQUEST['CLRSTATUS'], 0, b'')

        # Wait for device-specified delay
        delay = status['poll_timeout'] / 1000.0
        if delay > 0:
            time.sleep(delay)

        # Check status again
        status = get_status(dev)

def load_address(dev, address):
    """Load address pointer - direct translation from configurator"""
    cmd = bytes([0x21, address & 0xff, (address >> 8) & 0xff, (address >> 16) & 0xff, (address >> 24) & 0xff])

    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, cmd)
    status = get_status(dev)

    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay = status['poll_timeout'] / 1000.0
        time.sleep(delay)
        status = get_status(dev)

        if status['state'] != DFU_STATE['dfuDNLOAD_IDLE']:
            raise Exception(f"Failed to load address 0x{address:08x}")

def erase_page(dev, flash_layout, sector, page):
    """Erase a single flash page - direct translation from configurator"""
    page_addr = page * flash_layout['sectors'][sector]['page_size'] + flash_layout['sectors'][sector]['start_address']
    cmd = bytes([0x41, page_addr & 0xff, (page_addr >> 8) & 0xff, (page_addr >> 16) & 0xff, (page_addr >> 24) & 0xff])

    print(f"  Erasing sector {sector}, page {page} @ 0x{page_addr:08x}")

    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, cmd)
    status = get_status(dev)

    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay = status['poll_timeout'] / 1000.0
        time.sleep(delay)
        status = get_status(dev)

        # H7 workaround
        if status['state'] == DFU_STATE['dfuDNBUSY']:
            clear_status(dev)
            status = get_status(dev)

    if status['state'] not in [DFU_STATE['dfuDNLOAD_IDLE'], DFU_STATE['dfuIDLE']]:
        raise Exception(f"Failed to erase page @ 0x{page_addr:08x}, state={status['state']}")

def write_data(dev, block_num, data):
    """Write data block - direct translation from configurator"""
    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], block_num, bytes(data))
    status = get_status(dev)

    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay = status['poll_timeout'] / 1000.0
        time.sleep(delay)
        status = get_status(dev)

        if status['state'] != DFU_STATE['dfuDNLOAD_IDLE']:
            raise Exception(f"Write failed, state={status['state']}")
    else:
        raise Exception(f"Failed to initiate write, state={status['state']}")

def flash_firmware(hex_file, mcu_type=None):
    """Main flashing function - structure from configurator

    Args:
        hex_file: Path to Intel HEX firmware file
        mcu_type: Optional manual MCU type ('F4', 'F7', 'H7', 'AT32F435').
                  If None (default), auto-detects from DFU device descriptor.
    """
    print("INAV DFU Flasher with Settings Preservation")
    print("=" * 44)
    print()

    # Parse hex file first
    print(f"Reading {hex_file}...")
    hex_data = parse_intel_hex(hex_file)
    print(f"Parsed {len(hex_data['data'])} blocks, {hex_data['bytes_total']} bytes total\n")

    # Find DFU device
    print("Looking for STM32 DFU device...")
    dev = usb.core.find(idVendor=STM32_DFU_VID, idProduct=STM32_DFU_PID)

    if dev is None:
        raise Exception("No STM32 DFU device found. Put FC into DFU mode first.")

    print(f"Found DFU device\n")

    # Claim interface
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)

    dev.set_configuration()
    usb.util.claim_interface(dev, 0)

    # Determine flash layout
    flash_layout = None

    # Try automatic detection first (unless user explicitly specified MCU type)
    if mcu_type is None:
        flash_layout = detect_flash_layout(dev)
        if flash_layout:
            print()
        else:
            print("  Automatic detection failed, will try F7 default\n")
            mcu_type = 'F7'

    # Use manual MCU type if specified or auto-detection failed
    if flash_layout is None:
        if mcu_type not in FLASH_LAYOUTS:
            raise ValueError(f"Unknown MCU type '{mcu_type}'. Valid options: {', '.join(FLASH_LAYOUTS.keys())}")

        flash_layout = FLASH_LAYOUTS[mcu_type]
        print(f"Using manual MCU type: {mcu_type}")
        print(f"Flash layout: {len(flash_layout['sectors'])} sector(s)")
        total_flash = sum(s['page_size'] * s['num_pages'] for s in flash_layout['sectors'])
        print(f"Total flash: {total_flash / 1024:.0f}KB\n")

    # Safety check: verify firmware filename matches detected hardware
    if not check_firmware_hardware_match(hex_file, flash_layout):
        usb.util.release_interface(dev, 0)
        usb.util.dispose_resources(dev)
        raise Exception("Firmware/hardware mismatch - flash aborted for safety")

    print()

    try:
        # Clear any error state
        clear_status(dev)

        # Calculate pages to erase
        print("Calculating pages to erase...")
        pages_to_erase = calculate_pages_to_erase(hex_data, flash_layout)
        print(f"Will erase {len(pages_to_erase)} pages (preserving config area)\n")

        # Erase pages (case 3 in configurator)
        print("Erasing flash pages:")
        for i, page_info in enumerate(pages_to_erase):
            erase_page(dev, flash_layout, page_info['sector'], page_info['page'])
            progress = (i + 1) / len(pages_to_erase) * 100
            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
        print("\n")

        # Write firmware (case 4 in configurator)
        # "we dont need to clear the state as we are already using DFU_DNLOAD"
        print("Writing firmware:")
        TRANSFER_SIZE = 2048
        total_written = 0

        for block_idx, block in enumerate(hex_data['data']):
            # Load address first (like configurator line 943)
            load_address(dev, block['address'])

            # Write data in chunks
            wBlockNum = 2  # Required by DFU
            offset = 0
            while offset < block['bytes']:
                chunk_size = min(TRANSFER_SIZE, block['bytes'] - offset)
                chunk = block['data'][offset:offset + chunk_size]

                write_data(dev, wBlockNum, chunk)
                wBlockNum += 1
                total_written += chunk_size
                offset += chunk_size

                progress = total_written / hex_data['bytes_total'] * 100
                print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
        print("\n")

        # Exit DFU mode (like configurator's leave() function)
        print("Exiting DFU mode...")
        try:
            clear_status(dev)
            print("  Clear status: OK")
        except Exception as e:
            print(f"  Clear status: {e}")

        try:
            load_address(dev, hex_data['data'][0]['address'])
            print("  Load address: OK")
        except Exception as e:
            print(f"  Load address: {e}")

        # This is the critical command that triggers exit
        try:
            control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, b'')
            print("  Exit command sent: OK")
        except Exception as e:
            print(f"  Exit command: {e}")

        # Device may have already disconnected
        try:
            get_status(dev)
            print("  Get status: OK")
        except Exception as e:
            print(f"  Get status: {e} (expected)")

        print("\n✓ Firmware flashed successfully!")
        print("✓ Settings preserved!")
        print("\nFC will now reboot with new firmware.")

    finally:
        usb.util.release_interface(dev, 0)
        usb.util.dispose_resources(dev)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 flash-dfu-preserve-settings.py <firmware.hex> [mcu_type]")
        print()
        print("Arguments:")
        print("  firmware.hex    Path to Intel HEX firmware file")
        print("  mcu_type        Optional: F4, F7, H7, or AT32F435")
        print("                  If omitted, auto-detects from DFU device descriptor")
        print()
        print("Examples:")
        print("  # Automatic detection (recommended)")
        print("  python3 flash-dfu-preserve-settings.py inav_9.0.0_MATEKF405.hex")
        print()
        print("  # Manual MCU type (fallback if auto-detection fails)")
        print("  python3 flash-dfu-preserve-settings.py inav_9.0.0_MATEKF405.hex F4")
        print("  python3 flash-dfu-preserve-settings.py inav_9.0.0_MATEKF722.hex F7")
        print("  python3 flash-dfu-preserve-settings.py inav_9.0.0_MATEKH743.hex H7")
        print("  python3 flash-dfu-preserve-settings.py inav_9.0.0_AT32F435.hex AT32F435")
        sys.exit(1)

    hex_file = sys.argv[1]
    mcu_type = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        flash_firmware(hex_file, mcu_type)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
