# SITL Architecture Analysis

**Date:** 2025-12-01
**Phase:** 1 of 4 - Architecture Review

---

## Overview

INAV's SITL (Software In The Loop) target compiles the flight controller firmware as a native executable that runs on Linux/macOS/Windows. This enables firmware testing and simulation without physical hardware.

---

## Build Configuration

**Source:** `cmake/sitl.cmake`

### Dependencies

**Required Libraries:**
- `-lpthread` - POSIX threads
- `-lm` - Math library
- `-lc` - Standard C library
- `-lrt` - Real-time library (Linux only, not macOS)

### Compile Options

- Standard C17 (when CMake >= 3.22)
- `-funsigned-char`
- `-Wno-format` (32-bit compilation workaround)
- `-fsingle-precision-constant` (Linux only)

### Platform Differences

**macOS:**
- No linker script (no `-T` flag)
- No `-lrt` dependency
- Different compiler warnings

**Linux:**
- Uses linker script `target/link/sitl.ld`
- Includes real-time library

**Cygwin/Windows:**
- Static libgcc linking
- `.exe` extension

---

## Source Code Structure

### SITL-Specific Files

**Location:** `src/main/target/SITL/`

**Core Files:**
- `target.c` - SITL entry point and initialization (17KB)
- `target.h` - Platform abstractions
- `serial_proxy.c/h` - Serial port proxy (23KB)
- `config.c` - Configuration overrides

**Simulator Integration:** (`sim/` subdirectory)
- `realFlight.c/h` - RealFlight simulator protocol
- `xplane.c/h` - X-Plane simulator protocol
- `simHelper.c/h` - Simulation helpers
- `simple_soap_client.c/h` - SOAP client for sim communication

**Serial Communication:**
- `drivers/serial_tcp.c/h` - TCP socket server for MSP
- `drivers/serial_websocket.c/h` - WebSocket server for MSP (newly added)

### Excluded Files

**Files NOT compiled for SITL:**
```
drivers/system.c
drivers/time.c
drivers/timer.c
drivers/rcc.c
drivers/persistent.c
drivers/accgyro/accgyro_mpu.c
drivers/display_ug2864hsweg01.c
io/displayport_oled.c
```

These are hardware-specific drivers replaced by SITL abstractions.

---

## POSIX API Usage

### Threading (pthread)

**Usage in `serial_tcp.c` and `target.c`:**

```c
pthread_mutex_t mutex;
pthread_t receiveThread;

pthread_mutex_init(&mutex, NULL)
pthread_mutex_lock(&mutex)
pthread_mutex_unlock(&mutex)
pthread_create(&thread, NULL, function, arg)
pthread_setschedprio(pthread_self(), priority)
```

**Purpose:**
- One receive thread per UART (8 UARTs = 8 threads)
- Mutex protection for shared buffers
- Thread priority scheduling

### BSD Sockets

**Usage in `serial_tcp.c`:**

```c
socket(AF_INET6, SOCK_STREAM, IPPROTO_TCP)
bind(fd, &addr, addrlen)
listen(fd, 100)
accept(fd, &clientAddr, &addrLen)
recv(clientFd, buffer, size, 0)
send(clientFd, data, count, 0)
```

**Purpose:**
- TCP server listening on ports 5760-5767 (8 UARTs)
- Accepts MSP connections from configurator
- Non-blocking I/O with select()

### Time/Clock

**Usage in `target.c`:**

```c
struct timespec start_time;
clock_gettime(CLOCK_MONOTONIC, &start_time)
```

**Purpose:**
- High-resolution timing for scheduler
- Monotonic clock for consistent time deltas

### File I/O

**EEPROM Emulation:**
- File `eeprom.bin` stores persistent configuration
- Standard POSIX `fopen()`, `fread()`, `fwrite()`, `fclose()`

---

## Communication Architecture

### MSP Protocol

**Multiple transport layers:**
1. **TCP Sockets** - `serial_tcp.c`
   - Ports: 5760-5767 (8 UARTs)
   - Direct socket communication

2. **WebSockets** - `serial_websocket.c`
   - Ports: 5771-5778 (8 UARTs)
   - RFC 6455 compliant
   - Enables browser-based configurator

3. **Serial Proxy** - `serial_proxy.c`
   - Bridges different transport protocols
   - Handles UART abstraction

### Simulator Communication

**External Simulator Protocols:**

1. **RealFlight** (`sim/realFlight.c`)
   - UDP-based communication
   - Sends motor outputs, receives sensor data

2. **X-Plane** (`sim/xplane.c`)
   - UDP-based communication
   - Flight simulator integration

3. **SOAP** (`sim/simple_soap_client.c`)
   - HTTP-based SOAP protocol
   - XML messaging for sim control

---

## Hardware Abstraction

### Simulated Components

**Sensors:**
- Gyroscope (simulated from flight dynamics)
- Accelerometer (simulated from flight dynamics)
- Barometer (simulated altitude)
- Magnetometer/Compass (simulated heading)
- GPS (simulated position/velocity)

**Actuators:**
- PWM motors (output to simulator)
- Servos (output to simulator)

**Peripherals:**
- UARTs (TCP/WebSocket sockets)
- I2C (dummy implementation)
- SPI (dummy implementation)

### Fake Hardware

**From `target.c`:**

```c
const int timerHardwareCount = 0;
timerHardware_t timerHardware[1];
uint32_t SystemCoreClock = 500 * 1e6;  // Fake 500 MHz
```

---

## Dependency Summary

| Component | POSIX API | Purpose |
|-----------|-----------|---------|
| Threading | pthread_create, pthread_mutex_* | Multi-threaded I/O |
| Networking | socket, bind, listen, accept, send, recv | MSP communication |
| Timing | clock_gettime(CLOCK_MONOTONIC) | Scheduler timing |
| File I/O | fopen, fread, fwrite, fclose | EEPROM emulation |
| Scheduling | pthread_setschedprio, sched_get_priority_min | Thread priorities |

---

## Key Insights for WebAssembly Porting

**Critical Dependencies:**
1. ✅ **Standard C library** - Fully supported by Emscripten
2. ❓ **POSIX threads** - Emscripten supports via SharedArrayBuffer
3. ❓ **BSD sockets** - NOT directly available, need WebSocket API
4. ✅ **File I/O** - Emscripten has virtual file systems (MEMFS, IDBFS)
5. ❓ **High-resolution timing** - Limited clock_gettime support

**Architecture Advantages:**
- Already abstracted from hardware
- Clean separation between platform and firmware
- Modular simulator integration

**Potential Challenges:**
- Socket → WebSocket conversion required
- Thread synchronization in browser context
- Simulator integration (UDP not available)

---

**Next Phase:** Research Emscripten's support for these POSIX APIs
