# Task Assignment: Add BLE Debug Logging

**Date:** 2025-12-29 12:20
**Project:** add-ble-debug-logging
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 2-3 hours
**Type:** Debugging / Logging Enhancement

## Task

Add comprehensive debug logging to the BLE (Bluetooth Low Energy) connection code in inav-configurator to help diagnose connection issues on Windows.

## Problem

**User report:**
- Trying to connect to BLE device "SYNERDUINO7-BT-E-LE" on Windows
- Connection appears to establish successfully
- BLE notifications started
- **But: No data received** (Sent: 27 bytes, Received: 0 bytes)
- MSP requests timeout repeatedly

**Log analysis:** `/home/raymorris/Downloads/inav-log.txt`

**Key observations:**
```
Line 10: "Found BLE device: SYNERDUINO7-BT-E-LE"
Line 11: "Connect to: SYNERDUINO7-BT-E-LE"
Line 12: "BLE notifications started."
Line 13: "Connection opened with ID: 255, Baud: 115200"
Line 15: "MSP data request timed-out: 1"
Line 21: "Connection with ID: 255 closed, Sent: 27 bytes, Received: 0 bytes"
```

**The problem:**
- Data is being sent (27 bytes)
- Nothing is being received (0 bytes)
- We need more detailed logging to understand why

## What to Do

### 1. Find the BLE Implementation Code

**Search for BLE-related files:**
```bash
cd inav-configurator

# Find BLE implementation
grep -r "BLE notifications started" js/
grep -r "Request BLE Device" js/
grep -r "navigator.bluetooth" js/
grep -r "GATT" js/

# Common locations:
# - js/serial_backend_ble.js
# - js/serial.js
# - js/connection/connection_ble.js (or similar)
```

**Identify key functions:**
- Device discovery/pairing
- GATT server connection
- Service/characteristic discovery
- Data write operations
- Data read/notification handling
- Connection state management

### 2. Add Logging Around Data Transfer

**Data being sent (write operations):**

Add detailed logging before/after BLE writes:

```javascript
// BEFORE
console.log('[BLE] Writing data:', {
    length: data.length,
    hex: Array.from(data).map(b => b.toString(16).padStart(2, '0')).join(' '),
    ascii: Array.from(data).map(b => b >= 32 && b <= 126 ? String.fromCharCode(b) : '.').join('')
});

await characteristic.writeValue(data);

console.log('[BLE] Write completed successfully');
```

**Data being received (notifications/reads):**

Add detailed logging in notification handler:

```javascript
characteristic.addEventListener('characteristicvaluechanged', (event) => {
    const value = event.target.value;

    console.log('[BLE] Data received:', {
        length: value.byteLength,
        hex: Array.from(new Uint8Array(value.buffer))
            .map(b => b.toString(16).padStart(2, '0')).join(' '),
        ascii: Array.from(new Uint8Array(value.buffer))
            .map(b => b >= 32 && b <= 126 ? String.fromCharCode(b) : '.').join(''),
        timestamp: Date.now()
    });

    // Existing handler code...
});
```

### 3. Add Logging Around Connection Setup

**Service and characteristic discovery:**

```javascript
console.log('[BLE] Discovering GATT services...');
const services = await server.getPrimaryServices();
console.log('[BLE] Found services:', services.map(s => s.uuid));

for (const service of services) {
    console.log('[BLE] Getting characteristics for service:', service.uuid);
    const characteristics = await service.getCharacteristics();
    console.log('[BLE] Characteristics:', characteristics.map(c => ({
        uuid: c.uuid,
        properties: {
            read: c.properties.read,
            write: c.properties.write,
            writeWithoutResponse: c.properties.writeWithoutResponse,
            notify: c.properties.notify,
            indicate: c.properties.indicate
        }
    })));
}
```

**Notification subscription:**

