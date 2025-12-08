# PWA TCP/WebSocket Connection Analysis

**Date:** 2025-12-01
**Project:** configurator-web-cors-research (related)
**Issue:** TCP connections don't work in PWA mode
**Reporter:** Scavanger via user

---

## Problem Statement

Scavanger reports:
> "TCP would be possible via WebSockets, but somehow it doesn't connect properly with SITL. INAV SITL says it's connected, but web serial remains stuck on 'connecting'. Bug in INAV, TCP handshake problem?"

---

## Root Cause Analysis

### Finding #1: TCP Not Implemented for PWA

**File:** `js/bridge.js`

The bridge layer has TCP functions that **only work in Electron mode**:

```javascript
// Lines 114-130
tcpConnect: function(host, port, window, setNoDelay) {
    if (this.isElectron) {
        return window.electronAPI.tcpConnect(host, port)
    }
    // ← NO else clause! Returns undefined in PWA mode
},

tcpClose: function() {
    if (this.isElectron) {
        return window.electronAPI.tcpClose();
    }
    // ← NO else clause! Returns undefined in PWA mode
},

tcpSend: function(data) {
    if (this.isElectron) {
        return window.electronAPI.tcpSend(data);
    }
    // ← NO else clause! Returns undefined in PWA mode
}
```

**Compare to Serial (which DOES work in PWA):**

```javascript
// Lines 90-95
serialConnect: function(path, options) {
    if (this.isElectron) {
        return window.electronAPI.serialConnect(path, options);
    } else {
        return webSerial.connect(path, options);  // ← PWA implementation exists!
    }
}
```

### Finding #2: Missing js/web/tcp.js

**Expected architecture pattern:**

```
connectionSerial.js → bridge.serialConnect() → {
  if (isElectron): window.electronAPI.serialConnect() → js/main/serial.js
  else: webSerial.connect() → js/web/serial.js ✅ EXISTS
}

connectionTcp.js → bridge.tcpConnect() → {
  if (isElectron): window.electronAPI.tcpConnect() → js/main/tcp.js
  else: ??? → js/web/tcp.js ❌ MISSING
}
```

**Files in `js/web/`:**
- `dfu.js` ✅
- `localStoreage.js` ✅ (note: typo in filename)
- `serial.js` ✅ (implements Web Serial API for PWA)
- **`tcp.js` ❌ MISSING**

### Finding #3: Bugs in connectionTcp.js

**File:** `js/connection/connectionTcp.js` (lines 108-114)

```javascript
addOnReceiveCallback(callback){
    this._onReceiveErrorListeners.push(callback);  // ← BUG! Should be _onReceiveListeners
}

removeOnReceiveCallback(callback){
    this._onReceiveListeners = this._onReceiveErrorListeners.filter(listener => listener !== callback);
    // ← BUG! Filters wrong array and assigns to wrong variable
}
```

**Note:** Same bugs exist in `connectionSerial.js` lines 111-116!

### Finding #4: Why "Connected" in SITL but Stuck in Configurator

**Sequence:**

1. **User triggers TCP connection** in PWA
2. **`connectionTcp.js:55`** calls `bridge.tcpConnect(host, port)`
3. **`bridge.js:114`** returns `undefined` (no else clause)
4. **`connectionTcp.js:55-71`** - Promise never resolves, callback never fires
5. **UI stays stuck** on "Connecting..."
6. **SITL side:** May accept a connection attempt (if any WebSocket handshake occurs), logs "connected"
7. **Result:** Asymmetric state - SITL thinks connected, configurator stuck

---

## Technical Constraints

### Protocol Incompatibility

**Raw TCP** (what SITL uses):
- Direct TCP socket connection
- POSIX sockets (`SOCK_STREAM`)
- Binary stream protocol
- Works with: Node.js `net` module (Electron ✅), Browser WebSocket ❌

**WebSocket** (what browsers provide):
- HTTP-based protocol upgrade
- RFC 6455 - binary/text frames with masking
- Handshake: HTTP upgrade request
- Works with: Browser ✅, Electron ✅, Raw TCP ❌

**These protocols are fundamentally incompatible** - you cannot connect a WebSocket client directly to a raw TCP server.

### PWA Limitations

