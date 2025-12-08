#!/usr/bin/env python3
"""
SITL Arming Test - Diagnose and arm INAV SITL via MSP

This script:
1. Connects to SITL
2. Sets up mode activation for ARM on AUX1
3. Queries arming status to diagnose what's blocking
4. Attempts to arm by sending RC with AUX1 high

Usage:
    python3 sitl_arm_test.py [port]
    # Default port: 5761 (SITL UART2)

Requirements:
    pip3 install git+https://github.com/xznhj8129/uNAVlib
"""

import struct
import time
import sys
import threading

# MSP protocol constants
MSP_RC = 105
MSP_STATUS_EX = 150
MSP_REBOOT = 68
MSP_MODE_RANGES = 34
MSP_SET_MODE_RANGE = 35
MSP_RX_CONFIG = 44
MSP_SET_RX_CONFIG = 45
MSP_SET_RAW_RC = 200
MSP_EEPROM_WRITE = 250
MSP_SET_RAW_GPS = 201
MSP_ACC_CALIBRATION = 205
# MSP2 commands use 16-bit function IDs
# MSP2_INAV_STATUS = 0x2000 in MSPv2, but in uNAVlib it's just 8192
MSP2_INAV_STATUS = 0x2000
MSP_SIMULATOR = 0x201F  # Enable HITL mode

# Simulator flags (from runtime_config.h)
HITL_ENABLE = (1 << 0)
SIMULATOR_MSP_VERSION = 2

# Receiver types (from rx.h)
RX_TYPE_NONE = 0
RX_TYPE_SERIAL = 1
RX_TYPE_MSP = 2
RX_TYPE_SIM = 3

# Box IDs (from rc_modes.h)
BOXARM = 0
BOXANGLE = 1

# Arming disable flags (from runtime_config.h)
ARMING_FLAGS = {
    1 << 2: "ARMED",
    1 << 3: "WAS_EVER_ARMED",
    1 << 4: "SIMULATOR_MODE_HITL",
    1 << 5: "SIMULATOR_MODE_SITL",
    1 << 6: "ARMING_DISABLED_GEOZONE",
    1 << 7: "ARMING_DISABLED_FAILSAFE_SYSTEM",
    1 << 8: "ARMING_DISABLED_NOT_LEVEL",
    1 << 9: "ARMING_DISABLED_SENSORS_CALIBRATING",
    1 << 10: "ARMING_DISABLED_SYSTEM_OVERLOADED",
    1 << 11: "ARMING_DISABLED_NAVIGATION_UNSAFE",
    1 << 12: "ARMING_DISABLED_COMPASS_NOT_CALIBRATED",
    1 << 13: "ARMING_DISABLED_ACCELEROMETER_NOT_CALIBRATED",
    1 << 14: "ARMING_DISABLED_ARM_SWITCH",
    1 << 15: "ARMING_DISABLED_HARDWARE_FAILURE",
    1 << 16: "ARMING_DISABLED_BOXFAILSAFE",
    1 << 18: "ARMING_DISABLED_RC_LINK",
    1 << 19: "ARMING_DISABLED_THROTTLE",
    1 << 20: "ARMING_DISABLED_CLI",
    1 << 21: "ARMING_DISABLED_CMS_MENU",
    1 << 22: "ARMING_DISABLED_OSD_MENU",
    1 << 23: "ARMING_DISABLED_ROLLPITCH_NOT_CENTERED",
    1 << 24: "ARMING_DISABLED_SERVO_AUTOTRIM",
    1 << 25: "ARMING_DISABLED_OOM",
    1 << 26: "ARMING_DISABLED_INVALID_SETTING",
    1 << 27: "ARMING_DISABLED_PWM_OUTPUT_ERROR",
    1 << 28: "ARMING_DISABLED_NO_PREARM",
    1 << 29: "ARMING_DISABLED_DSHOT_BEEPER",
    1 << 30: "ARMING_DISABLED_LANDING_DETECTED",
}

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000


