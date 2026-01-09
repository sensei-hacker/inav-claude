# Jetrell Logic Conditions - Pseudocode Translation

This document translates the logic conditions from `jetrell-logic.txt` into readable
JavaScript-like pseudocode to understand the programming logic.

## Reference Key

### Operand Types
| Type | Name | Description |
|------|------|-------------|
| 0 | Value | Constant value |
| 1 | RC | RC channel value (1-indexed) |
| 2 | Flight | Flight parameter |
| 3 | FlightMode | Flight mode check |
| 4 | LC | Logic Condition result |
| 5 | GVAR | Global Variable |
| 6 | Waypoint | Waypoint data |

### Flight Parameters Used
| Value | Name | Unit |
|-------|------|------|
| 9 | Ground Speed | cm/s |
| 10 | 3D Speed | cm/s |
| 11 | Air Speed | cm/s |
| 12 | Altitude | cm |
| 17 | Is Armed | boolean |
| 18 | Is Autolaunch | boolean |
| 23 | Is Landing | boolean |
| 31 | GPS Valid Fix | boolean |

---

## Logic Condition Translations

### Group 1: GPS and Speed Checks (LC 0-5, 12)

```javascript
// logic 0 1 -1 1 2 31 0 1 0
// Operation 1 = EQUAL, Flight[31] = GPS Valid Fix
// Always active (activator -1)
LC[0] = (flight.gpsValidFix == 1);  // True if GPS has valid fix

// logic 1 1 0 2 2 9 0 1000 0
// Operation 2 = GT, Flight[9] = Ground Speed
// Active when LC[0] is true (GPS fix)
if (LC[0]) {
    LC[1] = (flight.groundSpeed > 1000);  // True if ground speed > 10 m/s
}

// logic 2 1 0 13 4 1 4 3 0
// Operation 13 = STICKY, Operands are LC[1] and LC[3]
// Sticky: activates on LC[1], deactivates on LC[3]
if (LC[0]) {
    LC[2] = sticky(LC[1], LC[3]);  // Latches when speed > 10 m/s, clears on disarm
}

// logic 3 1 -1 1 2 17 0 0 0
// Operation 1 = EQUAL, Flight[17] = Is Armed
// Always active
LC[3] = (flight.isArmed == 0);  // True when DISARMED

// logic 4 1 2 14 2 11 0 0 0
// Operation 14 = ADD, Flight[11] = Air Speed, Value = 0
// Active when LC[2] is true (sticky engaged)
if (LC[2]) {
    LC[4] = flight.airSpeed + 0;  // Just reads air speed value
}

// logic 5 1 2 14 2 10 0 0 0
// Operation 14 = ADD, Flight[10] = 3D Speed, Value = 0
// Active when LC[2] is true
if (LC[2]) {
    LC[5] = flight.speed3D + 0;  // Just reads 3D speed value
}

// logic 12 1 -1 1 2 31 0 0 0
// Operation 1 = EQUAL, Flight[31] = GPS Valid Fix, Value = 0
// Always active
LC[12] = (flight.gpsValidFix == 0);  // True when NO GPS fix
```

**Summary**: This group tracks whether the aircraft has achieved > 10 m/s ground speed
with GPS. Once triggered, it latches (`sticky`) until disarmed. LC[4] and LC[5] store
current speeds while that condition is active. LC[12] is the opposite - true when no GPS fix.

---

### Group 2: 3D Home Distance Calculation (LC 20-28)

