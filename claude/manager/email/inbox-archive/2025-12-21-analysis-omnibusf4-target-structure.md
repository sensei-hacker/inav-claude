# Analysis Complete: OMNIBUSF4 Target Structure

**Date:** 2025-12-21
**From:** Developer
**Type:** Analysis Report

## Status: COMPLETE

## Summary

Analyzed the OMNIBUSF4 target directory containing 9 targets with extensive conditional compilation. Identified natural groupings for potential split and evaluated softserial runtime configuration feasibility.

---

## Target Comparison Table

| Feature | DYSF4PRO | DYSF4PROV2 | OMNIBUSF4 | OMNIBUSF4PRO | OMNIBUSF4V3 | V3_S6_SS | V3_S5S6_SS | V3_S5_S6_2SS | V3_ICM |
|---------|----------|------------|-----------|--------------|-------------|----------|------------|--------------|---------|
| **Board ID** | DYS4 | DY42 | OBF4 | OBSD | OB43 | OB43 | OB43 | OB43 | OB4I |
| **I2C Bus** | I2C2 | I2C1 (PB8/9) | I2C2 | I2C2 | I2C2 | I2C2 | I2C2 | I2C2 | I2C2 |
| **Storage** | SPI Flash | SPI Flash | SPI Flash | SD Card (SPI2) | SD Card (SPI2) | SD Card | SD Card | SD Card | SD Card |
| **Barometer** | I2C | I2C | I2C | BMP280 (SPI3) | BMP280 (SPI3) | BMP280 | BMP280 | BMP280 | BMP280 |
| **Gyro** | MPU6000 | MPU6000 | MPU6000 | MPU6000/6500/BMI270 | MPU6000/6500/BMI270 | Same | Same | Same | **ICM42605** |
| **Gyro Align** | CW180 | CW180 | CW180 | CW270 | CW270 | CW270 | CW270 | CW270 | **CW180** |
| **SPI2** | No | No | No | Yes (SD card) | Yes (SD card) | Yes | Yes | Yes | Yes |
| **UART6 Inverter** | No | No | No | PC0 only | PC8/PC9 | PC8/PC9 | PC8/PC9 | PC8/PC9 | PC8/PC9 |
| **LED Strip Pin** | PA1 (S5) | PA1 (S5) | PA1 (S5) | PB6 | PB6 | PB6 | PB6 | PB6 | PB6 |
| **Softserial1 Pin** | PC8/PC9 | PC8/PC9 | PC8/PC9 | PC8/PC9 | PC6 (UART6 TX) | **PA8 (S6)** | **PA1/PA8 (S5/S6)** | **PA1 (S5)** | PC6 |
| **Softserial2 Pin** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | **PA8 (S6)** | N/A |
| **Serial Port Count** | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 5 |
| **ADC Channel 3** | PC3 | PA0 | PA0 | PA0 | PA0 | PA0 | PA0 | PA0 | PA0 |
| **Current Scale** | Default | Default | Default | 265 | Default | Default | Default | Default | Default |

---

## Answer to Question 1: Logical Split

### Recommended 3-Group Structure

**YES, there is a clear logical split into 3 groups:**

### **Group A: DYS Variants → `target/DYSF4/`**
- DYSF4PRO
- DYSF4PROV2

**Shared characteristics:**
- Different product name ("DysF4Pro" vs "Omnibus F4")
- SPI flash storage (not SD card)
- I2C barometer (not SPI)
- CW180 gyro alignment
- No SPI2 device
- DYSF4PRO has unique ADC3 pin (PC3)
- DYSF4PROV2 has unique I2C1 bus configuration

**Differences within group:** Minimal - mainly I2C bus selection (I2C1 vs I2C2)

---

### **Group B: Original Omnibus (Flash) → `target/OMNIBUSF4/`**
- OMNIBUSF4 (keep in existing directory)

**Characteristics:**
- SPI flash storage
- I2C barometer
- CW180 gyro alignment
- No SPI2 device
- LED strip on PA1 (motor output S5)
- Softserial on PC8/PC9

**Reason to keep separate:** This is the "base" variant - different enough from both DYS and PRO variants.

---

### **Group C: Omnibus PRO/V3 (SD Card) → `target/OMNIBUSF4PRO/`**
- OMNIBUSF4PRO
- OMNIBUSF4V3
- OMNIBUSF4V3_S6_SS
- OMNIBUSF4V3_S5S6_SS
- OMNIBUSF4V3_S5_S6_2SS
- OMNIBUSF4V3_ICM

**Shared characteristics:**
- SD card storage (SPI2)
- BMP280 barometer on SPI3
- CW270 gyro alignment
- LED strip on PB6
- Support multiple gyro types (MPU6000/6500/BMI270, plus ICM42605 for V3_ICM)
- SPI2 device enabled

**Differences within group:**
- OMNIBUSF4PRO: Only UART1 inverter (PC0)
- OMNIBUSF4V3 variants: UART6 inverter (PC8/PC9)
- OMNIBUSF4V3_ICM: Adds ICM42605 gyro with CW180 alignment
- Softserial variants: Only pin configuration differences

---

## Answer to Question 2: Runtime Softserial Configuration

### **NO - Current Architecture Prevents Runtime Configuration**

