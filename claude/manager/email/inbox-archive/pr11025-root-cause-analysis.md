# Root Cause Analysis: PR #11025 CRSF Telemetry Corruption

**Date:** 2025-12-18
**From:** Developer
**Type:** Investigation Report
**Project:** investigate-pr11025-telemetry-corruption

## Executive Summary

PR #11025 was reverted on the same day it was merged because it corrupted the CRSF telemetry stream, causing users to lose "all ESC telemetry sensors as well as alt and vspeed."

**Root Cause:** The implementation scheduled telemetry frames unconditionally but only wrote frame data when sensors were available. This resulted in malformed frames (sync byte + CRC only) being transmitted, corrupting the CRSF protocol stream.

**Impact:** Critical - breaks all telemetry communication when ESC/temperature/pitot sensors are disabled or unavailable.

---

## Timeline

- **November 28, 2025:** PR #11025 merged (added airspeed, RPM, temperature frames)
- **Same day:** Users reported losing all ESC telemetry, altitude, and vspeed sensors
- **Same day:** PR #11139 immediately reverted all changes

---

## Root Cause: Unconditional Scheduling + Conditional Writing

### The Bug Pattern

PR #11025 made two critical mistakes:

1. **Frames scheduled unconditionally** (if feature compiled in)
2. **Frame functions conditionally write data** (only if sensor available)

This mismatch creates malformed CRSF frames.

### Bug #1: RPM Frame (CRITICAL)

**Location:** `src/main/telemetry/crsf.c`

**Scheduling code (line ~574):**
```c
#ifdef USE_ESC_SENSOR
    crsfSchedule[index++] = BV(CRSF_FRAME_RPM_INDEX);  // ❌ UNCONDITIONAL
#endif
```

**Frame generation code:**
```c
static void crsfRpm(sbuf_t *dst)
{
    uint8_t motorCount = getMotorCount();

    if (STATE(ESC_SENSOR_ENABLED) && motorCount > 0) {  // ⚠️ CONDITIONAL
        sbufWriteU8(dst, 1 + (motorCount * 3) + CRSF_FRAME_LENGTH_TYPE_CRC);
        crsfSerialize8(dst, CRSF_FRAMETYPE_RPM);
        // ... write payload ...
    }
    // ❌ NO DATA WRITTEN if ESC_SENSOR_ENABLED is false!
}
```

**Processing code (line ~530):**
```c
#ifdef USE_ESC_SENSOR
    if (currentSchedule & BV(CRSF_FRAME_RPM_INDEX)) {
        crsfInitializeFrame(dst);  // Writes sync byte
        crsfRpm(dst);              // ❌ MAY WRITE NOTHING!
        crsfFinalize(dst);         // Writes CRC, sends frame
    }
#endif
```

**What happens when ESC sensors are DISABLED:**

1. `crsfInitializeFrame(dst)` - writes `CRSF_TELEMETRY_SYNC_BYTE` (0xC8)
2. `crsfRpm(dst)` - **WRITES NOTHING** (condition fails)
3. `crsfFinalize(dst)` - writes CRC byte and **sends malformed frame**

**Result:** Frame contains only sync byte + CRC = **PROTOCOL CORRUPTION**

### Bug #2: Temperature Frame (CRITICAL)

**Location:** `src/main/telemetry/crsf.c`

**Scheduling code (line ~576):**
```c
#if defined(USE_ESC_SENSOR) || defined(USE_TEMPERATURE_SENSOR)
    crsfSchedule[index++] = BV(CRSF_FRAME_TEMP_INDEX);  // ❌ UNCONDITIONAL
#endif
```

**Frame generation code:**
```c
static void crsfTemperature(sbuf_t *dst)
{
    uint8_t tempCount = 0;
    int16_t temperatures[20];

    #ifdef USE_ESC_SENSOR
    // ... collect ESC temps ...
    #endif

    #ifdef USE_TEMPERATURE_SENSOR
    // ... collect sensor temps ...
    #endif

    if (tempCount > 0) {  // ⚠️ CONDITIONAL - only writes if temps found
        sbufWriteU8(dst, 1 + (tempCount * 2) + CRSF_FRAME_LENGTH_TYPE_CRC);
        crsfSerialize8(dst, CRSF_FRAMETYPE_TEMP);
        // ... write payload ...
    }
    // ❌ NO DATA WRITTEN if tempCount == 0!
}
```

**Same failure mode:** Empty frame sent when no temperature sensors available.

### Bug #3: Airspeed Frame (MEDIUM)

