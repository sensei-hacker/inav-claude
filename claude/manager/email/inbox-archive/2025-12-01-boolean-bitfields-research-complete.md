# Boolean Struct Bitfields Research - Complete

**Date:** 2025-12-01
**From:** Developer
**To:** Manager
**Task:** investigate-boolean-struct-bitfields
**Status:** RESEARCH COMPLETE

---

## Executive Summary

Investigated whether INAV config structs with boolean members could benefit from bitfield optimization (`:1` syntax).

**Key Finding:** Converting boolean fields to bitfields **WILL BREAK EEPROM compatibility** and provides **minimal memory savings** (0-2 bytes per struct).

**Recommendation:** **DO NOT PROCEED** with bitfield conversion due to high migration cost and negligible benefit.

---

## 1. Boolean-Heavy Structs Found

### Config Structs (Stored in EEPROM)

| Struct | File | Bool Fields | Current Type |
|--------|------|-------------|--------------|
| **beeperConfig_t** | `fc/config.h:87-93` | 2 | `bool` (1 byte each) |
| **mixerConfig_t** | `flight/mixer_profile.h:12-25` | 5 | `bool` (1 byte each) |
| **controlConfig_t** | `fc/control_profile_config_struct.h:26-64` | 1 | `bool` (1 byte) |
| **navFwAutolandApproach_t** | `navigation/navigation.h:91-98` | 1 | `bool` (1 byte) |
| **geoZoneConfig_t** | `navigation/navigation.h:156-165` | 1 | `bool` (1 byte) |
| **geozone_config_t** | `navigation/navigation.h:167-176` | 1 | `bool` (1 byte) |
| **gpsOrigin_t** | `navigation/navigation.h:511-517` | 1 | `bool` (1 byte) |
| **pidProfile_t** | `flight/pid.h:99-165` | 1 | `bool` (1 byte) |
| **navSafeHome_t** | `navigation/navigation.h:49-53` | 1 | `uint8_t enabled` (boolean usage) |
| **positionEstimationConfig_t** | `navigation/navigation.h:349-385` | 2 | `uint8_t` (boolean usage) |
| **navConfig_t.general.flags** | `navigation/navigation.h:391-411` | 11 | `uint8_t` (boolean usage) |
| **navConfig_t.mc** | `navigation/navigation.h:446-467` | 1 | `bool` |
| **navConfig_t.fw** | `navigation/navigation.h:469-506` | 3 | `bool` |

### Runtime State Structs (Not Stored in EEPROM)

| Struct | File | Bool Fields | Current Type |
|--------|------|-------------|--------------|
| **failsafeState_t** | `flight/failsafe.h:140-162` | 4 | `bool` (1 byte each) |
| **geozone_t** | `navigation/navigation.h:190-208` | 6 | `bool` (1 byte each) |
| **mixerProfileAT_t** | `flight/mixer_profile.h:48-54` | 1 | `bool` (1 byte) |

---

## 2. Current Field Definitions

**All boolean fields currently use FULL TYPE declarations:**

- `bool fieldName;` → 1 byte (most common)
- `uint8_t fieldName;` → 1 byte (used as boolean in code)

**NO structs currently use bitfield syntax** (`:1`)

### Example: beeperConfig_t (fc/config.h:87-93)

```c
typedef struct beeperConfig_s {
    uint32_t beeper_off_flags;
    uint32_t preferred_beeper_off_flags;
    bool dshot_beeper_enabled;  // 1 byte, used as if (config.dshot_beeper_enabled)
    uint8_t dshot_beeper_tone;
    bool pwmMode;               // 1 byte, used as if (config.pwmMode)
} beeperConfig_t;
```

**Size:** 12 bytes (includes padding)

### Example: mixerConfig_t (mixer_profile.h:12-25)

```c
typedef struct mixerConfig_s {
    int8_t motorDirectionInverted;
    uint8_t platformType;
    bool hasFlaps;                        // 1 byte
    int16_t appliedMixerPreset;
    bool motorstopOnLow;                  // 1 byte
    bool controlProfileLinking;           // 1 byte
    bool automated_switch;                // 1 byte
    int16_t switchTransitionTimer;
    bool tailsitterOrientationOffset;     // 1 byte
    int16_t transition_PID_mmix_multiplier_roll;
    int16_t transition_PID_mmix_multiplier_pitch;
    int16_t transition_PID_mmix_multiplier_yaw;
} mixerConfig_t;
```

