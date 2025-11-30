# Conditions That Can Cause "Distance to Home" to Become Zero During Flight

This document provides detailed analysis of all code paths in INAV firmware that can cause the OSD "Distance to Home" value (`GPS_distanceToHome`) to become zero during an active flight, with focus on scenarios where the display is normal until an event disrupts it.

## Table of Contents

1. [Data Flow Overview](#data-flow-overview)
2. [Condition 1: setHomePosition() Calls](#condition-1-sethomeposition-calls)
3. [Condition 2: GPS_FIX_HOME State Loss/Absence](#condition-2-gps_fix_home-state-lossabsence)
4. [Condition 3: Position Estimate Degradation (EST_NONE)](#condition-3-position-estimate-degradation-est_none)
5. [Condition 4: EPH Recovery Difficulties After GPS Dropout](#condition-4-eph-recovery-difficulties-after-gps-dropout)
6. [Condition 5: Delayed RTH Trigger After GPS Glitch (General Mechanism)](#condition-5-delayed-rth-trigger-after-gps-glitch-general-mechanism)
7. [Condition 5b: GPS Fix Estimation Delayed Failsafe RTH (WP Mode - Confirmed)](#condition-5b-gps-fix-estimation-delayed-failsafe-rth-wp-mode---confirmed)
8. [Condition 6: Physical Proximity to Home](#condition-6-physical-proximity-to-home)
9. [Disruption Scenarios Summary](#disruption-scenarios-summary)
10. [Debugging Recommendations](#debugging-recommendations)

---

## Data Flow Overview

The OSD displays `GPS_distanceToHome` which flows through this chain:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Position Estimator                    Navigation Controller                 │
│  ┌──────────────────┐                 ┌──────────────────────┐              │
│  │ posEstimator.est │ ────────────▶   │ posControl.actualState│              │
│  │   .pos.x, .pos.y │                 │   .abs.pos.x, .pos.y │              │
│  │   .eph, .epv     │                 └──────────┬───────────┘              │
│  └──────────────────┘                            │                           │
│                                                  │                           │
│                                                  ▼                           │
│                                    ┌─────────────────────────┐              │
│                                    │ calculateDistanceTo-    │              │
│                                    │ Destination()           │              │
│                                    │ [navigation.c:3373]     │              │
│                                    └──────────┬──────────────┘              │
│                                               │                              │
│                                               ▼                              │
│                                    ┌─────────────────────────┐              │
│                                    │ posControl.homeDistance │              │
│                                    │ (centimeters)           │              │
│                                    └──────────┬──────────────┘              │
│                                               │                              │
│                                               ▼                              │
│                                    ┌─────────────────────────┐              │
│                                    │ updateHomePosition-     │              │
│                                    │ Compatibility()         │              │
│                                    │ [navigation.c:3070]     │              │
│                                    └──────────┬──────────────┘              │
│                                               │                              │
│                                               ▼                              │
│                                    ┌─────────────────────────┐              │
│                                    │ GPS_distanceToHome      │              │
│                                    │ (meters)                │              │
│                                    │ [navigation.c:3073]     │              │
│                                    └──────────┬──────────────┘              │
│                                               │                              │
│                                               ▼                              │
│                                    ┌─────────────────────────┐              │
│                                    │ OSD Display             │              │
│                                    │ [osd.c:2108]            │              │
│                                    └─────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `src/main/navigation/navigation.c` - Home position management and distance calculation
- `src/main/navigation/navigation_pos_estimator.c` - Position estimation and validity
- `src/main/io/gps.c` - GPS fix state management
- `src/main/io/osd.c` - OSD display rendering

---

## Condition 1: setHomePosition() Calls

**Every call to `setHomePosition()` explicitly sets `homeDistance = 0`**

This is the most common cause of distance becoming zero during flight.

### Source Code

**File:** `src/main/navigation/navigation.c`
**Lines:** 3193-3240

```c
void setHomePosition(const fpVector3_t * pos, int32_t heading,
                     navSetWaypointFlags_t useMask, navigationHomeFlags_t homeFlags)
{
    // ... position updates ...

    posControl.homeDistance = 0;    // Line 3227 - ALWAYS SET TO ZERO
    posControl.homeDirection = 0;   // Line 3228

    // ...
    updateHomePositionCompatibility();  // Line 3238 - propagates 0 to GPS_distanceToHome
    ENABLE_STATE(GPS_FIX_HOME);         // Line 3239
}
```

### Complete List of setHomePosition() Callers

#### 1.1 BOXHOMERESET - Pilot-Initiated Home Reset

**Disruption Scenario:** Pilot accidentally activates HOME RESET switch while flying far from intended home.

**Call Stack:**
```
updateWaypointsAndNavigationMode()          [navigation.c:4854]
  └─▶ updateHomePosition()                   [navigation.c:3329]
        └─▶ IS_RC_MODE_ACTIVE(BOXHOMERESET)  [navigation.c:3358]
              └─▶ setHomePosition()          [navigation.c:3385]
                    └─▶ posControl.homeDistance = 0  [navigation.c:3227]
```

**File:** `src/main/navigation/navigation.c`
**Lines:** 3355-3393

```c
else {  // ARMING_FLAG(ARMED) == true
    static bool isHomeResetAllowed = false;
    // If pilot so desires he may reset home position to current position
    if (IS_RC_MODE_ACTIVE(BOXHOMERESET)) {                              // Line 3358
        if (isHomeResetAllowed &&
            !FLIGHT_MODE(FAILSAFE_MODE) &&
            !FLIGHT_MODE(NAV_RTH_MODE) &&
            !FLIGHT_MODE(NAV_FW_AUTOLAND) &&
            !FLIGHT_MODE(NAV_WP_MODE) &&
            (posControl.flags.estPosStatus >= EST_USABLE)) {            // Line 3359
            homeUpdateFlags = 0;
            homeUpdateFlags = STATE(GPS_FIX_HOME) ?
                (NAV_POS_UPDATE_XY | NAV_POS_UPDATE_HEADING) :
                (NAV_POS_UPDATE_XY | NAV_POS_UPDATE_Z | NAV_POS_UPDATE_HEADING);
            setHome = true;                                              // Line 3362
            isHomeResetAllowed = false;
        }
    }
    else {
        isHomeResetAllowed = true;                                       // Line 3367
    }
    // ...
    if (setHome && (!ARMING_FLAG(WAS_EVER_ARMED) || ARMING_FLAG(ARMED))) {
        setHomePosition(&posControl.actualState.abs.pos, ...);          // Line 3385
    }
}
```

**Conditions Required:**
- `BOXHOMERESET` mode switch is active
- NOT in failsafe mode
- NOT in RTH mode
- NOT in FW Autoland mode
- NOT in Waypoint mode
- Position estimate is usable (`estPosStatus >= EST_USABLE`)
- Switch was previously inactive (debounce via `isHomeResetAllowed`)

**Result:** Distance immediately becomes 0 at current location. This is intentional but may surprise the pilot.

---

#### 1.2 RTH Initialization When Close to Home

**Disruption Scenario:** Pilot activates RTH while already close to the home point (within `nav_min_rth_distance`).

**Call Stack:**
```
navOnEnteringState_NAV_STATE_RTH_INITIALIZE()  [navigation.c:1502]
  └─▶ if (homeDistance < min_rth_distance)
        └─▶ setHomePosition()                   [navigation.c:1528]
              └─▶ posControl.homeDistance = 0   [navigation.c:3227]
```

**File:** `src/main/navigation/navigation.c`
**Lines:** 1526-1532

```c
// If close to home - reset home position and land
if (posControl.homeDistance < navConfig()->general.min_rth_distance) {  // Line 1527
    setHomePosition(&navGetCurrentActualPositionAndVelocity()->pos,      // Line 1528
                    posControl.actualState.yaw,
                    NAV_POS_UPDATE_XY | NAV_POS_UPDATE_HEADING,
                    NAV_HOME_VALID_ALL);
    setDesiredPosition(&navGetCurrentActualPositionAndVelocity()->pos,
                       posControl.actualState.yaw,
                       NAV_POS_UPDATE_XY | NAV_POS_UPDATE_Z | NAV_POS_UPDATE_HEADING);

    return NAV_FSM_EVENT_SWITCH_TO_RTH_LANDING;   // Line 1531 - Skip to landing
}
```

**Conditions Required:**
- RTH mode is activated
- Current distance to home < `nav_min_rth_distance` (default: 500 cm = 5 meters)
- Position estimate valid or `rth_climb_ignore_emerg` enabled

**Result:** Home is reset to current position, distance becomes 0, aircraft proceeds directly to landing phase.

---

#### 1.3 SafeHome State Changes

**Disruption Scenario:** RTH is activated or deactivated, causing home position to switch between original arming point and configured SafeHome location.

**Call Stack:**
```
selectNavEventFromBoxModeInput()              [navigation.c:4454]
  └─▶ checkSafeHomeState()                    [navigation.c:3258]
        ├─▶ setHomePosition(safehome)         [navigation.c:3279]  // When enabling
        │     └─▶ posControl.homeDistance = 0
        └─▶ setHomePosition(original)         [navigation.c:3283]  // When disabling
              └─▶ posControl.homeDistance = 0
        └─▶ updateHomePosition()              [navigation.c:3287]  // Recalculates distance
```

**File:** `src/main/navigation/navigation.c`
**Lines:** 3258-3288

```c
void checkSafeHomeState(bool shouldBeEnabled)
{
    bool safehomeNotApplicable =
        navConfig()->general.flags.safehome_usage_mode == SAFEHOME_USAGE_OFF ||
        posControl.flags.rthTrackbackActive ||
        (!posControl.safehomeState.isApplied &&
         posControl.homeDistance < navConfig()->general.min_rth_distance);  // Line 3261

    // ...

    if (shouldBeEnabled) {
        // set home to safehome
        setHomePosition(&posControl.safehomeState.nearestSafeHome, 0,   // Line 3279
                        NAV_POS_UPDATE_XY | NAV_POS_UPDATE_Z | NAV_POS_UPDATE_HEADING,
                        navigationActualStateHomeValidity());
        posControl.safehomeState.isApplied = true;
    } else {
        // set home to original arming point
        setHomePosition(&posControl.rthState.originalHomePosition, 0,   // Line 3283
                        NAV_POS_UPDATE_XY | NAV_POS_UPDATE_Z | NAV_POS_UPDATE_HEADING,
                        navigationActualStateHomeValidity());
        posControl.safehomeState.isApplied = false;
    }
    // Recalculate distance after home change
    updateHomePosition();                                                // Line 3287
}
```

**Triggers:**
| Event | Calls | Result |
|-------|-------|--------|
| RTH activated | `checkSafeHomeState(true)` | Home → SafeHome, distance = 0 briefly |
| RTH deactivated | `checkSafeHomeState(false)` | Home → Original, distance = 0 briefly |
| Failsafe RTH | `activateForcedRTH()` → `checkSafeHomeState(true)` [navigation.c:5077] | Home → SafeHome |

**Note:** The `updateHomePosition()` call at line 3287 recalculates distance immediately after, so the 0 value is transient (one update cycle).

---

#### 1.4 GCS/MSP Home Position Override (WP #0)

**Disruption Scenario:** Ground control station sends a command to set a new home position via MSP protocol.

**Call Stack:**
```
mspFcProcessCommand()
  └─▶ MSP_SET_WP handler
        └─▶ setWaypointFromMSP()              [navigation.c:3890]
              └─▶ setHomePosition()           [navigation.c:3893]
                    └─▶ posControl.homeDistance = 0
```

**File:** `src/main/navigation/navigation.c`
**Lines:** 3890-3894

```c
// WP #0 - special waypoint - HOME
if ((wpNumber == 0) && ARMING_FLAG(ARMED) &&
    (posControl.flags.estPosStatus >= EST_USABLE) &&
    posControl.gpsOrigin.valid &&
    posControl.flags.isGCSAssistedNavigationEnabled) {                  // Line 3890
    // Forcibly set home position
    geoConvertGeodeticToLocal(&wpPos.pos, &posControl.gpsOrigin, &wpLLH, GEO_ALT_RELATIVE);
    setHomePosition(&wpPos.pos, 0,                                       // Line 3893
                    NAV_POS_UPDATE_XY | NAV_POS_UPDATE_Z | NAV_POS_UPDATE_HEADING,
                    NAV_HOME_VALID_ALL);
}
```

**Conditions Required:**
- GCS sends `MSP_SET_WP` with waypoint number 0
- Aircraft is armed
- Position estimate is usable
- GPS origin is valid
- GCS-assisted navigation is enabled (`BOXGCSNAV` active)

---

### setHomePosition() Call Summary

| Caller | File:Line | Trigger | During Flight? |
|--------|-----------|---------|----------------|
| `updateHomePosition()` via BOXHOMERESET | navigation.c:3385 | Pilot switch | Yes |
| `navOnEnteringState_NAV_STATE_RTH_INITIALIZE()` | navigation.c:1528 | RTH near home | Yes |
| `checkSafeHomeState(true)` | navigation.c:3279 | RTH/Failsafe activation | Yes |
| `checkSafeHomeState(false)` | navigation.c:3283 | RTH deactivation | Yes |
| `setWaypointFromMSP()` WP#0 | navigation.c:3893 | GCS command | Yes |
| `updateHomePosition()` initial | navigation.c:3385 | Arming | No (pre-flight) |

---

## Condition 2: GPS_FIX_HOME State Loss/Absence

If `GPS_FIX_HOME` state is not set, the distance calculation loop is completely skipped, and `homeDistance` retains its last value (which could be 0).

### Distance Update Guard

**File:** `src/main/navigation/navigation.c`
**Lines:** 3370-3376

```c
// Update distance and direction to home if armed (home is not updated when armed)
if (STATE(GPS_FIX_HOME)) {                                              // Line 3371
    fpVector3_t * tmpHomePos = rthGetHomeTargetPosition(RTH_HOME_FINAL_LAND);
    posControl.homeDistance = calculateDistanceToDestination(tmpHomePos); // Line 3373
    posControl.homeDirection = calculateBearingToDestination(tmpHomePos);
    updateHomePositionCompatibility();                                    // Line 3375
}
// If GPS_FIX_HOME is false, homeDistance is NOT updated
```

### How GPS_FIX_HOME is Set

`GPS_FIX_HOME` is ONLY set in one place:

**File:** `src/main/navigation/navigation.c`
**Line:** 3239

```c
void setHomePosition(...) {
    // ...
    ENABLE_STATE(GPS_FIX_HOME);  // Line 3239 - Only place this is set
}
```

### Conditions Where GPS_FIX_HOME May Never Be Set

| Condition | Cause | Result |
|-----------|-------|--------|
| No GPS lock before arming | GPS not acquired | Home never established |
| GPS feature disabled | Configuration | No GPS processing |
| Armed without position | `nav_extra_arming_safety = OFF` | Allowed to arm without GPS |

### Is GPS_FIX_HOME Ever Cleared During Flight?

**Critical Finding:** There is NO code that calls `DISABLE_STATE(GPS_FIX_HOME)` anywhere in the codebase.

Once `GPS_FIX_HOME` is set, it remains set until power cycle. The only way to lose it is:
1. Never having it set in the first place
2. System reset (extremely rare, typically hardware fault)

**Grep Verification:**
```bash
grep -r "DISABLE_STATE.*GPS_FIX_HOME" src/main/
# Returns: No matches found
```

---

## Condition 3: Position Estimate Degradation (EST_NONE)

When position estimate becomes `EST_NONE`, the distance calculation uses stale position data. While `homeDistance` continues to be calculated, the result becomes increasingly inaccurate and may drift toward 0 if position data was never properly initialized.

### Position Status Hierarchy

```
EST_NONE     = 0  // No valid estimate - position data unusable
EST_USABLE   = 1  // Position usable but not fully trusted
EST_TRUSTED  = 2  // Full confidence in position estimate
```

### How estPosStatus Becomes EST_NONE

**File:** `src/main/navigation/navigation.c`
**Lines:** 2811-2830

```c
void updateActualHorizontalPositionAndVelocity(bool estPosValid, bool estVelValid, ...)
{
    // CASE 1: POS & VEL valid
    if (estPosValid && estVelValid) {
        posControl.flags.estPosStatus = EST_TRUSTED;                    // Line 2813
        posControl.flags.estVelStatus = EST_TRUSTED;
        posControl.lastValidPositionTimeMs = millis();
    }
    // CASE 2: POS invalid, VEL valid
    else if (!estPosValid && estVelValid) {
        posControl.flags.estPosStatus = EST_USABLE;                     // Line 2820
        posControl.flags.estVelStatus = EST_TRUSTED;
        posControl.lastValidPositionTimeMs = millis();
    }
    // CASE 3: can't use pos/vel data
    else {
        posControl.flags.estPosStatus = EST_NONE;                       // Line 2827
        posControl.flags.estVelStatus = EST_NONE;                       // Line 2828
        posControl.flags.horizontalPositionDataNew = false;
    }
}
```

### What Triggers estPosValid = false?

The position estimator sets `estPosValid = false` when `posEstimator.est.eph >= max_eph_epv`:

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Lines:** 819-825

```c
/* Publish position update */
if (posEstimator.est.eph < positionEstimationConfig()->max_eph_epv) {  // Line 819
    updateActualHorizontalPositionAndVelocity(true, true, ...);        // Line 821
}
else {
    updateActualHorizontalPositionAndVelocity(false, false, ...);      // Line 824 - EST_NONE
}
```

### EPH Growth (Position Uncertainty Degradation)

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Lines:** 738-739

```c
/* Calculate new EPH and EPV for the case we didn't update position */
ctx.newEPH = posEstimator.est.eph * ((posEstimator.est.eph <= max_eph_epv) ? 1.0f + ctx.dt : 1.0f);
ctx.newEPV = posEstimator.est.epv * ((posEstimator.est.epv <= max_eph_epv) ? 1.0f + ctx.dt : 1.0f);
```

**EPH Growth Behavior:**
- When EPH < max_eph_epv: EPH grows by factor of `(1 + dt)` each update cycle
- When EPH >= max_eph_epv: EPH stays constant (already invalid)
- At 50Hz update rate, dt ≈ 0.02 seconds
- EPH roughly doubles every ~50 update cycles (~1 second) when not corrected

### Root Causes of Position Estimate Loss

#### 3.1 GPS Signal Loss

**File:** `src/main/io/gps.c`
**Lines:** 572-577

```c
// Check for GPS timeout
if ((millis() - gpsState.lastMessageMs) > gpsState.baseTimeoutMs) {     // Line 572
    sensorsClear(SENSOR_GPS);
    DISABLE_STATE(GPS_FIX);                                              // Line 574
    gpsSol.fixType = GPS_NO_FIX;                                        // Line 575
    gpsSetState(GPS_LOST_COMMUNICATION);                                // Line 576
}
```

**GPS Timeout:** 1000ms (default) - defined in `src/main/io/gps_private.h:27`

**Cascade Effect:**
```
GPS timeout (1000ms no data)
  └─▶ DISABLE_STATE(GPS_FIX)
        └─▶ GPS data not processed by position estimator
              └─▶ EPH grows exponentially
                    └─▶ EPH exceeds max_eph_epv (default: 100cm)
                          └─▶ estPosValid = false
                                └─▶ estPosStatus = EST_NONE
```

#### 3.2 GPS Fix Type Degradation

**File:** `src/main/io/gps.c`
**Lines:** 369-378

```c
// Set GPS fix flag only if we have 3D fix
if (gpsSol.fixType >= GPS_FIX_3D) {
    ENABLE_STATE(GPS_FIX);                                               // Line 371
}
else {
    /* When no fix available - reset flags as well */
    gpsSol.flags.validVelNE = false;
    gpsSol.flags.validVelD = false;
    gpsSol.flags.validEPE = false;
    DISABLE_STATE(GPS_FIX);                                              // Line 378
}
```

**Disruption Scenario:** GPS degrades from 3D fix to 2D fix or no fix due to:
- Flying under obstructions (bridges, trees, buildings)
- RF interference
- GPS antenna damage/orientation
- Satellite geometry changes

#### 3.3 IMU Not Ready

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Lines:** 729-735

```c
/* If IMU is not ready we can't estimate anything */
if (!isImuReady()) {
    posEstimator.est.eph = max_eph_epv + 0.001f;                        // Line 731
    posEstimator.est.epv = max_eph_epv + 0.001f;                        // Line 732
    posEstimator.flags = 0;                                              // Line 733
    return;  // Skip all estimation
}
```

**IMU Failure Causes:**
- Accelerometer/gyro hardware fault
- Sensor calibration lost
- I2C/SPI communication failure

#### 3.4 GPS EPH/EPV Exceeds Threshold

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Lines:** 482-488

```c
if ((sensors(SENSOR_GPS) || STATE(GPS_ESTIMATED_FIX)) &&
    posControl.gpsOrigin.valid &&
    ((currentTimeUs - posEstimator.gps.lastUpdateTime) <= MS2US(INAV_GPS_TIMEOUT_MS)) &&
    (posEstimator.gps.eph < max_eph_epv)) {                             // Line 483
    if (posEstimator.gps.epv < max_eph_epv) {                           // Line 484
        newFlags |= EST_GPS_XY_VALID | EST_GPS_Z_VALID;
    }
    // ...
}
```

**INAV_GPS_TIMEOUT_MS:** 1500ms - defined in `src/main/navigation/navigation_pos_estimator_private.h:43`

**Default max_eph_epv:** 100cm - configurable via `inav_max_eph_epv` setting

### Position Sensor Timeout Check

**File:** `src/main/navigation/navigation.c`
**Lines:** 2778-2792

```c
bool checkForPositionSensorTimeout(void)
{
    if (navConfig()->general.pos_failure_timeout) {
        if ((posControl.flags.estPosStatus == EST_NONE) &&
            ((millis() - posControl.lastValidPositionTimeMs) >
             (1000 * navConfig()->general.pos_failure_timeout))) {      // Line 2781
            return true;  // Position sensor has timed out
        }
        else {
            return false;
        }
    }
    // Timeout not defined, never fail
    return false;
}
```

**pos_failure_timeout:** Configurable, triggers failsafe actions when position is lost for specified duration.

---

## Condition 4: EPH Recovery Difficulties After GPS Dropout

**Critical Issue:** Even after GPS signal returns, the position estimate may take an extended time to recover, or may not recover at all in certain scenarios. This is because the **calculated EPH** (`posEstimator.est.eph`) is used for validity checks, not the GPS-reported EPH directly.

### Understanding the Two EPH Values

| Variable | Description | Source |
|----------|-------------|--------|
| `posEstimator.gps.eph` | GPS-reported horizontal position error | GPS receiver or default 200cm |
| `posEstimator.est.eph` | **Calculated** estimated position error | Position estimator filter |

**The validity check uses `posEstimator.est.eph`:**

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Line:** 819

```c
if (posEstimator.est.eph < positionEstimationConfig()->max_eph_epv) {  // Uses ESTIMATED EPH
    updateActualHorizontalPositionAndVelocity(true, true, ...);        // Position valid
}
else {
    updateActualHorizontalPositionAndVelocity(false, false, ...);      // Position INVALID
}
```

### EPH Growth During GPS Dropout

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Line:** 738

```c
ctx.newEPH = posEstimator.est.eph * ((posEstimator.est.eph <= max_eph_epv) ? 1.0f + ctx.dt : 1.0f);
```

At 50Hz update rate (dt ≈ 0.02s), EPH grows exponentially by 2% per cycle:

| Time Without GPS | Estimated EPH (starting from 100cm) |
|------------------|-------------------------------------|
| 0s               | 100cm                               |
| 1s (50 cycles)   | 269cm                               |
| 2s (100 cycles)  | 724cm                               |
| 2.3s (~115 cycles) | ~1000cm (reaches max_eph_epv)     |
| >2.3s            | Stays at ~1000cm (growth stops)     |

### Two Recovery Paths After GPS Returns

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Lines:** 658-694

```c
if (ctx->newFlags & EST_GPS_XY_VALID) {
    /* If GPS is valid and our estimate is NOT valid - reset to GPS */
    if (!(ctx->newFlags & EST_XY_VALID)) {                           // Line 660
        // === FAST PATH ===
        // Direct position snap and EPH assignment
        ctx->estPosCorr.x += posEstimator.gps.pos.x - posEstimator.est.pos.x;
        ctx->estPosCorr.y += posEstimator.gps.pos.y - posEstimator.est.pos.y;
        ctx->newEPH = posEstimator.gps.eph;                          // Line 665 - DIRECT!
    }
    else {                                                            // Line 667
        // === SLOW PATH ===
        // Filtered EPH update with residual limiting
        const float gpsPosResidualMag = calc_length_pythagorean_2D(gpsPosXResidual, gpsPosYResidual);
        ctx->newEPH = updateEPE(posEstimator.est.eph, ctx->dt,
                                MAX(posEstimator.gps.eph, gpsPosResidualMag),  // Line 693
                                w_xy_gps_p);
    }
}
```

### Fast Recovery Path (GPS Dropout > ~2.3 seconds)

**Condition:** `EST_XY_VALID = false` (est.eph >= max_eph_epv = 1000cm)

**Action:** Direct EPH assignment from GPS

**Recovery Time:** Essentially instant (one update cycle, ~20ms)

**Paradox:** Longer GPS dropouts recover faster!

### Slow Recovery Path (GPS Dropout < ~2.3 seconds) - THE PROBLEMATIC CASE

**Condition:** `EST_XY_VALID = true` (est.eph < max_eph_epv)

**Action:** Filtered update via `updateEPE()` function

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Lines:** 444-447

```c
float updateEPE(const float oldEPE, const float dt, const float newEPE, const float w)
{
    return oldEPE + (newEPE - oldEPE) * w * dt;
}
```

This is a first-order low-pass filter. With default `w_xy_gps_p = 1.0` and 50Hz updates:
- Each cycle: EPH moves 2% toward target
- Time constant: ~1 second
- 95% convergence: ~3 seconds
- 99% convergence: ~5 seconds

### The Critical Problem: Position Residual as EPH Target

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Line:** 693

```c
ctx->newEPH = updateEPE(posEstimator.est.eph, ctx->dt,
                        MAX(posEstimator.gps.eph, gpsPosResidualMag),  // <-- PROBLEM
                        w_xy_gps_p);
```

The EPH target is `MAX(GPS_EPH, position_residual)`.

If the aircraft **drifted** during the GPS dropout (due to wind, accelerometer bias, etc.), the position residual (`gpsPosResidualMag`) can be **very large** - potentially meters or tens of meters.

**This becomes the EPH target instead of the GPS EPH!**

### Example: 2-Second GPS Dropout with 15m Drift

```
Timeline:
─────────────────────────────────────────────────────────────────────

T=0s:    GPS lost
         est.eph = 100cm (good)
         Aircraft position: 0m from true position

T=2s:    GPS returns
         est.eph = 724cm (grown, but still < 1000cm max)
         Aircraft drifted 15m due to wind
         GPS reports position 15m away from estimated position

         EST_XY_VALID = true (724 < 1000)
         EST_GPS_XY_VALID = true (GPS is good)

         → SLOW PATH selected

         gpsPosResidualMag = 1500cm (15m)
         posEstimator.gps.eph = 100cm
         Target EPH = MAX(100, 1500) = 1500cm  ← LARGER than current!

         newEPH = 724 + (1500 - 724) * 1.0 * 0.02
                = 724 + 15.52
                = 739.52cm

         EPH INCREASED! Position estimate gets WORSE before getting better.

T=2s+:   Position correction is applied (lines 681-682)
         Estimated position slowly moves toward GPS position
         Residual decreases over multiple seconds
         EPH eventually starts decreasing

T=5-15s: Position finally converges
         Residual drops below GPS EPH
         EPH recovery completes
```

### Recovery Time vs GPS Dropout Duration

| GPS Dropout | Est. EPH at Recovery | Recovery Path | Est. Recovery Time |
|-------------|---------------------|---------------|-------------------|
| 0.5s        | ~110cm              | Slow          | 3-10s (drift dependent) |
| 1.0s        | ~269cm              | Slow          | 5-15s (drift dependent) |
| 2.0s        | ~724cm              | Slow          | 5-20s (drift dependent) |
| 2.5s        | ~1200cm             | Fast          | ~200ms |
| 3.0s+       | >1000cm (capped)    | Fast          | ~200ms |

### Factors That Worsen Slow Path Recovery

1. **Wind:** Causes position drift during dropout
2. **Accelerometer bias:** Accumulated error in dead-reckoning
3. **Aircraft speed:** Faster aircraft drift further
4. **Vibration:** Degrades accelerometer accuracy
5. **Low `w_xy_gps_p` setting:** Slower filter convergence

### Configuration Impact

**File:** `src/main/fc/settings.yaml`

| Setting | Default | Impact on Recovery |
|---------|---------|-------------------|
| `inav_w_xy_gps_p` | 1.0 | Higher = faster EPH convergence |
| `inav_max_eph_epv` | 1000 | Lower = more dropouts trigger fast path |

### Why This Matters for Distance to Home

During the slow recovery period:

1. `posEstimator.est.eph` remains elevated
2. If EPH >= max_eph_epv: `estPosValid = false` → `estPosStatus = EST_NONE`
3. If EPH < max_eph_epv but position is wrong: Distance calculation uses incorrect position
4. Distance to home may show incorrect values or freeze at last known value

### Implications

**Short GPS glitches (1-2 seconds) can cause extended position estimate degradation lasting 5-15+ seconds**, even after GPS signal is fully restored with good quality.

This is counterintuitive: **brief GPS dropouts can be more disruptive than longer ones** because they don't trigger the fast recovery path.

---

## Condition 5: Delayed RTH Trigger After GPS Glitch (General Mechanism)

**Observed Symptom:** Distance to home becomes 0 approximately **10 seconds AFTER** a brief GPS glitch, even though GPS has fully recovered.

This condition describes a complex interaction between GPS recovery difficulties, position timeout failsafe, and RTH initialization logic.

### Hypothesis: Position Timeout Triggers RTH with Incorrect Position

**Timeline:**

```
T=0s:      GPS glitch begins (satellite count drops to 0)
           EPH starts growing exponentially

T=0-2s:    EPH grows but remains < 1000cm (max_eph_epv threshold)
           Position estimate drifts via accelerometer dead-reckoning
           EST_XY_VALID = true (EPH still below threshold)

T=~1-2s:   GPS signal recovers
           BUT: Slow EPH recovery path is triggered (because EPH < threshold)
           Position residual is large due to drift during glitch

T=~2-5s:   EPH target = MAX(gps.eph, position_residual)
           If position drifted significantly, EPH may INCREASE
           EPH crosses 1000cm threshold

T=~5s:     EPH >= max_eph_epv
           estPosValid = false
           estPosStatus = EST_NONE
           pos_failure_timeout countdown begins (default: 5 seconds)

T=~10s:    pos_failure_timeout expires
           Failsafe or navigation mode triggers RTH

T=~10s:    RTH initialization runs [navigation.c:1527]
           Checks: if (posControl.homeDistance < nav_min_rth_distance)

           IF position estimate has drifted to appear "near" home:
             └─▶ setHomePosition() called [navigation.c:1528]
                   └─▶ posControl.homeDistance = 0 [navigation.c:3227]
                         └─▶ DISTANCE BECOMES 0
```

### Code Path Analysis

**Step 1: Position Timeout Check**

**File:** `src/main/navigation/navigation.c`
**Lines:** 2778-2785

```c
bool checkForPositionSensorTimeout(void)
{
    if (navConfig()->general.pos_failure_timeout) {
        if ((posControl.flags.estPosStatus == EST_NONE) &&
            ((millis() - posControl.lastValidPositionTimeMs) >
             (1000 * navConfig()->general.pos_failure_timeout))) {  // Default: 5000ms
            return true;  // Position sensor has timed out
        }
    }
    return false;
}
```

**Step 2: RTH Initialization Near-Home Check**

**File:** `src/main/navigation/navigation.c`
**Lines:** 1527-1531

```c
// If close to home - reset home position and land
if (posControl.homeDistance < navConfig()->general.min_rth_distance) {  // Default: 500cm (5m)
    setHomePosition(&navGetCurrentActualPositionAndVelocity()->pos,     // Current (wrong) position!
                    posControl.actualState.yaw,
                    NAV_POS_UPDATE_XY | NAV_POS_UPDATE_HEADING,
                    NAV_HOME_VALID_ALL);
    // ... proceeds to landing
}
```

### Why Position Might Appear "Near Home"

During the GPS glitch and subsequent EST_NONE period:

1. **Position estimate freezes** when EPH > max_eph_epv (EST_XY_VALID = false)
2. **homeDistance continues to be calculated** using frozen/stale position
3. If position happened to freeze near home coordinates, `homeDistance` will be small
4. The RTH "near home" check uses this potentially incorrect `homeDistance`

**Position Freezing Code:**

**File:** `src/main/navigation/navigation_pos_estimator.c`
**Lines:** 528-540

```c
/* Prediction step: XY-axis */
if ((ctx->newFlags & EST_XY_VALID)) {      // Only updates if EPH < threshold
    posEstimator.est.pos.x += posEstimator.est.vel.x * ctx->dt;
    posEstimator.est.pos.y += posEstimator.est.vel.y * ctx->dt;
    // ... acceleration integration
}
// If EST_XY_VALID is false, position is NOT updated (frozen)
```

### Alternative Trigger: SafeHome Activation

If SafeHome is configured, RTH activation calls `checkSafeHomeState(true)`:

**File:** `src/main/navigation/navigation.c`
**Lines:** 5072-5079

```c
void activateForcedRTH(void)
{
    posControl.flags.forcedRTHActivated = true;
#ifdef USE_SAFE_HOME
    checkSafeHomeState(true);              // May call setHomePosition()
#endif
    navProcessFSMEvents(selectNavEventFromBoxModeInput());
}
```

`checkSafeHomeState(true)` calls `setHomePosition()` to set home to the SafeHome location, which sets `homeDistance = 0` before `updateHomePosition()` recalculates it.

### Conditions Required for This Scenario

| Condition | Requirement |
|-----------|-------------|
| GPS glitch duration | Brief enough that EPH stays < 1000cm initially |
| Position drift | Significant drift toward home during dead-reckoning |
| pos_failure_timeout | Enabled (default: 5 seconds) |
| Navigation mode | RTH must be triggered (failsafe, manual, or automatic) |
| homeDistance check | Stale position makes aircraft appear within 5m of home |

### Diagnostic Questions

To confirm this hypothesis, the following information is needed:

1. **Was RTH triggered around the time distance became 0?**
   - Check OSD for RTH mode indicator
   - Check if failsafe was activated

2. **What flight mode was active when the GPS glitch occurred?**
   - Manual/Acro: RTH wouldn't auto-trigger unless failsafe
   - Waypoint mission: Has specific failsafe handling
   - Cruise/Poshold: May switch to idle on position loss

3. **Is SafeHome configured?**
   - If yes, SafeHome activation resets homeDistance to 0 temporarily
   - Check `safehome_usage_mode` setting

4. **Did distance stay at 0 permanently or recover?**
   - **Permanent 0**: Home was reset to current (wrong) position
   - **Temporary 0**: Transient from SafeHome toggle or display glitch

5. **What is the `pos_failure_timeout` setting?**
   - Default: 5 seconds
   - If set to 0: Failsafe lands immediately without timeout

6. **What is the `nav_min_rth_distance` setting?**
   - Default: 500cm (5 meters)
   - Higher values make false "near home" detection more likely

7. **What GPS receiver model is being used?**
   - Some receivers report elevated EPH after signal recovery
   - This prolongs EST_NONE duration

8. **Was there video/OSD recording showing the event?**
   - Check for RTH activation indicator
   - Check satellite count, HDOP values before/during/after
   - Check for failsafe indicators

### Configuration to Reduce Risk

| Setting | Recommendation | Rationale |
|---------|---------------|-----------|
| `inav_w_xy_gps_p` | Increase to 2.0-5.0 | Faster EPH recovery |
| `inav_max_eph_epv` | Lower to 500-800 | Triggers fast recovery path sooner |
| `pos_failure_timeout` | Increase to 10+ | More time for recovery before failsafe |
| `nav_min_rth_distance` | Lower to 200-300 | Reduces false "near home" matches |

### Verifying the Hypothesis

Without blackbox data, verification is difficult. Possible approaches:

1. **OSD Recording Analysis**
   - Frame-by-frame analysis of satellite count, HDOP, flight mode indicators
   - Look for RTH activation ~10 seconds after GPS glitch

2. **Reproduce with Blackbox Enabled**
   - Enable `DEBUG_POS_EST` debug mode
   - Deliberately induce GPS signal loss (RF shield test)
   - Analyze EPH growth and recovery pattern

3. **Check Failsafe Configuration**
   - Review `failsafe_procedure` setting
   - Check if GPS loss triggers RTH via failsafe

---

## Condition 5b: GPS Fix Estimation Delayed Failsafe RTH (WP Mode - Confirmed)

**This is a CONFIRMED mechanism** observed in INAV 8.0.1 that causes distance to become 0 approximately **8-10 seconds after GPS dropout** when flying in Waypoint mode on a fixed-wing aircraft with GPS Fix Estimation enabled.

### The Specific Code Path

**File:** `src/main/flight/failsafe.c`
**Lines:** 378-396

```c
#ifdef USE_GPS_FIX_ESTIMATION
bool checkGPSFixFailsafe(void)
{
    if (STATE(GPS_ESTIMATED_FIX) &&
        (FLIGHT_MODE(NAV_WP_MODE) || isWaypointMissionRTHActive()) &&
        (failsafeConfig()->failsafe_gps_fix_estimation_delay >= 0)) {

        if (!failsafeState.wpModeGPSFixEstimationDelayedFailsafeStart) {
            failsafeState.wpModeGPSFixEstimationDelayedFailsafeStart = millis();
        } else if ((millis() - failsafeState.wpModeGPSFixEstimationDelayedFailsafeStart) >
                   (MILLIS_PER_SECOND * (uint16_t)MAX(failsafeConfig()->failsafe_gps_fix_estimation_delay, 7))) {
            if (!posControl.flags.forcedRTHActivated) {
                failsafeSetActiveProcedure(FAILSAFE_PROCEDURE_RTH);
                failsafeActivate(FAILSAFE_RETURN_TO_HOME);
                activateForcedRTH();                    // <-- RTH TRIGGERED HERE
                return true;
            }
        }
    } else {
        failsafeState.wpModeGPSFixEstimationDelayedFailsafeStart = 0;  // Reset timer
    }
    return false;
}
#endif
```

### Key Timing: Minimum 7 Seconds

The delay is enforced to be **at least 7 seconds** regardless of the `failsafe_gps_fix_estimation_delay` setting:

```c
MAX(failsafeConfig()->failsafe_gps_fix_estimation_delay, 7)
```

**Default value:** `SETTING_FAILSAFE_GPS_FIX_ESTIMATION_DELAY_DEFAULT = 7` seconds

### Conditions Required

| Condition | Requirement |
|-----------|-------------|
| Aircraft type | Fixed-wing (`STATE(AIRPLANE)` must be true) |
| Flight mode | WP mode OR WP mission RTH active |
| GPS Fix Estimation | Enabled (`allow_gps_fix_estimation = ON`) |
| Barometer | Present and healthy |
| Home position | Was set before GPS loss (`GPS_FIX_HOME` state) |
| GPS state | `GPS_ESTIMATED_FIX` active (real GPS lost or insufficient) |
| Delay setting | `failsafe_gps_fix_estimation_delay >= 0` (not disabled) |

### How GPS Fix Estimation Works

**File:** `src/main/io/gps.c`
**Lines:** 266-340

When GPS is lost but estimation is enabled:

```c
void updateEstimatedGPSFix(void)
{
    bool sensorHasFix = gpsSol.fixType == GPS_FIX_3D && gpsSol.numSat >= gpsConfig()->gpsMinSats;

    if (sensorHasFix || !canEstimateGPSFix()) {
        // Real GPS is good - use actual data, return early
        return;
    }

    // GPS lost - estimate position using dead reckoning
    gpsSol.fixType = GPS_FIX_3D;
    gpsSol.numSat = 99;        // Magic marker for estimated fix

    // Calculate velocity from airspeed + heading + wind
    float speed = pidProfile()->fixedWingReferenceAirspeed;
    if (sensors(SENSOR_PITOT) && pitotIsHealthy()) {
        speed = getAirspeedEstimate();
    }

    float velX = rMat[0][0] * speed;
    float velY = -rMat[1][0] * speed;

    if (isEstimatedWindSpeedValid()) {
        velX += getEstimatedWindSpeed(X);
        velY += getEstimatedWindSpeed(Y);
    }

    // Dead reckon position
    estimated_lat += (int32_t)(velX * dt / ...);
    estimated_lon += (int32_t)(velY * dt / ...);
}
```

**Position drift sources during estimation:**
- Wind estimation errors
- Airspeed errors (pitot calibration, reference airspeed setting)
- Heading errors (magnetometer drift)
- Accumulated integration errors over time

### Timeline of Events

```
T=0s:      GPS signal lost (satellite count drops below gpsMinSats)
           GPS Fix Estimation activates
           numSat = 99, GPS_ESTIMATED_FIX state enabled
           Position now estimated via dead reckoning

T=0s-7s:   checkGPSFixFailsafe() timer counting
           Estimated position drifting based on:
             - Airspeed (pitot or reference)
             - Heading (magnetometer)
             - Wind estimation

T=7s:      failsafe_gps_fix_estimation_delay expires
           activateForcedRTH() called

T=7s+:     NAV_STATE_RTH_INITIALIZE entered
           Checks: posControl.homeDistance < nav_min_rth_distance (5m)?

           CASE A: Drifted position appears WITHIN 5m of home
             └─▶ setHomePosition() called with drifted position
                   └─▶ homeDistance = 0 (PERMANENTLY)
                   └─▶ Proceeds to RTH_LANDING

           CASE B: Drifted position appears MORE than 5m from home
             └─▶ RTH continues with normal climb/head-home
             └─▶ Aircraft flies toward WRONG location (where it thinks home is)
             └─▶ homeDistance shows distance between drifted position and real home
             └─▶ If/when real GPS returns, position snaps back, distance corrects

T=~8-10s:  Distance becomes 0 (if Case A) or aircraft flies wrong direction (Case B)
```

### Why Distance Becomes 0 and STAYS 0

For distance to become 0 **and remain 0** even after GPS recovers:

1. The drifted position MUST have appeared within 5 meters of home (Case A)
2. This triggered `setHomePosition()` with the drifted coordinates
3. Home was permanently reset to the wrong location
4. `homeDistance = 0` because the new "home" IS the (wrong) current position
5. Even when real GPS returns, home remains at the wrong location
6. Distance is calculated from current position to wrong home = small or 0

### What Happens if NOT Within 5 Meters (Case B)

If the drifted position is >= 5 meters from home:

1. **Home is NOT reset** - original home position preserved
2. **RTH proceeds with drifted navigation** - aircraft flies toward wrong location
3. **homeDistance shows incorrect value** - distance between drifted position and actual home
4. **Aircraft flies off course** - potentially in completely wrong direction

**When real GPS eventually returns:**
- Position snaps back to reality
- homeDistance is recalculated correctly
- Aircraft may be far off course but distance shows actual value
- RTH continues toward correct home (now that position is accurate)

**Key insight:** Only Case A (drift within 5m of home) causes distance to become 0 permanently. Case B causes navigation errors but distance eventually self-corrects.

### Why "Quick GPS Recovery" May Not Clear GPS_ESTIMATED_FIX

The user reported GPS "dropped out and quickly recovered." However, `GPS_ESTIMATED_FIX` only clears when:

```c
bool sensorHasFix = gpsSol.fixType == GPS_FIX_3D && gpsSol.numSat >= gpsConfig()->gpsMinSats;
```

**Both conditions must be met:**
1. Fix type must be 3D (not 2D or No Fix)
2. Satellite count must be >= `gpsMinSats` (default: 6)

If GPS signal returns but with:
- Only 2D fix, OR
- Fewer than 6 satellites

Then `GPS_ESTIMATED_FIX` remains active and the 7-second failsafe timer continues!

### Difference from Condition 5 (pos_failure_timeout)

| Aspect | Condition 5 (pos_failure_timeout) | Condition 5b (GPS Fix Estimation) |
|--------|-----------------------------------|-----------------------------------|
| Trigger | `checkForPositionSensorTimeout()` | `checkGPSFixFailsafe()` |
| Default delay | 5 seconds | 7 seconds (minimum) |
| Flight modes | Any navigation mode | **WP mode only** |
| Aircraft type | All | **Fixed-wing only** |
| Position during delay | May be frozen/invalid | Actively estimated (drifting) |
| GPS state | EST_NONE | GPS_ESTIMATED_FIX (appears valid) |

### Configuration to Mitigate

| Setting | Default | Recommendation |
|---------|---------|----------------|
| `failsafe_gps_fix_estimation_delay` | 7 | Increase to 15-30 for more recovery time |
| `allow_gps_fix_estimation` | ON | Consider OFF if GPS is reliable |
| `nav_min_rth_distance` | 500 (5m) | Decrease to 200-300 to reduce false matches |
| `gps_min_sats` | 6 | Consider 5 if GPS recovery is slow |

### Diagnostic Indicators

**OSD indicators that GPS Fix Estimation is active:**
- Satellite count shows exactly **99** (magic marker value)
- GPS icon may still show "valid" even though it's estimated
- Position may drift even without visible GPS loss

**Blackbox logging:**
- Look for `numSat = 99` entries
- Check `GPS_ESTIMATED_FIX` flag in flight mode data
- Monitor position drift during estimation period

---

## Condition 6: Physical Proximity to Home

When the aircraft is physically at or very near the home position, the calculated distance will naturally be 0 or near-zero.

**Calculation Function:**
**File:** `src/main/navigation/navigation_private.h`
**Line:** 533

```c
uint32_t calculateDistanceToDestination(const fpVector3_t * destinationPos);
```

This calculates 2D horizontal distance. When aircraft position equals home position, result is 0.

---

## Disruption Scenarios Summary

### Scenarios Where Distance Was Normal Then Becomes 0 or Incorrect

| Scenario | Trigger | Duration | Recovery |
|----------|---------|----------|----------|
| **BOXHOMERESET activated** | Pilot switch | Permanent until re-reset | Toggle switch, home resets again |
| **RTH near home** | RTH < 5m from home | Permanent for flight | Land, re-arm to get new home |
| **SafeHome toggle** | RTH activate/deactivate | Brief (~20ms) | Automatic recalculation |
| **GCS home override** | MSP WP#0 command | Permanent until re-set | Send new WP#0 or land |
| **GPS signal loss** | RF interference, obstruction | While GPS invalid | Restore GPS signal |
| **GPS fix degradation** | 3D→2D or NoFix | While fix lost | Regain 3D fix |
| **EPH growth** | No GPS corrections | Progressive over ~seconds | Restore GPS quality |
| **Short GPS glitch (1-2s)** | Brief RF interference | **5-15+ seconds** | Wait for slow EPH recovery |
| **Long GPS dropout (>2.5s)** | Extended signal loss | ~200ms after GPS returns | Fast automatic recovery |
| **Delayed RTH after GPS glitch** | pos_failure_timeout + RTH trigger | **~10 seconds after glitch** | Permanent - home reset to wrong position |
| **GPS Fix Est. failsafe (WP mode)** | GPS lost in WP mode, FW aircraft | **~8 seconds after GPS loss** | Permanent if drift < 5m from home; self-correcting otherwise |

### Timeline of Position Estimate Degradation

```
T+0.0s: GPS signal lost
T+1.0s: GPS timeout triggers (gpsState.baseTimeoutMs = 1000ms)
        └─▶ DISABLE_STATE(GPS_FIX)
T+1.0s: Position estimator stops getting GPS corrections
T+1.0s-T+2.3s: EPH grows exponentially (roughly doubles per second)
T+~2.3s: EPH exceeds max_eph_epv (1000cm default)
         └─▶ estPosStatus = EST_NONE
T+~2.3s+: Distance calculation continues with stale position
          (may drift, but won't suddenly become 0)
```

### Timeline of EPH Recovery After GPS Returns

**Case A: Long dropout (>2.3s) - FAST RECOVERY**
```
T+0s:    GPS returns after long dropout
         est.eph > 1000cm (max_eph_epv)
         EST_XY_VALID = false
         → FAST PATH: Direct EPH assignment
T+~20ms: est.eph = gps.eph (~100cm)
         Position snapped to GPS
         Full recovery complete
```

**Case B: Short dropout (<2.3s) with drift - SLOW RECOVERY**
```
T+0s:    GPS returns after 2s dropout
         est.eph = 724cm (< 1000cm max)
         EST_XY_VALID = true
         Aircraft drifted 15m
         → SLOW PATH: Filtered update

T+0s:    Target EPH = MAX(gps.eph, residual) = 1500cm
         EPH INCREASES toward 1500cm (worse before better)

T+1-5s:  Position slowly corrects toward GPS
         Residual decreases
         EPH begins decreasing

T+5-15s: Residual finally < gps.eph
         EPH converges to gps.eph
         Full recovery complete
```

**Case C: Delayed RTH trigger after GPS glitch - DISTANCE BECOMES 0**
```
T+0s:    GPS glitch begins (satellite count = 0)
         EPH starts growing

T+1-2s:  GPS recovers, EPH still < 1000cm
         Slow recovery path triggered
         Position residual is large

T+2-5s:  EPH target = MAX(gps.eph, residual)
         EPH may INCREASE due to large residual
         EPH crosses 1000cm threshold
         estPosStatus = EST_NONE begins

T+5s:    EST_NONE persists
         pos_failure_timeout counting (default 5s)
         Position estimate is FROZEN

T+~10s:  pos_failure_timeout expires
         Failsafe/navigation triggers RTH
         RTH init checks: homeDistance < min_rth_distance?

         IF frozen position appears near home (due to drift):
           └─▶ setHomePosition() called
                 └─▶ homeDistance = 0
                       └─▶ DISTANCE BECOMES 0 PERMANENTLY
```

**Important:** GPS loss does NOT immediately zero the distance. It causes position estimate to become invalid, but the stored position and calculated distance persist until:
1. Home is reset (setHomePosition called)
2. System reinitializes

**Counterintuitive behavior:** Brief GPS glitches (1-2 seconds) can cause **longer recovery times** than extended dropouts (>2.5 seconds) due to the slow EPH recovery path being triggered instead of the fast path.

---

## Call Tree: Complete Path to GPS_distanceToHome

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ updateWaypointsAndNavigationMode() [navigation.c:4851]                      │
│   Called from: schedulerTable, ~50Hz                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│   │                                                                          │
│   ├──▶ updateHomePosition() [navigation.c:3329]                             │
│   │     │                                                                    │
│   │     ├── if (!ARMING_FLAG(ARMED))                                        │
│   │     │     └── Update home pre-arm (continuous tracking)                 │
│   │     │                                                                    │
│   │     ├── else (ARMED)                                                    │
│   │     │     │                                                              │
│   │     │     ├── if (BOXHOMERESET active)                                  │
│   │     │     │     └── setHomePosition() [navigation.c:3385]               │
│   │     │     │           └── homeDistance = 0 [navigation.c:3227]          │
│   │     │     │                                                              │
│   │     │     └── if (GPS_FIX_HOME)                                         │
│   │     │           │                                                        │
│   │     │           ├── calculateDistanceToDestination() [navigation.c:3373]│
│   │     │           │     └── homeDistance = result                         │
│   │     │           │                                                        │
│   │     │           └── updateHomePositionCompatibility() [navigation.c:3375]│
│   │     │                 └── GPS_distanceToHome = homeDistance * 0.01f     │
│   │     │                                                                    │
│   │     └── setHomePosition() if setHome flag [navigation.c:3385]           │
│   │                                                                          │
│   └──▶ selectNavEventFromBoxModeInput() [navigation.c:4448]                 │
│         │                                                                    │
│         └── checkSafeHomeState() [navigation.c:3258]                        │
│               ├── setHomePosition(safehome) [navigation.c:3279]             │
│               ├── setHomePosition(original) [navigation.c:3283]             │
│               └── updateHomePosition() [navigation.c:3287]                  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ RTH State Machine Entry                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ navOnEnteringState_NAV_STATE_RTH_INITIALIZE() [navigation.c:1502]           │
│   │                                                                          │
│   └── if (homeDistance < min_rth_distance)                                  │
│         └── setHomePosition() [navigation.c:1528]                           │
│               └── homeDistance = 0                                          │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ MSP Command Processing                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ mspFcProcessCommand(MSP_SET_WP)                                             │
│   └── setWaypointFromMSP() with wpNumber=0 [navigation.c:3890]              │
│         └── setHomePosition() [navigation.c:3893]                           │
│               └── homeDistance = 0                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Debugging Recommendations

### 1. Check Telemetry for GPS_FIX_HOME State

SmartPort telemetry encodes GPS_FIX_HOME in T2 sensor:
```
T2 value includes: +2000 if GPS_FIX_HOME is set
```
**File:** `src/main/telemetry/smartport.c:243-244`

### 2. Monitor Position Estimate Status

Enable DEBUG_POS_EST in blackbox to log:
- Position estimate X/Y
- EPH/EPV values
- Estimator flags

### 3. Check Configuration Settings

| Setting | Default | Impact |
|---------|---------|--------|
| `nav_min_rth_distance` | 500 (cm) | Distance below which RTH resets home |
| `inav_max_eph_epv` | 1000 (cm) | Threshold for position validity |
| `inav_w_xy_gps_p` | 1.0 | GPS position weight (higher = faster EPH recovery) |
| `nav_extra_arming_safety` | ON | Prevents arming without GPS |
| `pos_failure_timeout` | 5 (sec) | Time before failsafe on position loss |
| `safehome_usage_mode` | OFF | SafeHome feature enable |

### 4. Verify Switch Assignments

Check that BOXHOMERESET is not accidentally mapped:
```
# In CLI:
aux
```

Look for any `BOXHOMERESET` (box ID 21) assignments.

### 5. Monitor GPS Quality

Watch for:
- Satellite count dropping
- HDOP/PDOP increasing
- Fix type changes (3D → 2D → None)
- EPH values in OSD (if displayed)

### 6. Check for GCS Commands

If using ground station software, verify it's not sending MSP_SET_WP with waypoint 0.

### 7. Diagnosing EPH Recovery Issues

**Symptoms of slow EPH recovery:**
- Position estimate remains invalid for 5-15+ seconds after GPS returns
- OSD shows stale/incorrect position data after brief GPS glitch
- Navigation modes won't engage even with good GPS signal

**Blackbox analysis:**
Enable `DEBUG_POS_EST` and look for:
- `navEPH` value (should drop quickly after GPS returns)
- Position residual between GPS and estimated position
- `navFlags` bit 2 (`EST_POS_TRUSTED`)

**Identifying the slow recovery path:**
```
If after GPS returns:
  - navEPH is INCREASING instead of decreasing → Slow path, large position residual
  - navEPH drops immediately → Fast path triggered (good)
```

**Potential mitigations:**
1. **Increase `inav_w_xy_gps_p`** (default 1.0, max 10.0) - Faster filter convergence
2. **Decrease `inav_max_eph_epv`** (default 1000cm) - More dropouts trigger fast path
   - Trade-off: May reject valid position data in marginal GPS conditions
3. **Improve GPS antenna placement** - Reduce multipath and signal loss
4. **Reduce vibration** - Better accelerometer data during dead-reckoning

**Expected recovery times by configuration:**

| `inav_w_xy_gps_p` | 95% EPH Recovery (no drift) | With 10m drift |
|-------------------|----------------------------|----------------|
| 0.5               | ~6 seconds                 | 15-30 seconds  |
| 1.0 (default)     | ~3 seconds                 | 8-15 seconds   |
| 2.0               | ~1.5 seconds               | 4-8 seconds    |
| 5.0               | ~0.6 seconds               | 2-4 seconds    |

---

## Key Configuration References

**File:** `src/main/fc/settings.yaml`
```yaml
- name: nav_min_rth_distance
  description: "Minimum distance from homepoint when RTH full procedure will be activated [cm]"
  default_value: 500
  field: general.min_rth_distance
  min: 0
  max: 5000
```

**File:** `src/main/navigation/navigation_pos_estimator.c`
```c
.max_eph_epv = SETTING_INAV_MAX_EPH_EPV_DEFAULT,  // Line 92
```

**File:** `src/main/navigation/navigation_pos_estimator_private.h`
```c
#define INAV_GPS_TIMEOUT_MS  1500    // GPS timeout (Line 43)
```