**Location:** `src/main/telemetry/crsf.c`

**Scheduling code (line ~581):**
```c
#ifdef USE_PITOT
    if (sensors(SENSOR_PITOT)) {  // ✅ CONDITIONAL - only if sensor detected
        crsfSchedule[index++] = BV(CRSF_FRAME_AIRSPEED_INDEX);
    }
#endif
```

**Frame generation code:**
```c
static void crsfFrameAirSpeedSensor(sbuf_t *dst)
{
    // use sbufWrite since CRC does not include frame length
    sbufWriteU8(dst, CRSF_FRAME_AIRSPEED_PAYLOAD_SIZE + CRSF_FRAME_LENGTH_TYPE_CRC);
    crsfSerialize8(dst, CRSF_FRAMETYPE_AIRSPEED_SENSOR);
    crsfSerialize16(dst, (uint16_t)(getAirspeedEstimate() * 36 / 100));  // ⚠️ No health check
}
```

**Issue:** Airspeed scheduling is better (checks `sensors(SENSOR_PITOT)`), but the frame function doesn't validate that the pitot sensor is **healthy**. It will send potentially invalid airspeed values.

---

## Why This Corrupts the CRSF Protocol Stream

### CRSF Protocol Structure

CRSF frames have this structure:
```
[SYNC] [LENGTH] [TYPE] [PAYLOAD...] [CRC]
```

### Malformed Frames Sent by PR #11025

When sensors disabled/unavailable:
```
[SYNC] [CRC]  ❌ INVALID - missing LENGTH, TYPE, PAYLOAD
```

### Impact on Receiver

1. Receiver expects `[SYNC] [LENGTH] [TYPE] [PAYLOAD...] [CRC]`
2. Receives `[SYNC] [CRC]` instead
3. CRC byte interpreted as LENGTH field
4. Receiver reads garbage data looking for rest of frame
5. **Protocol desynchronization occurs**
6. Subsequent valid frames cannot be parsed
7. **All telemetry stops working** (not just RPM/temp/airspeed)

This explains user reports: "lost all ESC telemetry sensors as well as alt and vspeed"

---

## Correct Pattern (How GPS Frames Work)

### GPS Frame Implementation (REFERENCE)

**Scheduling code (line ~572):**
```c
#ifdef USE_GPS
    if (feature(FEATURE_GPS)) {  // ✅ CONDITIONAL - only if GPS enabled
        crsfSchedule[index++] = BV(CRSF_FRAME_GPS_INDEX);
    }
#endif
```

**Frame generation code:**
```c
static void crsfFrameGps(sbuf_t *dst)
{
    // ✅ ALWAYS writes data - no conditional skips
    sbufWriteU8(dst, CRSF_FRAME_GPS_PAYLOAD_SIZE + CRSF_FRAME_LENGTH_TYPE_CRC);
    crsfSerialize8(dst, CRSF_FRAMETYPE_GPS);
    crsfSerialize32(dst, gpsSol.llh.lat);
    crsfSerialize32(dst, gpsSol.llh.lon);
    // ... always writes complete frame ...
}
```

**Key principle:**
- ✅ **Conditional scheduling** - only schedule if sensor available
- ✅ **Unconditional writing** - always write complete frame data

---

## Additional Issues Identified by Code Reviewer

The automated code reviewer on PR #11025 flagged three issues:

### 1. Invalid Frame Emission (PRIMARY BUG)
> "CRSF frames for RPM and Temperature are finalized even when no payload is written (e.g., ESC sensor disabled or no temps collected). This can emit empty/invalid frames."

**Status:** ✅ CONFIRMED - This is the root cause of the revert.

### 2. Buffer Overflow Risk
> "Accumulates temperatures into fixed 20-element array without bounding checks, risking buffer overrun and oversized payloads if more than 20 values available."

**Code location:**
```c
int16_t temperatures[20];
// ...
if (STATE(ESC_SENSOR_ENABLED) && motorCount > 0) {
    for (uint8_t i = 0; i < motorCount; i++) {  // ⚠️ No check: motorCount < 20
        const escSensorData_t *escState = getEscTelemetry(i);
        temperatures[tempCount++] = ...;  // ❌ Could overflow if motorCount > 20
    }
}
```

**Status:** ⚠️ VALID CONCERN - No bounds checking before array access.

### 3. Protocol Violations
> "Writes motorCount 24-bit values without enforcing protocol's stated limit (1–19 values)."