**Size:** 20 bytes

### Example: failsafeState_t (failsafe.h:140-162)

```c
typedef struct failsafeState_s {
    int16_t events;
    bool monitoring;      // 1 byte
    bool suspended;       // 1 byte
    bool active;          // 1 byte
    bool controlling;     // 1 byte
    timeMs_t rxDataFailurePeriod;
    // ... (additional fields)
} failsafeState_t;
```

**Size:** ~70 bytes (full struct with all fields)

---

## 3. EEPROM Storage Mechanism

### How Config is Stored

INAV uses a **Parameter Group (PG) system** for config persistence:

**File:** `src/main/config/parameter_group.c`

**Key Functions:**

```c
int pgStore(const pgRegistry_t* reg, void *to, int size, uint8_t profileIndex)
{
    const int take = MIN(size, pgSize(reg));
    memcpy(to, pgOffset(reg, profileIndex), take);  // <-- DIRECT MEMORY COPY
    return take;
}

void pgLoad(const pgRegistry_t* reg, int profileIndex, const void *from, int size, int version)
{
    pgReset(reg, profileIndex);
    if (version == pgVersion(reg)) {
        const int take = MIN(size, pgSize(reg));
        memcpy(pgOffset(reg, profileIndex), from, take);  // <-- DIRECT MEMORY COPY
    }
}
```

### Critical Findings:

1. **Direct memcpy-based serialization** - The exact binary layout of the struct is copied to/from EEPROM
2. **Version checking** - Config is only loaded if version matches: `if (version == pgVersion(reg))`
3. **Size-based** - Uses `sizeof(structType)` to determine how much to copy
4. **No field-by-field encoding** - The entire struct is treated as a binary blob

**Implication:** Any change to struct size or field layout = EEPROM format change

---

## 4. Binary Format Compatibility Impact

### Would Bitfields Change Binary Format?

**YES. Absolutely.**

### Size Impact Analysis

Created test program (`bitfield_analysis.c`) to measure actual size differences:

**Results:**

| Struct | Current Size | Bitfield Size | Savings | Impact |
|--------|--------------|---------------|---------|--------|
| beeperConfig_t | 12 bytes | 12 bytes | **0 bytes** | No change (padding) |
| failsafeState_t (partial) | 6 bytes | 4 bytes | 2 bytes | Size changed |
| mixerConfig_t | 20 bytes | 18 bytes | 2 bytes | Size changed |

**Key Insight:** Due to struct padding and alignment, bitfields often provide **ZERO savings** when boolean fields are interleaved with other types.

### What Happens If We Change These Structs?

**Scenario:** Convert `bool field` → `uint8_t field:1`

1. **Struct size changes** (in most cases, 0-2 bytes)
2. **Byte offsets of fields change** (bitfields pack differently)
3. **Binary EEPROM format becomes incompatible**

**When user updates firmware:**

```c
void pgLoad(const pgRegistry_t* reg, int profileIndex, const void *from, int size, int version)
{
    pgReset(reg, profileIndex);
    if (version == pgVersion(reg)) {  // <-- THIS WILL FAIL
        // ... load saved settings
    }
    // User gets DEFAULT settings instead
}
```

**Result:**
- Old EEPROM data rejected due to version mismatch
- All user settings **LOST**
- Flight controller reverts to defaults
- User must **reconfigure everything**

---

## 5. Migration Path (If We Proceeded)

If we wanted to make this change despite the compatibility issues:

### Required Steps:

1. **Change struct definitions** to use bitfields
2. **Bump PG version numbers** in all `PG_REGISTER()` calls for affected structs
3. **Document breaking change** in release notes
4. **Add CLI backup/restore commands** (maybe) to help users migrate
5. **Test extensively** on real hardware with existing EEPROMs

### Example:

**Current:**
```c
PG_REGISTER_WITH_RESET_TEMPLATE(beeperConfig_t, beeperConfig, PGN_BEEPER_CONFIG, 1);
                                                                                 ^
                                                                             version 1
```

**After bitfield change:**
```c
PG_REGISTER_WITH_RESET_TEMPLATE(beeperConfig_t, beeperConfig, PGN_BEEPER_CONFIG, 2);
                                                                                 ^
                                                                             version 2
```

### User Impact:

- **Major:** All users lose settings on firmware update
- **High effort:** Reconfiguration of all PIDs, rates, navigation settings, etc.
- **Risk:** Incorrect defaults could cause crashes
- **Support burden:** Increased support requests

