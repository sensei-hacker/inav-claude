#!/usr/bin/env python3
"""
GPS Recovery Test v6 - Main thread RC sending (like sitl_arm_test.py)

This version sends RC/GPS from the main thread to avoid socket conflicts.

Speed: 0.7 degrees/hour = 1,944 units/second = 39 units per 50Hz update

Usage:
    python3 gps_test_v6.py 5761
"""

import struct
import time
import sys
import argparse

# MSP protocol constants
MSP_REBOOT = 68
MSP_SET_MODE_RANGE = 35
MSP_RX_CONFIG = 44
MSP_SET_RX_CONFIG = 45
MSP_SET_RAW_RC = 200
MSP_EEPROM_WRITE = 250
MSP_SET_RAW_GPS = 201
MSP_COMP_GPS = 107
MSP2_INAV_STATUS = 0x2000
MSP_SIMULATOR = 0x201F

# Simulator flags
HITL_ENABLE = (1 << 0)
SIMULATOR_MSP_VERSION = 2

# Receiver types
RX_TYPE_MSP = 2

# Box IDs
BOXARM = 0

# Arming flags
ARMING_FLAGS = {
    1 << 2: "ARMED",
    1 << 4: "SIMULATOR_MODE_HITL",
    1 << 18: "ARMING_DISABLED_RC_LINK",
    1 << 19: "ARMING_DISABLED_THROTTLE",
    1 << 9: "ARMING_DISABLED_SENSORS_CALIBRATING",
    1 << 13: "ARMING_DISABLED_ACCELEROMETER_NOT_CALIBRATED",
    1 << 14: "ARMING_DISABLED_ARM_SWITCH",
}

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000

# Travel speed: 0.7 degrees per hour
# 0.7 degrees = 7,000,000 units (1 unit = 1e-7 degrees)
# Per hour = 7,000,000 / 3600 = 1,944 units/second
# At 50Hz = 1,944 / 50 = 39 units per update
UNITS_PER_UPDATE = 39

# Approximate meters per INAV unit at mid-latitudes
METERS_PER_UNIT = 0.0111


def consume_response(board):
    """Consume MSP response to prevent buffer overflow."""
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass


def send_rc_gps(board, throttle=RC_LOW, aux1=RC_LOW, gps_fix=2, gps_sats=12,
                gps_lat=515074000, gps_lon=-1278000, gps_alt=100, gps_speed=0):
    """Send RC and GPS data via MSP and consume responses."""
    # Send RC - AETR order
    channels = [RC_MID, RC_MID, throttle, RC_MID, aux1, RC_LOW, RC_LOW, RC_LOW]
    while len(channels) < 16:
        channels.append(RC_MID)
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
    board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
    consume_response(board)

    # Send GPS
    payload = list(struct.pack('<BBiiHH', gps_fix, gps_sats, gps_lat, gps_lon, gps_alt, gps_speed))
    board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)
    consume_response(board)


def decode_arming_flags(flags):
    """Decode arming flags into human readable list."""
    result = []
    for bit, name in ARMING_FLAGS.items():
        if flags & bit:
            result.append(name)
    return result


def set_receiver_type_msp(board):
    """Set receiver type to MSP."""
    board.send_RAW_msg(MSP_RX_CONFIG, data=[])
    time.sleep(0.2)
    dataHandler = board.receive_msg()
    data = dataHandler.get('dataView', []) if dataHandler else []

    if data and len(data) >= 24:
        current_data = list(data)
    else:
        current_data = [
            0, 0x6C, 0x07, 0xDC, 0x05, 0x4C, 0x04, 0,
            0x75, 0x03, 0x43, 0x08, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, RX_TYPE_MSP
        ]

    current_data[23] = RX_TYPE_MSP
    board.send_RAW_msg(MSP_SET_RX_CONFIG, data=current_data[:24])
    consume_response(board)


def setup_arm_mode(board):
    """Configure ARM mode on AUX1 for range 1700-2100."""
    payload = [0, BOXARM, 0, 32, 48]
    board.send_RAW_msg(MSP_SET_MODE_RANGE, data=payload)
    consume_response(board)


def save_config(board):
    """Save configuration to EEPROM."""
    board.send_RAW_msg(MSP_EEPROM_WRITE, data=[])
    time.sleep(0.5)
    consume_response(board)


def enable_hitl_mode(board):
    """Enable HITL mode to bypass sensor calibration."""
    payload = [SIMULATOR_MSP_VERSION, HITL_ENABLE]
    board.send_RAW_msg(MSP_SIMULATOR, data=payload)
    consume_response(board)


def query_arming_flags(board):
    """Query MSP2_INAV_STATUS to get arming flags."""
    board.send_RAW_msg(MSP2_INAV_STATUS, data=[])
    time.sleep(0.05)
    dataHandler = board.receive_msg()
    if dataHandler:
        board.process_recv_data(dataHandler)
    return board.CONFIG.get('armingDisableFlags', 0)


def is_armed(board):
    """Check if FC is armed."""
    return bool(board.CONFIG.get('mode', 0) & 1)