class ContinuousRCSender:
    """
    Background thread that sends RC data continuously to maintain MSP RC link.

    The MSP receiver times out after 200ms (DELAY_5_HZ) without data.
    This class sends RC at 50Hz (20ms) to keep the link alive.
    """
    def __init__(self, board):
        self.board = board
        self.throttle = RC_LOW
        self.aux1 = RC_LOW
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.send_gps = True

    def set_values(self, throttle=None, aux1=None):
        """Thread-safe way to update RC values."""
        with self.lock:
            if throttle is not None:
                self.throttle = throttle
            if aux1 is not None:
                self.aux1 = aux1

    def _send_loop(self):
        """Background thread loop."""
        while self.running:
            with self.lock:
                throttle = self.throttle
                aux1 = self.aux1
                send_gps = self.send_gps

            # Send RC - AETR order: Roll, Pitch, Throttle, Yaw, AUX1...
            channels = [RC_MID, RC_MID, throttle, RC_MID, aux1, RC_LOW, RC_LOW, RC_LOW]
            while len(channels) < 16:
                channels.append(RC_MID)
            data = []
            for ch in channels:
                data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
            try:
                self.board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
            except:
                pass

            # Send GPS too
            if send_gps:
                try:
                    payload = list(struct.pack('<BBiiHH', 2, 12, 515074000, -1278000, 100, 0))
                    self.board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)
                except:
                    pass

            time.sleep(0.02)  # 50Hz

    def start(self):
        """Start the background RC sender."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._send_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop the background RC sender."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
            self.thread = None


def decode_arming_flags(flags):
    """Decode arming flags into human readable list."""
    result = []
    for bit, name in ARMING_FLAGS.items():
        if flags & bit:
            result.append(name)
    return result


def set_receiver_type_msp(board):
    """
    Set receiver type to MSP.

    MSP_SET_RX_CONFIG payload (24 bytes):
    - byte 0: serialrx_provider
    - bytes 1-2: maxcheck
    - bytes 3-4: midrc
    - bytes 5-6: mincheck
    - byte 7: spektrum_sat_bind
    - bytes 8-9: rx_min_usec
    - bytes 10-11: rx_max_usec
    - byte 12: rcInterpolation (ignored)
    - byte 13: rcInterpolationInterval (ignored)
    - bytes 14-15: airModeActivateThreshold (ignored)
    - byte 16: (ignored)
    - bytes 17-20: (ignored, u32)
    - byte 21: (ignored)
    - byte 22: fpvCamAngleDegrees (ignored)
    - byte 23: receiverType (RX_TYPE_MSP = 2)
    """
    # First read current config - retry up to 3 times
    current_data = None
    for attempt in range(3):
        board.send_RAW_msg(MSP_RX_CONFIG, data=[])
        time.sleep(0.2)
        dataHandler = board.receive_msg()

        # dataHandler is a dict with 'dataView' key, not an object with 'data' attribute
        data = dataHandler.get('dataView', []) if dataHandler else []
        if data and len(data) > 0:
            current_data = list(data)
            break
        print(f"  Retry {attempt + 1}/3 reading RX config...")
        time.sleep(0.2)

    if current_data is None:
        print("  WARNING: Could not read RX config, using defaults")
        # Use sensible defaults for INAV
        # serialrx_provider=0, maxcheck=1900, midrc=1500, mincheck=1100
        # spektrum_sat_bind=0, rx_min_usec=885, rx_max_usec=2115
        current_data = [
            0,                  # serialrx_provider
            0x6C, 0x07,        # maxcheck = 1900
            0xDC, 0x05,        # midrc = 1500
            0x4C, 0x04,        # mincheck = 1100
            0,                  # spektrum_sat_bind
            0x75, 0x03,        # rx_min_usec = 885
            0x43, 0x08,        # rx_max_usec = 2115
            0, 0,              # rcInterpolation, rcInterpolationInterval
            0, 0,              # airModeActivateThreshold
            0,                  # ignored
            0, 0, 0, 0,        # ignored u32
            0,                  # ignored
            0,                  # fpvCamAngleDegrees
            RX_TYPE_MSP        # receiverType
        ]
    else:
        print(f"  Current RX config length: {len(current_data)} bytes")

    if len(current_data) < 24:
        # Pad to 24 bytes if needed
        current_data.extend([0] * (24 - len(current_data)))

    # Current receiver type is at byte 23
    current_rx_type = current_data[23] if len(current_data) > 23 else 0
    print(f"  Current receiver type: {current_rx_type}")

    if current_rx_type == RX_TYPE_MSP:
        print("  Receiver type already set to MSP")
        return True

    # Set receiver type to MSP
    current_data[23] = RX_TYPE_MSP
    print(f"  Setting receiver type to MSP ({RX_TYPE_MSP})")

    board.send_RAW_msg(MSP_SET_RX_CONFIG, data=current_data[:24])
    time.sleep(0.1)

    # Try to receive acknowledgment
    try:
        dataHandler = board.receive_msg()
    except:
        pass

    return True


def setup_arm_mode(board):
    """
    Configure ARM mode to be activated on AUX1 (channel 5) when value > 1700.

    MSP_SET_MODE_RANGE payload:
    - byte 0: slot index (0-39)
    - byte 1: box permanent ID (BOXARM = 0)
    - byte 2: aux channel index (0 = AUX1 = channel 5)
    - byte 3: range start step ((1700-900)/25 = 32)
    - byte 4: range end step ((2100-900)/25 = 48)
    """
    slot_index = 0
    box_id = BOXARM  # 0 = ARM
    aux_channel = 0  # AUX1 = channel 5
    start_step = 32  # 1700
    end_step = 48    # 2100

    payload = [slot_index, box_id, aux_channel, start_step, end_step]
    print(f"  Setting ARM mode: slot={slot_index}, box=BOXARM, aux=AUX1, range=1700-2100")
    board.send_RAW_msg(MSP_SET_MODE_RANGE, data=payload)
    time.sleep(0.1)

    # Try to receive acknowledgment
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass


def save_config(board):
    """Save configuration to EEPROM."""
    print("  Saving config to EEPROM...")
    board.send_RAW_msg(MSP_EEPROM_WRITE, data=[])
    time.sleep(0.5)  # Give time for EEPROM write


def enable_hitl_mode(board):
    """
    Enable HITL (Hardware-In-The-Loop) simulator mode.

    This bypasses sensor calibration requirements by setting:
    - SIMULATOR_MODE_HITL flag
    - ACCELEROMETER_CALIBRATED state
    - COMPASS_CALIBRATED state

    MSP_SIMULATOR packet format:
    - byte 0: SIMULATOR_MSP_VERSION (2)
    - byte 1: flags (HITL_ENABLE = 1)
    """
    print("  Enabling HITL simulator mode...")
    payload = [SIMULATOR_MSP_VERSION, HITL_ENABLE]
    board.send_RAW_msg(MSP_SIMULATOR, data=payload)
    time.sleep(0.1)

    # Consume response
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass


def send_rc(board, throttle=RC_LOW, roll=RC_MID, pitch=RC_MID, yaw=RC_MID,
            aux1=RC_LOW, aux2=RC_LOW, aux3=RC_LOW, aux4=RC_LOW):
    """Send RC channel values via MSP and consume response."""
    # INAV raw channel order is AETR (default rcmap = {0,1,3,2}):
    # Raw 0: Roll (Aileron)
    # Raw 1: Pitch (Elevator)
    # Raw 2: Throttle (NOT Yaw!)
    # Raw 3: Yaw (Rudder)
    # Raw 4+: AUX channels
    channels = [roll, pitch, throttle, yaw, aux1, aux2, aux3, aux4]
    # Extend to 16 channels
    while len(channels) < 16:
        channels.append(RC_MID)

    # Convert to bytes (16-bit per channel)
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

    board.send_RAW_msg(MSP_SET_RAW_RC, data=data)

    # CRITICAL: Consume the acknowledgment response to prevent socket buffer overflow
    # MSP_SET_RAW_RC sends back an empty response (code 200)
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass


def send_gps(board, fix=2, sats=12, lat=515074000, lon=-1278000, alt=100, speed=0):
    """Send GPS data via MSP and consume response."""
    payload = list(struct.pack('<BBiiHH', fix, sats, lat, lon, alt, speed))
    board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)

    # CRITICAL: Consume the acknowledgment response to prevent socket buffer overflow
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass


def query_arming_flags(board, debug=False, send_rc_func=None):
    """
    Query MSP2_INAV_STATUS to get arming flags using the library's processing.

    This uses MSP2_INAV_STATUS which the library knows how to process,
    and updates board.CONFIG['armingDisableFlags'] and board.CONFIG['mode'].

    IMPORTANT: If send_rc_func is provided, it will be called to maintain RC link
    since the MSP receiver times out after 200ms without RC data.
    """
    # Send RC before query to maintain link
    if send_rc_func:
        send_rc_func()

    board.send_RAW_msg(MSP2_INAV_STATUS, data=[])
    time.sleep(0.05)  # Reduced from 0.1 to maintain tighter RC timing

    # Send RC again after wait
    if send_rc_func:
        send_rc_func()

    dataHandler = board.receive_msg()

    if dataHandler:
        board.process_recv_data(dataHandler)
        if debug:
            print(f"    [DEBUG] armingDisableFlags: 0x{board.CONFIG.get('armingDisableFlags', 0):08X}")
            print(f"    [DEBUG] mode: 0x{board.CONFIG.get('mode', 0):08X}")
        return board.CONFIG.get('armingDisableFlags', 0)

    if debug:
        print(f"    [DEBUG] No data received")
    return 0


def is_armed(board):
    """Check if FC is armed by looking at mode bits."""
    # BOXARM is bit 0 in mode flags
    return bool(board.CONFIG.get('mode', 0) & 1)


def get_arming_flags(board):
    """Get arming disable flags from CONFIG."""
    return board.CONFIG.get('armingDisableFlags', 0)


def read_rx_config(board, debug=False):
    """Read RX config from FC using the library's built-in method."""
    board.send_RAW_msg(MSP_RX_CONFIG, data=[])
    time.sleep(0.15)
    dataHandler = board.receive_msg()

    # dataHandler is a dict with 'dataView' key, not an object with 'data' attribute
    data = dataHandler.get('dataView', []) if dataHandler else []

    if debug:
        if data:
            print(f"    [DEBUG] MSP_RX_CONFIG response: {len(data)} bytes")
            if len(data) > 23:
                print(f"    [DEBUG] receiverType byte: {data[23]}")
        else:
            print(f"    [DEBUG] MSP_RX_CONFIG: No data received (packet_error={dataHandler.get('packet_error', 'N/A')})")

    if data and len(data) > 23:
        return data[23]  # receiverType is at byte 23
    return None


