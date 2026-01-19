#!/usr/bin/env python3
"""
Simple Settings Save Test - Minimal version for quick testing

This script simply triggers MSP_EEPROM_WRITE once per second.
Monitor motor output with oscilloscope to see if DMA stalls during flash write.

Usage:
    python3 test_settings_save_simple.py [port] [interval]

Examples:
    python3 test_settings_save_simple.py                    # defaults
    python3 test_settings_save_simple.py /dev/ttyUSB0       # different port
    python3 test_settings_save_simple.py /dev/ttyACM0 0.5   # save every 0.5s

Safety: PROPS OFF
"""

import sys
import time
import serial

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

    print(f"Settings Save Test")
    print(f"Don't forget to disconnect Configurator!")
    print(f"Port: {port}, Interval: {interval}s")
    print(f"⚠️  PROPS OFF - ARM FC - OBSERVE SCOPE")
    print()

    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"✓ Connected to {port}")
    except serial.SerialException as e:
        print(f"✗ FAILED to connect to {port}: {e}")
        print(f"  Check:")
        print(f"  - Is FC plugged in?")
        print(f"  - Is configurator closed?")
        print(f"  - Does {port} exist? (try: ls /dev/ttyACM*)")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error opening serial port: {e}")
        return 1

    # MSP v2 EEPROM_WRITE command
    # Header: '$','X','<', 0(flag), 250(cmd_low), 0(cmd_high), 0(size_low), 0(size_high), CRC
    # MSP_EEPROM_WRITE = 250 (0xFA)

    # MSPv1 is simpler for EEPROM_WRITE (no payload)
    # Format: $M<{size}{cmd}{checksum}
    msp_eeprom_write = b'$M<\x00\xFA\xFA'  # size=0, cmd=250, checksum=250

    # Verify FC is responding by sending a test command first
    print("Verifying FC is responding...")
    try:
        # Send MSP_API_VERSION (1) to verify connection
        msp_api_version = b'$M<\x00\x01\x01'
        ser.write(msp_api_version)
        time.sleep(0.1)

        # Check if we got any response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"✓ FC is responding (got {len(response)} bytes)")
        else:
            print(f"✗ WARNING: FC not responding to MSP commands")
            print(f"  The test will run but may not trigger settings saves!")
            print(f"  Check:")
            print(f"  - Is FC running INAV firmware?")
            print(f"  - Is configurator definitely closed?")
            user_input = input("Continue anyway? (y/N): ")
            if user_input.lower() != 'y':
                ser.close()
                return 1
    except Exception as e:
        print(f"✗ Error verifying FC connection: {e}")
        ser.close()
        return 1

    count = 0
    start_time = time.time()
    failed_writes = 0

    print("\n✓ Starting test - triggering saves... (Ctrl+C to stop)\n")

    try:
        while True:
            # Send EEPROM write command
            try:
                bytes_written = ser.write(msp_eeprom_write)
                if bytes_written != len(msp_eeprom_write):
                    print(f"✗ WARNING: Only wrote {bytes_written}/{len(msp_eeprom_write)} bytes")
                    failed_writes += 1
            except serial.SerialException as e:
                print(f"✗ FAILED to write MSP command: {e}")
                print(f"  Connection may be lost!")
                failed_writes += 1

            count += 1
            elapsed = time.time() - start_time

            # Show status with visual indicator
            status = "✓" if failed_writes == 0 else f"⚠ ({failed_writes} failed)"
            print(f"[{elapsed:6.1f}s] Save #{count} {status}")

            # Wait for interval
            time.sleep(interval)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\nStopped. {count} saves in {elapsed:.1f}s")
        print(f"Check scope for {interval}s gaps in DShot signal")

    finally:
        ser.close()


if __name__ == '__main__':
    main()