def query_distance_to_home(board):
    """Query MSP_COMP_GPS to get distance to home."""
    board.send_RAW_msg(MSP_COMP_GPS, data=[])
    time.sleep(0.05)
    dataHandler = board.receive_msg()
    if dataHandler:
        board.process_recv_data(dataHandler)
    return board.GPS_DATA.get('distanceToHome', None)


def run_gps_recovery_test(board, base_lat, base_lon, base_alt, log_file=None):
    """Run the GPS recovery test scenario with main thread RC/GPS sending."""

    def log(msg):
        print(msg)
        if log_file:
            log_file.write(msg + "\n")
            log_file.flush()

    # Current state
    current_lat = base_lat
    current_lon = base_lon
    throttle = RC_LOW
    aux1 = RC_LOW
    gps_fix = 2
    gps_sats = 12
    gps_alt = base_alt
    gps_speed = 0

    def send_now():
        """Send current RC/GPS state."""
        send_rc_gps(board, throttle=throttle, aux1=aux1, gps_fix=gps_fix,
                    gps_sats=gps_sats, gps_lat=current_lat, gps_lon=current_lon,
                    gps_alt=gps_alt, gps_speed=gps_speed)

    log("\n" + "="*60)
    log("GPS Recovery Test - Issue #11049")
    log("="*60)
    log(f"Home position: lat={base_lat/1e7:.6f}, lon={base_lon/1e7:.6f}, alt={base_alt}m")
    log(f"Travel speed: 0.7 degrees/hour = {UNITS_PER_UPDATE} units per 50Hz update")
    log(f"             = {UNITS_PER_UPDATE * 50 * METERS_PER_UNIT:.1f} m/s")

    # Phase 1: Establish GPS fix and RC link (2 seconds at 50Hz)
    log("\n[Phase 1] Establishing GPS fix and RC link (2 seconds)...")
    start_time = time.time()
    while time.time() - start_time < 2.0:
        send_now()
        time.sleep(0.02)
    log("  -> GPS fix and RC link established")

    # Phase 2: Arm the FC
    log("\n[Phase 2] Arming FC...")
    aux1 = RC_HIGH  # ARM!

    start_time = time.time()
    last_status_time = 0
    armed = False

    while time.time() - start_time < 5.0:
        send_now()
        time.sleep(0.02)

        # Check arming status every 500ms
        if time.time() - last_status_time >= 0.5:
            send_now()  # Send RC before query
            query_arming_flags(board)
            send_now()  # Send RC after query

            if is_armed(board):
                armed = True
                break

            elapsed = time.time() - start_time
            flags = board.CONFIG.get('armingDisableFlags', 0)
            blockers = [f for f in decode_arming_flags(flags) if 'DISABLED' in f]
            log(f"  t={elapsed:.1f}s: Not armed. Blockers: {blockers}")
            last_status_time = time.time()

    if not armed:
        log("  ERROR: Failed to arm!")
        return None

    send_now()
    dist = query_distance_to_home(board)
    send_now()
    log(f"  -> Armed! Distance to home: {dist}m (should be ~0)")

    # Phase 3: Fly away at 0.7 degrees per hour
    log("\n[Phase 3] Flying away at 0.7 degrees/hour...")
    throttle = 1600
    gps_alt = base_alt + 50
    gps_speed = int(UNITS_PER_UPDATE * 50 * METERS_PER_UNIT * 100)

    start_time = time.time()
    max_fly_time = 30
    last_log_time = 0

    while time.time() - start_time < max_fly_time:
        current_lat += UNITS_PER_UPDATE
        send_now()
        time.sleep(0.02)

        elapsed = time.time() - start_time
        if elapsed - last_log_time >= 1.0:
            send_now()
            dist = query_distance_to_home(board)
            send_now()
            traveled_deg = (current_lat - base_lat) / 1e7
            traveled_m = traveled_deg * 111000
            log(f"  t={elapsed:.1f}s: Traveled {traveled_deg:.4f} deg ({traveled_m:.0f}m), Distance to home = {dist}m")
            last_log_time = elapsed

            if dist is not None and dist >= 100:
                break

    send_now()
    dist_before_loss = query_distance_to_home(board)
    send_now()
    log(f"  -> Reached: {dist_before_loss}m from home")

    if dist_before_loss is None or dist_before_loss < 50:
        log("  WARNING: Did not reach sufficient distance. Test may be invalid.")

    # Phase 4: GPS loss for 3 seconds (3000ms)
    log("\n[Phase 4] Simulating GPS loss for 3 seconds (3000ms)...")
    loss_lat = current_lat
    loss_lon = current_lon

    gps_fix = 0
    gps_sats = 0
    current_lat = 0
    current_lon = 0
    gps_alt = 0
    gps_speed = 0

    start_time = time.time()
    while time.time() - start_time < 3.0:
        send_now()
        time.sleep(0.02)

    send_now()
    dist_during_loss = query_distance_to_home(board)
    send_now()
    log(f"  -> GPS lost. Distance to home: {dist_during_loss}m")

    # Phase 5: GPS recovery
    log("\n[Phase 5] Simulating GPS recovery...")
    gps_fix = 2
    gps_sats = 10
    current_lat = loss_lat + int(20 / METERS_PER_UNIT)
    current_lon = loss_lon
    gps_alt = base_alt + 50
    gps_speed = 500

    start_time = time.time()
    while time.time() - start_time < 5.0:
        send_now()
        time.sleep(0.02)

    send_now()
    dist_after_recovery = query_distance_to_home(board)
    send_now()
    log(f"  -> GPS recovered. Distance to home: {dist_after_recovery}m")

    # Results
    log("\n" + "="*60)
    log("TEST RESULTS")
    log("="*60)
    log(f"Distance before GPS loss: {dist_before_loss}m")
    log(f"Distance during GPS loss: {dist_during_loss}m")
    log(f"Distance after recovery:  {dist_after_recovery}m")

    if dist_after_recovery is not None and dist_after_recovery > 50:
        log("\nSUCCESS: Distance to home recovered correctly!")
        log("The GPS recovery fix is working.")
        return True
    elif dist_after_recovery == 0:
        log("\nBUG CONFIRMED: Distance to home stuck at 0!")
        log("Issue #11049 is present - GPS recovery bug.")
        return False
    else:
        log(f"\nINCONCLUSIVE: Unexpected distance value ({dist_after_recovery})")
        return None


