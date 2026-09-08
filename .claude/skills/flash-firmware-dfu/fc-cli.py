#!/usr/bin/env python3
"""
fc-cli.py - Send CLI commands to INAV flight controller via serial

Usage:
  ./fc-cli.py dfu [port]              - Reboot to DFU mode
  ./fc-cli.py tasks [port]            - Show task execution times
  ./fc-cli.py status [port]           - Show FC status
  ./fc-cli.py <command> [port]        - Send custom CLI command and print output

Arguments:
  command: CLI command to send (e.g., 'dfu', 'tasks', 'status', 'version')
  port: Serial port (default: /dev/ttyACM0)

Examples:
  ./fc-cli.py dfu
  ./fc-cli.py tasks /dev/ttyUSB0
  ./fc-cli.py version
  ./fc-cli.py "get gyro_lpf1_static_hz"
"""

import sys
import time
import serial


class FlightControllerCLI:
    """
    Flight controller CLI interface.

    Handles entering CLI mode and sending commands to INAV flight controllers.
    """

    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        """
        Initialize CLI interface.

        Args:
            port: Serial port device path
            baudrate: Serial baud rate (default 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def enter_cli_mode(self, timeout=2.0):
        """
        Enter CLI mode by sending #### and waiting for CLI prompt.

        Args:
            timeout: Timeout in seconds waiting for CLI prompt

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Opening serial port: {self.port}")
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.5)
            time.sleep(0.1)  # Let port settle

            # Flush any existing data
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            # Send #### to enter CLI mode
            print("Entering CLI mode...")
            self.ser.write(b'####\r\n')
            self.ser.flush()

            # Wait for "CLI" prompt in response
            print("Waiting for CLI prompt...")
            start_time = time.time()
            received_data = b''

            while time.time() - start_time < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read(self.ser.in_waiting)
                    received_data += chunk

                    # Check if we received the CLI prompt
                    # Accept either "CLI" (fresh entry) or "#" (already in CLI mode)
                    if b'CLI' in received_data or b'#' in received_data:
                        print("✓ CLI mode entered successfully")
                        return True

                time.sleep(0.05)  # Small delay to avoid busy-waiting

            # Timeout occurred
            print(f"✗ ERROR: Timeout waiting for CLI prompt")
            print(f"Received: {received_data.decode('ascii', errors='replace')}")
            return False

        except serial.SerialException as e:
            print(f"✗ ERROR: Serial port error: {e}")
            return False
        except Exception as e:
            print(f"✗ ERROR: Unexpected error: {e}")
            return False

    def send_command(self, command, read_response=True, response_timeout=1.0):
        """
        Send a CLI command and optionally read the response.

        Args:
            command: CLI command to send (without \\r\\n)
            read_response: Whether to read and return the response
            response_timeout: How long to wait for response data

        Returns:
            Response string if read_response=True, None otherwise
        """
        if not self.ser or not self.ser.is_open:
            print("✗ ERROR: Serial port not open")
            return None

        try:
            # Send command
            cmd_bytes = f"{command}\r\n".encode('ascii')
            self.ser.write(cmd_bytes)
            self.ser.flush()
            print(f"Sent command: {command}")

            if not read_response:
                return None

            # Read response
            time.sleep(0.1)  # Give FC time to start responding
            start_time = time.time()
            response_data = b''
            last_data_time = time.time()

            while time.time() - start_time < response_timeout + 2.0:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read(self.ser.in_waiting)
                    response_data += chunk
                    last_data_time = time.time()
                elif time.time() - last_data_time > response_timeout:
                    # No new data for response_timeout seconds, assume done
                    break

                time.sleep(0.05)

            return response_data.decode('ascii', errors='replace')

        except Exception as e:
            print(f"✗ ERROR: Failed to send command: {e}")
            return None

    def close(self):
        """Close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed")


def cmd_dfu(cli):
    """
    DFU command handler - reboot to DFU bootloader mode.

    Args:
        cli: FlightControllerCLI instance (already in CLI mode)

    Returns:
        Exit code (0 for success)
    """
    print("\nSending DFU reboot command...")
    cli.send_command('dfu', read_response=False)
    time.sleep(0.2)
    cli.close()

    print("\nWaiting for DFU device to appear (10 seconds)...")
    time.sleep(10)

    # Verify DFU device
    import subprocess
    try:
        result = subprocess.run(['dfu-util', '-l'],
                                capture_output=True,
                                text=True,
                                timeout=5)

        if '0483:df11' in result.stdout:
            print("\n✓ SUCCESS: Flight controller is now in DFU mode\n")
            print(result.stdout)
            return 0
        else:
            print("\n⚠ WARNING: DFU device not detected. Check connection.")
            return 1

    except FileNotFoundError:
        print("\nNote: dfu-util not found, cannot verify DFU mode")
        print("Install with: sudo apt install dfu-util")
        return 0
    except Exception as e:
        print(f"\nNote: Could not verify DFU mode: {e}")
        return 0


def cmd_tasks(cli):
    """
    Tasks command handler - show task execution times.

    Args:
        cli: FlightControllerCLI instance (already in CLI mode)

    Returns:
        Exit code (0 for success)
    """
    response = cli.send_command('tasks', read_response=True, response_timeout=0.5)
    cli.send_command('exit', read_response=False)
    cli.close()

    if response:
        print("\n" + "="*60)
        print("Task Execution Times:")
        print("="*60)
        print(response)
        return 0
    else:
        print("✗ ERROR: No response received")
        return 1


def cmd_generic(cli, command):
    """
    Generic command handler - send command and print response.

    Args:
        cli: FlightControllerCLI instance (already in CLI mode)
        command: CLI command to send

    Returns:
        Exit code (0 for success)
    """
    response = cli.send_command(command, read_response=True, response_timeout=0.5)
    # Leave CLI mode so the FC returns to MSP — otherwise it stays latched in
    # CLI (visible as the CLI arming-disabled flag) and ignores MSP/RC frames
    # from any script that connects afterward.
    cli.send_command('exit', read_response=False)
    cli.close()

    if response:
        print("\n" + "="*60)
        print(f"Response to '{command}':")
        print("="*60)
        print(response)
        return 0
    else:
        print("✗ ERROR: No response received")
        return 1


# Command registry
# Maps command names to handler functions and descriptions
COMMANDS = {
    'dfu': {
        'handler': cmd_dfu,
        'description': 'Reboot to DFU bootloader mode',
        'read_response': False,
    },
    'tasks': {
        'handler': cmd_tasks,
        'description': 'Show task execution times',
        'read_response': True,
    },
    'status': {
        'handler': lambda cli: cmd_generic(cli, 'status'),
        'description': 'Show flight controller status',
        'read_response': True,
    },
    'version': {
        'handler': lambda cli: cmd_generic(cli, 'version'),
        'description': 'Show firmware version',
        'read_response': True,
    },
}


def print_usage():
    """Print usage information."""
    print(__doc__)
    print("\nAvailable commands:")
    for cmd, info in sorted(COMMANDS.items()):
        print(f"  {cmd:12} - {info['description']}")
    print("\nFor any other CLI command, just pass it as the first argument.")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return 1

    command = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else '/dev/ttyACM0'

    # Handle help
    if command in ['-h', '--help', 'help']:
        print_usage()
        return 0

    # Create CLI interface and enter CLI mode
    cli = FlightControllerCLI(port)

    if not cli.enter_cli_mode():
        print("\n✗ FAILED: Could not enter CLI mode")
        return 1

    # Execute command
    if command in COMMANDS:
        # Use registered handler
        return COMMANDS[command]['handler'](cli)
    else:
        # Generic command
        return cmd_generic(cli, command)


if __name__ == '__main__':
    sys.exit(main())