```javascript
// logic 20 1 -1 16 0 50 0 28 0
// Operation 16 = MULTIPLY, Value 50 * Value 28
// Always active
LC[20] = 50 * 28;  // = 1400 (constant calculation)

// logic 21 1 33 2 4 5 4 4 0
// Operation 2 = GT, LC[5] > LC[4]
// Active when LC[33] is true (PID system active)
if (LC[33]) {
    LC[21] = (LC[5] > LC[4]);  // True if 3D speed > air speed
}

// logic 22 1 21 3 4 4 4 20 0
// Operation 3 = LT, LC[4] < LC[20]
// Active when LC[21] is true
if (LC[21]) {
    LC[22] = (LC[4] < LC[20]);  // True if air speed < 1400 cm/s (14 m/s)
}

// logic 23 1 22 15 4 20 4 4 0
// Operation 15 = SUBTRACT, LC[20] - LC[4]
// Active when LC[22] is true
if (LC[22]) {
    LC[23] = LC[20] - LC[4];  // 1400 - airSpeed (clamped value)
}

// logic 24 1 23 19 0 0 4 23 0
// Operation 19 = GVAR_INC, GVAR[0] += LC[23]
// Active when LC[23] is active
if (LC[23]) {
    gvar[0] += LC[23];  // Increment GVAR[0] by the speed difference
}

// logic 25 1 27 13 4 24 4 26 0
// Operation 13 = STICKY, activates on LC[24], deactivates on LC[26]
// Active when LC[27] is true
if (LC[27]) {
    LC[25] = sticky(LC[24], LC[26]);
}

// logic 26 1 25 2 4 4 4 20 0
// Operation 2 = GT, LC[4] > LC[20]
// Active when LC[25] is true
if (LC[25]) {
    LC[26] = (LC[4] > LC[20]);  // True if air speed > 1400
}

// logic 27 1 53 2 1 11 0 1480 0
// Operation 2 = GT, RC[11] > 1480
// Active when LC[53] is true (autolaunch not active)
if (LC[53]) {
    LC[27] = (rc[11] > 1480);  // True if RC channel 11 > 1480
}

// logic 28 1 -1 47 4 27 0 100 0
// Operation 47 = EDGE, triggers on LC[27] for 100ms
// Always active
LC[28] = edge(LC[27], 100);  // Momentary pulse when RC[11] goes high
```

**Summary**: Complex speed-based calculations. When RC channel 11 goes high and autolaunch
is not active, this calculates differences between speeds and accumulates values in GVAR[0].
Appears to be a speed integration/tracking system.

---

### Group 3: Delta Detection and Landing Override (LC 29-38)

```javascript
// logic 29 1 -1 50 1 4 0 90 0
// Operation 50 = DELTA, RC[4] (throttle) changed by 90+
// Always active
LC[29] = delta(rc[4], 90);  // True if throttle changed by >= 90 in 100ms

// logic 30 1 -1 1 2 23 0 1 0
// Operation 1 = EQUAL, Flight[23] = Is Landing
// Always active
LC[30] = (flight.isLanding == 1);  // True when auto-landing

// logic 31 1 -1 8 4 12 4 29 0
// Operation 8 = OR, LC[12] OR LC[29]
// Always active
LC[31] = LC[12] || LC[29];  // True if no GPS OR throttle moved fast

// logic 32 1 -1 8 4 31 4 30 0
// Operation 8 = OR, LC[31] OR LC[30]
// Always active
LC[32] = LC[31] || LC[30];  // True if (no GPS OR throttle moved) OR landing

// logic 33 1 27 13 4 28 4 32 0
// Operation 13 = STICKY, activates on LC[28], deactivates on LC[32]
// Active when LC[27] is true
if (LC[27]) {
    LC[33] = sticky(LC[28], LC[32]);
}
// LC[33] = MAIN PID SYSTEM ENABLE FLAG
// Activates: when RC[11] edge detected (LC[28])
// Deactivates: when landing, no GPS, or throttle moved significantly

// logic 34 1 33 12 4 25 0 0 0
// Operation 12 = NOT, !LC[25]
// Active when LC[33] is true
if (LC[33]) {
    LC[34] = !LC[25];
}

// logic 35 1 34 15 1 12 0 1000 0
// Operation 15 = SUBTRACT, RC[12] - 1000
// Active when LC[34] is true
if (LC[34]) {
    LC[35] = rc[12] - 1000;  // Normalize RC[12] to 0-based
}

// logic 36 1 35 37 4 35 0 110 0
// Operation 37 = MAP_OUT, maps LC[35] from [0:1000] to [0:110]
// Active when LC[35] is active
if (LC[35]) {
    LC[36] = mapOutput(LC[35], 110);  // Scale to 0-110 range
}

// logic 37 1 36 16 4 36 0 28 0
// Operation 16 = MULTIPLY, LC[36] * 28
// Active when LC[36] is active
if (LC[36]) {
    LC[37] = LC[36] * 28;  // Scale up by factor of 28
}

// logic 38 1 37 18 0 0 4 37 0
// Operation 18 = GVAR_SET, GVAR[0] = LC[37]
// Active when LC[37] is active
if (LC[37]) {
    gvar[0] = LC[37];  // Store scaled value in GVAR[0]
}
```

