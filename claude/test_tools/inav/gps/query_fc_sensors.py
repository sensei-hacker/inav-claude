#!/usr/bin/env python3
"""
Query Flight Controller Sensor Status

Diagnose ARMING_DISABLED_HARDWARE_FAILURE by checking sensor health.

Usage:
    python3 query_fc_sensors.py --port /dev/ttyACM0
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
MSP_STATUS = 101
MSP_STATUS_EX = 150
MSP_SENSOR_STATUS = 151
MSP_ANALOG = 110
MSP_RAW_IMU = 102
MSP_ALTITUDE = 109
MSP_COMP_GPS = 107

def main():
    parser = argparse.ArgumentParser(description='Query FC sensor status')
    parser.add_argument('--port', type=str, default='/dev/ttyACM1',
                        help='Serial port (default: /dev/ttyACM1)')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Baud rate (default: 115200)')

    args = parser.parse_args()

    print("=" * 70)
    print("Flight Controller Sensor Diagnostic")
    print("=" * 70)
    print()
    print(f"Connecting to {args.port}...")

    try:
        with MSPy(device=args.port, baudrate=args.baud, use_tcp=False, loglevel='WARNING') as board:
            if board == 1:
                print("✗ Connection failed")
                return 1

            # Get FC info
            board.send_RAW_msg(2, data=[])
            board.receive_msg()
            variant = board.CONFIG.get('flightControllerIdentifier', 'Unknown')

            print(f"✓ Connected to {variant}")
            print()

            # Query MSP2_INAV_STATUS for detailed arming flags
            print("[1] Arming Status")
            print("-" * 70)
            board.send_RAW_msg(0x2000, data=[])
            board.receive_msg()

            flags = board.CONFIG.get('armingDisableFlags', 0)
            mode = board.CONFIG.get('mode', 0)
            armed = (mode & 0x01) != 0

            print(f"Armed: {armed}")
            print(f"Arming flags: 0x{flags:08X}")

            flag_names = {
                0x00000001: 'FAILSAFE_SYSTEM',
                0x00000002: 'NOT_LEVEL',
                0x00000004: 'SENSORS_CALIBRATING',
                0x00000008: 'SYSTEM_OVERLOADED',
                0x00000010: 'NAVIGATION_UNSAFE',
                0x00000020: 'COMPASS_NOT_CALIBRATED',
                0x00000040: 'ACCELEROMETER_NOT_CALIBRATED',
                0x00000080: 'ARM_SWITCH',
                0x00000200: 'HARDWARE_FAILURE',
                0x00001000: 'BOXFAILSAFE',
                0x00002000: 'BOXKILLSWITCH',
                0x00004000: 'RC_LINK',
                0x00008000: 'THROTTLE',
                0x00010000: 'CLI',
                0x00020000: 'CMS_MENU',
                0x00040000: 'MSP',
                0x00080000: 'PARALYZE',
                0x00100000: 'GPS',
                0x00200000: 'RESC',
                0x00400000: 'RPMFILTER',
                0x00800000: 'REBOOT_REQUIRED',
                0x01000000: 'DSHOT_BEEPER',
                0x02000000: 'LANDING_DETECTED',
            }

            if flags != 0:
                print("Active blockers:")
                for flag, name in flag_names.items():
                    if flags & flag:
                        print(f"  - {name} (0x{flag:08X})")
            else:
                print("  None - ready to arm!")

            print()

            # Query sensor status
            print("[2] Sensor Status (MSP_SENSOR_STATUS)")
            print("-" * 70)
            board.send_RAW_msg(MSP_SENSOR_STATUS, data=[])
            try:
                board.receive_msg()
                if 'SENSOR_STATUS' in board.CONFIG:
                    sensor_status = board.CONFIG['SENSOR_STATUS']
                    print(f"Sensor status data: {sensor_status}")
                else:
                    print("No SENSOR_STATUS data returned")
            except Exception as e:
                print(f"Error querying sensor status: {e}")

            print()

            # Query IMU
            print("[3] IMU Data (MSP_RAW_IMU)")
            print("-" * 70)
            board.send_RAW_msg(MSP_RAW_IMU, data=[])
            try:
                board.receive_msg()
                if 'RAW_IMU' in board.CONFIG:
                    imu = board.CONFIG['RAW_IMU']
                    print(f"Accelerometer: {imu.get('accx', 0)}, {imu.get('accy', 0)}, {imu.get('accz', 0)}")
                    print(f"Gyroscope:     {imu.get('gyrx', 0)}, {imu.get('gyry', 0)}, {imu.get('gyrz', 0)}")
                    print(f"Magnetometer:  {imu.get('magx', 0)}, {imu.get('magy', 0)}, {imu.get('magz', 0)}")
                else:
                    print("No RAW_IMU data returned")
            except Exception as e:
                print(f"Error querying IMU: {e}")

            print()

            # Query analog/voltage
            print("[4] Analog Sensors (MSP_ANALOG)")
            print("-" * 70)
            board.send_RAW_msg(MSP_ANALOG, data=[])
            try:
                board.receive_msg()
                if 'ANALOG' in board.CONFIG:
                    analog = board.CONFIG['ANALOG']
                    print(f"Battery voltage: {analog.get('voltage', 0) / 10:.2f}V")
                    print(f"Battery current: {analog.get('amperage', 0) / 100:.2f}A")
                    print(f"RSSI: {analog.get('rssi', 0)}")
                else:
                    print("No ANALOG data returned")
            except Exception as e:
                print(f"Error querying analog: {e}")

            print()

            # Query altitude/baro
            print("[5] Altitude/Barometer (MSP_ALTITUDE)")
            print("-" * 70)
            board.send_RAW_msg(MSP_ALTITUDE, data=[])
            try:
                board.receive_msg()
                if 'ALTITUDE' in board.CONFIG:
                    alt = board.CONFIG['ALTITUDE']
                    print(f"Estimated altitude: {alt.get('altitude', 0) / 100:.2f}m")
                    print(f"Vertical speed: {alt.get('vario', 0)}cm/s")
                else:
                    print("No ALTITUDE data returned")
            except Exception as e:
                print(f"Error querying altitude: {e}")

            print()

            # Check active sensors
            print("[6] Active Sensors")
            print("-" * 70)
            active_sensors = board.CONFIG.get('activeSensors', 0)
            print(f"Active sensors bitmask: 0x{active_sensors:08X}")

            sensor_bits = {
                0x01: 'ACC (Accelerometer)',
                0x02: 'BARO (Barometer)',
                0x04: 'MAG (Magnetometer/Compass)',
                0x08: 'GPS',
                0x10: 'RANGEFINDER',
                0x20: 'OPFLOW (Optical Flow)',
                0x40: 'PITOT (Airspeed)',
                0x80: 'TEMP (Temperature)',
            }

            detected = []
            for bit, name in sensor_bits.items():
                if active_sensors & bit:
                    detected.append(name)

            if detected:
                print("Detected sensors:")
                for sensor in detected:
                    print(f"  ✓ {sensor}")
            else:
                print("⚠ No sensors detected!")

            print()
            print("=" * 70)
            print("Diagnostic Complete")
            print("=" * 70)

            return 0

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
