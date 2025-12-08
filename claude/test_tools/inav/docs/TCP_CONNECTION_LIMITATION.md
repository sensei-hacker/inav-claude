# CRSF Telemetry Testing - TCP Connection Limitation

## The Problem

When testing CRSF telemetry with INAV SITL, you might be tempted to use separate scripts:
1. One script to send RC frames to the flight controller
2. Another script to read telemetry responses

**This will NOT work!**

## Why It Doesn't Work

### TCP Connection Constraint
A TCP server port can accept **only ONE client connection at a time**. SITL's UART2 (port 5761) is a TCP server that:
- Accepts a single client connection
- Uses that connection for **bidirectional communication**
- Cannot accept a second client while the first is connected

### What Happens If You Try
```bash
# Terminal 1: Start RC sender
python3 crsf_rc_sender.py 2 --rate 50

# Terminal 2: Try to read telemetry (FAILS!)
python3 test_telemetry_simple.py
# Error: Connection refused (port already in use by RC sender)
```

The second script will get `ConnectionRefusedError` because the RC sender already has the connection.

## The Solution

### Use Bidirectional Communication
The RC sender script must handle **both** sending and receiving on the same socket:

```python
# CORRECT: Single script with bidirectional communication
sock.connect(('127.0.0.1', 5761))

while True:
    # Send RC frames
    sock.sendall(rc_frame)

    # Read telemetry responses (non-blocking)
    if select.select([sock], [], [], 0)[0]:
        telemetry_data = sock.recv(256)
        parse_telemetry(telemetry_data)
```

This matches **real-world CRSF behavior** where the transmitter and flight controller communicate bidirectionally over a single serial link.

## Updated Script

The `crsf_rc_sender.py` script now implements bidirectional communication:

### Features
- **Sends RC frames** at specified rate (default 50Hz)
- **Receives telemetry frames** on the same connection
- **Counts telemetry** by frame type (GPS, BATTERY, ATTITUDE, etc.)
- **Optional telemetry display** to STDOUT with `--show-telemetry` flag

### Usage Examples

```bash
# Send RC frames and display telemetry statistics (default)
python3 crsf_rc_sender.py 2 --rate 50

# Send RC frames and show all telemetry frames on STDOUT
python3 crsf_rc_sender.py 2 --rate 50 --show-telemetry

# Run for 60 seconds with telemetry display
python3 crsf_rc_sender.py 2 --rate 50 --duration 60 --show-telemetry
```

### Output Modes

**Without `--show-telemetry` (clean output):**
```
=== CRSF RC Frame Sender ===
Connecting to SITL UART2 on port 5761...
✓ Connected to 127.0.0.1:5761 (after 0 retries)

Sending RC frames at 50Hz...
Channels: All at 1500us (midpoint)
Telemetry display: DISABLED (use --show-telemetry to enable)

Sent 50 frames (50.2 Hz) | Received 14 telemetry frames [ATTITUDE:4, BATTERY:5, GPS:5]
Sent 100 frames (49.9 Hz) | Received 28 telemetry frames [ATTITUDE:8, BATTERY:10, GPS:10]
...
```

**With `--show-telemetry` (verbose output):**
```
Sent 50 frames (50.2 Hz) | Received 14 telemetry frames [ATTITUDE:4, BATTERY:5, GPS:5]
[TELEM] GPS          (19 bytes): C8 11 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B
[TELEM] BATTERY      (12 bytes): C8 0A 08 00 00 00 00 00 00 00 00 7D
[TELEM] ATTITUDE     (10 bytes): C8 08 1E 00 00 00 00 00 00 F2
...
```

## Alternative: Port Forwarding

If you **must** use separate scripts (e.g., for testing or debugging), you can:

1. **Have RC sender listen on a separate port** and forward telemetry data
2. **Use a relay process** that connects to SITL and provides multiple client connections

Example relay architecture:
```
SITL:5761 <---> Relay Script <---> Multiple clients (RC sender, telemetry reader, etc.)
   (1 conn)     (bidirectional)         (N connections)
```

However, this adds complexity and is not recommended for normal testing.

## Summary

**Problem:** TCP ports accept only one client. Can't have separate RC sender and telemetry reader.

**Solution:** Use bidirectional communication in a single script (matches real CRSF behavior).

**Script:** `crsf_rc_sender.py` now handles both RC transmission and telemetry reception.

**Flag:** Use `--show-telemetry` to display telemetry frames on STDOUT.

---

## Related Skills

- **test-crsf-sitl** - Complete CRSF telemetry testing workflow with SITL
- **build-sitl** - Build SITL firmware for CRSF testing
