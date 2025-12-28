#!/usr/bin/env python3
"""Configure SITL for MSP receiver and arming."""

import struct
import time
from mspapi2 import MSPApi, InavMSP

def configure_sitl_for_arming():
    """Set up SITL for MSP receiver and ARM on AUX1."""
    print("Connecting to SITL on port 5760...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()

    time.sleep(0.5)

    print("\n=== Configuring SITL for MSP Arming ===\n")

    # Step 1: Set receiver type to MSP (byte 23 in RX_CONFIG)
    print("1. Setting receiver type to MSP...")

    # Read current RX_CONFIG
    response = api._serial.request(int(InavMSP.MSP_RX_CONFIG))
    rx_config = response[1] if isinstance(response, tuple) else response

    # MSP_RX_CONFIG structure (24 bytes total):
    # 0: serialrx_provider (uint8)
    # 1-2: maxcheck (uint16)
    # 3-4: midrc (uint16)
    # 5-6: mincheck (uint16)
    # 7: spektrum_sat_bind (uint8)
    # 8-9: rx_min_usec (uint16)
    # 10-11: rx_max_usec (uint16)
    # 12: rcInterpolation (uint8)
    # 13: rcInterpolationInterval (uint8)
    # 14-15: airModeActivateThreshold (uint16)
    # 16-19: rx_spi_protocol/rx_spi_id/rx_spi_rf_channel_count (uint32)
    # 20: fpvCamAngleDegrees (uint8)
    # 21: rcSmoothingType (uint8)
    # 22: rcSmoothingChannels (uint8)
    # 23: rx_type (uint8) <- THIS ONE

    # Modify byte 23 to set RX_TYPE_MSP (2)
    rx_config_list = list(rx_config)
    rx_config_list[23] = 2  # RX_TYPE_MSP
    new_rx_config = bytes(rx_config_list)

    # Send modified config
    api._serial.send(int(InavMSP.MSP_SET_RX_CONFIG), new_rx_config)
    time.sleep(0.2)
    print("   ✓ RX type set to MSP")

    # Step 2: Configure ARM mode on AUX1
    print("\n2. Configuring ARM switch on AUX1...")

    # MSP_SET_MODE_RANGE: [slot, boxId, auxChannel, startStep, endStep]
    # slot: 0 (first mode slot)
    # boxId: 0 (ARM)
    # auxChannel: 0 (AUX1)
    # startStep: 32 (1700us)
    # endStep: 48 (2100us)
    mode_range = struct.pack('<BBBBB', 0, 0, 0, 32, 48)
    api._serial.send(int(InavMSP.MSP_SET_MODE_RANGE), mode_range)
    time.sleep(0.2)
    print("   ✓ ARM configured on AUX1 (1700-2100us)")

    # Step 3: Save configuration
    print("\n3. Saving configuration...")
    api._serial.send(int(InavMSP.MSP_EEPROM_WRITE), b'')
    time.sleep(1)
    print("   ✓ Configuration saved")

    # Step 4: Reboot SITL
    print("\n4. Rebooting SITL...")
    api._serial.send(int(InavMSP.MSP_REBOOT), b'')
    time.sleep(0.5)

    api.close()

    print("\n   ✓ SITL will reboot now")
    print("\n" + "=" * 70)
    print("Configuration complete!")
    print("=" * 70)
    print("\nWait 15 seconds for SITL to restart, then run:")
    print("  python3 run_blackbox_test.py")

if __name__ == '__main__':
    configure_sitl_for_arming()
