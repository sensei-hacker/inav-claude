#!/usr/bin/env python3
"""
Configure SITL for CRSF Telemetry Testing

Uses uNAVlib to enable CRSF RX on UART2, which automatically enables CRSF telemetry.
Also configures HITL mode and ARM activation for full telemetry testing.
"""

import sys
import time
import struct
import os

# Add uNAVlib to path (relative to this script's location)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)

from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

# MSP command codes not in uNAVlib
MSP_SIMULATOR = 0x201F  # Enable HITL mode
MSP_SET_MODE_RANGE = 35  # Set mode activation range

# Constants
SIMULATOR_MSP_VERSION = 2
HITL_ENABLE = 1
BOXARM = 0  # ARM mode box ID


def enable_hitl_mode(port=5760):
    """
    Enable HITL (Hardware-In-The-Loop) simulator mode.

    This bypasses sensor calibration requirements. Must be called
    after every boot as it's not saved to EEPROM.

    Args:
        port: MSP port number (default 5760)

    Returns:
        True if successful, False otherwise
    """
    print(f"Enabling HITL mode on port {port}...")

    with MSPy(device=str(port), use_tcp=True, loglevel='WARNING') as board:
        if board == 1:
            print("✗ Connection failed")
            return False

        # Send MSP_SIMULATOR with HITL_ENABLE flag
        payload = [SIMULATOR_MSP_VERSION, HITL_ENABLE]
        board.send_RAW_msg(MSP_SIMULATOR, data=payload)
        time.sleep(0.1)

        try:
            board.receive_msg()
        except:
            pass

        print("✓ HITL mode enabled")
        return True


def setup_arm_mode(board):
    """
    Configure ARM mode to activate on AUX1 (channel 5) when value > 1700.

    MSP_SET_MODE_RANGE payload:
    - byte 0: slot index (0-39)
    - byte 1: box permanent ID (BOXARM = 0)
    - byte 2: aux channel index (0 = AUX1 = channel 5)
    - byte 3: range start step ((1700-900)/25 = 32)
    - byte 4: range end step ((2100-900)/25 = 48)
    """
    slot_index = 0
    box_id = BOXARM
    aux_channel = 0  # AUX1
    start_step = 32  # 1700
    end_step = 48    # 2100

    payload = [slot_index, box_id, aux_channel, start_step, end_step]
    print(f"  Setting ARM mode: AUX1 range 1700-2100")
    board.send_RAW_msg(MSP_SET_MODE_RANGE, data=payload)
    time.sleep(0.1)

    try:
        board.receive_msg()
    except:
        pass