---

## 6. Memory Savings Analysis

### Best-Case Scenario

If ALL identified boolean fields were converted to bitfields:

**Config structs (stored in EEPROM):**
- ~13 config structs with 1-11 boolean fields each
- Estimated savings: **10-30 bytes total** (accounting for padding)
- EEPROM total capacity: ~4-16 KB (depends on target)
- **Savings: < 1% of EEPROM**

**Runtime structs (RAM only):**
- ~3 runtime state structs with 1-6 boolean fields each
- Estimated savings: **5-10 bytes total**
- Total RAM: 64-512 KB (depends on target)
- **Savings: < 0.01% of RAM**

### Worst-Case Scenario

Due to struct padding and alignment:
- Actual savings could be **ZERO bytes** if fields are already aligned
- Example: `beeperConfig_t` showed 0 bytes savings in testing

---

## 7. Recommendation

### **DO NOT PROCEED with bitfield conversion**

**Reasons:**

1. **Negligible benefit:**
   - Memory savings: 0-30 bytes (< 1% of EEPROM)
   - No performance improvement
   - Code readability reduced (`bool:1` vs `bool`)

2. **High cost:**
   - **BREAKS EEPROM compatibility** for all users
   - Requires version bumps for every affected struct
   - Users lose all configured settings
   - Extensive testing required
   - High support burden

3. **Risk:**
   - Potential for bugs during migration
   - User confusion during upgrade
   - Possible flight crashes if defaults incorrect

### Cost-Benefit Analysis:

| Aspect | Benefit | Cost |
|--------|---------|------|
| Memory saved | 10-30 bytes | N/A |
| User impact | None | ALL users lose settings |
| Development time | N/A | 5-10 hours |
| Testing time | N/A | 10-20 hours |
| Support burden | N/A | High (ongoing) |
| Risk | N/A | Medium (crashes possible) |

**Verdict:** Cost far exceeds benefit.

---

## 8. Alternative Recommendations

If memory optimization is a priority, consider these alternatives:

### A. Optimize Large Arrays/Buffers

Look for opportunities in:
- Waypoint storage
- Blackbox buffers
- Telemetry buffers
- Large config arrays (mixer tables, servo tables)

**Potential savings:** 100s-1000s of bytes

### B. Remove Unused Features

Identify and remove dead code:
- Unused flight modes
- Deprecated protocols
- Optional features not used by most users

**Potential savings:** 1-10 KB code space

### C. Compress Settings for Transmission

If EEPROM space is constrained:
- Implement settings compression for MSP protocol
- Don't change memory layout in RAM

**Benefit:** Backward compatible

---

## 9. Technical Details

### Files Analyzed:

**Config headers:**
- `src/main/fc/config.h`
- `src/main/fc/control_profile_config_struct.h`
- `src/main/navigation/navigation.h`
- `src/main/flight/failsafe.h`
- `src/main/flight/pid.h`
- `src/main/flight/mixer_profile.h`
- `src/main/sensors/battery_config_structs.h`
- `src/main/flight/imu.h`

**Storage mechanism:**
- `src/main/config/parameter_group.h`
- `src/main/config/parameter_group.c`
- `src/main/config/config_streamer.c`

### Test Code:

Created `bitfield_analysis.c` to measure actual struct sizes with different field definitions.

**Test results confirm:**
- Bitfields can change struct size
- Padding often negates savings
- Binary layout changes are guaranteed

---

## 10. Success Criteria Met

- [x] All structs with boolean-only members identified (13 config, 3 runtime)
- [x] Current field sizes documented (all use full `bool` or `uint8_t`, none use `:1`)
- [x] EEPROM storage mechanism understood (direct `memcpy` of struct binary data)
- [x] Binary format compatibility impact clearly explained (BREAKS compatibility)
- [x] Recommendation provided: **DO NOT PROCEED** (unsafe, minimal benefit)
- [x] **NO code changes made** ✓
- [x] **NO branches created** ✓

---

## Conclusion

Boolean bitfields in INAV config structs would:
- Save 0-30 bytes (< 1% of EEPROM)
- Break EEPROM compatibility for all users
- Require extensive migration work
- Provide no functional or performance benefits

**Recommendation: DO NOT IMPLEMENT**

If memory optimization is genuinely needed, focus on larger opportunities (buffers, arrays, unused features) that can provide 100x better returns with less user impact.

---

**Developer**
2025-12-01
