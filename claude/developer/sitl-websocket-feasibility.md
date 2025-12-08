# SITL WebSocket Support - Feasibility Assessment

**Date:** 2025-12-01
**Investigator:** Developer
**Related:** pwa-tcp-websocket-analysis.md

---

## Executive Summary

**Feasibility:** ✅ **HIGH - Recommended to implement**

Adding WebSocket support to INAV SITL is:
- **Technically feasible** - No major architectural barriers
- **Moderately invasive** - ~300-500 lines of new code
- **Low risk** - Can coexist with existing TCP implementation
- **High value** - Enables PWA support with zero external dependencies

**Recommendation:** Implement minimal WebSocket server alongside existing TCP server.

---

## Current SITL Architecture Analysis

### Existing Code Structure

**File:** `src/main/drivers/serial_tcp.c` (345 lines)

**Current capabilities:**
- ✅ Raw TCP socket server (POSIX sockets)
- ✅ IPv4/IPv6 dual-stack support
- ✅ Multi-port support (base port + UART ID)
- ✅ Non-blocking I/O with select()
- ✅ Threaded receive handling (pthread)
- ✅ Connection state management

**Key functions:**
```c
tcpPort_t *tcpReConfigure(tcpPort_t *port, uint32_t id)
    → socket() → bind() → listen()

void *tcpReceiveThread(void* arg)
    → tcpReceive() in loop

int tcpReceive(tcpPort_t *port)
    → select() → accept() → recv() → tcpReceiveBytes()

void tcpWritBuf(serialPort_t *instance, const void *data, int count)
    → send() to client socket
```

**Dependencies:**
```c
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <fcntl.h>
#include <pthread.h>
```

All standard POSIX - no external libraries required.

---

### Existing HTTP/Protocol Experience

**File:** `src/main/target/SITL/sim/simple_soap_client.c`

**SITL already handles HTTP protocol:**

```c
// Line 90 - Builds HTTP POST request
asprintf(&request,
    "POST / HTTP/1.1\r\n"
    "soapaction: %s\r\n"
    "content-length: %u\r\n"
    "content-type: text/xml;charset='UTF-8'\r\n"
    "Connection: Keep-Alive\r\n\r\n"
    "<soap:Envelope...>%s</soap:Body></soap:Envelope>",
    action, strlen(requestBody), requestBody);

send(client->sockedFd, request, strlen(request), 0);
```

**What this tells us:**
- ✅ Team is comfortable with HTTP protocol structure
- ✅ HTTP header parsing exists (for SOAP responses)
- ✅ Text protocol handling over sockets
- ✅ Formatted protocol message construction

This significantly reduces implementation complexity - not learning entirely new territory.

---

## WebSocket Protocol Requirements

### Minimal Implementation Needs

**For server-side WebSocket (what SITL needs):**

1. **HTTP Upgrade Handshake** (one-time, per connection)
   - Parse: `GET /` request
   - Validate: `Upgrade: websocket`, `Connection: Upgrade`
   - Extract: `Sec-WebSocket-Key` header
   - Compute: SHA-1 hash of key + magic GUID
   - Send: HTTP 101 response with `Sec-WebSocket-Accept`

2. **Frame Decoding** (receive from client)
   - Read 2-14 bytes header
   - Extract: FIN bit, opcode, mask bit, payload length
   - Read: 4-byte mask key
   - Read: payload data
   - Unmask: payload XOR mask key

3. **Frame Encoding** (send to client)
   - Build: 2-10 bytes header (FIN, opcode, length)
   - Append: payload data (no masking for server→client)

4. **Control Frames** (optional but recommended)
   - Handle: PING frame → respond with PONG
   - Handle: CLOSE frame → respond with CLOSE, close socket

**What's NOT needed:**
- ❌ Extensions (compression, etc.)
- ❌ Multiple subprotocols
- ❌ Fragmentation (can send whole frames)
- ❌ TLS/WSS (local connections only)
- ❌ Client-side masking (only server side needed)

---

## Implementation Strategies

### Option A: Minimal Standalone Implementation (Recommended)

**Create:** `src/main/drivers/serial_websocket.c` (~400 lines)

**Approach:**
- Self-contained WebSocket server
- Parallel to `serial_tcp.c` architecture
- Share same port structure and threading model
- Use different port range (e.g., 5770-5779)

