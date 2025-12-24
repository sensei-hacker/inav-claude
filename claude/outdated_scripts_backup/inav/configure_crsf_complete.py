#!/usr/bin/env python3
"""
Complete CRSF Configuration for SITL Telemetry Testing

This script configures SITL with all necessary settings for CRSF telemetry:
1. Enable TELEMETRY feature flag
2. Configure serial port for CRSF (RX_SERIAL function)
3. Set receiver type to SERIAL
4. Set serial RX provider to CRSF
5. Save and reboot

Usage: python3 configure_crsf_complete.py [port]
       Default port: 5760 (UART1/MSP)
"""

import sys
import struct
import time

sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/uNAVlib')
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

MSP_PORT = sys.argv[1] if len(sys.argv) > 1 else "5760"

print("=" * 70)
print("COMPLETE CRSF CONFIGURATION FOR SITL")
print("=" * 70)
print()

# Connect to SITL
print(f"[1/6] Connecting to SITL on port {MSP_PORT}...")
with MSPy(device=MSP_PORT, use_tcp=True, loglevel='WARNING') as board:
    if board == 1:
        print("✗ Connection failed")
        sys.exit(1)

    print("✓ Connected to SITL")
    print(f"  FC: {board.CONFIG['flightControllerIdentifier']}")
    print(f"  Version: {board.CONFIG['flightControllerVersion']}")
    print()

    # Step 1: Enable TELEMETRY feature
    print("[2/6] Enabling TELEMETRY feature flag...")

    if board.send_RAW_msg(MSPCodes['MSP_FEATURE_CONFIG'], data=[]):
        dataHandler = board.receive_msg()
        board.process_recv_data(dataHandler)

    current_features = board.FEATURE_CONFIG.get('featureMask', 0)
    FEATURE_TELEMETRY = 0x400  # Bit 10

    print(f"  Current features: 0x{current_features:08X}")

    if current_features & FEATURE_TELEMETRY:
        print("  ✓ TELEMETRY already enabled")
    else:
        new_features = current_features | FEATURE_TELEMETRY
        print(f"  Setting features: 0x{new_features:08X}")

        data = struct.pack('<I', new_features)
        if board.send_RAW_msg(MSPCodes['MSP_SET_FEATURE_CONFIG'], data=list(data)):
            dataHandler = board.receive_msg()

        print("  ✓ TELEMETRY enabled")
    print()

    # Step 2: Read current serial configuration
    print("[3/6] Reading serial port configuration...")

    if board.send_RAW_msg(MSPCodes['MSP_CF_SERIAL_CONFIG'], data=[]):
        dataHandler = board.receive_msg()
        raw_data = dataHandler.get('dataView', [])

        # Parse serial config
        # Each port: 1 byte identifier + 4 bytes function mask + 1 byte MSP baud + 1 byte GPS baud + 1 byte TELEM baud + 1 byte PERIPH baud
        num_ports = len(raw_data) // 8 if len(raw_data) >= 8 else 0

        print(f"  ✓ Found {num_ports} serial ports configured")

        for i in range(num_ports):
            offset = i * 8
            port_id = raw_data[offset]
            function_mask = struct.unpack('<I', bytes(raw_data[offset+1:offset+5]))[0]
            print(f"    Port {port_id}: functions=0x{function_mask:04X}")
    print()

    # Step 3: Configure UART2 for CRSF RX
    print("[4/6] Configuring UART2 for CRSF (RX_SERIAL)...")

    # MSP_SET_CF_SERIAL_CONFIG format:
    # For each port: [identifier][function_mask:4bytes][msp_baud][gps_baud][telem_baud][periph_baud]

    FUNCTION_RX_SERIAL = 0x40  # RX_SERIAL function (bit 6)
    PERIPH_BAUD_420000 = 5     # 420000 baud for CRSF

    # Configure only UART2 (identifier = 2)
    serial_config = [
        2,                          # UART2 identifier
        FUNCTION_RX_SERIAL, 0, 0, 0,  # function_mask (little-endian)
        0,                          # msp_baud (unused)
        0,                          # gps_baud (unused)
        0,                          # telem_baud (unused)
        PERIPH_BAUD_420000         # periph_baud (420000)
    ]

    print(f"  Port: UART2")
    print(f"  Function: RX_SERIAL (0x{FUNCTION_RX_SERIAL:02X})")
    print(f"  Baud: 420000")

    if board.send_RAW_msg(MSPCodes['MSP_SET_CF_SERIAL_CONFIG'], data=serial_config):
        dataHandler = board.receive_msg()

    print("  ✓ Serial port configured")
    print()

    # Step 4: Configure RX provider
    print("[5/6] Configuring RX: type=SERIAL, provider=CRSF...")

    # MSP_SET_RX_CONFIG format (24 bytes):
    # [0]    serialrx_provider (6 = CRSF)
    # [1-2]  maxcheck (1900)
    # [3-4]  midrc (1500, ignored for CRSF)
    # [5-6]  mincheck (1100)
    # [7]    spektrum_sat_bind (0)
    # [8-9]  rx_min_usec (885)
    # [10-11] rx_max_usec (2115)
    # [12-22] compatibility padding (11 bytes)
    # [23]   receiverType (1 = RX_TYPE_SERIAL)

    SERIALRX_CRSF = 6
    RX_TYPE_SERIAL = 1

    rx_config = [
        SERIALRX_CRSF,              # [0] provider = CRSF
        0x6C, 0x07,                 # [1-2] maxcheck = 1900
        0xDC, 0x05,                 # [3-4] midrc = 1500
        0x4C, 0x04,                 # [5-6] mincheck = 1100
        0,                          # [7] spektrum_sat_bind
        0x75, 0x03,                 # [8-9] rx_min_usec = 885
        0x43, 0x08,                 # [10-11] rx_max_usec = 2115
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # [12-22] padding
        RX_TYPE_SERIAL              # [23] receiverType = SERIAL
    ]

    print(f"  RX Type: SERIAL ({RX_TYPE_SERIAL})")
    print(f"  Serial RX Provider: CRSF ({SERIALRX_CRSF})")

    if board.send_RAW_msg(MSPCodes['MSP_SET_RX_CONFIG'], data=rx_config):
        dataHandler = board.receive_msg()

    print("  ✓ RX provider configured")
    print()

    # Step 5: Save and reboot
    print("[6/6] Saving configuration and rebooting...")

    if board.send_RAW_msg(MSPCodes['MSP_EEPROM_WRITE'], data=[]):
        time.sleep(0.5)

    print("  ✓ Configuration saved to EEPROM")

    board.send_RAW_msg(MSPCodes['MSP_REBOOT'], data=[])
    print("  ✓ Reboot command sent")
    print()

    print("=" * 70)
    print("CONFIGURATION COMPLETE")
    print("=" * 70)
    print()
    print("Wait 15 seconds for SITL to restart, then:")
    print("  1. Verify UART2 listening: ss -tlnp | grep 5761")
    print("  2. Check SITL log for: [CRSF TELEM] debug messages")
    print("  3. Test telemetry: python3 crsf_stream_parser.py 2")
    print()
