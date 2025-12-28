#!/usr/bin/env python3
"""
Configure Hardware FC for MSP Receiver and Test Arming

Configures flight controller to accept RC via MSP and sets up ARM mode.

Usage:
    python3 configure_fc_msp_rx.py --port /dev/ttyACM0
"""

import sys
import time
import struct
import argparse
import os

# Add uNAVlib to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)
from unavlib.main import MSPy

# MSP commands
MSP_SERIAL_CONFIG = 54
MSP_SET_SERIAL_CONFIG = 55
MSP_SET_RAW_RC = 200
MSP_EEPROM_WRITE = 250
MSP_REBOOT = 68
MSP_SIMULATOR = 0x201F

# Serial function bits
FUNCTION_MSP = 1

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000


def send_rc(board, throttle=RC_LOW, aux1=RC_HIGH):
    """Send RC data (AETR order)."""
    channels = [RC_MID, RC_MID, throttle, RC_MID, aux1] + [RC_MID] * 11
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
    board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
    try:
        board.receive_msg()
    except:
        pass


def main():
    parser = argparse.ArgumentParser(description='Configure FC for MSP receiver and test arming')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0',
                        help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Baud rate (default: 115200)')

    args = parser.parse_args()

    print("=" * 70)
    print("Hardware FC MSP RX Configuration")
    print("=" * 70)
    print()
    print(f"Connecting to {args.port}...")

    try:
        with MSPy(device=args.port, baudrate=args.baud, use_tcp=False, loglevel='WARNING') as board:
            if board == 1:
                print("✗ Connection failed")
                return 1

            # Get FC info
            board.send_RAW_msg(2, data=[])  # MSP_FC_VARIANT
            board.receive_msg()
            variant = board.CONFIG.get('flightControllerIdentifier', 'Unknown')

            board.send_RAW_msg(3, data=[])  # MSP_FC_VERSION
            board.receive_msg()
            version = board.CONFIG.get('flightControllerVersion', 'Unknown')

            print(f"Connected! FC: {variant}")
            print(f"API Version: {board.CONFIG.get('apiVersion', 'Unknown')}")

            # Get initial arming flags
            board.send_RAW_msg(0x2000, data=[])  # MSP2_INAV_STATUS
            board.receive_msg()
            initial_flags = board.CONFIG.get('armingDisableFlags', 0)
            print(f"Initial arming flags: 0x{initial_flags:08X}")

            # Decode arming flags
            flag_names = {
                0x00000001: 'ARMING_DISABLED_FAILSAFE_SYSTEM',
                0x00000002: 'ARMING_DISABLED_NOT_LEVEL',
                0x00000004: 'ARMING_DISABLED_SENSORS_CALIBRATING',
                0x00000008: 'ARMING_DISABLED_SYSTEM_OVERLOADED',
                0x00000010: 'ARMING_DISABLED_NAVIGATION_UNSAFE',
                0x00000020: 'ARMING_DISABLED_COMPASS_NOT_CALIBRATED',
                0x00000040: 'ARMING_DISABLED_ACCELEROMETER_NOT_CALIBRATED',
                0x00000080: 'ARMING_DISABLED_ARM_SWITCH',
                0x00000200: 'ARMING_DISABLED_HARDWARE_FAILURE',
                0x00001000: 'ARMING_DISABLED_BOXFAILSAFE',
                0x00002000: 'ARMING_DISABLED_BOXKILLSWITCH',
                0x00004000: 'ARMING_DISABLED_RC_LINK',
                0x00008000: 'ARMING_DISABLED_THROTTLE',
                0x00010000: 'ARMING_DISABLED_CLI',
                0x00020000: 'ARMING_DISABLED_CMS_MENU',
                0x00040000: 'ARMING_DISABLED_MSP',
                0x00080000: 'ARMING_DISABLED_PARALYZE',
                0x00100000: 'ARMING_DISABLED_GPS',
                0x00200000: 'ARMING_DISABLED_RESC',
                0x00400000: 'ARMING_DISABLED_RPMFILTER',
                0x00800000: 'ARMING_DISABLED_REBOOT_REQUIRED',
                0x01000000: 'ARMING_DISABLED_DSHOT_BEEPER',
                0x02000000: 'ARMING_DISABLED_LANDING_DETECTED',
            }

            for flag, name in flag_names.items():
                if initial_flags & flag:
                    print(f"  - {name}")

            print()
            print("[Step 1] Clearing UART2 functions (for MSP receiver)...")

            # For MSP receiver type, RC data comes via MSP_SET_RAW_RC on the
            # existing MSP connection (USB VCP), NOT via a dedicated UART.
            # So UART2 should have NO receiver-related functions.

            setting_name = b'serial_2_function\0'
            # Function value: 0 = NONE (clear RX_SERIAL if it was set)
            setting_value = struct.pack('<i', 0)
            payload = setting_name + setting_value

            print(f"  Setting serial_2_function = 0 (NONE)")
            print(f"  (MSP receiver uses existing MSP connection, not UART)")
            board.send_RAW_msg(0x1004, data=list(payload))  # MSP2_COMMON_SET_SETTING
            try:
                board.receive_msg()
                print(f"  ✓ UART2 function cleared")
            except:
                print(f"  ⚠ Could not confirm setting (may still have worked)")
            time.sleep(0.2)

            print()
            print("[Step 2] Setting receiver type to MSP...")

            # Read current RX config
            board.send_RAW_msg(44, data=[])  # MSP_RX_CONFIG
            board.receive_msg()

            if 'RX_CONFIG' in board.CONFIG:
                rx_config = board.CONFIG['RX_CONFIG']
                print(f"  Current RX config length: {len(rx_config)} bytes")
                if len(rx_config) >= 24:
                    current_receiver_type = rx_config[23]
                    print(f"  Current receiver type: {current_receiver_type}")

                    # Set to MSP (type 2)
                    rx_config_list = list(rx_config)
                    rx_config_list[23] = 2  # MSP receiver
                    print(f"  Setting receiver type to MSP (2)")

                    # Send updated config
                    board.send_RAW_msg(45, data=rx_config_list)  # MSP_SET_RX_CONFIG
                    try:
                        board.receive_msg()
                    except:
                        pass
                    time.sleep(0.2)

            print()
            print("[Step 2b] Setting up ARM mode activation...")

            # Set ARM mode on AUX1 (slot 0, box BOXARM, aux channel 0, range 1700-2100)
            # MSP_SET_MODE_RANGE format: slot(u8), box(u8), aux(u8), start(u16), end(u16)
            BOXARM = 0
            mode_range_data = [
                0,      # slot 0
                BOXARM, # BOXARM
                0,      # AUX1 (aux channel 0)
                170,    # start range (1700us - 900us) / 25 = 32 -> but we use raw value 170
                210     # end range (2100us - 900us) / 25 = 48 -> but we use raw value 210
            ]

            # The range values are ((value - 900) / 25)
            # So for 1700: (1700 - 900) / 25 = 32
            # For 2100: (2100 - 900) / 25 = 48
            mode_range_data_packed = struct.pack('<BBBBB', 0, BOXARM, 0, 32, 48)

            print(f"  Setting ARM mode: slot=0, box=BOXARM, aux=AUX1, range=1700-2100")
            board.send_RAW_msg(35, data=list(mode_range_data_packed))  # MSP_SET_MODE_RANGE
            try:
                board.receive_msg()
            except:
                pass
            time.sleep(0.2)

            print("  Saving config to EEPROM...")
            board.send_RAW_msg(MSP_EEPROM_WRITE, data=[])
            try:
                board.receive_msg()
            except:
                pass
            time.sleep(1)

            print()
            print("[Step 3] Rebooting FC to apply configuration...")
            print("  Reboot command sent. Waiting for FC to restart...")
            board.send_RAW_msg(MSP_REBOOT, data=[])
            time.sleep(5)

        # Reconnect after reboot (device path may have changed)
        print()
        print("[Step 4] Reconnecting to FC after reboot...")
        print("  Waiting for device to appear...")
        time.sleep(3)

        # Try to find the device (may be /dev/ttyACM0 or /dev/ttyACM1)
        import glob
        devices = sorted(glob.glob('/dev/ttyACM*'))
        if not devices:
            print("✗ No /dev/ttyACM* devices found")
            return 1

        reconnect_port = devices[0]  # Use the first available
        print(f"  Found device: {reconnect_port}")

        with MSPy(device=reconnect_port, baudrate=args.baud, use_tcp=False, loglevel='WARNING') as board:
            if board == 1:
                print("✗ Reconnection failed")
                return 1

            board.send_RAW_msg(2, data=[])  # MSP_FC_VARIANT
            board.receive_msg()
            variant = board.CONFIG.get('flightControllerIdentifier', 'Unknown')
            print(f"Reconnected! FC: {variant}")

            # Verify receiver type
            board.send_RAW_msg(44, data=[])  # MSP_RX_CONFIG
            board.receive_msg()
            if 'RX_CONFIG' in board.CONFIG:
                rx_config = board.CONFIG['RX_CONFIG']
                if len(rx_config) >= 24:
                    receiver_type = rx_config[23]
                    print(f"  Receiver type after reboot: {receiver_type} {'(MSP)' if receiver_type == 2 else ''}")

            # Check arming flags
            board.send_RAW_msg(0x2000, data=[])  # MSP2_INAV_STATUS
            board.receive_msg()
            flags = board.CONFIG.get('armingDisableFlags', 0)
            print(f"Arming flags after reboot: 0x{flags:08X}")

            for flag, name in flag_names.items():
                if flags & flag:
                    print(f"  - {name}")

            print()
            print("[Step 4b] Enabling HITL mode to bypass sensor calibration...")
            print("  Enabling HITL simulator mode...")
            hitl_data = struct.pack('<B', 1)
            board.send_RAW_msg(MSP_SIMULATOR, data=list(hitl_data))
            try:
                board.receive_msg()
            except:
                pass
            time.sleep(0.5)

            print()
            print("[Step 5] Establishing RC link (sending RC data every 50ms)...")
            print("  RC link should be established after 2s of continuous data")

            # Send RC for 2 seconds
            for i in range(40):
                send_rc(board)
                time.sleep(0.05)

            # Check RC values
            board.send_RAW_msg(105, data=[])  # MSP_RC
            board.receive_msg()
            if 'RC' in board.CONFIG:
                rc_channels = board.CONFIG['RC']
                print(f"  RC channels read from FC: {rc_channels[:5]}...")

            print()
            print("[Step 6] Querying arming status (while sending RC)...")

            for i in range(10):
                send_rc(board)
                time.sleep(0.05)

                if i % 3 == 0:
                    board.send_RAW_msg(0x2000, data=[])  # MSP2_INAV_STATUS
                    board.receive_msg()
                    flags = board.CONFIG.get('armingDisableFlags', 0)
                    mode = board.CONFIG.get('mode', 0)

                    print(f"  Arming flags: 0x{flags:04X}")
                    if flags != 0:
                        print("  Active flags:")
                        for flag, name in flag_names.items():
                            if flags & flag:
                                print(f"    - {name}")

            print()
            print("[Step 7] Attempting to arm (AUX1 high, throttle low)...")

            for i in range(20):
                send_rc(board, throttle=RC_LOW, aux1=RC_HIGH)
                time.sleep(0.05)

                if i % 5 == 0:
                    board.send_RAW_msg(0x2000, data=[])  # MSP2_INAV_STATUS
                    board.receive_msg()
                    mode = board.CONFIG.get('mode', 0)
                    armed = (mode & 0x01) != 0

                    if armed:
                        print(f"  t={(i*0.05):.1f}s: ARMED!")
                        break

            print()
            print("[Final] Checking final status...")
            board.send_RAW_msg(0x2000, data=[])  # MSP2_INAV_STATUS
            board.receive_msg()
            flags = board.CONFIG.get('armingDisableFlags', 0)
            mode = board.CONFIG.get('mode', 0)
            armed = (mode & 0x01) != 0

            print(f"  Final arming flags: 0x{flags:08X}")
            if flags != 0:
                for flag, name in flag_names.items():
                    if flags & flag:
                        print(f"    - {name}")

            if armed:
                print()
                print("  SUCCESS: FC is ARMED!")
                print()
                print("=" * 70)
                print("Configuration Complete!")
                print("=" * 70)
                print()
                print("Next steps:")
                print("1. Immediately run GPS injection test (FC is armed):")
                print(f"   python3 claude/test_tools/inav/gps/gps_with_rc_keeper.py \\")
                print(f"     --port {reconnect_port} --profile climb --duration 30")
                print()
                print("   NOTE: Must start within ~200ms or FC will disarm!")
                print()
                return 0
            else:
                print()
                print("  FC failed to arm. Check arming blockers above.")
                return 1

    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