```javascript
console.log('[BLE] Starting notifications on characteristic:', characteristic.uuid);
console.log('[BLE] Characteristic properties:', {
    canNotify: characteristic.properties.notify,
    canIndicate: characteristic.properties.indicate,
    canRead: characteristic.properties.read,
    canWrite: characteristic.properties.write
});

await characteristic.startNotifications();
console.log('[BLE] Notifications started successfully');
```

### 4. Add Error Logging

**Wrap operations in try-catch with detailed errors:**

```javascript
try {
    await characteristic.writeValue(data);
} catch (error) {
    console.error('[BLE] Write failed:', {
        error: error.message,
        code: error.code,
        name: error.name,
        characteristic: characteristic.uuid,
        dataLength: data.length
    });
    throw error;
}
```

**Add connection state change logging:**

```javascript
device.addEventListener('gattserverdisconnected', () => {
    console.log('[BLE] GATT server disconnected', {
        deviceName: device.name,
        deviceId: device.id,
        timestamp: Date.now()
    });
});
```

### 5. Add Timing Information

**Track time between operations:**

```javascript
const writeStart = Date.now();
await characteristic.writeValue(data);
const writeEnd = Date.now();
console.log('[BLE] Write duration:', writeEnd - writeStart, 'ms');
```

**Track time between send and receive:**

```javascript
let lastSendTime = 0;

// In write function
lastSendTime = Date.now();
console.log('[BLE] Data sent at:', lastSendTime);

// In notification handler
const receiveTime = Date.now();
const latency = receiveTime - lastSendTime;
console.log('[BLE] Data received at:', receiveTime, 'latency:', latency, 'ms');
```

### 6. Add MTU and Connection Parameter Logging

**Log BLE connection parameters:**

```javascript
// If available via Web Bluetooth API
console.log('[BLE] Connection parameters:', {
    mtu: characteristic.service.device.gatt.mtu,
    connected: characteristic.service.device.gatt.connected
});
```

### 7. Testing Instructions

**Reproduce the issue:**
1. Build configurator with new logging
2. Connect to BLE device on Windows
3. Capture new log file
4. Look for:
   - Are notifications actually being subscribed?
   - What are the characteristic UUIDs and properties?
   - Are write operations succeeding?
   - Are any errors being thrown and caught silently?
   - What is the timing between operations?

**Specific things to check:**
- Is the correct characteristic being used for write?
- Is the correct characteristic being used for notifications?
- Are the characteristic properties correct (notify vs indicate)?
- Is the data format correct (ArrayBuffer vs other)?

## Success Criteria

- [ ] BLE implementation code located
- [ ] Logging added around all data write operations
- [ ] Logging added for received data (notifications)
- [ ] Logging added for service/characteristic discovery
- [ ] Logging added for connection state changes
- [ ] Error logging improved with details
- [ ] Timing information added
- [ ] Code tested on Windows with BLE device
- [ ] New log file captured and analyzed
- [ ] Report sent to manager with findings

## Important Notes

**Log file location:**
The log file was found at: `/home/raymorris/Downloads/inav-log.txt`

This is likely Electron's console output. Check where logs are written:
- Console.log goes to Electron dev tools console
- May also be written to a log file
- Check Electron logging configuration

**Known working behavior:**
- Device discovery works
- Device pairing works
- Connection establishment works
- Notification subscription appears to work

**Known failing behavior:**
- No data is received (0 bytes)
- MSP requests timeout
- Data is being sent (27 bytes)

**Hypothesis to investigate:**
1. Wrong characteristic being used for RX (receiving)?
2. Notifications not actually working despite success message?
3. Data format mismatch (endianness, framing)?
4. MTU issues (data too large)?
5. Timing issues (device not ready)?

**Platform-specific:**
This is on Windows. Check if there are any Windows-specific BLE quirks.

**Similar working platforms:**
Does BLE work on other platforms (Linux, macOS)? That would help isolate the issue.

---
**Manager**