**Advantages:**
- ✅ No external dependencies
- ✅ Full control over implementation
- ✅ Small code footprint (~400 lines)
- ✅ No license concerns (write from RFC)
- ✅ Educational value for team
- ✅ Doesn't modify existing TCP code (low risk)

**Code structure:**
```c
// serial_websocket.c

// Handshake handling
static bool wsHandshake(wsPort_t *port, int clientFd);
static void wsComputeAcceptKey(const char *clientKey, char *acceptKey);

// Frame handling
static int wsDecodeFrame(uint8_t *data, size_t len, wsFrame_t *frame);
static int wsEncodeFrame(uint8_t *payload, size_t len, uint8_t opcode, uint8_t *out);

// Port functions (mirror TCP API)
wsPort_t *wsReConfigure(wsPort_t *port, uint32_t id);
void *wsReceiveThread(void* arg);
int wsReceive(wsPort_t *port);
void wsWritBuf(serialPort_t *instance, const void *data, int count);
serialPort_t *wsOpen(USART_TypeDef *USARTx, ...);
```

**Estimated size breakdown:**
```
HTTP handshake:       ~100 lines
Frame encode/decode:  ~150 lines
Port management:      ~100 lines (copied from serial_tcp.c)
Send/receive:         ~50 lines
```

**Complexity:** Medium

---

### Option B: Use Tiny WebSocket Library

**Libraries evaluated:**

