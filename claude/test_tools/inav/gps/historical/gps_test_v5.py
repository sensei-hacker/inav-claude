#!/usr/bin/env python3
"""
GPS Recovery Test v5 - Fixed version for SITL testing.

This version properly configures the FC and handles SITL restart.

Key differences from v4:
- Configures receiver type to MSP
- Sets up ARM mode on AUX1
- Enables HITL mode for sensor bypass
- Restarts SITL externally (not via MSP reboot)

Usage:
    python3 gps_test_v5.py 5761 --sitl-path /path/to/SITL.elf
"""

import struct
import time
import sys
import argparse
import subprocess
import os
import signal

# MSP protocol constants
MSP_SET_RAW_GPS = 201
MSP_RAW_GPS = 106
MSP_COMP_GPS = 107
MSP_SET_RAW_RC = 200
MSP_RX_CONFIG = 44
MSP_SET_RX_CONFIG = 45
MSP_SET_MODE_RANGE = 35
MSP_EEPROM_WRITE = 250
MSP_SIMULATOR = 0x201F  # Enable HITL mode
MSP2_INAV_STATUS = 0x2000

# Receiver types
RX_TYPE_MSP = 2

# Simulator flags
HITL_ENABLE = (1 << 0)
SIMULATOR_MSP_VERSION = 2

# 30 mph = 48.28 km/h = 13.41 m/s = 1341 cm/s
FLIGHT_SPEED_CMS = 1341

# RC channel values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000

# Approximate meters per INAV unit (1e-7 degrees) at mid-latitudes
# 1 degree latitude ~ 111,000 meters
# 1 INAV unit (1e-7 degrees) ~ 0.0111 meters
METERS_PER_UNIT = 0.0111


def create_gps_payload(fix_type, num_sat, lat, lon, alt_m, ground_speed):
    """Create MSP_SET_RAW_GPS payload."""
    return list(struct.pack('<BBiiHH',
        fix_type, num_sat, lat, lon, alt_m, ground_speed
    ))


def consume_response(board):
    """Consume MSP response to prevent buffer overflow."""
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass


def send_rc(board, throttle=RC_LOW, roll=RC_MID, pitch=RC_MID, yaw=RC_MID,
            aux1=RC_LOW, aux2=RC_LOW, aux3=RC_LOW, aux4=RC_LOW):
    """Send RC channel values via MSP."""
    channels = [roll, pitch, throttle, yaw, aux1, aux2, aux3, aux4]
    while len(channels) < 16:
        channels.append(RC_MID)
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
    board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
    consume_response(board)


def send_gps(board, fix_type, num_sat, lat, lon, alt_m, ground_speed):
    """Send GPS data via MSP and consume response."""
    payload = create_gps_payload(fix_type, num_sat, lat, lon, alt_m, ground_speed)
    board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)
    consume_response(board)


def query_distance_to_home(board):
    """Query MSP_COMP_GPS to get distance to home."""
    board.send_RAW_msg(MSP_COMP_GPS, data=[])
    dataHandler = board.receive_msg()
    if dataHandler:
        board.process_recv_data(dataHandler)
    return board.GPS_DATA.get('distanceToHome', None)


def setup_receiver_type(board):
    """Set receiver type to MSP."""
    board.send_RAW_msg(MSP_RX_CONFIG, data=[])
    time.sleep(0.2)
    dataHandler = board.receive_msg()
    data = dataHandler.get('dataView', []) if dataHandler else []

    if data and len(data) >= 24:
        current_data = list(data)
    else:
        current_data = [0] * 24
        current_data[1], current_data[2] = 0x6C, 0x07  # maxcheck = 1900
        current_data[3], current_data[4] = 0xDC, 0x05  # midrc = 1500
        current_data[5], current_data[6] = 0x4C, 0x04  # mincheck = 1100
        current_data[8], current_data[9] = 0x75, 0x03  # rx_min_usec = 885
        current_data[10], current_data[11] = 0x43, 0x08  # rx_max_usec = 2115

    current_data[23] = RX_TYPE_MSP
    board.send_RAW_msg(MSP_SET_RX_CONFIG, data=current_data[:24])
    consume_response(board)


def setup_arm_mode(board):
    """Configure ARM mode on AUX1 for range 1700-2100."""
    payload = [0, 0, 0, 32, 48]
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


def kill_sitl():
    """Kill any running SITL processes."""
    subprocess.run(['pkill', '-9', 'SITL'], capture_output=True)
    time.sleep(1)


