# DMA Usage in INAV Firmware

## Table of Contents

1. [Overview](#overview)
2. [DMA Architecture](#dma-architecture)
3. [Platform Differences](#platform-differences)
4. [Peripheral DMA Mappings](#peripheral-dma-mappings)
5. [Resource Allocation](#resource-allocation)
6. [Common Conflicts and Solutions](#common-conflicts-and-solutions)
7. [Best Practices](#best-practices)
8. [CLI Commands](#cli-commands)
9. [For Developers](#for-developers)

---

## Overview

Direct Memory Access (DMA) is a hardware feature that allows peripherals to transfer data to/from memory without CPU intervention, improving efficiency and reducing CPU load. INAV uses DMA extensively for high-throughput and time-critical operations.

### Why DMA Matters

- **Performance**: DMA offloads data transfers from the CPU, allowing it to focus on flight control algorithms
- **Efficiency**: Critical for high-frequency operations like gyro sampling (8kHz) and DShot motor protocols
- **Resource Management**: Limited DMA streams must be carefully allocated to avoid conflicts

### Key Peripherals Using DMA

| Peripheral | Priority | Reason |
|------------|----------|--------|
| Gyro (SPI) | **Critical** | High-frequency sampling (8kHz), essential for flight stability |
| Motors (Timers) | **Critical** | DShot motor protocol timing requirements |
| UART | Medium | Efficient telemetry, GPS, and RC receiver handling |
| ADC | Medium | Continuous voltage/current/sensor monitoring |
| SD Card/Flash | Low | Blackbox logging, non-blocking writes |
| LED Strip | Low | WS2811/WS2812 LED protocol |

---

## DMA Architecture

### DMA Tag System

INAV uses a packed 32-bit tag to encode DMA information:

```c
typedef uint32_t dmaTag_t;
#define DMA_TAG(dma, stream, channel) \
    ( (((dma) & 0x03) << 12) | (((stream) & 0x0F) << 8) | (((channel) & 0xFF) << 0) )
```

**Encoding:**
- Bits 12-13: DMA controller (1 or 2)
- Bits 8-11: Stream number (0-7 for STM32 F4/F7/H7)
- Bits 0-7: Channel number

**Example:** `DMA_TAG(2, 4, 3)` = DMA2, Stream 4, Channel 3

### DMA Descriptor Structure

Each DMA stream has a descriptor that tracks its state:

```c
typedef struct dmaChannelDescriptor_s {
    dmaTag_t                    tag;               // Packed DMA/stream/channel
    DMA_TypeDef*                dma;               // Hardware controller
    DMA_Stream_TypeDef*         ref;               // Stream reference
    dmaCallbackHandlerFuncPtr   irqHandlerCallback;// Interrupt handler
    uint32_t                    flagsShift;        // Status register offset
    IRQn_Type                   irqNumber;         // IRQ number
    uint32_t                    userParam;         // User data (often timer context)
    resourceOwner_e             owner;             // Owner tracking (see below)
    uint8_t                     resourceIndex;     // Resource index
} dmaChannelDescriptor_t;
```

### Resource Ownership

INAV tracks which peripheral owns each DMA stream:

```c
typedef enum {
    OWNER_FREE = 0,       // Unallocated
    OWNER_MOTOR,          // Motor/servo output
    OWNER_TIMER,          // Timer operations
    OWNER_SERIAL,         // UART
    OWNER_SPI,            // SPI bus
    OWNER_ADC,            // ADC
    OWNER_SDCARD,         // SD card
    OWNER_LED_STRIP,      // WS2811/2812 LEDs
    // ... 29 total types
} resourceOwner_e;
```

### Core DMA Files

- `drivers/dma.h` - Platform-agnostic abstraction layer
- `drivers/dma_stm32f4xx.c` - F4 implementation
- `drivers/dma_stm32f7xx.c` - F7 implementation
- `drivers/dma_stm32h7xx.c` - H7 implementation
- `drivers/dma_at32f43x.c` - AT32 implementation (with DMAMUX)
- `drivers/dma_cli_stm32_impl.c` - CLI interface
- `drivers/resource.h` - Resource ownership definitions

---

## Platform Differences

### STM32 F4 and F7

**Hardware:**
- 2 DMA controllers (DMA1, DMA2)
- 8 streams per controller (16 total)
- Fixed stream-to-peripheral mapping
- Channel selection per stream

**Limitations:**
- **No DMAMUX**: Stream assignments are hardcoded in silicon
- **F4 DMA2 Errata**: Corruption may occur if AHB peripherals (GPIO) and APB peripherals (SPI) access DMA2 concurrently
  - **Impact**: Bitbanged DShot (GPIO writes via DMA2) conflicts with SPI1 Gyro (typically DMA2)
  - **Mitigation**: F4 should use PWM-based DShot, not bitbanged

**DMA Resource Table (F4/F7):**
| Controller | Streams | Common Usage |
|------------|---------|--------------|
| DMA1 | 0-7 | Motors (timers), UART2-5, SPI2/3 |
| DMA2 | 0-7 | SPI1 (Gyro), UART1/6, ADC, SDIO |

### STM32 H7

**Hardware:**
- 2 DMA controllers (DMA1, DMA2)
- 8 streams per controller (16 total)
- **DMAMUX**: Flexible request routing

**Advantages:**
- DMAMUX eliminates hardcoded stream assignments
- Any DMA request can be routed to any available stream
- Greatly reduces resource conflicts
- Simplifies board design for >4 motor outputs

**Example:** On F4/F7, two timers might compete for the same DMA stream. On H7, DMAMUX can assign them to different streams automatically.

### AT32F43x

**Hardware:**
- Similar to H7 with DMAMUX support
- Flexible DMA channel assignment
- Enhanced flexibility for complex configurations

**Code Integration:**
```c
typedef struct dmaChannelDescriptor_s {
    // ... standard fields ...
    dmamux_channel_type* dmaMuxref;  // AT32-specific DMAMUX reference
} dmaChannelDescriptor_t;
```

### Platform Summary

| Platform | DMA Controllers | Streams/Controller | DMAMUX | Flexibility | Recommended For |
|----------|-----------------|-------------------|--------|-------------|-----------------|
| **F4** | 2 | 8 | ❌ No | Low | ≤4 motors, legacy |
| **F7** | 2 | 8 | ❌ No | Low | 4-6 motors, good balance |
| **H7** | 2 | 8 | ✅ Yes | **High** | 6-12 motors, best performance |
| **AT32F43x** | 2 | Varies | ✅ Yes | **High** | Alternative to H7 |

---

## Peripheral DMA Mappings

### Motor Outputs (Timer DMA)

Motor outputs use timer DMA for precise PWM and DShot timing.

**Example: MATEKF722SE (F7 Board)**

| Output | Timer | Pin | DMA Assignment | Notes |
|--------|-------|-----|----------------|-------|
| S1 | TIM3_CH1 | PB4 | DMA1 Stream 4, Chan 5 | ✅ Available |
| S2 | TIM3_CH2 | PB5 | DMA1 Stream 5, Chan 5 | ⚠️ Conflicts with S5 |
| S3 | TIM3_CH3 | PB0 | DMA1 Stream 7, Chan 5 | ✅ Available |
| S4 | TIM3_CH4 | PB1 | DMA1 Stream 2, Chan 5 | ✅ Available |
| S5 | TIM2_CH1 | PA15 | DMA1 Stream 5, Chan 3 | ⚠️ Conflicts with S2 |
| S6 | TIM2_CH2 | PB3 | DMA1 Stream 6, Chan 3 | ✅ Available |
| S7 | TIM4_CH1 | PB6 | DMA1 Stream 0, Chan 2 | ✅ Available |
| S8 | TIM4_CH2 | PB7 | DMA1 Stream 3, Chan 2 | ✅ Available |
| LED | TIM1_CH1 | PA8 | DMA2 Stream 6, Chan 0 | ✅ Uses DMA2 |

**Conflict Resolution:**
- S2 and S5 both require DMA1 Stream 5 (different channels)
- F4/F7 cannot share streams - one will fail to initialize
- Solutions:
  1. Don't use conflicting outputs simultaneously
  2. Use polling mode (disable DMA) for one output
  3. Choose different timer pins in board design

**H7 Advantage:**
With DMAMUX, S2 and S5 can be assigned to different streams automatically, eliminating the conflict.

### Gyro (SPI DMA)

**Critical for Flight Performance**

The gyro provides orientation data at high frequency (typically 8kHz). DMA enables non-blocking SPI transfers, ensuring the CPU can focus on PID calculations.

**Typical Configuration:**
- SPI1: Gyro (MPU6000, MPU6500, ICM20689, ICM42605, BMI270)
- DMA2: Preferred controller (avoids DMA1 motor conflicts)

**Code Pattern:**
```c
// Drivers automatically claim DMA for SPI gyro
// See: drivers/accgyro/*.c, drivers/bus_spi_*.c
```

### UART (Serial DMA)

UARTs use DMA for efficient data transfer without CPU intervention.

**Usage:**
- RC Receivers (SBUS, CRSF, IBUS, FPort, GHST)
- GPS (NMEA, UBX protocols)
- Telemetry (SmartPort, CRSF, MAVLink, LTM)
- MSP (Configurator communication)

**Typical Assignment:**
- UART1: DMA2 (telemetry or RC)
- UART2-5: DMA1
- UART6: DMA2 (if available)

**Example (from target files):**
```c
#define UART1_AHB1_PERIPHERALS  RCC_AHB1Periph_DMA2
```

### ADC

Continuous analog-to-digital conversion for monitoring:
- Battery voltage (VBAT)
- Current consumption
- RSSI (signal strength)
- Airspeed (pitot tube)

**Typical Assignment:**
```c
#define ADC_INSTANCE        ADC1
#define ADC1_DMA_STREAM     DMA2_Stream0
```

Uses DMA2 to avoid conflicts with DMA1 motor outputs.

### SD Card / Flash (Blackbox Logging)

**SPI Mode:**
- Uses SPI3 DMA (typically)
- Non-blocking writes beneficial for performance
- Shares SPI DMA infrastructure

**SDIO Mode:**
- Dedicated SDIO peripheral with DMA
- Faster than SPI mode
- Used on higher-end boards

**Owner:** `OWNER_SDCARD`

### LED Strip (WS2811/WS2812)

Uses timer DMA for precise timing of LED protocol.

**Configuration:**
```c
#define USE_LED_STRIP
#define WS2811_PIN  PA8  // Timer pin with DMA
```

Typically uses DMA2 to avoid motor conflicts.

---

## Resource Allocation

### DMA Initialization API

**Claiming a DMA Stream:**
```c
void dmaInit(DMA_t dma, resourceOwner_e owner, uint8_t resourceIndex);
```

- `dma`: DMA descriptor obtained from `dmaGetByTag()` or `dmaGetByRef()`
- `owner`: Owner type (OWNER_TIMER, OWNER_SPI, etc.)
- `resourceIndex`: Index within owner type

**Checking Ownership:**
```c
resourceOwner_e dmaGetOwner(DMA_t dma);
```

Returns `OWNER_FREE` if unallocated, otherwise returns the current owner.

**Getting DMA Descriptor:**
```c
DMA_t dmaGetByTag(dmaTag_t tag);      // Find by DMA tag
DMA_t dmaGetByRef(DMA_Stream_TypeDef* ref);  // Find by hardware reference
```

### Resource Validation

**Current State:** ⚠️ Inconsistent

INAV has infrastructure for conflict detection but doesn't consistently enforce it:

**Best Practice (HAL Timer Implementation):**
```c
// Check if DMA is available before claiming
if (dmaGetOwner(tch->dma) != OWNER_FREE) {
    return false;  // Already in use!
}

dmaInit(tch->dma, OWNER_TIMER, 0);
```

**Problem:** Most peripherals (ADC, SD card, some timers) don't validate before claiming, potentially causing silent conflicts.

**Recommendation:** All DMA users should check `dmaGetOwner()` before calling `dmaInit()`.

### DMA Allocation Priority

Recommended allocation priority:

1. **Critical - Must Have DMA:**
   - Gyro SPI (DMA2 preferred)
   - Motors (DShot) (DMA1 primarily)

2. **High Priority:**
   - Primary UART (RC receiver or telemetry)
   - ADC (battery/current monitoring)

3. **Medium Priority:**
   - Secondary UARTs (GPS, additional telemetry)
   - SD Card (blackbox logging)

4. **Low Priority:**
   - LED Strip
   - OSD SPI (low data rate, polling sufficient)

---

## Common Conflicts and Solutions

### 1. Motor Output Conflicts (F4/F7)

**Problem:**
Limited DMA streams for 6-8 motor outputs. Some timer channels may require the same DMA stream.

**Example:** MATEKF722SE - S2 (TIM3_CH2) and S5 (TIM2_CH1) both need DMA1 Stream 5.

**Solutions:**
- **Board Design:** Choose timer pins with non-conflicting DMA assignments
- **Runtime:** Use only non-conflicting outputs
- **Fallback:** Configure one output for polling mode (disable DMA)
- **H7 Upgrade:** Use H7 boards with DMAMUX for automatic resolution

### 2. F4 DMA2 Errata (Bitbanged DShot vs Gyro)

**Problem:**
STM32 F4 has a silicon errata: DMA2 can corrupt data if AHB peripherals (GPIO) and APB peripherals (SPI) access it concurrently.

**Impact:**
- Bitbanged DShot writes motor values via GPIO using DMA2
- Gyro (SPI1) typically uses DMA2
- Concurrent usage → data corruption → flight instability

**Solutions:**
- ✅ **Use PWM-based DShot on F4** (timer PWM, not GPIO bitbang)
- ✅ **Design motor pins** on timers with DMA1 assignments
- ✅ **Upgrade to F7/H7** for better DMA management

**Reference:** [Betaflight Design Guidelines - F4 DShot](https://www.betaflight.com/docs/development/manufacturer/manufacturer-design-guidelines)

### 3. UART vs Motor Timer Conflicts

**Problem:**
Some pins can function as either UART or timer outputs, causing resource conflicts.

**Example:** MATEKF722SE - PA2 can be UART2 TX or TIM5_CH3.

**Solutions:**
- **Board Designers:** Avoid pin conflicts in schematic
- **Users:** Choose only one function per pin in configuration
- **Resource Manager:** Pin ownership tracked separately from DMA

### 4. LED Strip vs Motors

**Problem:**
LED strip (WS2811/2812) uses timer DMA, potentially conflicting with motor outputs.

**Solutions:**
- **Best Practice:** Use timer on DMA2 for LED strip
- **Alternative:** Use separate timer not used by motors
- **Example:** MATEKF722SE uses TIM1 (DMA2) for LED, avoiding TIM2/3/4 (DMA1) motor conflicts

---

## Best Practices

### For Board Designers

1. **Motor Outputs:**
   - Place M1-M4 on one GPIO port, one 4-channel timer with DMA
   - Avoid motor pins requiring the same DMA stream
   - Use DMA1 for motors, DMA2 for peripherals
   - For >4 motors on F4/F7, verify no DMA conflicts

2. **SPI1 (Gyro):**
   - Always use DMA2 for gyro SPI
   - Avoid bitbanged DShot on F4 (use PWM DShot)
   - Ensure SPI1 DMA2 assignment doesn't conflict with UART1/6

3. **UARTs:**
   - UART1: DMA2 (primary telemetry/RC)
   - UART2-5: DMA1 (GPS, secondary telemetry)
   - Document which UARTs share DMA streams

4. **LED Strip:**
   - Use timer on DMA2 to avoid motor conflicts
   - Example: TIM1 or TIM8 on DMA2

5. **Platform Selection:**
   - F4: ≤4 motors, basic configurations
   - F7: 4-6 motors, good balance
   - H7: 6-12 motors, complex configurations, DMAMUX flexibility

### For Firmware Developers

1. **Always Validate Before Claiming:**
   ```c
   if (dmaGetOwner(dma) != OWNER_FREE) {
       // Handle conflict: log error, disable feature, or return failure
       return false;
   }
   dmaInit(dma, OWNER_XXX, index);
   ```

2. **Use Appropriate Owner Types:**
   - Choose correct `resourceOwner_e` for your peripheral
   - Helps CLI `dma` command display accurate information

3. **Handle Initialization Failures:**
   - If DMA unavailable, fall back to polling mode (if possible)
   - Log warnings for users to diagnose conflicts

4. **Document DMA Requirements:**
   - In driver code, document which DMA streams are expected
   - Note any platform-specific limitations

5. **Test on Multiple Platforms:**
   - Verify DMA allocation on F4, F7, H7
   - Check for conflicts with common configurations

### For Users

1. **Understand Your Board:**
   - Check target.c for DMA assignments
   - Note conflicting outputs (marked in comments)

2. **Motor Outputs:**
   - If some motors don't initialize, check DMA conflicts
   - Use `dma` CLI command to view allocations

3. **Upgrade Path:**
   - For complex configurations (>6 motors), prefer H7 boards
   - F4 limited to 4 reliable DMA motor outputs

4. **Troubleshooting:**
   - Motor initialization failures → DMA conflict likely
   - Check CLI: `dma` command shows current allocations
   - Look for "DMA already in use" messages in logs

---

## CLI Commands

### `dma` Command

View current DMA allocations:

```
# dma
DMA:
 DMA1 Stream 0: TIMER
 DMA1 Stream 2: TIMER
 DMA1 Stream 3: TIMER
 DMA1 Stream 4: TIMER
 DMA1 Stream 5: TIMER (conflict possible!)
 DMA1 Stream 6: TIMER
 DMA1 Stream 7: TIMER
 DMA2 Stream 0: ADC
 DMA2 Stream 4: SPI
 DMA2 Stream 6: TIMER (LED)
```

**Usage:**
- Identify which streams are allocated
- Diagnose conflicts (multiple owners or failed allocations)
- Verify critical peripherals (gyro, motors) have DMA

**Implementation:**
- `drivers/dma_cli_stm32_impl.c` - STM32 CLI
- `drivers/dma_cli_at32f43x_impl.c` - AT32 CLI

---

## For Developers

### Adding DMA to a New Peripheral

**1. Define DMA Tag/Stream:**

In target files or driver:
```c
// Option A: Target-specific
#define MY_PERIPHERAL_DMA_STREAM  DMA2_Stream3

// Option B: Driver discovers from hardware
dmaTag_t dmaTag = timerChannelDmaTag(timerHardware);
```

**2. Get DMA Descriptor:**
```c
DMA_t dma = dmaGetByTag(DMA_TAG(2, 3, 5));  // DMA2, Stream 3, Channel 5
// or
DMA_t dma = dmaGetByRef(MY_PERIPHERAL_DMA_STREAM);
```

**3. Validate and Claim:**
```c
if (!dma) {
    // DMA not available on this platform
    return false;
}

if (dmaGetOwner(dma) != OWNER_FREE) {
    // Conflict! DMA already claimed
    LOG_ERROR("DMA conflict: stream already in use");
    return false;
}

dmaInit(dma, OWNER_MY_PERIPHERAL, peripheralIndex);
dmaSetHandler(dma, myDmaIrqHandler, NVIC_PRIO_MY_DMA, (uint32_t)context);
```

**4. Configure DMA Hardware:**
```c
// Platform-specific (HAL, LL, or StdPeriph)
LL_DMA_SetMemoryAddress(dma->ref, (uint32_t)buffer);
LL_DMA_SetPeriphAddress(dma->ref, (uint32_t)&PERIPHERAL->DR);
LL_DMA_SetDataLength(dma->ref, length);
// ... configure mode, priority, etc.
LL_DMA_EnableStream(dma->ref);
```

**5. Implement IRQ Handler:**
```c
static void myDmaIrqHandler(DMA_t dma)
{
    if (DMA_GET_FLAG_STATUS(dma, DMA_IT_TCIF)) {
        // Transfer complete
        DMA_CLEAR_FLAG(dma, DMA_IT_TCIF);
        // Handle completion
    }
    if (DMA_GET_FLAG_STATUS(dma, DMA_IT_TEIF)) {
        // Transfer error
        DMA_CLEAR_FLAG(dma, DMA_IT_TEIF);
        // Handle error
    }
}
```

### Debugging DMA Issues

**1. Check Allocations:**
Use CLI `dma` command or add debug logging:
```c
for (int i = 0; i < 16; i++) {
    if (dmaDescriptors[i].owner != OWNER_FREE) {
        LOG_DEBUG("DMA%d Stream%d: Owner=%d Index=%d",
                  DMATAG_GET_DMA(dmaDescriptors[i].tag),
                  DMATAG_GET_STREAM(dmaDescriptors[i].tag),
                  dmaDescriptors[i].owner,
                  dmaDescriptors[i].resourceIndex);
    }
}
```

**2. Verify Hardware Configuration:**
- Check GPIO alternate functions
- Verify timer channel mappings
- Confirm DMA stream/channel assignments match silicon datasheet

**3. Test Graceful Degradation:**
- Ensure features work without DMA (polling mode)
- Provide user-friendly error messages

**4. Platform Testing:**
- Test on all supported platforms (F4, F7, H7, AT32)
- Verify DMAMUX behavior on H7/AT32

### Comparison with Betaflight

INAV's DMA architecture is similar to Betaflight with key differences:

| Feature | Betaflight | INAV | Status |
|---------|-----------|------|--------|
| Owner tracking | ✅ Yes | ✅ Yes | Similar |
| Resource validation | ✅ Enforced | ⚠️ Partial | **INAV Gap** |
| HAL timer validation | ✅ Yes | ✅ Yes | Similar |
| StdPeriph validation | ✅ Yes (PR #10895) | ❌ No | **INAV Gap** |
| **SPI DMA** | ✅ Yes | ❌ **Polling only** | **MAJOR INAV Gap** |
| **Gyro SPI** | ✅ DMA | ❌ **Polling** | **Performance Gap** |
| **Blackbox SPI** | ✅ Non-blocking DMA | ❌ **Blocking polling** | **Performance Gap** |
| Per-peripheral DMA spec | ✅ USE_DMA_SPEC | ❓ TBD | Research needed |
| CLI viewing | ✅ Yes | ✅ Yes | Similar |
| DMAMUX (H7/AT32) | ✅ Yes | ✅ Yes | Similar |

**Key Recommendations:**
1. **Critical:** INAV should adopt Betaflight's consistent resource validation (PR #10895) to prevent silent DMA conflicts
2. **Important:** Implement SPI DMA for gyro and blackbox - INAV currently uses polling mode (see Section 3 below for detailed analysis)

---

## Improvement Opportunities

Based on research (comparing with Betaflight's DMA optimization work):

### 1. Consistent Resource Validation (High Priority)

**Problem:** Only HAL timer code checks `OWNER_FREE` before claiming DMA. StdPeriph timers, ADC, SD card, and other peripherals don't validate.

**Recommendation:**
- Add validation to core `dmaInit()` function:
  ```c
  void dmaInit(DMA_t dma, resourceOwner_e owner, uint8_t resourceIndex)
  {
      if (dma->owner != OWNER_FREE) {
          LOG_ERROR("DMA conflict: DMA%d Stream%d already owned by %d",
                    DMATAG_GET_DMA(dma->tag),
                    DMATAG_GET_STREAM(dma->tag),
                    dma->owner);
          // Option: return error code instead of void
          return;
      }
      dmaEnableClock(dma);
      dma->owner = owner;
      dma->resourceIndex = resourceIndex;
  }
  ```
- **OR** Require all callers to check before calling `dmaInit()`
- Audit all DMA users and add missing validation

**Impact:** Prevents silent conflicts and firmware lockups.

### 2. Per-Peripheral DMA Specification (Medium Priority)

**Betaflight Feature:** `USE_DMA_SPEC` allows runtime DMA configuration via CLI.

**Example:**
```
set adc1_dma_opt = 2  # Choose DMA stream option
set uart1_tx_dma_opt = 1
```

**Benefits:**
- Enables unified targets without recompilation
- Users can resolve conflicts without firmware changes
- Simplifies board design (less hardcoded assignments)

**Recommendation:** Investigate Betaflight PR #6837 for implementation approach.

### 3. Implement SPI DMA - Currently Using Polling Mode! (Medium-High Priority)

**Critical Finding:** INAV's SPI implementation uses **byte-by-byte polling**, not DMA at all.

#### Current Implementation Analysis

Examining `drivers/bus_spi_hal_ll.c:325-388`, the core `spiTransfer()` function:

```c
bool spiTransfer(SPI_TypeDef *instance, uint8_t *rxData, const uint8_t *txData, int len)
{
    while (len) {
        // BLOCKING: Busy-wait for TX ready
        while(!LL_SPI_IsActiveFlag_TXP(instance)) {
            if ((spiTimeout--) == 0) return false;
        }
        LL_SPI_TransmitData8(instance, b);

        // BLOCKING: Busy-wait for RX ready
        while (!LL_SPI_IsActiveFlag_RXP(instance)) {
            if ((spiTimeout--) == 0) return false;
        }
        b = LL_SPI_ReceiveData8(instance);
        --len;
    }
    // BLOCKING: Wait for transfer complete
    while (!LL_SPI_IsActiveFlag_EOT(instance));
}
```

**This is pure polling mode - the CPU busy-waits for each byte transfer!**

#### Performance Impact

**Gyro (SPI1) - High Frequency Reads:**
- 12-16 bytes per sample at 8kHz sampling rate
- ~10-20µs blocking time per read at 10-20 MHz SPI
- Total: **~160µs per second** spent in busy-wait loops
- Prevents CPU from doing useful work (PID calculations) during transfers
- At high loop rates (8kHz), even small delays impact consistency

**Blackbox Logging (SPI3 or SDIO):**
- Large frames: 100-500 bytes per write
- Blocking writes cause jitter in main loop timing
- Can interfere with gyro sampling and PID loop consistency
- Particularly problematic during logging bursts

**OSD (SPI2 - MAX7456):**
- Low update rate (~10Hz), minimal impact
- Already low priority peripheral

#### Comparison with Betaflight

Betaflight has implemented:
- **PR #10525 (2020-2021):** Non-blocking SPI DMA for blackbox logging
- DMA-based gyro SPI reads (needs verification)
- Significant reduction in main loop jitter

INAV appears to have fallen behind in this optimization area.

#### Recommended Implementation Strategy

**Phase 1: Gyro SPI DMA (Highest Impact)**
- **Priority:** High
- **Effort:** 1-2 weeks
- **Approach:**
  1. Implement DMA-based SPI layer for gyro reads
  2. Use DMA2 to avoid conflicts with motor timers (DMA1)
  3. Callback/interrupt on completion
  4. Fallback to polling if DMA unavailable
  5. Start with F7/H7 (HAL APIs simplify DMA setup)

**Code Structure:**
```c
// New API functions needed
bool spiTransferDMA(SPI_TypeDef *instance, uint8_t *rxBuf, const uint8_t *txBuf, int len,
                    dmaCallbackHandlerFuncPtr callback, void *context);
bool spiTransferDMAStart(SPI_TypeDef *instance, ...);
bool spiTransferDMAWait(SPI_TypeDef *instance, uint32_t timeout);

// Gyro driver changes
void gyroReadDMACallback(void *context) {
    // Process gyro data
    // Signal scheduler that data is ready
}

// In gyro sampling task
spiTransferDMAStart(gyroSPI, rxBuf, txBuf, length, gyroReadDMACallback, ctx);
// CPU now free to do other work
// Callback fires when complete
```

**Phase 2: Non-Blocking Blackbox Writes**
- **Priority:** Medium
- **Effort:** 1-2 weeks
- **Approach:**
  1. Implement async write API for SD card/flash
  2. Queue management for multiple frames
  3. Write-complete callbacks
  4. Follow Betaflight PR #10525 design

**Code Structure:**
```c
// Async blackbox API
bool blackboxWriteAsync(uint8_t *data, uint16_t length);
bool blackboxWritePending(void);
void blackboxWriteComplete(void);  // Callback

// In blackbox task
if (!blackboxWritePending()) {
    blackboxWriteAsync(frame, frameSize);
    // Continue without waiting
}
```

**Phase 3: Platform Rollout**
1. F7/H7 first (HAL DMA APIs)
2. F4 next (more manual DMA setup)
3. AT32F43x (similar to H7)

#### Expected Performance Improvements

**Conservative Estimates:**

| Metric | Before (Polling) | After (DMA) | Improvement |
|--------|------------------|-------------|-------------|
| Gyro read CPU time | 160µs/sec blocking | ~5µs/sec (setup only) | **97% reduction** |
| Worst-case loop jitter | +20µs (gyro) | +2µs (DMA setup) | **10µs improvement** |
| Blackbox write jitter | +50-200µs | +5µs | **45-195µs improvement** |
| CPU availability | Blocked during SPI | Free during transfer | **Concurrent processing** |
| Loop consistency | Variable | More consistent | **Better flight performance** |

**Real-World Impact:**
- More consistent PID loop execution
- Better handling of high gyro rates (8kHz+)
- Reduced jitter during blackbox logging
- Overall ~5-10% improvement in loop timing consistency

#### Why This Matters

1. **Flight Performance:** Even small improvements in loop consistency translate to better flight characteristics, especially in aggressive flying or windy conditions

2. **High-Rate Gyros:** Modern gyros support 8kHz sampling. DMA becomes increasingly important at higher rates.

3. **Blackbox Quality:** Consistent logging without impacting flight performance improves data quality for tuning.

4. **CPU Headroom:** Freeing CPU during SPI transfers allows for future features without degrading flight performance.

#### Priority Justification: Medium-High

**Not Critical Because:**
- Current polling implementation works - INAV flies well
- Impact is measurable but not dramatic (sub-millisecond level)
- No crashes or safety issues

**Important Because:**
- Measurable flight performance improvement
- Betaflight has already implemented this (competitive gap)
- Relatively straightforward implementation (1-2 weeks per phase)
- Enables future high-rate features
- Industry best practice (DMA for high-throughput peripherals)

#### Implementation Risks

**Low Risk:**
- Polling mode can remain as fallback
- Incremental rollout (gyro first, then blackbox)
- Each phase independently testable
- No architectural changes required

**Testing Required:**
- Verify no data corruption (DMA cache coherency on H7)
- Confirm timing improvements with blackbox logging
- Stress testing at maximum gyro rates
- Multi-platform validation (F4/F7/H7)

#### Recommendation

**Implement in 2 phases with separate PRs:**

1. **PR 1: Gyro SPI DMA** (4-6 weeks)
   - Week 1-2: Implement DMA layer, F7/H7 first
   - Week 3-4: Integrate with gyro drivers, testing
   - Week 5-6: F4 support, edge case handling

2. **PR 2: Async Blackbox** (4-6 weeks)
   - Week 1-2: Non-blocking write API
   - Week 3-4: Queue management, callbacks
   - Week 5-6: Integration, testing

**Total effort: 8-12 weeks across two contributors**

This would bring INAV's SPI performance in line with Betaflight and modern best practices.

### 4. DMA Usage Documentation in Target Files (Low Priority)

**Enhancement:** Annotate DMA assignments in target.c comments (like MATEKF722SE motor outputs).

**Example:**
```c
// Motors use DMA1 streams - note conflicts:
DEF_TIM(TIM3, CH2, PB5, TIM_USE_OUTPUT_AUTO, 0, 0),  // S2  D(1,5,5) - conflicts with S5
DEF_TIM(TIM2, CH1, PA15, TIM_USE_OUTPUT_AUTO, 0, 0), // S5  D(1,5,3) - conflicts with S2
```

**Benefits:**
- Helps board designers identify conflicts
- Assists users in troubleshooting
- Documents intended DMA usage

---

## References

### INAV Source Files

- `src/main/drivers/dma.h` - DMA abstraction API
- `src/main/drivers/dma_stm32f4xx.c` - F4 implementation
- `src/main/drivers/dma_stm32f7xx.c` - F7 implementation
- `src/main/drivers/dma_stm32h7xx.c` - H7 implementation
- `src/main/drivers/dma_at32f43x.c` - AT32 implementation
- `src/main/drivers/resource.h` - Resource ownership types
- `src/main/target/*/target.c` - Board-specific DMA assignments

### Betaflight DMA Research

- [PR #10895 - DMA Resource Validation](https://github.com/betaflight/betaflight/pull/10895)
- [PR #6837 - Per-Peripheral DMA Spec](https://github.com/betaflight/betaflight/pull/6837)
- [PR #14320 - Platform-Specific DMA Refactoring](https://github.com/betaflight/betaflight/pull/14320)
- [PR #10525 - Non-Blocking SPI DMA](https://github.com/betaflight/betaflight/pull/10525)
- [Issue #4847 - F4 DShot DMA Burst](https://github.com/betaflight/betaflight/issues/4847)
- [Betaflight Design Guidelines](https://www.betaflight.com/docs/development/manufacturer/manufacturer-design-guidelines)

### STM32 Documentation

- STM32F4 Reference Manual (RM0090) - DMA Controller section
- STM32F7 Reference Manual (RM0385) - DMA Controller section
- STM32H7 Reference Manual (RM0433) - DMA and DMAMUX sections
- STM32F4 Errata (ES0206) - DMA2 concurrent access errata

---

**Last Updated:** 2025-11-24
**Maintainer:** INAV Development Team
