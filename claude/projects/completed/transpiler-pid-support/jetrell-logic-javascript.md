# Jetrell Logic - Clean JavaScript Translation

This is a readable JavaScript translation of the logic conditions from `jetrell-logic.txt`.
Logic condition references (LC[N]) have been inlined where possible to show the actual logic flow.

## State Variables

```javascript
// Persistent state (survives across loop iterations)
let hasReachedFlightSpeed = false;  // LC[2] - sticky latch
let pidSystemEnabled = false;       // LC[33] - master PID enable
let speedIntegrationActive = false; // LC[25] - speed integration latch

// Global variables for PID and OSD
let gvar = [0, 0, 0, 0];  // GVAR[0-3]
```

---

## Main Logic Loop

```javascript
function runLogicConditions() {
    // =========================================================================
    // SECTION 1: GPS and Flight State Detection
    // =========================================================================

    const hasGpsFix = (flight.gpsValidFix === 1);
    const noGpsFix = !hasGpsFix;
    const isDisarmed = (flight.isArmed === 0);
    const isInPositionHold = (flightMode.positionHold === 1);
    const isAutoLanding = (flight.isLanding === 1);

    // Detect when aircraft first exceeds 10 m/s (sticky until disarm)
    if (hasGpsFix) {
        const speedExceeded = (flight.groundSpeed > 1000);  // > 10 m/s
        if (speedExceeded) {
            hasReachedFlightSpeed = true;
        }
        if (isDisarmed) {
            hasReachedFlightSpeed = false;  // Reset on disarm
        }
    }

    // Read current speeds (only when in flight)
    let currentAirSpeed = 0;
    let current3DSpeed = 0;
    if (hasReachedFlightSpeed) {
        currentAirSpeed = flight.airSpeed;
        current3DSpeed = flight.speed3D;

        // Check if autolaunch is complete
        var autolaunchComplete = (flight.isAutolaunch === 0);
    }

    // =========================================================================
    // SECTION 2: PID System Activation Control
    // =========================================================================

    // Detect pilot override (rapid throttle movement)
    const throttleMoved = delta(rc[4], 90);  // Throttle changed by >= 90 in 100ms

    // Conditions that should disable PID system
    const shouldDisablePID = noGpsFix || throttleMoved || isAutoLanding;

    // RC channel 11 controls PID activation (only after autolaunch)
    let pidSwitchHigh = false;
    if (hasReachedFlightSpeed && autolaunchComplete) {
        pidSwitchHigh = (rc[11] > 1480);
    }

    // Edge detect on switch going high (100ms pulse)
    const pidSwitchTriggered = edge(pidSwitchHigh, 100);

    // Master PID enable (sticky latch)
    if (pidSwitchHigh) {
        if (pidSwitchTriggered) {
            pidSystemEnabled = true;
        }
        if (shouldDisablePID) {
            pidSystemEnabled = false;
        }
    }

    // =========================================================================
    // SECTION 3: Speed Integration System
    // =========================================================================

    const SPEED_THRESHOLD = 1400;  // 14 m/s in cm/s

    if (pidSystemEnabled) {
        // Compare 3D speed vs air speed
        if (current3DSpeed > currentAirSpeed) {
            if (currentAirSpeed < SPEED_THRESHOLD) {
                // Aircraft is slow - accumulate speed deficit
                const speedDeficit = SPEED_THRESHOLD - currentAirSpeed;
                gvar[0] += speedDeficit;
            }
        }
    }

    // Speed integration latch control
    if (pidSwitchHigh) {
        // Activate when GVAR increment happens, deactivate when speed recovered
        if (gvar[0] > 0 && !speedIntegrationActive) {
            speedIntegrationActive = true;
        }
        if (speedIntegrationActive && currentAirSpeed > SPEED_THRESHOLD) {
            speedIntegrationActive = false;
        }
    }

    // =========================================================================
    // SECTION 4: Throttle Setpoint Calculation (from RC[12])
    // =========================================================================

    if (pidSystemEnabled && !speedIntegrationActive) {
        // Normalize RC[12] from [1000-2000] to [0-1000]
        const normalizedInput = rc[12] - 1000;

        // Scale to [0-110] range
        const scaledValue = mapOutput(normalizedInput, 110);

        // Multiply by 28 for final setpoint
        const throttleSetpoint = scaledValue * 28;

        // Store in GVAR[0] for PID controller
        gvar[0] = throttleSetpoint;
    }

    // =========================================================================
    // SECTION 5: Throttle Override (from PID Controller Output)
    // =========================================================================

    if (pidSystemEnabled) {
        // Calculate base throttle from PID controller 3 output
        const baseThrottle = pid[3].output + 3000;
        const halfThrottle = Math.floor(baseThrottle / 2);

        // Clamp to safe range [1250-1800] microseconds
        const clampedHigh = Math.min(1800, halfThrottle);
        const clampedLow = Math.max(1250, clampedHigh);
        const finalThrottle = Math.max(clampedHigh, clampedLow);

        // Override motor throttle
        overrideThrottle(finalThrottle);

        // Calculate display value for OSD (throttle percentage)
        const throttlePercent = Math.floor(finalThrottle / 10) - 100;
        // throttlePercent available for OSD display
    }

    // =========================================================================
    // SECTION 6: Speed Display Selection (for OSD)
    // =========================================================================

    if (pidSystemEnabled) {
        const useAirSpeed = isInPositionHold || (rc[11] > 1666);

        if (useAirSpeed) {
            gvar[1] = currentAirSpeed;
        } else {
            gvar[1] = current3DSpeed;
        }
    }
}
```

---

## PID Controller Configuration

```javascript
// PID controller 3 - Throttle control
const pidController3 = {
    enabled: true,
    setpoint: () => gvar[0],     // Target from logic calculations
    measurement: () => rc[1],    // Actual throttle stick position
    gains: {
        P: 0.800,
        I: 0.550,
        D: 0.080,
        FF: 0.400
    }
};
```

---

## Helper Functions (provided by INAV)

```javascript
// Sticky latch - activates on 'set', deactivates on 'reset'
function sticky(set, reset) {
    // Returns true after 'set' becomes true, until 'reset' becomes true
}

// Edge detection - returns true for 'duration' ms when 'trigger' goes true
function edge(trigger, duration) {
    // Momentary pulse on rising edge
}

// Delta detection - returns true if value changed by >= threshold in 100ms
function delta(value, threshold) {
    // Detects rapid changes
}

// Map output - scales value from [0:1000] to [0:max]
function mapOutput(value, max) {
    return Math.floor((Math.min(1000, Math.max(0, value)) * max) / 1000);
}

// Override throttle - sets motor output directly (1000-2000 µs)
function overrideThrottle(value) {
    // Bypasses normal throttle processing
}
```

---

## System Behavior Summary

This logic implements an **automated throttle management system** for fixed-wing aircraft:

1. **Activation**: Triggered by RC channel 11 switch after autolaunch completes
2. **Safety Overrides**: Disables on GPS loss, rapid throttle input, or auto-landing
3. **Throttle Control**: Uses PID controller 3 output to calculate throttle, clamped to 1250-1800 µs
4. **Speed Integration**: Accumulates speed deficit when below 14 m/s threshold
5. **OSD Display**: Shows air speed in position hold, 3D speed otherwise

The PID controller (index 3) uses GVAR[0] as its setpoint and RC[1] as measurement,
applying moderate PID gains to smooth the throttle response.