def query_rc_channels(board, num_channels=8, debug=False):
    """Query RC channel values from the FC."""
    board.send_RAW_msg(MSP_RC, data=[])
    time.sleep(0.1)
    dataHandler = board.receive_msg()

    # dataHandler is a dict with 'dataView' key
    data = dataHandler.get('dataView', []) if dataHandler else []

    if debug:
        if data:
            print(f"    [DEBUG] MSP_RC response: {len(data)} bytes")
            if len(data) > 0:
                print(f"    [DEBUG] Raw data: {list(data)[:32]}...")
        else:
            print(f"    [DEBUG] MSP_RC: No data (packet_error={dataHandler.get('packet_error', 'N/A') if dataHandler else 'N/A'})")

    if data and len(data) >= num_channels * 2:
        channels = []
        for i in range(num_channels):
            ch = data[i*2] | (data[i*2+1] << 8)
            channels.append(ch)
        return channels
    return None


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "5761"

    try:
        from unavlib.main import MSPy
    except ImportError:
        print("Error: uNAVlib not installed. Install with:")
        print("  pip3 install git+https://github.com/xznhj8129/uNAVlib")
        return 1

    print(f"Connecting to SITL on port {port}...")

    with MSPy(device=port, use_tcp=True, loglevel='WARNING') as board:
        if board == 1:
            print(f"Error: Could not connect to port {port}")
            return 1

        print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")
        print(f"API Version: {board.CONFIG.get('apiVersion', 'Unknown')}")

        # Initial arming flags from connection
        initial_flags = get_arming_flags(board)
        print(f"Initial arming flags: 0x{initial_flags:08X}")
        for flag in decode_arming_flags(initial_flags):
            print(f"  - {flag}")

        # Step 1: Set receiver type to MSP
        print("\n[Step 1] Setting receiver type to MSP...")
        set_receiver_type_msp(board)

        # Step 1b: Setup ARM mode on AUX1
        print("\n[Step 1b] Setting up ARM mode activation...")
        setup_arm_mode(board)
        save_config(board)

        # Reboot FC to apply receiver type change
        print("\n[Step 2] Rebooting FC to apply receiver type change...")
        board.send_RAW_msg(MSP_REBOOT, data=[])
        print("  Reboot command sent. Waiting for FC to restart...")

    # Wait for SITL to come back up (SITL can take 8+ seconds to reinitialize EEPROM)
    # Plus sensor calibration takes: Gyro 2s, Baro 2s, Pitot 4s, Acc 0.5s
    # Total: need at least 12-15 seconds after reboot
    time.sleep(15)

    # Reconnect
    print("\n[Step 3] Reconnecting to FC after reboot...")
    with MSPy(device=port, use_tcp=True, loglevel='WARNING') as board:
        if board == 1:
            print(f"Error: Could not reconnect to port {port}")
            return 1

        print(f"Reconnected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")

        # Verify receiver type after reboot
        rx_type = read_rx_config(board, debug=True)
        if rx_type is not None:
            print(f"  Receiver type after reboot: {rx_type} ({'MSP' if rx_type == 2 else 'OTHER'})")
            if rx_type != RX_TYPE_MSP:
                print(f"  WARNING: Receiver type is NOT MSP! Config may not have saved.")
        else:
            print(f"  WARNING: Could not verify receiver type after reboot")

        # Check arming flags after reboot
        flags_after_reboot = get_arming_flags(board)
        print(f"Arming flags after reboot: 0x{flags_after_reboot:08X}")
        for flag in decode_arming_flags(flags_after_reboot):
            print(f"  - {flag}")

        # Step 3b: Enable HITL mode to bypass sensor calibration
        # This is much faster than waiting for real calibration
        print("\n[Step 3b] Enabling HITL mode to bypass sensor calibration...")
        enable_hitl_mode(board)

        # Step 4: Send RC data in main thread (more reliable than background thread)
        # The MSP receiver times out after 200ms without RC data
        print("\n[Step 4] Establishing RC link (sending RC data every 50ms)...")

        aux1_value = RC_LOW  # Start disarmed

        def send_rc_now():
            """Send RC and GPS in main thread."""
            send_rc(board, throttle=RC_LOW, aux1=aux1_value)
            send_gps(board)

        # Send RC for 2 seconds to establish link
        for i in range(40):  # 2 seconds at 50Hz
            send_rc_now()
            time.sleep(0.05)
        print("  RC link should be established after 2s of continuous data")

        # Debug: Query RC values - but keep sending RC around the query
        send_rc_now()
        rc_channels = query_rc_channels(board, debug=True)
        send_rc_now()
        if rc_channels:
            print(f"  RC channels read from FC: {rc_channels[:5]}...")
        else:
            print("  WARNING: Could not read RC channels from FC")

        # Step 5: Query status while sending RC
        print("\n[Step 5] Querying arming status (while sending RC)...")
        send_rc_now()
        arming_flags = query_arming_flags(board, debug=True)
        send_rc_now()
        print(f"  Arming flags: 0x{arming_flags:04X}")
        flags = decode_arming_flags(arming_flags)
        if flags:
            print("  Active flags:")
            for flag in flags:
                print(f"    - {flag}")

        # Check ARMED state
        if is_armed(board):
            print("  Status: ARMED!")
            return 0

        # Step 6: Try to arm - set AUX1 high
        print("\n[Step 6] Attempting to arm (AUX1 high, throttle low)...")
        aux1_value = RC_HIGH  # ARM!

        # Send RC at 50Hz with periodic status checks
        start_time = time.time()
        last_status_check = 0
        last_rc_send = 0

        while time.time() - start_time < 5.0:  # 5 second timeout
            current_time = time.time()

            # Send RC every 20ms (50Hz)
            if current_time - last_rc_send >= 0.02:
                send_rc_now()
                last_rc_send = current_time

            # Check status every 500ms
            if current_time - last_status_check >= 0.5:
                send_rc_now()  # Ensure RC is fresh before status query
                arming_flags = query_arming_flags(board, debug=(last_status_check == 0))
                send_rc_now()  # Send RC right after status query

                elapsed = current_time - start_time
                if is_armed(board):
                    print(f"  t={elapsed:.1f}s: ARMED!")
                    break
                else:
                    blockers = [f for f in decode_arming_flags(arming_flags)
                               if "DISABLED" in f]
                    print(f"  t={elapsed:.1f}s: Not armed (0x{arming_flags:08X}). Blockers: {blockers}")
                last_status_check = current_time

            time.sleep(0.005)  # Small sleep to avoid busy loop

        # Final status check
        print("\n[Final] Checking final status...")
        send_rc_now()  # One more RC send
        arming_flags = query_arming_flags(board, debug=True)
        print(f"  Final arming flags: 0x{arming_flags:08X}")
        flags = decode_arming_flags(arming_flags)
        for flag in flags:
            print(f"    - {flag}")

        if is_armed(board):
            print("\n  SUCCESS: FC is ARMED!")
            return 0
        else:
            print("\n  FAILED: FC did not arm")
            print("  Remaining blockers:")
            for flag in flags:
                if "DISABLED" in flag:
                    print(f"    - {flag}")
            return 1


if __name__ == '__main__':
    sys.exit(main())