**Current System:**
- Softserial pins are **compile-time #defines** (`SOFTSERIAL_1_RX_PIN`, etc.)
- Timer allocation checks these defines at compile time
- Pin usage flags (`TIM_USE_ANY` vs `TIM_USE_OUTPUT_AUTO`) are set in `timerHardware[]` array at compile time

**From `target.c` analysis:**
```c
// Normal build: S5/S6 for motors
DEF_TIM(TIM5, CH2, PA1, TIM_USE_OUTPUT_AUTO, 0, 0)  // S5 - motor/servo
DEF_TIM(TIM1, CH1, PA8, TIM_USE_OUTPUT_AUTO, 0, 0)  // S6 - motor/servo

// Softserial build: S5/S6 marked as "any use"
DEF_TIM(TIM5, CH2, PA1, TIM_USE_ANY, 0, 0)  // S5 - available for softserial
DEF_TIM(TIM1, CH1, PA8, TIM_USE_ANY, 0, 0)  // S6 - available for softserial
```

**From `pwm_mapping.c` analysis:**
- Softserial pins are looked up using `timerGetByTag(IO_TAG(SOFTSERIAL_1_RX_PIN), TIM_USE_ANY)`
- The system prevents motor allocation on pins marked for softserial
- But this is all **compile-time**, not runtime

**What would be needed for runtime configuration:**
1. Remove compile-time `SOFTSERIAL_X_RX_PIN` defines
2. Add runtime softserial pin configuration (via CLI/Configurator)
3. Modify timer allocation to support dynamic pin assignment
4. Allow `TIM_USE_ANY` on all potential softserial pins (S5, S6, PC6, PC8, PC9)
5. Dynamically allocate timers based on user configuration

**Technical barriers:**
- Timer hardware array (`timerHardware[]`) is const and initialized at compile time
- Major refactoring of timer/PWM allocation system required
- Potential DMA conflicts would need runtime detection
- Breaking change to configurator UI and CLI
- Backward compatibility concerns with saved configurations

---

## Recommendations

### Recommendation 1: Split into 3 Target Directories

**Effort:** 4-6 hours

**Benefits:**
- Reduces conditional compilation from 290 lines to ~50-80 lines per directory
- Each group is more maintainable and understandable
- Clear separation of hardware variants
- Easier to add new variants within each group

**Implementation:**
1. Create `src/main/target/DYSF4/` (2 targets)
2. Keep `src/main/target/OMNIBUSF4/` (1 target - base variant)
3. Create `src/main/target/OMNIBUSF4PRO/` (6 targets - PRO/V3 family)

**Backward compatibility:**
- All target names preserved
- Board IDs unchanged
- No impact on users

**File structure:**
```
target/DYSF4/
  ├── CMakeLists.txt         (2 targets)
  ├── target.h               (~100 lines, minimal conditionals)
  └── target.c               (~40 lines)

target/OMNIBUSF4/
  ├── CMakeLists.txt         (1 target)
  ├── target.h               (~150 lines, no conditionals)
  └── target.c               (~30 lines)

target/OMNIBUSF4PRO/
  ├── CMakeLists.txt         (6 targets)
  ├── target.h               (~180 lines, V3 vs PRO conditionals)
  └── target.c               (~60 lines, softserial conditionals)
```

---

### Recommendation 2: DO NOT Pursue Runtime Softserial Configuration

**Effort:** 20-40 hours (major refactoring)

**Reasons NOT to implement:**
1. **High complexity** - Requires refactoring core timer/PWM allocation system
2. **Breaking change** - Affects configurator, CLI, and saved configurations
3. **Limited benefit** - Only affects 4 of 282 targets
4. **Alternative exists** - Users can build custom firmware if needed
5. **Risk** - High chance of introducing bugs in motor/timer allocation

**Better alternative:**
- Keep softserial variants as separate builds
- They only differ by 3-5 lines in `target.c` (timer definitions)
- Very low maintenance burden after directory split
- No risk to core system

---

### Recommendation 3: After Split, Document Softserial Variants

**Effort:** 1 hour

**Create documentation explaining:**
- Which motor outputs are sacrificed for softserial
- Use cases for each variant (e.g., GPS on S6 for fixed-wing)
- How to choose the right variant
- Add to target README.md or wiki

---

## Effort Estimates Summary

| Task | Effort | Priority | Risk |
|------|--------|----------|------|
| Split into 3 directories | 4-6 hours | High | Low |
| Update build system (CMake) | 1 hour | High | Low |
| Test all 9 targets build | 1 hour | High | Low |
| Documentation | 1 hour | Medium | Low |
| Runtime softserial | 20-40 hours | **NOT RECOMMENDED** | High |

**Total recommended effort:** 7-9 hours

---

## Files Analyzed

- `src/main/target/OMNIBUSF4/CMakeLists.txt` (12 lines)
- `src/main/target/OMNIBUSF4/target.h` (281 lines)
- `src/main/target/OMNIBUSF4/target.c` (68 lines)
- `src/main/drivers/pwm_mapping.c` (softserial allocation logic)
- `src/main/drivers/timer.h` (TIM_USE flags)

---

## Next Steps (If Approved)

1. Create new directory structure
2. Copy and split target files
3. Update CMakeLists.txt in each directory
4. Remove cross-directory conditionals
5. Build all 9 targets to verify
6. Create PR with clear explanation

---

**Developer**