PWAs are completely sandboxed and **cannot**:
- Run Node.js or native code ❌
- Execute local processes ❌
- Bind to network ports (can't run servers) ❌
- Make raw TCP connections ❌
- Access file system (except IndexedDB/LocalStorage) ❌

PWAs **can**:
- Use WebSocket API ✅
- Use Web Serial API ✅
- Use fetch/XMLHttpRequest ✅
- Use WebRTC ✅

---

## Solution Options

### Option 1: Add WebSocket Support to SITL (Ideal)

**Modify SITL to support both protocols:**
- Port 5761: Raw TCP (legacy, Electron compatibility)
- Port 5762: WebSocket (modern, PWA + Electron)

**Implementation:**
- Add WebSocket server to SITL firmware (`serial_tcp.c`)
- Handle HTTP upgrade handshake
- Decode WebSocket frames
- Bridge WebSocket ↔ serial port data

**Result:**
- ✅ **100% code sharing** - Single WebSocket client for both Electron and PWA
- ✅ Remove all Electron-specific TCP code (`js/main/tcp.js`, preload TCP IPC)
- ✅ Single code path = fewer bugs
- ✅ Native SITL support, no external dependencies

**Effort:**
- TBD - Need to investigate SITL architecture

**Files to modify:**
- `inav/src/main/target/SITL/`
- `inav/src/main/drivers/serial_tcp.c`
- Possibly add WebSocket library dependency

---

### Option 2: Separate Implementations (Current Pattern)

Keep platform-specific transport, share higher-level logic.

**Electron:**
```
connectionTcp.js → bridge.tcpConnect() → window.electronAPI.tcpConnect()
                                      → IPC → js/main/tcp.js (Node.js net)
                                      → SITL port 5761 (raw TCP)
```

**PWA:**
```
connectionTcp.js → bridge.tcpConnect() → js/web/tcp.js (WebSocket)
                                      → WebSocket proxy on localhost
                                      → SITL port 5761 (raw TCP)
```

**Required:**
1. Create `js/web/tcp.js` with WebSocket client implementation
2. Update `bridge.js` with proper `else` clause
3. Add TCP event listeners to `bridge.init()` for PWA mode
4. User must manually run WebSocket-to-TCP proxy process

**WebSocket-to-TCP Proxy** (example):
```javascript
// tools/ws-tcp-proxy.js (Node.js)
const WebSocket = require('ws');
const net = require('net');

const wss = new WebSocket.Server({ port: 9876 });

wss.on('connection', (ws, req) => {
    const match = req.url.match(/\/tcp\/([^:]+):(\d+)/);
    const [, host, port] = match;

    const tcpSocket = net.connect(port, host);

    tcpSocket.on('data', data => ws.send(data));
    tcpSocket.on('close', () => ws.close());

    ws.on('message', data => tcpSocket.write(data));
    ws.on('close', () => tcpSocket.end());
});
```

**Pros:**
- ✅ No SITL modification required
- ✅ Matches existing architecture pattern (like Serial)
- ✅ Works today with external proxy

**Cons:**
- ❌ Two code paths to maintain
- ❌ Requires user to manually run proxy process
- ❌ More complex user setup

---

### Option 3: Document as Limitation

**Accept current state:**
- TCP connections only work in Electron version
- Document in PWA limitations
- Focus PWA on Web Serial API

**Pros:**
- ✅ No code changes needed
- ✅ Simple

**Cons:**
- ❌ SITL doesn't work in PWA
- ❌ Poor user experience
- ❌ Incomplete PWA implementation

---

## Current SITL Architecture

**File:** `inav/src/main/drivers/serial_tcp.c`

**Key findings:**

1. **Raw POSIX sockets** - `SOCK_STREAM`, `IPPROTO_TCP`
2. **Server mode** - Binds to port and listens (`bind()`, `listen()`, `accept()`)
3. **Port numbering** - Base port (default 5761) + UART ID
4. **Non-blocking** - Uses `O_NONBLOCK` with `select()`
5. **Thread per port** - `pthread` for receive handling
6. **IPv4/IPv6 support** - Dual-stack capable

**TCP Server Flow:**
```
tcpReConfigure() → socket() → bind() → listen()
                             ↓
tcpReceiveThread() → select() → accept() → recv() loop
                                          → tcpReceiveBytes()
                                          → serialPort.rxCallback() or buffer
```

**No WebSocket support:**
- No HTTP upgrade handling
- No WebSocket frame parsing
- No masking/unmasking
- Pure binary TCP stream

---

## Code Sharing Analysis

**What CAN be shared (already shared):**
- `js/connection/connectionTcp.js` - Connection class and callbacks
- Event dispatching pattern
- Buffer handling logic
- Connection state management

**What CANNOT be shared (platform-specific):**

**Without SITL WebSocket support:**
- Electron: Must use Node.js `net` module (`js/main/tcp.js`)
- PWA: Must use WebSocket API (`js/web/tcp.js` → proxy → SITL)
- **No transport-layer code sharing possible**

**With SITL WebSocket support:**
- Both: Can use WebSocket API (browser native)
- **100% transport-layer code sharing possible**
- Can remove `js/main/tcp.js` entirely

---

## Recommended Approach

### Short Term (Immediate Fix)

1. **Implement PWA WebSocket client:**
   - Create `js/web/tcp.js` with WebSocket wrapper
   - Update `bridge.js` with `else` clause
   - Add TCP event listeners in `bridge.init()`

2. **Provide proxy tool:**
   - Create `tools/ws-tcp-proxy.js` (50 lines)
   - Document user must run it manually
   - Include in PWA documentation

3. **Fix callback bugs:**
   - Fix `connectionTcp.js` lines 108-114
   - Fix `connectionSerial.js` lines 111-116 (same bug)

4. **Update documentation:**
   - PWA requires manual proxy for SITL
   - Electron continues to work natively

### Long Term (Best Solution)

1. **Investigate SITL WebSocket implementation:**
   - Assess difficulty/invasiveness
   - Identify required libraries
   - Estimate effort

2. **If feasible: Add WebSocket to SITL:**
   - Submit RFC to INAV project
   - Implement WebSocket server alongside TCP
   - Maintain backward compatibility (keep TCP port)

3. **Refactor configurator:**
   - Remove `js/main/tcp.js`
   - Use shared `js/web/tcp.js` for both platforms
   - Simplify bridge.js

---

## Files Analysis

### Configurator Files

**To modify (short term):**
- [ ] `js/web/tcp.js` - Create new (WebSocket client)
- [ ] `js/bridge.js` - Add else clause for PWA TCP functions
- [ ] `js/connection/connectionTcp.js` - Fix callback bugs (lines 108-114)
- [ ] `js/connection/connectionSerial.js` - Fix callback bugs (lines 111-116)
- [ ] `tools/ws-tcp-proxy.js` - Create new (Node.js proxy tool)

**Could remove (long term with SITL WebSocket):**
- [ ] `js/main/tcp.js` - Electron main process TCP (Node.js net)
- [ ] `js/main/preload.js` - Remove TCP IPC lines 16-21
- [ ] `js/main/main.js` - Remove TCP IPC handlers

### INAV Firmware Files (long term)

**To investigate:**
- `src/main/drivers/serial_tcp.c` - Current TCP implementation
- `src/main/drivers/serial_tcp.h` - Header file
- `src/main/target/SITL/` - SITL-specific code

**Potentially add:**
- WebSocket library (libwebsockets? standalone implementation?)
- WebSocket protocol handler
- Frame parser/encoder
- HTTP upgrade handler

---

## Next Steps

1. **Document this analysis** ✅ (this file)
2. **Investigate SITL** - Assess WebSocket implementation difficulty
3. **Decision point:** SITL modification vs proxy approach
4. **Implement chosen solution**
5. **Test with real SITL**

---

## References

**Related Files:**
- `js/connection/connectionTcp.js` - TCP connection class
- `js/connection/connectionSerial.js` - Serial connection (working example)
- `js/bridge.js` - Platform abstraction layer
- `js/web/serial.js` - PWA serial implementation (pattern to follow)
- `js/main/tcp.js` - Electron TCP implementation (Node.js net)
- `inav/src/main/drivers/serial_tcp.c` - SITL TCP server

**Protocols:**
- RFC 6455 - The WebSocket Protocol
- POSIX sockets - `socket(2)`, `bind(2)`, `listen(2)`, `accept(2)`

**PWA APIs:**
- WebSocket API - https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- Web Serial API - https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API

---

**Developer**
2025-12-01