**Code location:**
```c
for (uint8_t i = 0; i < motorCount; i++) {
    const escSensorData_t *escState = getEscTelemetry(i);
    crsfSerialize24(dst, (escState) ? escState->rpm : 0);  // ⚠️ No limit check
}
```

**Status:** ⚠️ VALID CONCERN - Protocol specifies 1-19 values, code doesn't enforce.

---

## Recommended Fix Strategy

### Fix #1: RPM Frame (REQUIRED)

**Option A: Conditional Scheduling (RECOMMENDED)**
```c
// In initCrsfTelemetry():
#ifdef USE_ESC_SENSOR
    if (STATE(ESC_SENSOR_ENABLED) && getMotorCount() > 0) {
        crsfSchedule[index++] = BV(CRSF_FRAME_RPM_INDEX);
    }
#endif
```

**Option B: Always Write Data**
```c
static void crsfRpm(sbuf_t *dst)
{
    uint8_t motorCount = getMotorCount();

    // ✅ Always write frame, even if no motors
    sbufWriteU8(dst, 1 + (motorCount * 3) + CRSF_FRAME_LENGTH_TYPE_CRC);
    crsfSerialize8(dst, CRSF_FRAMETYPE_RPM);
    crsfSerialize8(dst, 0);  // source_id = 0 (FC)

    for (uint8_t i = 0; i < motorCount; i++) {
        const escSensorData_t *escState = getEscTelemetry(i);
        crsfSerialize24(dst, (escState) ? escState->rpm : 0);
    }
}
```

**Recommendation:** Use **Option A** (conditional scheduling) - it's more efficient and follows the GPS pattern.

### Fix #2: Temperature Frame (REQUIRED)

**Conditional Scheduling:**
```c
// In initCrsfTelemetry():
#if defined(USE_ESC_SENSOR) || defined(USE_TEMPERATURE_SENSOR)
    bool hasTemperatureSensors = false;

    #ifdef USE_ESC_SENSOR
    if (STATE(ESC_SENSOR_ENABLED) && getMotorCount() > 0) {
        hasTemperatureSensors = true;
    }
    #endif

    #ifdef USE_TEMPERATURE_SENSOR
    for (uint8_t i = 0; i < MAX_TEMP_SENSORS; i++) {
        int16_t value;
        if (getSensorTemperature(i, &value)) {
            hasTemperatureSensors = true;
            break;
        }
    }
    #endif

    if (hasTemperatureSensors) {
        crsfSchedule[index++] = BV(CRSF_FRAME_TEMP_INDEX);
    }
#endif
```

**Alternative:** Keep the conditional check in `crsfTemperature()` but add an early return in the processing code if no data written.

### Fix #3: Airspeed Frame (RECOMMENDED)

**Add Health Check:**
```c
static void crsfFrameAirSpeedSensor(sbuf_t *dst)
{
    // ✅ Add health check (if available in codebase)
    // if (!pitotIsHealthy()) return;  // Don't send if sensor unhealthy

    sbufWriteU8(dst, CRSF_FRAME_AIRSPEED_PAYLOAD_SIZE + CRSF_FRAME_LENGTH_TYPE_CRC);
    crsfSerialize8(dst, CRSF_FRAMETYPE_AIRSPEED_SENSOR);
    crsfSerialize16(dst, (uint16_t)(getAirspeedEstimate() * 36 / 100));
}
```

**Note:** This is already better than RPM/temp because scheduling is conditional.

### Fix #4: Buffer Overflow Protection (REQUIRED)

```c
static void crsfTemperature(sbuf_t *dst)
{
    uint8_t tempCount = 0;
    int16_t temperatures[20];
    const uint8_t MAX_TEMPS = 20;  // ✅ Define constant

    #ifdef USE_ESC_SENSOR
    uint8_t motorCount = getMotorCount();
    if (STATE(ESC_SENSOR_ENABLED) && motorCount > 0) {
        for (uint8_t i = 0; i < motorCount && tempCount < MAX_TEMPS; i++) {  // ✅ Bounds check
            const escSensorData_t *escState = getEscTelemetry(i);
            temperatures[tempCount++] = (escState) ? escState->temperature * 10 : TEMPERATURE_INVALID_VALUE;
        }
    }
    #endif

    #ifdef USE_TEMPERATURE_SENSOR
    for (uint8_t i = 0; i < MAX_TEMP_SENSORS && tempCount < MAX_TEMPS; i++) {  // ✅ Bounds check
        int16_t value;
        if (getSensorTemperature(i, &value))
            temperatures[tempCount++] = value;
    }
    #endif

    if (tempCount > 0) {
        sbufWriteU8(dst, 1 + (tempCount * 2) + CRSF_FRAME_LENGTH_TYPE_CRC);
        crsfSerialize8(dst, CRSF_FRAMETYPE_TEMP);
        crsfSerialize8(dst, 0);
        for (uint8_t i = 0; i < tempCount; i++)
            crsfSerialize16(dst, temperatures[i]);
    }
}
```

