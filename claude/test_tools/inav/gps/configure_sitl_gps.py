#!/usr/bin/env python3
"""Configure SITL for MSP GPS testing."""

import time
from mspapi2 import MSPApi

def configure_gps():
    """Configure SITL to use MSP GPS."""
    print("Connecting to SITL on port 5761...")
    api = MSPApi(tcp_endpoint='localhost:5761')

    try:
        # Give connection time to establish
        time.sleep(0.5)

        print("Sending configuration commands...")

        # Set GPS provider to MSP
        print("  - set gps_provider = MSP")
        api.send_cli_command("set gps_provider = MSP")
        time.sleep(0.2)

        # Enable GPS feature
        print("  - feature GPS")
        api.send_cli_command("feature GPS")
        time.sleep(0.2)

        # Save configuration
        print("  - save")
        api.send_cli_command("save")
        time.sleep(0.5)

        print("\n✓ Configuration complete!")
        print("\nSITL will reboot with MSP GPS enabled.")

    finally:
        api.disconnect()

if __name__ == '__main__':
    configure_gps()