def start_sitl(sitl_path, workdir):
    """Start SITL in background."""
    proc = subprocess.Popen(
        [sitl_path],
        cwd=workdir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    time.sleep(3)  # Wait for SITL to start
    return proc


def run_gps_recovery_test(board, base_lat, base_lon, base_alt, log_file=None):
    """Run the GPS recovery test scenario."""

    def log(msg):
        print(msg)
        if log_file:
            log_file.write(msg + "\n")
            log_file.flush()

    log("\n" + "="*60)
    log("GPS Recovery Test - Issue #11049")
    log("="*60)
    log(f"Home position: lat={base_lat/1e7:.6f}, lon={base_lon/1e7:.6f}, alt={base_alt}m")
    log(f"Flight speed: {FLIGHT_SPEED_CMS} cm/s (~30 mph)")

    # Phase 1: Send GPS fix for 2 seconds (pre-arm)
    log("\n[Phase 1] Sending GPS fix for 2 seconds (pre-arm)...")
    start_time = time.time()
    while time.time() - start_time < 2.0:
        send_gps(board, fix_type=2, num_sat=12, lat=base_lat, lon=base_lon,
                 alt_m=base_alt, ground_speed=0)
        send_rc(board, throttle=RC_LOW)
        time.sleep(0.02)
    log("  -> GPS fix sent")

    # Phase 2: Arm the FC
    log("\n[Phase 2] Arming FC (home position set on arm)...")
    start_time = time.time()
    while time.time() - start_time < 2.0:
        send_gps(board, fix_type=2, num_sat=12, lat=base_lat, lon=base_lon,
                 alt_m=base_alt, ground_speed=0)
        send_rc(board, throttle=RC_LOW, aux1=RC_HIGH)
        time.sleep(0.02)

    dist = query_distance_to_home(board)
    log(f"  -> Armed. Distance to home: {dist}m (should be ~0)")

    # Phase 3: Fly away
    log("\n[Phase 3] Flying away at 30 mph until >100m from home...")
    current_lat = base_lat
    current_lon = base_lon

    meters_per_update = FLIGHT_SPEED_CMS / 100.0 / 50.0
    units_per_update = int(meters_per_update / METERS_PER_UNIT)

    log(f"  Movement: {meters_per_update:.2f}m per update, {units_per_update} lat/lon units")

    start_time = time.time()
    max_fly_time = 30
    last_log_time = 0

    while time.time() - start_time < max_fly_time:
        current_lat += units_per_update
        send_gps(board, fix_type=2, num_sat=12, lat=current_lat, lon=current_lon,
                 alt_m=base_alt + 50, ground_speed=FLIGHT_SPEED_CMS)
        send_rc(board, throttle=1600, aux1=RC_HIGH)
        time.sleep(0.02)

        elapsed = time.time() - start_time
        if elapsed - last_log_time >= 1.0:
            dist = query_distance_to_home(board)
            log(f"  t={elapsed:.1f}s: Distance to home = {dist}m")
            last_log_time = elapsed
            if dist is not None and dist >= 100:
                break

    dist_before_loss = query_distance_to_home(board)
    log(f"  -> Reached distance: {dist_before_loss}m from home")

    if dist_before_loss is None or dist_before_loss < 50:
        log("  WARNING: Did not reach sufficient distance. Test may be invalid.")

    # Phase 4: GPS loss
    log("\n[Phase 4] Simulating GPS loss for 5 seconds...")
    loss_lat = current_lat
    loss_lon = current_lon

    start_time = time.time()
    while time.time() - start_time < 5.0:
        send_gps(board, fix_type=0, num_sat=0, lat=0, lon=0, alt_m=0, ground_speed=0)
        send_rc(board, throttle=1600, aux1=RC_HIGH)
        time.sleep(0.02)

    dist_during_loss = query_distance_to_home(board)
    log(f"  -> GPS lost. Distance to home: {dist_during_loss}m")

    # Phase 5: GPS recovery
    log("\n[Phase 5] Simulating GPS recovery...")
    recovery_lat = loss_lat + int(20 / METERS_PER_UNIT)
    recovery_lon = loss_lon

    start_time = time.time()
    while time.time() - start_time < 5.0:
        send_gps(board, fix_type=2, num_sat=10, lat=recovery_lat, lon=recovery_lon,
                 alt_m=base_alt + 50, ground_speed=500)
        send_rc(board, throttle=1600, aux1=RC_HIGH)
        time.sleep(0.02)

    dist_after_recovery = query_distance_to_home(board)
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
    parser = argparse.ArgumentParser(description='GPS Recovery Test v5 - Fixed for SITL')
    parser.add_argument('target', help='TCP port number for SITL')
    parser.add_argument('--sitl-path', type=str, default=None,
                        help='Path to SITL executable (for auto-restart)')
    parser.add_argument('--lat', type=float, default=51.5074,
                        help='Base latitude in degrees')
    parser.add_argument('--lon', type=float, default=-0.1278,
                        help='Base longitude in degrees')
    parser.add_argument('--alt', type=int, default=100,
                        help='Base altitude in meters')
    parser.add_argument('--log', type=str, default=None,
                        help='Log file path')
    parser.add_argument('--skip-setup', action='store_true',
                        help='Skip FC setup (use pre-configured EEPROM)')

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
        log_file.write(f"GPS Recovery Test v5 Log\n")
        log_file.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    sitl_proc = None
    sitl_workdir = None

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
                setup_receiver_type(board)
                print("  Setting up ARM mode on AUX1...")
                setup_arm_mode(board)
                print("  Saving config to EEPROM...")
                save_config(board)
                print("  Config saved!")

            # Restart SITL if path provided
            if args.sitl_path:
                sitl_workdir = os.path.dirname(args.sitl_path)
                print("\n[Restart] Restarting SITL...")
                kill_sitl()
                sitl_proc = start_sitl(args.sitl_path, sitl_workdir)
                print(f"  SITL restarted (PID: {sitl_proc.pid})")
            else:
                print("\n[Manual] Please restart SITL manually and press Enter...")
                input()

        # Run the test
        print("\n[Test] Running GPS recovery test...")
        print(f"Connecting to TCP port {device}...")

        with MSPy(device=device, use_tcp=True, loglevel='WARNING') as board:
            if board == 1:
                print(f"Error: Could not connect to {device}")
                return 1

            print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")

            print("  Enabling HITL mode...")
            enable_hitl_mode(board)

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
        if sitl_proc:
            os.killpg(os.getpgid(sitl_proc.pid), signal.SIGTERM)


if __name__ == '__main__':
    sys.exit(main())