### Fix #5: Protocol Limit Enforcement (RECOMMENDED)

```c
static void crsfRpm(sbuf_t *dst)
{
    uint8_t motorCount = getMotorCount();
    const uint8_t MAX_RPM_VALUES = 19;  // ✅ Protocol limit

    if (motorCount > MAX_RPM_VALUES) {
        motorCount = MAX_RPM_VALUES;  // ✅ Clamp to protocol limit
    }

    if (STATE(ESC_SENSOR_ENABLED) && motorCount > 0) {
        sbufWriteU8(dst, 1 + (motorCount * 3) + CRSF_FRAME_LENGTH_TYPE_CRC);
        crsfSerialize8(dst, CRSF_FRAMETYPE_RPM);
        crsfSerialize8(dst, 0);

        for (uint8_t i = 0; i < motorCount; i++) {
            const escSensorData_t *escState = getEscTelemetry(i);
            crsfSerialize24(dst, (escState) ? escState->rpm : 0);
        }
    }
}
```

---

## Testing Strategy

### Test Case 1: ESC Sensors Disabled
**Setup:** Build firmware with `USE_ESC_SENSOR` enabled, but disable ESC sensors in configuration
**Expected:** No RPM frames sent, other telemetry (GPS, Battery, Attitude) continues working
**Validates:** Fix for Bug #1

### Test Case 2: No Temperature Sensors
**Setup:** Build firmware with temperature support, but no temperature sensors configured
**Expected:** No temperature frames sent, other telemetry continues working
**Validates:** Fix for Bug #2

### Test Case 3: Pitot Sensor Unhealthy
**Setup:** Pitot sensor detected but reporting unhealthy/invalid data
**Expected:** No airspeed frames sent, or frames sent with valid fallback data
**Validates:** Fix for Bug #3

### Test Case 4: >20 Temperature Sensors
**Setup:** Configure more than 20 temperature sources (ESCs + temp sensors)
**Expected:** Only first 20 temperatures sent, no buffer overflow
**Validates:** Fix for Buffer Overflow

### Test Case 5: >19 Motors
**Setup:** Configure more than 19 motors (unlikely but possible in theory)
**Expected:** Only first 19 RPM values sent
**Validates:** Protocol Limit Enforcement

### Test Case 6: Mixed Telemetry
**Setup:** Enable GPS, Battery, Attitude, plus new frames (RPM, Temp, Airspeed)
**Expected:** All frames sent correctly, no corruption
**Validates:** Overall integration

---

## Code References

**Key files:**
- `src/main/telemetry/crsf.c:419-448` - crsfRpm() and crsfTemperature() functions (reverted)
- `src/main/telemetry/crsf.c:528-565` - Frame processing loop
- `src/main/telemetry/crsf.c:566-589` - Frame scheduling in initCrsfTelemetry()
- `src/main/rx/crsf.h` - Frame type definitions (reverted)

**Working reference implementations:**
- `src/main/telemetry/crsf.c:219-231` - crsfFrameGps() (correct pattern)
- `src/main/telemetry/crsf.c:248-258` - crsfFrameBatterySensor() (correct pattern)
- `src/main/telemetry/crsf.c:341-348` - crsfFrameAttitude() (correct pattern)

---

## Summary

**Root Cause:** Mismatch between unconditional frame scheduling and conditional frame data writing.

**Impact:** Malformed frames (sync + CRC only) corrupted CRSF protocol stream, breaking all telemetry.

**Fix Priority:**
1. **CRITICAL:** Add conditional scheduling for RPM and Temperature frames
2. **CRITICAL:** Add buffer overflow protection for temperature array
3. **HIGH:** Add protocol limit enforcement (19 RPM values max)
4. **MEDIUM:** Add pitot health check for airspeed frames

**Implementation Pattern:** Follow GPS frame pattern:
- Schedule frames conditionally (only if sensor available)
- Write frame data unconditionally (always complete frames)

**Estimated Re-implementation Effort:** 2-3 hours (with proper testing)

---

**Developer**