1. **libwebsockets** (https://libwebsockets.org/)
   - ❌ Too heavy (50K+ lines, many features)
   - ❌ Many dependencies
   - ❌ Overkill for our needs

2. **wsServer** (https://github.com/Theldus/wsServer)
   - ✅ Minimal (~1000 lines total)
   - ✅ Single header implementation
   - ✅ MIT license
   - ⚠️ Still has TLS dependencies

3. **mongoose** WebSocket
   - ✅ Embedded-friendly
   - ❌ Larger than needed
   - ❌ HTTP server overhead

**Decision:** Libraries add more complexity than value for this use case.

---

### Option C: Hybrid - Add WebSocket to Existing serial_tcp.c

**Modify** `serial_tcp.c` to detect and handle both protocols.

**Approach:**
- Peek at first bytes of connection
- If "GET ", handle as WebSocket
- Otherwise, handle as raw TCP

**Advantages:**
- ✅ Single file
- ✅ Share port numbers and infrastructure
- ✅ Automatic protocol detection

**Disadvantages:**
- ❌ More invasive to existing code
- ❌ Harder to maintain
- ❌ Mixes two protocols in one file
- ❌ Higher risk of breaking existing TCP

**Complexity:** Medium-High

---

## Recommended Implementation Plan

### Phase 1: Minimal WebSocket Server (Recommended)

**Create new file:** `src/main/drivers/serial_websocket.c`

**Port allocation:**
- TCP ports: 5761-5768 (existing, UART 1-8)
- WebSocket ports: 5771-5778 (new, UART 1-8)
- OR: Single port 5761 with protocol detection (Option C)

**Implementation steps:**

1. **Copy serial_tcp.c as template** (~2 hours)
   - Port structure and initialization
   - Thread management
   - Socket setup and accept loop

2. **Implement HTTP handshake** (~3 hours)
   ```c
   static bool wsHandshake(int clientFd) {
       char buffer[1024];
       recv(clientFd, buffer, sizeof(buffer), 0);

       // Parse headers
       char *key = extractHeader(buffer, "Sec-WebSocket-Key");

       // Compute accept key (SHA-1 + base64)
       char acceptKey[29];
       wsComputeAcceptKey(key, acceptKey);

       // Send 101 response
       char response[256];
       snprintf(response, sizeof(response),
           "HTTP/1.1 101 Switching Protocols\r\n"
           "Upgrade: websocket\r\n"
           "Connection: Upgrade\r\n"
           "Sec-WebSocket-Accept: %s\r\n\r\n",
           acceptKey);
       send(clientFd, response, strlen(response), 0);

       return true;
   }
   ```

3. **Implement frame decoder** (~2 hours)
   ```c
   static int wsDecodeFrame(uint8_t *data, size_t len, uint8_t *payload, size_t *payloadLen) {
       uint8_t *p = data;

       // Byte 0: FIN and opcode
       bool fin = (*p & 0x80) != 0;
       uint8_t opcode = *p & 0x0F;
       p++;

       // Byte 1: Mask and length
       bool masked = (*p & 0x80) != 0;
       uint64_t payloadLength = *p & 0x7F;
       p++;

       // Extended length
       if (payloadLength == 126) {
           payloadLength = (p[0] << 8) | p[1];
           p += 2;
       } else if (payloadLength == 127) {
           // 64-bit length (rarely needed)
           payloadLength = ...;
           p += 8;
       }

       // Masking key (clients always mask)
       uint8_t mask[4];
       if (masked) {
           memcpy(mask, p, 4);
           p += 4;
       }

       // Unmask payload
       for (size_t i = 0; i < payloadLength; i++) {
           payload[i] = p[i] ^ mask[i % 4];
       }

       *payloadLen = payloadLength;
       return opcode;
   }
   ```

4. **Implement frame encoder** (~1 hour)
   ```c
   static int wsEncodeFrame(uint8_t *payload, size_t len, uint8_t *out) {
       uint8_t *p = out;

       // Byte 0: FIN=1, opcode=2 (binary)
       *p++ = 0x82;

       // Byte 1+: Length (no mask for server)
       if (len < 126) {
           *p++ = len;
       } else if (len < 65536) {
           *p++ = 126;
           *p++ = (len >> 8) & 0xFF;
           *p++ = len & 0xFF;
       } else {
           // 64-bit length
           *p++ = 127;
           // ... write 8 bytes
       }

       // Payload (no masking needed for server→client)
       memcpy(p, payload, len);
       p += len;

       return p - out;
   }
   ```

5. **SHA-1 for handshake** (~1 hour)
   - Option A: Use OpenSSL SHA-1 (if available)
   - Option B: Include tiny SHA-1 implementation (~100 lines)
   - Option C: Use existing crypto if INAV has any

6. **Base64 encoding** (~30 min)
   - Simple base64 encode function (~30 lines)
   - Only needed for accept key

7. **Integration and testing** (~2 hours)
   - Add to CMake build
   - Test with browser WebSocket client
   - Test with configurator
   - Verify coexistence with TCP

**Total estimated effort:** 10-12 hours

---

### Phase 2: Dual-Mode Support (Optional)

**Make both TCP and WebSocket available simultaneously:**

**Option 2A: Separate Ports**
- TCP: 5761-5768
- WebSocket: 5771-5778
- Both protocols available
- User chooses which to use

**Option 2B: Protocol Detection (Elegant)**
- Single port: 5761
- Peek at first bytes:
  - If "GET ": WebSocket
  - Otherwise: Raw TCP
- Transparent to user

**Effort:** +2 hours

---

## Risk Assessment

### Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| SHA-1 dependency | Low | Use tiny standalone implementation |
| Frame parsing bugs | Medium | Thorough testing, use RFC test vectors |
| Thread safety | Low | Copy proven pthread model from TCP |
| Performance | Low | WebSocket overhead minimal (<5%) |
| Compatibility | Low | Standard protocol, widely tested |

### Integration Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking existing TCP | Low | Separate file, no modifications to serial_tcp.c |
| Build complexity | Low | Single CMake line addition |
| Platform compatibility | Low | Same POSIX APIs as existing TCP code |
| Maintenance burden | Medium | Well-documented, based on RFC |

### Project Acceptance Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Code review rejection | Low | Clean implementation, clear benefit |
| Feature creep concerns | Low | Minimal, focused implementation |
| Testing requirements | Medium | Provide test suite and documentation |

**Overall Risk:** ✅ **LOW**

---

## Code Size Impact

**New files:**
```
src/main/drivers/serial_websocket.c    ~400 lines
src/main/drivers/serial_websocket.h    ~50 lines
src/main/drivers/sha1_tiny.c           ~100 lines (if needed)
src/main/drivers/sha1_tiny.h           ~20 lines
```

**Modified files:**
```
cmake/sitl.cmake                       +4 lines
```

**Total addition:** ~570 lines
**Binary size increase:** ~15-20 KB

**For reference:**
- Current serial_tcp.c: 345 lines
- SITL binary size: ~2-3 MB
- **Impact: <1% binary size increase**

---

## Alternative: Minimal Viable Implementation

**Even simpler approach for MVP:**

**Handshake only - no framing:**
1. Accept WebSocket handshake
2. Treat subsequent data as raw binary
3. Skip frame encoding/decoding
4. **Won't be RFC-compliant** but might work for testing

**Pros:**
- ✅ ~100 lines of code
- ✅ Quick proof-of-concept

**Cons:**
- ❌ Browsers enforce framing
- ❌ Won't actually work
- ❌ Not worth doing

**Verdict:** Not recommended - proper implementation not much harder.

---

## External Dependencies Analysis

**Required:**
- ✅ POSIX sockets - already used ✅
- ✅ pthread - already used ✅
- ✅ SHA-1 - can use tiny implementation ✅
- ✅ Base64 - trivial to implement ✅

**Optional:**
- ⚠️ OpenSSL - only if we want TLS (WSS)
  - Not needed for localhost/LAN
  - Can add later if needed

**Verdict:** ✅ **Zero new dependencies required**

---

## Browser Compatibility

**WebSocket support (RFC 6455):**
- Chrome: ✅ Since 2011 (v16)
- Firefox: ✅ Since 2012 (v11)
- Safari: ✅ Since 2012 (v6)
- Edge: ✅ Since 2015
- **All modern browsers fully support WebSocket**

**Binary frames (opcode 0x02):**
- ✅ Fully supported in all browsers
- ✅ Can send/receive binary data (Uint8Array)

**Verdict:** ✅ **No compatibility concerns**

---

## Comparison: Implementation vs Proxy

### Option 1: Implement WebSocket in SITL

**Effort:**
- Initial: 10-12 hours development
- Testing: 2-3 hours
- Documentation: 1 hour
- **Total: ~15 hours one-time**

**Benefits:**
- ✅ Native support, no external processes
- ✅ Cleaner user experience
- ✅ 100% code sharing in configurator
- ✅ Better performance (no extra hop)
- ✅ One-time effort, permanent solution

**Maintenance:**
- Very low (standard protocol)
- Code is self-contained

---

### Option 2: User-Run Proxy

**Effort:**
- Write proxy: 2 hours
- Documentation: 2 hours
- User support: Ongoing
- **Total: 4 hours + ongoing support**

**Benefits:**
- ✅ No SITL modification
- ✅ Quick to implement

**Drawbacks:**
- ❌ User must manually run proxy
- ❌ Extra process to manage
- ❌ More complex setup
- ❌ Potential port conflicts
- ❌ User confusion
- ❌ Ongoing support burden

---

## Recommendation

### ✅ Implement WebSocket in SITL (Option A)

**Rationale:**

1. **Moderate effort** (10-15 hours) for permanent solution
2. **Low risk** - proven protocol, self-contained implementation
3. **High value** - enables PWA with no user complexity
4. **Clean architecture** - separate file, no external deps
5. **Future-proof** - Electron can also migrate to WebSocket
6. **Team capability** - already handle HTTP (SOAP client)

**Implementation priority:** Medium-High

**Suggested timeline:**
- Week 1: Implement core WebSocket server
- Week 2: Testing and integration
- Week 3: Code review and refinement
- Week 4: Merge and document

---

## Next Actions

### Immediate (Developer):
1. ✅ Document feasibility (this file)
2. [ ] Create POC WebSocket handshake
3. [ ] Test with simple browser client
4. [ ] Measure actual effort

### Short Term (Team Decision):
1. [ ] Review feasibility assessment
2. [ ] Decide: SITL implementation vs proxy
3. [ ] Assign owner if approved
4. [ ] Create INAV GitHub issue/RFC

### Long Term (If Approved):
1. [ ] Implement serial_websocket.c
2. [ ] Write test suite
3. [ ] Update configurator bridge.js
4. [ ] Submit PR to INAV
5. [ ] Documentation and examples

---

## Test Plan

**Unit tests:**
- SHA-1 computation (test vectors from RFC)
- Base64 encoding
- Frame encoding/decoding
- Handshake generation

**Integration tests:**
- Browser WebSocket connection
- Binary data send/receive
- Multi-client support
- Graceful disconnect

**Compatibility tests:**
- Chrome, Firefox, Safari, Edge
- Electron app
- Different operating systems

**Performance tests:**
- Latency vs raw TCP
- Throughput comparison
- Memory usage

---

## References

**Specifications:**
- RFC 6455: The WebSocket Protocol
- RFC 4648: Base64 encoding
- RFC 3174: SHA-1 (or use existing crypto)

**Existing code:**
- `src/main/drivers/serial_tcp.c` - Architecture template
- `src/main/target/SITL/sim/simple_soap_client.c` - HTTP example

**Minimal implementations:**
- https://github.com/Theldus/wsServer - Reference
- https://github.com/m8rge/cwebsocket - Minimal example

---

**Developer**
2025-12-01

**Status:** Feasibility confirmed - **Recommended to implement**
