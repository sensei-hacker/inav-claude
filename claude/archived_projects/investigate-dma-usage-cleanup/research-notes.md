# DMA Usage Investigation - Research Notes

**Project:** investigate-dma-usage-cleanup
**Date Started:** 2025-11-24
**Researcher:** Claude (AI Assistant)

---

## Phase 1: Betaflight DMA Cleanup Research

### Executive Summary

Betaflight has performed extensive DMA optimization work over several years, focusing on:
1. Resource allocation validation to prevent double-allocation bugs
2. Per-peripheral DMA channel specification for unified targets
3. Platform-specific DMA optimizations (F4 burst mode, F7/H7 bitbanged DShot)
4. Code refactoring to consolidate platform-specific DMA logic

### Key Pull Requests and Changes

#### 1. PR #10895 - Added Resource Allocation for DMA
**Date:** ~2021
**Author:** mikeller
**Link:** [https://github.com/betaflight/betaflight/pull/10895](https://github.com/betaflight/betaflight/pull/10895)

**Problem Solved:**
- Firmware lockups caused by DMA resource conflicts
- Multiple peripherals (motors, SPI, ADC) competing for same DMA streams
- Silent failures making debugging difficult

**Technical Approach:**
- Added validation checks in DMA allocation layer
- Prevents claiming resources already assigned to different owners
- Makes conflicts immediately apparent instead of causing silent lockups

**Affected Components:**
- `src/main/drivers/dma.c` - Core DMA driver
- `src/main/drivers/bus_spi.c` - SPI bus driver
- `src/main/drivers/pwm_output_dshot_hal.c` - Motor control
- ADC drivers (F1/F3 variants)

**Impact:**
- Motor initialization failures now visible (e.g., Motor 4 failing on certain boards)
- Improved debuggability
- Better resource conflict visibility

**Tested Boards:**
- Matek F411, F722 Mini
- FOXEER F722 V2
- SPRacing H7 Extreme

#### 2. PR #6837 - Per-Peripheral DMA Channel Spec
**Date:** ~2018-2019
**Author:** jflyper
**Link:** [https://github.com/betaflight/betaflight/pull/6837](https://github.com/betaflight/betaflight/pull/6837)

**Problem Solved:**
- Hardcoded DMA stream assignments blocked unified target development
- Targets required recompilation to change DMA configurations
- No flexibility for different hardware configurations

**Solution - USE_DMA_SPEC:**
- CLI-accessible parameters for DMA options (e.g., `ADC1_DMA_OPT`, `ADC2_DMA_OPT`)
- Per-peripheral DMA channel assignment control
- Backward compatibility with pre-4.0 defaults
- Support for optional DMA (e.g., SD card using `-1` to disable)

**Benefits:**
- Enables generic flight controller targets
- User-configurable DMA assignments
- Reduces need for target-specific firmware builds

#### 3. PR #14320 - Platform-Specific DMA Code Refactoring
**Date:** March 2025
**Author:** blckmn
**Link:** [https://github.com/betaflight/betaflight/pull/14320](https://github.com/betaflight/betaflight/pull/14320)
**Milestone:** 4.6

**Changes:**
- Moved platform-specific DMA definitions to `platform/dma.h`
- Removed redundant platform-specific code from `src/main/drivers/dma.h`
- Consolidated DMA traits and definitions per platform
- Simplified driver code structure

**Benefits:**
- Cleaner code organization
- Easier platform maintenance
- Reduced code duplication

#### 4. PR #5729 - F7 Optimizations Cleanup
**Date:** ~2017-2018
**Author:** DieHertz
**Link:** [https://github.com/betaflight/betaflight/pull/5729](https://github.com/betaflight/betaflight/pull/5729)

**Changes:**
- Added `stm32f7xx_ll_ex.h` to simplify LL TIM and DMA functions
- Allowed passing `DMA_Stream_TypeDef* stream` instead of separate `DMA_TypeDef* DMA` and `uint32_t Stream`
- F7 DShot implementation refactored using new functions
- General cleanup and consolidation

#### 5. PR #10525 - Optimized SPI DMA for F4/F7/H7
**Date:** ~2020-2021
**Author:** SteveCEvans
**Link:** [https://github.com/betaflight/betaflight/pull/10525](https://github.com/betaflight/betaflight/pull/10525)

**Features:**
- New SPI bus API supporting non-blocking DMAs
- Modified blackbox FLASH writing to be non-blocking
- Sequence of SPI accesses processed under interrupt/DMA control
- Optional callbacks and chip select negation
- Polled mode during initialization, DMA mode after all devices claim descriptors

**Benefits:**
- No DMA descriptor conflicts during initialization
- More efficient SPI operations
- Non-blocking blackbox logging

#### 6. Issue #4847 - F4 DShot DMA Burst
**Link:** [https://github.com/betaflight/betaflight/issues/4847](https://github.com/betaflight/betaflight/issues/4847)

**Key Innovation:**
- F4 targets use DMA burst feature for DShot
- Drastically reduces DMA stream usage
- Reduces motor output selection constraints
- Slightly better motor command timing skew

**Technical Details:**
- Timer outputs "abused" for writing digital data using DMA burst function
- TIM_UP (burst) DSHOT wasn't meant to solve all problems but helps F4 resource constraints

### Platform-Specific DMA Strategies

#### STM32 F4 Series

**Critical Limitations:**
- DMA2 errata: Corruption may occur if AHB peripherals (GPIO) accessed concurrently with APB peripherals (SPI)
- Bitbanged DShot uses DMA2 to write GPIO - conflicts with SPI1 DMA (typically gyro)
- Cannot simultaneously support DMA on bitbanged DShot AND SPI Bus #1

**F4 Best Practices:**
- Use PWM-based DShot by default (not bitbanged)
- Design motor outputs on timers with non-conflicting DMA assignments
- Motor pins should use 1 GPIO port, max 2 ports
- M1-M4 required to use 1 GPIO port, preferably one 4-channel timer with DMA
- Well-designed F4 FCs allow both `dshot_burst` and `dshot_bitbang` disabled

**Workarounds:**
- `dshot_burst = ON` can resolve some TIM8 DMA conflicts
- F4 limited to 4 motor outputs for new designs

#### STM32 F7 Series

**Advantages:**
- No SPI1 DMA limitations of F4
- Greater flexibility in resource assignments
- Better suited for bitbanged DShot

**Recommendations:**
- Use bitbanged DShot by default for best performance
- Most efficient use of timer and DMA resources
- Compatible with bidirectional DShot

**Considerations:**
- F4/F7 have different dmaopt ordering on TIM8 channels
- Some conflicts still exist (e.g., LEDSTRIP vs TIM2_UP burst DSHOT)

#### STM32 H7, G4, AT32F435 Series

**Key Feature - DMAMUX:**
- Flexible DMA stream allocation
- Greatly reduces resource assignment challenges
- Timer conflicts more important than DMA stream availability

**Recommendations:**
- Use bitbanged DShot by default
- Advanced timers (TIM1/TIM8) use DMA to drive GPIO directly
- GPIO timer AF modes NOT used for bitbanged DShot
- Highly recommended for designs requiring >4 motor outputs

### Motor Output DMA Considerations

**Port Consolidation (All Platforms):**
- Optimal: 8 motors on 1 GPIO port
- Acceptable: 8 motors across 2 GPIO ports
- Unacceptable: 8 motors across >2 GPIO ports

**Default Protocols:**
- F4: PWM-based DShot (due to errata)
- F7/H7/G4/AT32: Bitbanged DShot (best performance)

**Timer Restrictions:**
- F4/F7: Bitbanged DShot always uses TIM1 and TIM8 - don't use for other functions
- H7/G4/AT32: More flexible timer assignment with DMAMUX

### Betaflight Design Philosophy

**Resource Priority:**
1. Motor channels (highest priority)
2. Gyro SPI (critical for flight performance)
3. Other peripherals

**DMA Allocation Principles:**
- Validate before claiming resources
- Fail visibly, not silently
- Make conflicts immediately apparent
- Support runtime configuration where possible

### Common DMA Conflicts Identified

1. **F4: Bitbanged DShot vs SPI1 (gyro)**
   - Both use DMA2
   - STM32 errata prevents concurrent use
   - Solution: Use PWM DShot or design motor pins on non-conflicting streams

2. **Motor Output vs ADC**
   - ADC is heavy DMA consumer
   - Per-peripheral DMA spec helps resolve

3. **LED Strip vs Motor Burst Mode**
   - LEDSTRIP can conflict with TIM2_UP using burst DSHOT
   - Platform-specific

4. **SD Card DMA**
   - Can be made optional (-1 to disable)
   - SDIO vs SPI different DMA usage

### Key Takeaways for INAV

1. **Resource Validation Critical**
   - Betaflight's PR #10895 approach prevents lockups
   - INAV should verify no double-allocation possible

2. **Platform-Specific Optimization**
   - F4/F7/H7 require different strategies
   - H7 DMAMUX significantly simplifies resource management

3. **Motor Output Priority**
   - Bitbanged DShot most efficient for F7/H7
   - F4 needs PWM DShot or careful timer selection

4. **Configurable DMA Specs**
   - Per-peripheral DMA options enable unified targets
   - CLI-accessible configuration valuable

5. **Non-blocking DMA**
   - Blackbox and SPI optimizations use non-blocking approach
   - Better CPU utilization

---

## Sources

- [PR #10895 - Added resource allocation for DMA](https://github.com/betaflight/betaflight/pull/10895)
- [PR #6837 - Introduce per peripheral DMA channel spec option](https://github.com/betaflight/betaflight/pull/6837)
- [PR #14320 - REFACTOR: Moving platform specific DMA code](https://github.com/betaflight/betaflight/pull/14320)
- [PR #5729 - Post-cleanup of F7 optimizations](https://github.com/betaflight/betaflight/pull/5729)
- [PR #10525 - Added optimised SPI DMA support for F4/F7/H7](https://github.com/betaflight/betaflight/pull/10525)
- [Issue #4847 - F4 DShot goes DMA burst](https://github.com/betaflight/betaflight/issues/4847)
- [Betaflight Manufacturer Design Guidelines](https://www.betaflight.com/docs/development/manufacturer/manufacturer-design-guidelines)
- [PR #12050 - Use USE_DMA_SPEC without preconditions](https://github.com/betaflight/betaflight/pull/12050)
- [PR #10865 - Changed naming of SPI DMA resources](https://github.com/betaflight/betaflight/pull/10865)
- [PR #10747 - New memory section types for DMA](https://github.com/betaflight/betaflight/pull/10747)

---

---

## Phase 2: INAV DMA Architecture Analysis

### DMA Abstraction Layer

**Core Files:**
- `drivers/dma.h` - Platform-agnostic abstraction layer
- `drivers/dma_stm32f4xx.c` - F4 implementation (identical to F7 except for copyright)
- `drivers/dma_stm32f7xx.c` - F7 implementation
- `drivers/dma_stm32h7xx.c` - H7 implementation
- `drivers/dma_at32f43x.c` - AT32 implementation (includes DMAMUX)
- `drivers/dma_cli_stm32_impl.c` - CLI interface for DMA viewing
- `drivers/resource.h` - Resource ownership enumeration

### DMA Tag System

INAV uses a packed 32-bit tag to encode DMA information:

```c
typedef uint32_t dmaTag_t;
#define DMA_TAG(dma, stream, channel) ( (((dma) & 0x03) << 12) | (((stream) & 0x0F) << 8) | (((channel) & 0xFF) << 0) )
```

**Encoding:**
- Bits 12-13: DMA controller (1 or 2)
- Bits 8-11: Stream number (0-7)
- Bits 0-7: Channel number

**Extraction macros:**
```c
#define DMATAG_GET_DMA(x)     ( ((x) >> 12) & 0x03 )
#define DMATAG_GET_STREAM(x)  ( ((x) >> 8)  & 0x0F )
#define DMATAG_GET_CHANNEL(x) ( ((x) >> 0)  & 0xFF )
```

### DMA Descriptor Structure

Each DMA stream has a descriptor tracking its state:

```c
typedef struct dmaChannelDescriptor_s {
    dmaTag_t                    tag;              // Packed DMA/stream/channel
    DMA_TypeDef*                dma;              // Hardware controller (DMA1/DMA2)
    DMA_Stream_TypeDef*         ref;              // Stream reference
    dmaCallbackHandlerFuncPtr   irqHandlerCallback; // Interrupt handler
    uint32_t                    flagsShift;       // Status register bit offset
    IRQn_Type                   irqNumber;        // IRQ number
    uint32_t                    userParam;        // User data (often TCH_t pointer)
    resourceOwner_e             owner;            // Owner tracking
    uint8_t                     resourceIndex;    // Resource index within owner type
} dmaChannelDescriptor_t;
```

**Key field: `owner`** - Tracks which peripheral owns the DMA stream using `resourceOwner_e` enum.

### Resource Ownership System

**Ownership States (from `resource.h`):**
```c
OWNER_FREE = 0           // Unallocated
OWNER_MOTOR              // Motor/servo output (PWM/DShot)
OWNER_TIMER              // Timer-based operations
OWNER_SERIAL             // UART
OWNER_SPI                // SPI bus
OWNER_ADC                // Analog-to-digital converter
OWNER_SDCARD             // SD card (SDIO)
OWNER_LED_STRIP          // WS2811/2812 LED strips
... (29 total owner types)
```

### DMA Allocation - Resource Validation

**Q: Does INAV have resource validation like Betaflight PR #10895?**
**A: PARTIALLY IMPLEMENTED**

INAV has owner tracking and some validation, but implementation is inconsistent:

**HAL Timer Implementation (`timer_impl_hal.c`) - HAS VALIDATION:**
```c
// If DMA is already in use - abort
if (dmaGetOwner(tch->dma) != OWNER_FREE) {
    return false;  // Properly prevents double allocation
}

dmaInit(tch->dma, OWNER_TIMER, 0);
```

**StdPeriph Timer Implementation (`timer_impl_stdperiph.c`) - NO VALIDATION:**
```c
dmaInit(tch->dma, OWNER_TIMER, 0);  // No check - could overwrite!
```

**ADC (`adc_at32f43x.c`) - NO VALIDATION:**
```c
dmaInit(dmadac, OWNER_ADC, adcDevice);  // No check
```

**SD Card (`sdmmc_sdio_hal.c`) - NO VALIDATION:**
```c
dmaInit(dmaGetByRef(sd_dma.Instance), OWNER_SDCARD, 0);  // No check
```

**Core `dmaInit()` - NO VALIDATION:**
```c
void dmaInit(DMA_t dma, resourceOwner_e owner, uint8_t resourceIndex)
{
    dmaEnableClock(dma);
    dma->owner = owner;           // Simply overwrites owner!
    dma->resourceIndex = resourceIndex;
}
```

**Finding:** INAV has the infrastructure for conflict detection (`owner` field, `dmaGetOwner()`) but doesn't consistently enforce validation. Only HAL timer code checks before claiming. Most peripherals could silently overwrite DMA ownership.

### Platform Implementations

**F4 and F7 - Identical Structure:**
- 16 DMA descriptors (DMA1: streams 0-7, DMA2: streams 0-7)
- No DMAMUX - hardcoded channel assignments
- `dmaGetByTag()` matches only DMA controller and stream (channel ignored)

**H7 - Similar to F4/F7:**
- Same 16 descriptor structure
- DMA2 available
- Code nearly identical to F7

**AT32F43x - Enhanced:**
- Includes DMAMUX support (`dmaMuxref` field in descriptor)
- `dmaMuxEnable()` function for flexible channel assignment
- More similar to H7's flexibility

### DMA Usage by Peripheral

From grep analysis, DMA is used by:

1. **TIMER (Motor Output)**
   - Files: `timer_impl_hal.c`, `timer_impl_stdperiph.c`, `timer_impl_stdperiph_at32.c`
   - Owner: `OWNER_TIMER`
   - Validation: HAL version checks, StdPeriph doesn't
   - Used for: PWM motor output, DShot, LED strip (WS2811/2812)

2. **UART (Serial)**
   - Files: `serial_uart_stm32f4xx.c`, `serial_uart_stm32f7xx.c`, `serial_uart_stm32h7xx.c`
   - Owner: `OWNER_SERIAL`
   - Validation: Not visible in initial review (would need deeper analysis)

3. **ADC**
   - Files: `adc_at32f43x.c`
   - Owner: `OWNER_ADC`
   - Validation: None observed
   - Heavy DMA user per Betaflight research

4. **SD CARD (SDIO/SDMMC)**
   - Files: `sdcard_sdio.c`, `sdmmc_sdio_f4xx.c`, `sdmmc_sdio_hal.c`
   - Owner: `OWNER_SDCARD`
   - Validation: None observed

5. **SPI**
   - Files: `bus_spi_hal_ll.c`, `bus_spi.c`, `bus_spi_at32f43x.c`
   - Owner: `OWNER_SPI`
   - Analysis: Configuration visible but DMA usage not directly seen in initial 200 lines

### CLI Support

INAV includes DMA CLI commands for viewing allocation:

**Files:**
- `dma_cli_stm32_impl.c` - STM32 implementation
- `dma_cli_at32f43x_impl.c` - AT32 implementation

**Features:**
- Convert tags to human-readable format
- Show DMA controller/stream mappings
- Display timer names and pins for DMA channels
- Extract UART TX/RX pins for DMA assignments

This enables `dma` command in CLI to view resource allocation status.

### Key Findings - INAV vs Betaflight

| Feature | Betaflight | INAV | Status |
|---------|-----------|------|--------|
| Owner tracking | ✅ Yes | ✅ Yes | **Match** |
| Resource validation in core | ✅ In dmaInit | ❌ No check in dmaInit | **INAV Gap** |
| HAL timer validation | ✅ Yes | ✅ Yes | **Match** |
| StdPeriph timer validation | ✅ Yes (after PR #10895) | ❌ No | **INAV Gap** |
| ADC validation | ✅ Yes | ❌ No | **INAV Gap** |
| Per-peripheral DMA spec | ✅ USE_DMA_SPEC | ❓ Unknown (Phase 3) | **TBD** |
| CLI DMA viewing | ✅ Yes | ✅ Yes | **Match** |
| Platform abstraction | ✅ Yes | ✅ Yes | **Match** |
| DMAMUX (H7/AT32) | ✅ Yes | ✅ Yes (AT32) | **Match** |

### Potential Issues

1. **Inconsistent Validation**
   - Most peripherals don't check `OWNER_FREE` before claiming DMA
   - Could lead to silent conflicts and lockups
   - Betaflight PR #10895 approach would prevent this

2. **No Central Enforcement**
   - `dmaInit()` doesn't validate - just overwrites owner
   - Each peripheral responsible for checking (most don't)
   - Easy for new code to introduce conflicts

3. **StdPeriph Legacy Code**
   - Older StdPeriph drivers lack validation
   - HAL drivers have better checks
   - Migration to HAL ongoing but incomplete

### Comparison Summary

INAV's DMA architecture is similar to Betaflight's foundation but **lacks consistent resource conflict detection**. The infrastructure exists (`owner` field, `dmaGetOwner()`) but isn't enforced.

**Recommendation Areas:**
1. Add validation to `dmaInit()` or require all callers to check
2. Audit all DMA users for conflict checking
3. Document DMA allocation requirements for new code
4. Investigate per-peripheral DMA spec support

---

---

## Phase 3: Peripheral DMA Usage Mapping

### Analysis Method

Examined target configurations for representative F7 and H7 boards:
- **MATEKF722SE** (F7 - popular fixed-wing/multirotor board)
- **MATEKH743** (H7 - newer with DMAMUX)

### DMA Allocation Patterns

#### Motor Output (Timer DMA)

**F7 (MATEKF722SE) - Explicit DMA Assignments:**

Motor outputs use timer DMA with hardcoded stream/channel assignments:

| Output | Timer | Pin | DMA Assignment | Notes |
|--------|-------|-----|----------------|-------|
| S1 | TIM3_CH1 | PB4 | D(1, 4, 5) | DMA1 Stream 4 |
| S2 | TIM3_CH2 | PB5 | D(1, 5, 5) | DMA1 Stream 5 |
| S3 | TIM3_CH3 | PB0 | D(1, 7, 5) | DMA1 Stream 7 |
| S4 | TIM3_CH4 | PB1 | D(1, 2, 5) | DMA1 Stream 2 |
| S5 | TIM2_CH1 | PA15 | D(1, 5, 3) | **Conflicts with S2!** |
| S6 | TIM2_CH2 | PB3 | D(1, 6, 3) | DMA1 Stream 6 |
| S7 | TIM4_CH1 | PB6 | D(1, 0, 2) | DMA1 Stream 0 |
| S8 | TIM4_CH2 | PB7 | D(1, 3, 2) | DMA1 Stream 3 |
| LED | TIM1_CH1 | PA8 | D(2, 6, 0) | DMA2 Stream 6 - WS2811 strip |

**Key Finding:**
- Documented DMA conflict: S5 (TIM2_CH1) and S2 (TIM3_CH2) both need DMA1 Stream 5
- This limits usable motor outputs if both are used with DMA-based DShot
- LED strip uses DMA2 to avoid motor output conflicts

**H7 (MATEKH743) - No Explicit Assignments:**

```c
DEF_TIM(TIM3, CH3, PB0, TIM_USE_OUTPUT_AUTO, 0, 0),   // S1
DEF_TIM(TIM3, CH4, PB1, TIM_USE_OUTPUT_AUTO, 0, 1),   // S2
DEF_TIM(TIM5, CH1, PA0, TIM_USE_OUTPUT_AUTO, 0, 2),   // S3
...
DEF_TIM(TIM4, CH4, PD15, TIM_USE_OUTPUT_AUTO, 0, 0),   // S10 DMA_NONE
DEF_TIM(TIM15, CH2, PE6, TIM_USE_OUTPUT_AUTO, 0, 0),   // S12 DMA_NONE
```

- No hardcoded DMA stream/channel in comments
- DMAMUX allows runtime assignment
- Some outputs marked "DMA_NONE" - polled or without DMA capability
- More flexible than F4/F7 fixed assignments

#### ADC

**F7 (MATEKF722SE):**
```c
#define ADC_INSTANCE        ADC1
#define ADC1_DMA_STREAM     DMA2_Stream0
```

- Explicitly assigns ADC1 to DMA2 Stream 0
- Avoids conflicts with DMA1 motor outputs
- Typical for voltage/current/RSSI monitoring

**H7:** Similar explicit assignment expected but platform uses DMAMUX.

#### UART (Serial)

Found in various F4 targets:
```c
#define UART1_AHB1_PERIPHERALS  RCC_AHB1Periph_DMA2
```

- UART1 typically uses DMA2 (avoids DMA1 motor conflicts)
- Other UARTs likely platform-specific assignments
- DMA enables efficient telemetry, GPS, and RC protocols

**Usage Patterns:**
- RC receivers (SBUS, CRSF, IBUS, FPort)
- GPS (NMEA, UBX)
- Telemetry (SmartPort, CRSF, MAVLink, LTM)
- MSP (Configurator communication)

#### SPI

**Target Configuration (MATEKF722SE):**
```c
#define USE_SPI_DEVICE_1
#define SPI1_SCK_PIN            PA5  // Gyro
#define USE_SPI_DEVICE_2
#define SPI2_SCK_PIN            PB13 // OSD (MAX7456)
#define USE_SPI_DEVICE_3
#define SPI3_SCK_PIN            PC10 // SD Card / Flash
```

**DMA Usage:**
- SPI1: Gyro (MPU6000/6500/ICM-series) - **CRITICAL for high-frequency sampling**
- SPI2: OSD (MAX7456) - Lower priority, may not need DMA
- SPI3: SD card / Flash (blackbox logging) - Benefits from DMA for non-blocking writes

**Expected Assignments (not explicitly documented in target files):**
- SPI1 on DMA2 (high-speed gyro)
- SPI3 on DMA1/DMA2 depending on availability

#### SD Card / Flash (SDIO)

SD card can use either SPI or SDIO interface:

**SPI Mode (MATEKF722SE):**
```c
#define USE_SDCARD_SPI
#define SDCARD_SPI_BUS          BUS_SPI3
```
- Uses SPI3 DMA (see above)

**SDIO Mode (other boards):**
- Uses dedicated SDIO DMA stream
- Found in `sdcard_sdio.c`, `sdmmc_sdio_f4xx.c`, `sdmmc_sdio_hal.c`
- Owner: `OWNER_SDCARD`
- Blackbox logging to onboard storage

### DMA Usage Summary by Peripheral

| Peripheral | Owner Type | DMA Controller Preference | Critical? | Notes |
|------------|------------|---------------------------|-----------|-------|
| **Gyro (SPI1)** | OWNER_SPI | DMA2 preferred | **YES** | High-frequency sampling (8kHz), critical for flight performance |
| **Motors (Timers)** | OWNER_TIMER | DMA1 primarily | **YES** | DShot protocol, potential conflicts between outputs |
| **UART (Serial)** | OWNER_SERIAL | DMA2 preferred | Medium | Telemetry, GPS, RC receiver - efficiency benefit |
| **ADC** | OWNER_ADC | DMA2 typical | Medium | Voltage, current, RSSI monitoring |
| **OSD (SPI2)** | OWNER_SPI | Either | Low | MAX7456, lower data rate |
| **SD Card/Flash** | OWNER_SDCARD | Either | Low | Blackbox logging, non-blocking writes desirable |
| **LED Strip** | OWNER_LED_STRIP | DMA2 typical | Low | WS2811/2812, uses timer DMA |

### Common Conflict Patterns

From target analysis and code review:

1. **Motor Output Conflicts (F4/F7)**
   - Limited DMA streams for 6-8 motor outputs
   - Example: MATEKF722SE S2 vs S5 both want DMA1 Stream 5
   - Forces some outputs to use polling or causes initialization failure
   - Addressed by careful timer selection in board design

2. **F4 DMA2 Contention (per Betaflight research)**
   - Bitbanged DShot (GPIO writes) uses DMA2
   - SPI1 Gyro needs DMA2
   - STM32 errata prevents concurrent usage
   - **Mitigation:** F4 boards should use PWM-based DShot, not bitbanged

3. **UART vs Motor Timers**
   - Some pins can be used for either UART or timer
   - Resource manager must prevent conflicts
   - Example: MATEKF722SE PA2 used for both UART2 TX and softserial

4. **LED Strip vs Motors**
   - LED strip uses timer DMA (WS2811/2812 protocol)
   - Can conflict with motor timer resources
   - Typically placed on separate timer/DMA to avoid issues

### Platform Differences

| Platform | DMA Controllers | Streams per Controller | DMAMUX | Flexibility |
|----------|-----------------|----------------------|--------|-------------|
| **F4** | DMA1, DMA2 | 8 each | No | Low - hardcoded assignments |
| **F7** | DMA1, DMA2 | 8 each | No | Low - hardcoded assignments |
| **H7** | DMA1, DMA2 | 8 each | **Yes** | **High** - runtime assignment |
| **AT32F43x** | DMA1, DMA2 | Varies | **Yes** | **High** - runtime assignment |

**H7/AT32 Advantage:**
- DMAMUX eliminates most hardcoded conflicts
- Can assign any request to any stream dynamically
- More motor outputs possible without DMA conflicts
- Simplifies board design

### Wasted or Unnecessary DMA Usage?

**Potential Optimization Areas:**

1. **OSD (MAX7456)**
   - Low data rate (text overlay updates)
   - Polling likely sufficient
   - DMA may be wasted resource
   - **Finding:** Likely doesn't use DMA in current code

2. **Low-frequency UART ports**
   - Configuration/debug ports rarely used
   - Could use polling instead of DMA
   - **Finding:** Needs deeper code analysis to confirm if all UARTs claim DMA

3. **SD Card writes (non-critical)**
   - Blackbox logging not real-time critical
   - Non-blocking DMA beneficial but not required
   - **Finding:** Betaflight optimized this (PR #10525), INAV should review

4. **ADC for non-critical sensors**
   - Airspeed, temperature - low sample rates
   - Could consolidate into single ADC DMA channel
   - **Finding:** Current implementation needs review

**No Evidence of Major Waste:**
Most DMA usage appears intentional and beneficial. Critical peripherals (gyro, motors) appropriately prioritized.

---

## Next Steps

Phase 4-5: Synthesize findings into comprehensive DMA documentation for `inav/docs/development/DMA-USAGE.md`

**Documentation Structure:**
1. DMA Architecture Overview
2. Platform Differences (F4/F7/H7/AT32)
3. Peripheral DMA Mappings
4. Common Conflict Patterns and Solutions
5. Resource Allocation Best Practices
6. Improvement Recommendations
