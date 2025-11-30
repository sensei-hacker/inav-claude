#!/usr/bin/env python3
"""
GPS RTH Bug Reproduction Test

This test reproduces the bug from issues #10893 and #11049 where GPS loss
during RTH causes the drone to falsely think it's at home and start landing.

The bug mechanism:
1. GPS is lost -> lastUpdateTime not updated
2. GPS recovers but lastUpdateTime is stale (the bug)
3. GPS data still considered invalid -> EPH grows
4. Position estimate degrades
5. homeDistance calculated incorrectly (possibly small)
6. If RTH active and homeDistance < min_rth_distance -> "close to home" logic triggers
7. setHomePosition() called -> homeDistance = 0
8. Drone thinks it's at home and starts landing!

Usage:
    python3 gps_rth_bug_test.py 5761 --sitl-path /path/to/SITL.elf
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
MSP_SIMULATOR = 0x201F
MSP2_INAV_STATUS = 0x2000
MSP_NAV_STATUS = 121
MSP_SET_WP = 209

# Receiver types
RX_TYPE_MSP = 2

# Simulator flags
HITL_ENABLE = (1 << 0)
SIMULATOR_MSP_VERSION = 2

# RC channel values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000

# Flight parameters
FLIGHT_SPEED_CMS = 1341  # 30 mph
METERS_PER_UNIT = 0.0111  # 1 INAV unit (1e-7 degrees) ~ 0.0111m

# Mode IDs (from INAV)
NAV_RTH_MODE_ID = 10  # BOXNAVRTH


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
    # INAV channel order: Roll, Pitch, Throttle, Yaw, AUX1, AUX2, ...
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


def query_nav_status(board):
    """Query MSP_NAV_STATUS to get navigation state."""
    board.send_RAW_msg(MSP_NAV_STATUS, data=[])
    dataHandler = board.receive_msg()
    if dataHandler:
        board.process_recv_data(dataHandler)
        data = dataHandler.get('dataView', [])
        if data and len(data) >= 7:
            return {
                'mode': data[0],
                'state': data[1],
                'action': data[2],
                'wp_number': data[3],
                'nav_error': data[4],
                'target_bearing': struct.unpack('<h', bytes(data[5:7]))[0] if len(data) >= 7 else 0
            }
    return None


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


def setup_rth_mode(board):
    """Configure NAV RTH mode on AUX2 for range 1700-2100."""
    # Mode range: index, mode_id, aux_channel, range_start, range_end
    # NAV_RTH_MODE_ID = 10, AUX2 = channel index 1
    payload = [1, NAV_RTH_MODE_ID, 1, 32, 48]  # index 1, RTH mode, AUX2, 1700-2100
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
    time.sleep(3)
    return proc


def run_rth_bug_test(board, base_lat, base_lon, base_alt, log_file=None):
    """
    Run the RTH GPS recovery bug test.

    Test scenario:
    1. Establish GPS fix and arm
    2. Fly away from home (>100m)
    3. Activate RTH mode
    4. Simulate GPS loss for 5 seconds
    5. Simulate GPS recovery
    6. Check if homeDistance incorrectly becomes 0 (bug present)
    """

    def log(msg):
        print(msg)
        if log_file:
            log_file.write(msg + "\n")
            log_file.flush()

    log("\n" + "="*70)
    log("GPS RTH Bug Reproduction Test - Issues #10893, #11049")
    log("="*70)
    log(f"Home position: lat={base_lat/1e7:.6f}, lon={base_lon/1e7:.6f}, alt={base_alt}m")

    # Phase 1: Send GPS fix for 2 seconds (pre-arm)
    log("\n[Phase 1] Establishing GPS fix (pre-arm)...")
    start_time = time.time()
    while time.time() - start_time < 2.0:
        send_gps(board, fix_type=2, num_sat=12, lat=base_lat, lon=base_lon,
                 alt_m=base_alt, ground_speed=0)
        send_rc(board, throttle=RC_LOW)
        time.sleep(0.02)
    log("  -> GPS fix established")

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

    # Phase 3: Fly away to >100m from home
    log("\n[Phase 3] Flying away from home...")
    current_lat = base_lat
    current_lon = base_lon

    meters_per_update = FLIGHT_SPEED_CMS / 100.0 / 50.0
    units_per_update = int(meters_per_update / METERS_PER_UNIT)

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
        if elapsed - last_log_time >= 2.0:
            dist = query_distance_to_home(board)
            log(f"  t={elapsed:.1f}s: Distance to home = {dist}m")
            last_log_time = elapsed
            if dist is not None and dist >= 150:
                break

    dist_before_rth = query_distance_to_home(board)
    log(f"  -> Reached distance: {dist_before_rth}m from home")

    if dist_before_rth is None or dist_before_rth < 100:
        log("  WARNING: Did not reach sufficient distance. Test may be invalid.")

    # Phase 4: Activate RTH mode
    log("\n[Phase 4] Activating RTH mode...")
    rth_lat = current_lat
    rth_lon = current_lon

    start_time = time.time()
    while time.time() - start_time < 2.0:
        send_gps(board, fix_type=2, num_sat=12, lat=rth_lat, lon=rth_lon,
                 alt_m=base_alt + 50, ground_speed=500)
        # AUX1 = ARM, AUX2 = RTH
        send_rc(board, throttle=1500, aux1=RC_HIGH, aux2=RC_HIGH)
        time.sleep(0.02)

    nav_status = query_nav_status(board)
    dist_at_rth = query_distance_to_home(board)
    log(f"  -> RTH active. Nav status: {nav_status}")
    log(f"  -> Distance to home at RTH start: {dist_at_rth}m")

    # Phase 5: GPS loss for 5 seconds (longer than 1.5s timeout)
    log("\n[Phase 5] Simulating GPS loss for 5 seconds...")
    loss_lat = rth_lat
    loss_lon = rth_lon

    dist_readings_during_loss = []
    start_time = time.time()
    last_query_time = 0
    while time.time() - start_time < 5.0:
        send_gps(board, fix_type=0, num_sat=0, lat=0, lon=0, alt_m=0, ground_speed=0)
        send_rc(board, throttle=1500, aux1=RC_HIGH, aux2=RC_HIGH)
        time.sleep(0.02)

        elapsed = time.time() - start_time
        if elapsed - last_query_time >= 1.0:
            dist = query_distance_to_home(board)
            nav = query_nav_status(board)
            dist_readings_during_loss.append((elapsed, dist, nav))
            log(f"  t={elapsed:.1f}s: Distance={dist}m, NavStatus={nav}")
            last_query_time = elapsed

    dist_after_loss = query_distance_to_home(board)
    log(f"  -> GPS loss complete. Distance to home: {dist_after_loss}m")

    # Phase 6: GPS recovery
    log("\n[Phase 6] Simulating GPS recovery...")
    recovery_lat = loss_lat + int(10 / METERS_PER_UNIT)  # Moved 10m during loss
    recovery_lon = loss_lon

    dist_readings_after_recovery = []
    start_time = time.time()
    last_query_time = 0
    while time.time() - start_time < 5.0:
        send_gps(board, fix_type=2, num_sat=10, lat=recovery_lat, lon=recovery_lon,
                 alt_m=base_alt + 50, ground_speed=500)
        send_rc(board, throttle=1500, aux1=RC_HIGH, aux2=RC_HIGH)
        time.sleep(0.02)

        elapsed = time.time() - start_time
        if elapsed - last_query_time >= 0.5:
            dist = query_distance_to_home(board)
            nav = query_nav_status(board)
            dist_readings_after_recovery.append((elapsed, dist, nav))
            log(f"  t={elapsed:.1f}s: Distance={dist}m, NavStatus={nav}")
            last_query_time = elapsed

    dist_after_recovery = query_distance_to_home(board)
    nav_after_recovery = query_nav_status(board)
    log(f"  -> GPS recovered. Final distance to home: {dist_after_recovery}m")
    log(f"  -> Final nav status: {nav_after_recovery}")

    # Results
    log("\n" + "="*70)
    log("TEST RESULTS")
    log("="*70)
    log(f"Distance before RTH:      {dist_before_rth}m")
    log(f"Distance at RTH start:    {dist_at_rth}m")
    log(f"Distance after GPS loss:  {dist_after_loss}m")
    log(f"Distance after recovery:  {dist_after_recovery}m")

    # Check for bug
    bug_detected = False

    # Bug indicator 1: Distance became 0 during recovery
    if dist_after_recovery == 0:
        log("\nBUG DETECTED: Distance to home stuck at 0!")
        log("This indicates the 'close to home' logic was falsely triggered.")
        bug_detected = True

    # Bug indicator 2: Distance dropped significantly during/after GPS loss
    if dist_after_loss is not None and dist_at_rth is not None:
        if dist_after_loss < dist_at_rth * 0.5:
            log(f"\nBUG DETECTED: Distance dropped from {dist_at_rth}m to {dist_after_loss}m during GPS loss!")
            bug_detected = True

    # Bug indicator 3: Check if any reading during loss showed 0
    for elapsed, dist, nav in dist_readings_during_loss:
        if dist == 0:
            log(f"\nBUG DETECTED: Distance became 0 at t={elapsed:.1f}s during GPS loss!")
            bug_detected = True
            break

    if not bug_detected:
        if dist_after_recovery is not None and dist_after_recovery > 50:
            log("\nSUCCESS: Distance to home recovered correctly!")
            log("The GPS recovery fix appears to be working.")
            return True
        else:
            log(f"\nINCONCLUSIVE: Unexpected distance value ({dist_after_recovery})")
            return None
    else:
        log("\nBug confirmed - Issue #11049 is present.")
        return False


def main():
    parser = argparse.ArgumentParser(description='GPS RTH Bug Reproduction Test')
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
        log_file.write(f"GPS RTH Bug Test Log\n")
        log_file.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    sitl_proc = None
    sitl_workdir = None

    try:
        if not args.skip_setup:
            print("\n[Setup] Configuring FC for MSP receiver and RTH mode...")
            print(f"Connecting to TCP port {device}...")

            with MSPy(device=device, use_tcp=True, loglevel='WARNING') as board:
                if board == 1:
                    print(f"Error: Could not connect to {device}")
                    return 1

                print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")

                print("  Setting receiver type to MSP...")
                setup_receiver_type(board)
                print("  Setting up ARM mode on AUX1...")
                setup_arm_mode(board)
                print("  Setting up RTH mode on AUX2...")
                setup_rth_mode(board)
                print("  Saving config to EEPROM...")
                save_config(board)
                print("  Config saved!")

            if args.sitl_path:
                sitl_workdir = os.path.dirname(args.sitl_path)
                print("\n[Restart] Restarting SITL...")
                kill_sitl()
                sitl_proc = start_sitl(args.sitl_path, sitl_workdir)
                print(f"  SITL restarted (PID: {sitl_proc.pid})")
            else:
                print("\n[Manual] Please restart SITL manually and press Enter...")
                input()

        print("\n[Test] Running GPS RTH bug reproduction test...")
        print(f"Connecting to TCP port {device}...")

        with MSPy(device=device, use_tcp=True, loglevel='WARNING') as board:
            if board == 1:
                print(f"Error: Could not connect to {device}")
                return 1

            print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")

            print("  Enabling HITL mode...")
            enable_hitl_mode(board)

            result = run_rth_bug_test(board, base_lat, base_lon, args.alt, log_file)

            if log_file:
                log_file.write(f"\nFinal result: {'PASS' if result else 'FAIL/BUG' if result is False else 'INCONCLUSIVE'}\n")

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