def configure_crsf_telemetry(auto_reboot=True):
    """Configure SITL UART2 for CRSF RX/Telemetry

    Args:
        auto_reboot: If True, automatically reboot SITL after saving config.
                     If False, save config and return (caller must reboot).
    """

    print("=" * 70)
    print("SITL CRSF Configuration Script")
    print("=" * 70)

    # Connect to SITL MSP port
    print("\nConnecting to SITL on port 5760...")

    with MSPy(device="5760", use_tcp=True, loglevel='WARNING') as board:
        if board == 1:
            print("✗ Connection failed!")
            return

        try:
            print("✓ Connected to SITL")
            print(f"FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")

            # Get current serial config
            print("\nReading current serial configuration...")
            if board.send_RAW_msg(MSPCodes['MSP2_COMMON_SERIAL_CONFIG'], data=[]):
                dataHandler = board.receive_msg()
                board.process_recv_data(dataHandler)

            if hasattr(board, 'SERIAL_CONFIG') and 'ports' in board.SERIAL_CONFIG:
                print(f"✓ Found {len(board.SERIAL_CONFIG['ports'])} serial ports")

                # Display current config
                for port in board.SERIAL_CONFIG['ports']:
                    print(f"  UART{port['identifier']}: functions={port['functions']}")

            # Configure UART2 for CRSF RX
            # UART identifier: 1 (UART2)
            # Function mask: 64 (FUNCTION_RX_SERIAL)
            # Baudrate: 420000 (CRSF standard)

            print("\nConfiguring UART2 for CRSF...")
            print("  Function: RX_SERIAL (0x40 = 64)")
            print("  Baudrate: 420000")

            # MSP2_COMMON_SET_SERIAL_CONFIG format: <BIBBBB
            # B = identifier (1 for UART2)
            # I = functionMask (64 for RX_SERIAL)
            # B = msp_baudrate_index (not used for RX)
            # B = gps_baudrate_index (not used)
            # B = telemetry_baudrate_index (not used)
            # B = peripheral_baudrate_index (CRSF baudrate)

            # Baudrate index for 420000 (need to find correct index)
            # Common baudrates: 0=auto, 1=9600, 2=19200, 3=38400, 4=57600, 5=115200, 6=230400, 7=250000, 8=400000, 9=460800
            # CRSF uses 420000, might need index 8 (400000) or custom

            uart_id = 1  # UART2
            function_mask = 64  # FUNCTION_RX_SERIAL
            msp_baud = 0
            gps_baud = 0
            telem_baud = 0
            periph_baud = 5  # Try 115200 first, then adjust

            data = struct.pack('<BIBBBB', uart_id, function_mask, msp_baud, gps_baud, telem_baud, periph_baud)

            print(f"\nSending config: UART{uart_id + 1}, mask=0x{function_mask:X}, periph_baud={periph_baud}")

            if board.send_RAW_msg(MSPCodes['MSP2_COMMON_SET_SERIAL_CONFIG'], data=list(data)):
                dataHandler = board.receive_msg()
                print("✓ Configuration sent")

            # Configure RX provider to use CRSF
            print("\nConfiguring RX provider for CRSF...")
            print("  RX Receiver Type: RX_TYPE_SERIAL (1)")
            print("  Serial RX Provider: SERIALRX_CRSF (6)")

            # Get current RX config to preserve existing settings
            if board.send_RAW_msg(MSPCodes['MSP_RX_CONFIG'], data=[]):
                dataHandler = board.receive_msg()
                board.process_recv_data(dataHandler)

            # Enable TELEMETRY and GPS feature flags
            print("\nEnabling feature flags (TELEMETRY, GPS)...")

            # Read current features
            if board.send_RAW_msg(MSPCodes['MSP_FEATURE_CONFIG'], data=[]):
                dataHandler = board.receive_msg()
                board.process_recv_data(dataHandler)

            features = board.FEATURE_CONFIG.get('featureMask', 0)
            FEATURE_GPS = 0x80         # Bit 7
            FEATURE_TELEMETRY = 0x400  # Bit 10

            print(f"  Current features: 0x{features:08X}")

            # Check and enable GPS
            if features & FEATURE_GPS:
                print("  ✓ GPS already enabled")
            else:
                print("  Enabling GPS feature...")

            # Check and enable TELEMETRY
            if features & FEATURE_TELEMETRY:
                print("  ✓ TELEMETRY already enabled")
            else:
                print("  Enabling TELEMETRY feature...")

            # Set both features
            new_features = features | FEATURE_GPS | FEATURE_TELEMETRY
            if new_features != features:
                data = struct.pack('<I', new_features)
                if board.send_RAW_msg(MSPCodes['MSP_SET_FEATURE_CONFIG'], data=list(data)):
                    dataHandler = board.receive_msg()
                print(f"  ✓ Features updated: 0x{new_features:08X}")
            else:
                print("  ✓ All required features already enabled")

            # Get current config or use defaults
            current_rx_config = board.RX_CONFIG if hasattr(board, 'RX_CONFIG') else {}

            # MSP_SET_RX_CONFIG format (from src/main/fc/fc_msp.c:2964-2987):
            # byte 0:    serialrx_provider (SERIALRX_CRSF = 6)
            # bytes 1-2: maxcheck (uint16, use default 1900)
            # bytes 3-4: midrc (uint16, ignored, use 1500)
            # bytes 5-6: mincheck (uint16, use default 1100)
            # byte 7:    spektrum_sat_bind (use 0)
            # bytes 8-9: rx_min_usec (uint16, use 885)
            # bytes 10-11: rx_max_usec (uint16, use 2115)
            # bytes 12-22: compatibility bytes (11 bytes)
            # byte 23:   receiverType (RX_TYPE_SERIAL = 1)

            rx_config = []
            rx_config.append(6)  # byte 0: serialrx_provider = SERIALRX_CRSF
            rx_config += list(struct.pack('<H', 1900))  # bytes 1-2: maxcheck
            rx_config += list(struct.pack('<H', 1500))  # bytes 3-4: midrc
            rx_config += list(struct.pack('<H', 1100))  # bytes 5-6: mincheck
            rx_config.append(0)  # byte 7: spektrum_sat_bind
            rx_config += list(struct.pack('<H', 885))   # bytes 8-9: rx_min_usec
            rx_config += list(struct.pack('<H', 2115))  # bytes 10-11: rx_max_usec
            rx_config += [0] * 11  # bytes 12-22: compatibility padding
            rx_config.append(1)  # byte 23: receiverType = RX_TYPE_SERIAL

            if board.send_RAW_msg(MSPCodes['MSP_SET_RX_CONFIG'], data=rx_config):
                dataHandler = board.receive_msg()
                print("✓ RX provider configured (byte 0=6 CRSF, byte 23=1 SERIAL)")

            # Setup ARM mode activation on AUX1
            print("\nConfiguring ARM mode activation...")
            setup_arm_mode(board)
            print("✓ ARM mode configured (AUX1 > 1700)")

            # Save configuration
            print("\nSaving configuration...")
            if board.send_RAW_msg(MSPCodes['MSP_EEPROM_WRITE'], data=[]):
                time.sleep(0.5)
                print("✓ Configuration saved to EEPROM")

            if auto_reboot:
                # Reboot to persist eeprom.bin to disk
                print("\nRebooting SITL to persist configuration...")
                board.send_RAW_msg(MSPCodes['MSP_REBOOT'], data=[])
                print("✓ Reboot command sent")
                print("  Waiting 15 seconds for SITL to restart and initialize EEPROM...")

                print("\n" + "=" * 70)
                print("Configuration Complete!")
                print("=" * 70)
                print("\nNext steps:")
                print("1. Wait 15 seconds for SITL to fully restart")
                print("2. Verify UART2 is listening: ss -tlnp | grep 5761")
                print("3. Run: python3 crsf_stream_parser.py 2")
                print("4. You should see CRSF telemetry frames")
            else:
                print("\n" + "=" * 70)
                print("Configuration saved (reboot deferred)")
                print("=" * 70)
                print("\nIMPORTANT: You must reboot SITL for config to take effect")
                print("Caller is responsible for:")
                print("1. Starting RC sender")
                print("2. Sending MSP_REBOOT command")
                print("3. Waiting for SITL to restart")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    auto_reboot = True
    if len(sys.argv) > 1 and sys.argv[1] == "--no-reboot":
        auto_reboot = False
    configure_crsf_telemetry(auto_reboot=auto_reboot)