def main():
    parser = argparse.ArgumentParser(description='GPS Recovery Test v6')
    parser.add_argument('target', help='TCP port number for SITL')
    parser.add_argument('--lat', type=float, default=51.5074, help='Base latitude')
    parser.add_argument('--lon', type=float, default=-0.1278, help='Base longitude')
    parser.add_argument('--alt', type=int, default=100, help='Base altitude')
    parser.add_argument('--log', type=str, default=None, help='Log file path')
    parser.add_argument('--skip-setup', action='store_true', help='Skip FC setup')

    args = parser.parse_args()

    base_lat = int(args.lat * 1e7)
    base_lon = int(args.lon * 1e7)

    try:
        from unavlib.main import MSPy
    except ImportError:
        print("Error: uNAVlib not installed. Install with:")
        print("  pip3 install git+https://github.com/xznhj8129/uNAVlib")
        return 1

    try:
        port = int(args.target)
        device = str(port)
    except ValueError:
        print("Error: target must be a TCP port number")
        return 1

    log_file = None
    if args.log:
        log_file = open(args.log, 'w')
        log_file.write(f"GPS Recovery Test v6 Log\n")
        log_file.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        if not args.skip_setup:
            # Phase 0: Configure FC
            print("\n[Setup] Configuring FC for MSP receiver...")
            print(f"Connecting to TCP port {device}...")

            with MSPy(device=device, use_tcp=True, loglevel='WARNING') as board:
                if board == 1:
                    print(f"Error: Could not connect to {device}")
                    return 1

                print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")
                print(f"API Version: {board.CONFIG.get('apiVersion', 'Unknown')}")

                print("  Setting receiver type to MSP...")
                set_receiver_type_msp(board)
                print("  Setting up ARM mode on AUX1...")
                setup_arm_mode(board)
                print("  Saving config to EEPROM...")
                save_config(board)
                print("  Config saved!")

                print("\n[Reboot] Rebooting FC to apply changes...")
                board.send_RAW_msg(MSP_REBOOT, data=[])

            # Wait 15 seconds for SITL to restart and calibrate
            print("  Waiting 15 seconds for FC to restart...")
            time.sleep(15)

        # Run the test
        print("\n[Test] Running GPS recovery test...")
        print(f"Connecting to TCP port {device}...")

        with MSPy(device=device, use_tcp=True, loglevel='WARNING') as board:
            if board == 1:
                print(f"Error: Could not connect to {device}")
                return 1

            print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")

            # Enable HITL mode
            print("  Enabling HITL mode...")
            enable_hitl_mode(board)

            # Establish RC link with main thread sending
            print("  Establishing RC link (2 seconds)...")
            start_time = time.time()
            while time.time() - start_time < 2.0:
                send_rc_gps(board, gps_lat=base_lat, gps_lon=base_lon, gps_alt=args.alt)
                time.sleep(0.02)

            # Check initial arming status
            send_rc_gps(board, gps_lat=base_lat, gps_lon=base_lon, gps_alt=args.alt)
            flags = query_arming_flags(board)
            send_rc_gps(board, gps_lat=base_lat, gps_lon=base_lon, gps_alt=args.alt)
            print(f"  Initial arming flags: 0x{flags:08X}")
            blockers = [f for f in decode_arming_flags(flags) if 'DISABLED' in f]
            if blockers:
                print(f"  Blockers: {blockers}")

            # Run the test
            result = run_gps_recovery_test(board, base_lat, base_lon, args.alt, log_file)

            if log_file:
                log_file.write(f"\nFinal result: {'PASS' if result else 'FAIL' if result is False else 'INCONCLUSIVE'}\n")

            return 0 if result else 1

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        if log_file:
            log_file.write(f"\nError: {e}\n")
        return 1
    finally:
        if log_file:
            log_file.close()


if __name__ == '__main__':
    sys.exit(main())
