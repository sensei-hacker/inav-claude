#!/usr/bin/env python3
"""
CRSF Configuration for SITL - PROPER SEQUENCE

This script configures SITL for CRSF telemetry using the correct MSP sequence:
1. Remove MSP from UART2
2. Set UART2 to SERIAL_RX
3. Set receiver type to SERIAL and protocol to CRSF
4. Enable TELEMETRY feature
5. Save and reboot

Usage: python3 configure_crsf_proper_sequence.py [port]
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
print("CRSF CONFIGURATION - PROPER SEQUENCE")
print("=" * 70)
print()

with MSPy(device=MSP_PORT, use_tcp=True, loglevel='WARNING') as board:
    if board == 1:
        print("✗ Connection failed")
        sys.exit(1)

    print("✓ Connected to SITL")
    print()

    # ========================================================================
    # STEP 1: Remove MSP from UART2
    # ========================================================================
    print("[1/5] Removing MSP from UART2...")

    serial_config = [
        2,              # UART2 identifier
        0, 0, 0, 0,     # functionMask = 0 (remove all functions)
        0, 0, 0, 0      # baud rates (unused)
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_CF_SERIAL_CONFIG'], data=serial_config):
        dataHandler = board.receive_msg()

    print("  ✓ MSP removed from UART2")
    print()

    # ========================================================================
    # STEP 2: Set UART2 to SERIAL_RX
    # ========================================================================
    print("[2/5] Setting UART2 to SERIAL_RX...")

    FUNCTION_RX_SERIAL = 0x40
    PERIPH_BAUD_420000 = 5

    serial_config = [
        2,                          # UART2 identifier
        FUNCTION_RX_SERIAL, 0, 0, 0,  # functionMask (little-endian)
        0, 0, 0,                    # unused baud rates
        PERIPH_BAUD_420000         # periph_baud = 420000 for CRSF
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_CF_SERIAL_CONFIG'], data=serial_config):
        dataHandler = board.receive_msg()

    print("  ✓ UART2 set to SERIAL_RX @ 420000 baud")
    print()

    # ========================================================================
    # STEP 3: Set receiver type to SERIAL and protocol to CRSF
    # ========================================================================
    print("[3/5] Setting receiver: type=SERIAL, protocol=CRSF...")

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
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # [12-22] padding (11 bytes)
        RX_TYPE_SERIAL              # [23] receiverType = SERIAL
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_RX_CONFIG'], data=rx_config):
        dataHandler = board.receive_msg()

    print(f"  ✓ Receiver type: SERIAL ({RX_TYPE_SERIAL})")
    print(f"  ✓ Serial RX provider: CRSF ({SERIALRX_CRSF})")
    print()

    # ========================================================================
    # STEP 4: Enable TELEMETRY feature
    # ========================================================================
    print("[4/5] Enabling TELEMETRY feature...")

    if board.send_RAW_msg(MSPCodes['MSP_FEATURE_CONFIG'], data=[]):
        dataHandler = board.receive_msg()
        board.process_recv_data(dataHandler)

    current_features = board.FEATURE_CONFIG.get('featureMask', 0)
    FEATURE_TELEMETRY = 0x400

    new_features = current_features | FEATURE_TELEMETRY
    data = struct.pack('<I', new_features)

    if board.send_RAW_msg(MSPCodes['MSP_SET_FEATURE_CONFIG'], data=list(data)):
        dataHandler = board.receive_msg()

    print(f"  ✓ TELEMETRY enabled (0x{new_features:08X})")
    print()

    # ========================================================================
    # STEP 5: Save and reboot
    # ========================================================================
    print("[5/5] Saving configuration and rebooting...")

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
print("Wait 10 seconds for SITL to restart, then check for:")
print("  [CRSF TELEM] initCrsfTelemetry called, crsfRxIsActive=1, enabled=1")
print("  [CRSF TELEM] handleCrsfTelemetry called, telemetry ENABLED")
print()
