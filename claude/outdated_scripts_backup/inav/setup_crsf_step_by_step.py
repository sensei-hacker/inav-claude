#!/usr/bin/env python3
"""
Step-by-step CRSF Configuration - Fix the timing issue

Step 1: Configure serial port for RX, save, reboot
Step 2: Configure RX type and protocol, save, reboot with RC already running
"""

import sys
import struct
import time

sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/uNAVlib')
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

MSP_PORT = "5760"

print("=" * 70)
print("STEP 1: Configure Serial Port for SERIAL_RX")
print("=" * 70)
print()

with MSPy(device=MSP_PORT, use_tcp=True, loglevel='WARNING') as board:
    if board == 1:
        print("✗ Connection failed")
        sys.exit(1)

    print("✓ Connected to SITL")
    print()

    # Step 1a: Configure UART2 for SERIAL_RX function
    print("[1] Configuring UART2 for SERIAL_RX...")

    FUNCTION_RX_SERIAL = 0x40
    PERIPH_BAUD_420000 = 5

    serial_config = [
        2,                          # UART2
        FUNCTION_RX_SERIAL, 0, 0, 0,  # function_mask
        0, 0, 0,                    # unused bauds
        PERIPH_BAUD_420000         # periph_baud
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_CF_SERIAL_CONFIG'], data=serial_config):
        dataHandler = board.receive_msg()

    print("  ✓ UART2 set to SERIAL_RX function")
    print()

    # Step 1b: Enable TELEMETRY feature
    print("[2] Enabling TELEMETRY feature...")

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

    # Step 1c: Save and reboot
    print("[3] Saving and rebooting...")

    if board.send_RAW_msg(MSPCodes['MSP_EEPROM_WRITE'], data=[]):
        time.sleep(0.5)

    print("  ✓ Saved to EEPROM")

    board.send_RAW_msg(MSPCodes['MSP_REBOOT'], data=[])
    print("  ✓ Reboot command sent")
    print()

print("=" * 70)
print("STEP 1 COMPLETE - Wait 10 seconds for reboot")
print("=" * 70)
print()
time.sleep(10)

print("=" * 70)
print("STEP 2: Configure RX Type and Protocol")
print("=" * 70)
print()

with MSPy(device=MSP_PORT, use_tcp=True, loglevel='WARNING') as board:
    if board == 1:
        print("✗ Connection failed after reboot")
        sys.exit(1)

    print("✓ Reconnected to SITL")
    print()

    # Step 2a: Configure RX provider
    print("[1] Configuring RX: type=SERIAL, protocol=CRSF...")

    SERIALRX_CRSF = 6
    RX_TYPE_SERIAL = 1

    rx_config = [
        SERIALRX_CRSF,              # provider = CRSF
        0x6C, 0x07,                 # maxcheck = 1900
        0xDC, 0x05,                 # midrc = 1500
        0x4C, 0x04,                 # mincheck = 1100
        0,                          # spektrum_sat_bind
        0x75, 0x03,                 # rx_min_usec = 885
        0x43, 0x08,                 # rx_max_usec = 2115
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # padding
        RX_TYPE_SERIAL              # receiverType = SERIAL
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_RX_CONFIG'], data=rx_config):
        dataHandler = board.receive_msg()

    print("  ✓ RX configured (SERIAL + CRSF)")
    print()

    # Step 2b: Save
    print("[2] Saving configuration...")

    if board.send_RAW_msg(MSPCodes['MSP_EEPROM_WRITE'], data=[]):
        time.sleep(0.5)

    print("  ✓ Saved to EEPROM")
    print()

print("=" * 70)
print("CONFIGURATION COMPLETE")
print("=" * 70)
print()
print("Next steps:")
print("  1. Start RC sender: python3 crsf_rc_sender.py 2 --rate 50 &")
print("  2. Wait 2 seconds")
print("  3. Reboot SITL (it will reload with RC already active)")
print("  4. Check log for: [CRSF TELEM] initCrsfTelemetry called, crsfRxIsActive=1")
print()