**Summary**: LC[33] is the master enable for the PID system. It activates when RC[11]
triggers and deactivates on landing, GPS loss, or significant throttle input.
RC[12] is used to set a scaled value (0-110 scaled by 28) into GVAR[0].

---

### Group 4: Throttle Override System (LC 39-46)

```javascript
// logic 39 1 33 14 6 3 0 3000 0
// Operation 14 = ADD, Waypoint[3] (next WP action) + 3000
// Active when LC[33] is true (PID system active)
if (LC[33]) {
    LC[39] = waypoint.nextAction + 3000;
}

// logic 40 1 33 17 4 39 0 2 0
// Operation 17 = DIVIDE, LC[39] / 2
// Active when LC[33] is true
if (LC[33]) {
    LC[40] = Math.floor(LC[39] / 2);  // Integer division
}

// logic 41 1 33 43 0 1800 4 40 0
// Operation 43 = MIN, minimum of 1800 and LC[40]
// Active when LC[33] is true
if (LC[33]) {
    LC[41] = Math.min(1800, LC[40]);
}

// logic 42 1 33 44 0 1250 4 41 0
// Operation 44 = MAX, maximum of 1250 and LC[41]
// Active when LC[33] is true
if (LC[33]) {
    LC[42] = Math.max(1250, LC[41]);  // Clamp between 1250-1800
}

// logic 43 1 33 44 4 41 4 42 0
// Operation 44 = MAX, maximum of LC[41] and LC[42]
// Active when LC[33] is true
if (LC[33]) {
    LC[43] = Math.max(LC[41], LC[42]);
}

// logic 44 1 33 29 4 43 0 0 0
// Operation 29 = OVERRIDE_THROTTLE, set throttle to LC[43]
// Active when LC[33] is true
if (LC[33]) {
    overrideThrottle(LC[43]);  // Override motor throttle in µs (1250-1800 range)
}

// logic 45 1 33 17 4 43 0 10 0
// Operation 17 = DIVIDE, LC[43] / 10
// Active when LC[33] is true
if (LC[33]) {
    LC[45] = Math.floor(LC[43] / 10);  // Scale down by 10
}

// logic 46 1 33 15 4 45 0 100 0
// Operation 15 = SUBTRACT, LC[45] - 100
// Active when LC[33] is true
if (LC[33]) {
    LC[46] = LC[45] - 100;  // Further adjust (throttle % - 100?)
}
```

**Summary**: When the PID system (LC[33]) is active, this calculates a throttle value
based on waypoint data, clamps it to 1250-1800 µs range, and overrides the motor throttle.
LC[45] and LC[46] appear to be for OSD display purposes (scaling for readout).

---

### Group 5: Position Hold Override (LC 47-52)

```javascript
// logic 47 1 -1 1 3 3 0 1 0
// Operation 1 = EQUAL, FlightMode[3] (Position Hold) == 1
// Always active
LC[47] = (flightMode.positionHold == 1);  // True if in Position Hold mode

// logic 48 1 33 6 1 11 0 0 0
// Operation 6 = HIGH, RC[11] > 1666
// Active when LC[33] is true
if (LC[33]) {
    LC[48] = (rc[11] > 1666);  // True if RC[11] is HIGH
}

// logic 49 1 33 8 4 47 4 48 0
// Operation 8 = OR, LC[47] OR LC[48]
// Active when LC[33] is true
if (LC[33]) {
    LC[49] = LC[47] || LC[48];  // True if pos hold OR RC[11] high
}

// logic 50 1 49 18 0 1 4 4 0
// Operation 18 = GVAR_SET, GVAR[1] = LC[4]
// Active when LC[49] is true
if (LC[49]) {
    gvar[1] = LC[4];  // Store air speed in GVAR[1]
}

// logic 51 1 33 12 4 50 0 0 0
// Operation 12 = NOT, !LC[50]
// Active when LC[33] is true
if (LC[33]) {
    LC[51] = !LC[50];
}

// logic 52 1 51 18 0 1 4 5 0
// Operation 18 = GVAR_SET, GVAR[1] = LC[5]
// Active when LC[51] is true
if (LC[51]) {
    gvar[1] = LC[5];  // Store 3D speed in GVAR[1]
}
```

**Summary**: Manages which speed value to store in GVAR[1] based on flight mode.
In position hold OR when RC[11] is high, it stores air speed. Otherwise, it stores
3D speed. This allows the OSD or other systems to show the appropriate speed metric.

---

### Group 6: Autolaunch Check (LC 53)

```javascript
// logic 53 1 2 1 2 18 0 0 0
// Operation 1 = EQUAL, Flight[18] (Is Autolaunch) == 0
// Active when LC[2] is true (sticky from ground speed trigger)
if (LC[2]) {
    LC[53] = (flight.isAutolaunch == 0);  // True when NOT in autolaunch
}
```

**Summary**: LC[53] is true when autolaunch is not active, but only evaluated when
the aircraft has achieved the speed threshold (LC[2]). This prevents the PID system
from activating during the autolaunch phase.

---

## PID Controller

```javascript
// pid 3 1 5 0 5 1 800 550 80 400
// PID index 3, enabled
// Setpoint: GVAR[0] (operand type 5, value 0)
// Measurement: RC[1] (operand type 1, value 1 = throttle stick?)
// Gains: P=0.8, I=0.55, D=0.08, FF=0.4

pid[3] = {
    enabled: true,
    setpoint: gvar[0],      // Target value from GVAR[0]
    measurement: rc[1],     // Current value from RC channel 1
    P: 0.800,               // Proportional gain
    I: 0.550,               // Integral gain
    D: 0.080,               // Derivative gain
    FF: 0.400               // Feed-forward gain
};
```

---

## Overall System Behavior

This logic program implements an **automated throttle/speed management system** for a fixed-wing aircraft:

1. **Initialization Phase (LC 0-5, 12, 53)**
   - Waits for GPS fix
   - Monitors when aircraft exceeds 10 m/s ground speed
   - Latches this "flying" state until disarm
   - Tracks autolaunch status

2. **PID System Activation (LC 27-28, 33)**
   - Activates when RC channel 11 goes high (switch trigger)
   - Only activates after autolaunch completes
   - Deactivates on: landing, GPS loss, or significant throttle input (pilot override)

3. **Throttle Control (LC 39-44)**
   - Calculates throttle based on waypoint data
   - Clamps throttle to safe range (1250-1800 µs)
   - Overrides motor throttle when PID system active

4. **Speed Display (LC 47-52)**
   - Selects appropriate speed metric for display
   - Uses air speed in position hold, 3D speed otherwise

5. **PID Controller (PID 3)**
   - Uses GVAR[0] as setpoint (computed throttle target)
   - Uses RC[1] as measurement (actual throttle position)
   - Applies PID control with moderate gains

---

## Notes for Transpiler PID Support

Key observations for transpiler implementation:

1. **PID Controllers** use the same operand system as logic conditions
2. **GVAR operations** (SET, INC, DEC) are essential for PID setpoint management
3. **Edge detection** (operation 47) is used for switch triggers
4. **Delta detection** (operation 50) is used for pilot override detection
5. **Sticky conditions** (operation 13) maintain state across cycles
6. **MIN/MAX operations** (43, 44) are used for clamping values
7. **MAP_OUT** (operation 37) scales values to specific ranges
8. **OVERRIDE_THROTTLE** (operation 29) is the key action operation
