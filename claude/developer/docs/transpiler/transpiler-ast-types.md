# INAV Transpiler AST Types Reference

**Purpose:** Complete type reference for the INAV JavaScript transpiler
**Author:** Developer
**Date:** 2025-12-13
**Location:** `inav-configurator/js/transpiler/`

This document provides a comprehensive hierarchical overview of all types manipulated by the INAV JavaScript transpiler, including Acorn AST nodes, operators, and INAV-specific internal structures.

---

## Table of Contents

1. [Acorn AST Node Types](#acorn-ast-node-types)
2. [Operators](#operators)
3. [Transpiler Internal Types](#transpiler-internal-types)
4. [INAV Logic Condition Structure](#inav-logic-condition-structure)
5. [API Variable Types](#api-variable-types)

---

## 1. Acorn AST Node Types

The transpiler uses [Acorn](https://github.com/acornjs/acorn) to parse JavaScript (ES2020). The parser (`parser.js`) transforms Acorn's full AST into a simplified INAV AST containing only supported constructs.

### Top-Level Nodes

```
Program
└── body: Statement[]
```

### Statement Types

```bnf
<statement> ::= <variable-declaration>
              | <expression-statement>
              | <if-statement>

<variable-declaration> ::= "const" | "let" | "var"
<expression-statement> ::= <call-expression> | <assignment-expression> | <update-expression>
<if-statement>         ::= "if" "(" <condition> ")" <block> ["else" <block-or-if>]
```

#### VariableDeclaration
Handles variable declarations:
- `const { flight, rc } = inav` - Destructuring import
- `let x = 5` - Local variable
- `var latch = sticky({on: ..., off: ...})` - Sticky latch assignment

**Properties:**
- `declarations: VariableDeclarator[]`
- `kind: "const" | "let" | "var"`

#### ExpressionStatement
Wrapper for expressions used as statements.

**Properties:**
- `expression: Expression`

#### IfStatement
Conditional control flow. Transpiler converts to INAV logic conditions with activators.

**Properties:**
- `test: Expression` - Condition
- `consequent: BlockStatement | Statement` - Then branch
- `alternate: IfStatement | BlockStatement | Statement | null` - Else/else-if branch

**Example:**
```javascript
// User code:
if (flight.altitude > 1000) {
  override.throttleScale = 50;
}

// Transpiles to:
// LC0: flight.altitude > 1000  (condition)
// LC1: override.throttleScale = 50 (activated by LC0)
```

### Expression Types

```bnf
<expression> ::= <binary-expression>
               | <logical-expression>
               | <unary-expression>
               | <call-expression>
               | <member-expression>
               | <update-expression>
               | <assignment-expression>
               | <conditional-expression>
               | <literal>
               | <identifier>

<literal>    ::= <number> | <boolean> | <string>
```

#### BinaryExpression
Comparison and arithmetic operations.

**Properties:**
- `operator: BinaryOperator` (see [Operators](#2-operators))
- `left: Expression`
- `right: Expression`

**Example:**
```javascript
flight.altitude > 1000        // Comparison
gvar[0] + 5                   // Arithmetic
flight.cellVoltage === 350    // Equality
```

#### LogicalExpression
Boolean logic operations.

**Properties:**
- `operator: "&&" | "||"`
- `left: Expression`
- `right: Expression`

**Example:**
```javascript
flight.altitude > 1000 && flight.cellVoltage < 350
rc[1].high || rc[2].high
```

#### UnaryExpression
Unary operations.

**Properties:**
- `operator: "!" | "-" | "+"`
- `argument: Expression`
- `prefix: boolean`

**Example:**
```javascript
!flight.mode.failsafe    // Logical NOT
-gvar[0]                 // Negation
```

#### CallExpression
Function calls.

**Properties:**
- `callee: Expression` (usually `Identifier` or `MemberExpression`)
- `arguments: Expression[]`

**Supported functions:**
- **Event handlers:** `on.arm()`, `on.always()`
- **Helpers:** `sticky()`, `edge()`, `delay()`, `timer()`, `whenChanged()`
- **Math:** `Math.min()`, `Math.max()`, `Math.abs()`
- **Condition helpers:** `approxEqual()`, `xor()`, `nand()`, `nor()`, `delta()`
- **Mapping:** `mapInput()`, `mapOutput()`

**Example:**
```javascript
on.arm(() => { gvar[0] = 0; })
Math.max(gvar[0], gvar[1])
approxEqual(flight.altitude, 1000, 50)
```

#### MemberExpression
Property access.

**Properties:**
- `object: Expression`
- `property: Identifier | Expression`
- `computed: boolean` (true for `arr[0]`, false for `obj.prop`)

**Example:**
```javascript
flight.altitude        // object: flight, property: altitude, computed: false
gvar[0]               // object: gvar, property: 0, computed: true
rc[1].high            // nested: rc[1].high
```

#### AssignmentExpression
Assignment operations.

**Properties:**
- `operator: "=" | "+=" | "-=" | "*=" | "/="`
- `left: MemberExpression | Identifier`
- `right: Expression`

**Example:**
```javascript
gvar[0] = 100
override.throttleScale = 50
gvar[1] += 5
```

#### UpdateExpression
Increment/decrement operators.

**Properties:**
- `operator: "++" | "--"`
- `argument: Expression`
- `prefix: boolean`

**Example:**
```javascript
gvar[0]++    // Transpiles to: gvar[0] = gvar[0] + 1
++gvar[1]    // Same output (prefix/postfix not distinguished)
```

#### ConditionalExpression
Ternary operator.

**Properties:**
- `test: Expression`
- `consequent: Expression`
- `alternate: Expression`

**Example:**
```javascript
gvar[0] = flight.isArmed ? 1 : 0
override.throttleScale = (flight.cellVoltage < 350) ? 50 : 100
```

#### Identifier
Variable or property name.

**Properties:**
- `name: string`

**Example:**
```javascript
flight    // Identifier: "flight"
x         // Identifier: "x" (local variable)
```

#### Literal
Constant value.

**Properties:**
- `value: number | boolean | string | null`

**Example:**
```javascript
100       // Literal: 100
true      // Literal: true
"hello"   // Literal: "hello" (strings not fully supported)
```

---

## 2. Operators

### Comparison Operators

Used in `BinaryExpression` nodes for conditions.

| Operator | JavaScript | INAV Operation | Notes |
|----------|-----------|----------------|-------|
| `>`      | Greater than | `OPERATION.GREATER_THAN` | Native |
| `<`      | Less than | `OPERATION.LOWER_THAN` | Native |
| `===`    | Equal | `OPERATION.EQUAL` | Native |
| `>=`     | Greater or equal | `NOT(LOWER_THAN)` | Synthesized |
| `<=`     | Less or equal | `NOT(GREATER_THAN)` | Synthesized |
| `!==`    | Not equal | `NOT(EQUAL)` | Synthesized |

**Example:**
```javascript
// User writes:
if (flight.altitude >= 1000) { ... }

// Transpiles to:
// LC0: flight.altitude < 1000
// LC1: NOT(LC0)
```

### Logical Operators

Used in `LogicalExpression` and `UnaryExpression`.

| Operator | JavaScript | INAV Operation | Implementation |
|----------|-----------|----------------|----------------|
| `&&`     | Logical AND | Activator chaining | `LC1.activator = LC0` |
| `\|\|`   | Logical OR | `OPERATION.OR` | Native |
| `!`      | Logical NOT | `OPERATION.NOT` | Native |

**Special operators** (via function calls):
- `xor(a, b)` → `OPERATION.XOR`
- `nand(a, b)` → `OPERATION.NAND`
- `nor(a, b)` → `OPERATION.NOR`

**Example:**
```javascript
// AND via activator chaining:
if (a && b && c) { ... }
// LC0: a
// LC1: b (activator=0)
// LC2: c (activator=1)

// OR explicit operation:
if (a || b) { ... }
// LC0: OR(a, b)
```

### Arithmetic Operators

Used in `BinaryExpression` for value computation.

| Operator | JavaScript | INAV Operation |
|----------|-----------|----------------|
| `+`      | Addition | `OPERATION.ADD` |
| `-`      | Subtraction | `OPERATION.SUB` |
| `*`      | Multiplication | `OPERATION.MUL` |
| `/`      | Division | `OPERATION.DIV` |
| `%`      | Modulus | `OPERATION.MODULUS` |

**Example:**
```javascript
gvar[0] = gvar[1] + gvar[2] * 10
// LC0: MUL(gvar[2], 10)
// LC1: ADD(gvar[1], LC0)
// LC2: GVAR_SET(0, LC1)
```

### Assignment Operators

| Operator | JavaScript | Implementation |
|----------|-----------|----------------|
| `=`      | Simple assignment | Direct operation |
| `+=`     | Add and assign | Expand to `x = x + y` |
| `-=`     | Subtract and assign | Expand to `x = x - y` |
| `*=`     | Multiply and assign | Expand to `x = x * y` |
| `/=`     | Divide and assign | Expand to `x = x / y` |
| `++`     | Increment | Expand to `x = x + 1` |
| `--`     | Decrement | Expand to `x = x - 1` |

**Optimizations:**
```javascript
gvar[0]++              // Optimized to: GVAR_INC(0, 1)
gvar[0] = gvar[0] + 5  // Optimized to: GVAR_INC(0, 5)
gvar[0] = gvar[0] - 3  // Optimized to: GVAR_DEC(0, 3)
```

### Special Function Operators

| Function | Purpose | INAV Operation |
|----------|---------|----------------|
| `Math.min(a, b)` | Minimum | `OPERATION.MIN` |
| `Math.max(a, b)` | Maximum | `OPERATION.MAX` |
| `Math.abs(x)` | Absolute value | Computed |
| `mapInput(x, inMin, inMax, outMin, outMax)` | Map input range | `OPERATION.MAP_INPUT` |
| `mapOutput(x, inMin, inMax, outMin, outMax)` | Map output range | `OPERATION.MAP_OUTPUT` |
| `approxEqual(a, b, tolerance)` | Approximate equality | `OPERATION.APPROX_EQUAL` |
| `delta(x)` | Rate of change | `OPERATION.DELTA` |

---

## 3. Transpiler Internal Types

### Simplified INAV AST

The parser transforms Acorn AST into a simplified format used by the analyzer and code generator.

```typescript
// Top-level result
interface ParseResult {
  statements: Statement[];
  warnings: Warning[];
  variableHandler: VariableHandler;
}

// Statements
type Statement =
  | EventHandler
  | Destructuring
  | StickyAssignment
  | VariableDeclaration;

interface EventHandler {
  type: 'EventHandler';
  handler: 'on.arm' | 'on.always' | 'ifthen' | 'edge' | 'sticky' | 'delay' | 'timer';
  condition?: Condition;
  config?: { delay?: number };
  body: Action[];
  args?: Expression[];  // For helper functions
  loc: SourceLocation;
  range: [number, number];
}

interface Destructuring {
  type: 'Destructuring';
  // Represents: const { flight, rc } = inav
}

interface StickyAssignment {
  type: 'StickyAssignment';
  target: string;  // Variable name
  args: Expression[];  // sticky() arguments
}

interface VariableDeclaration {
  type: 'VariableDeclaration';
  kind: 'let' | 'const' | 'var';
  name: string;
  initValue?: number;
  initExpr?: Expression;
}

// Actions (assignments)
interface Action {
  type: 'Assignment';
  target: string;  // e.g., "gvar[0]", "override.throttleScale"
  value?: any;
  operation?: '+' | '-' | '*' | '/';
  left?: any;
  right?: any;
}

// Conditions (simplified)
interface Condition {
  type: 'BinaryExpression' | 'LogicalExpression' | 'UnaryExpression' |
        'MemberExpression' | 'Literal' | 'Identifier' | 'CallExpression' |
        'ConditionalExpression';
  operator?: string;
  left?: Condition;
  right?: Condition;
  argument?: Condition;
  value?: any;
  // ... other properties depending on type
}
```

### Code Generator Output

The code generator produces INAV Logic Condition commands.

```typescript
interface LogicCommand {
  enabled: number;        // 0 or 1
  activatorId: number;    // -1 (always) or LC index
  operation: number;      // OPERATION enum value
  operandA: Operand;
  operandB: Operand;
  flags: number;          // Bitfield
}

interface Operand {
  type: number;   // OPERAND_TYPE enum value
  value: number;  // Interpretation depends on type
}
```

**Example:**
```javascript
// User code:
if (flight.altitude > 1000) {
  override.throttleScale = 50;
}

// Generated LogicCommands:
[
  {
    enabled: 1,
    activatorId: -1,
    operation: 2,  // GREATER_THAN
    operandA: { type: 2, value: 12 },  // FLIGHT:ALTITUDE
    operandB: { type: 0, value: 1000 }, // VALUE:1000
    flags: 0
  },
  {
    enabled: 1,
    activatorId: 0,  // Activated by LC0
    operation: 23,   // OVERRIDE_THROTTLE_SCALE
    operandA: { type: 0, value: 0 },
    operandB: { type: 0, value: 50 },
    flags: 0
  }
]
```

---

## 4. INAV Logic Condition Structure

### Operand Types (`OPERAND_TYPE`)

Defines what kind of value an operand represents.

```javascript
OPERAND_TYPE = {
  VALUE: 0,        // Literal integer value
  RC_CHANNEL: 1,   // RC channel (1-18)
  FLIGHT: 2,       // Flight parameter (see FLIGHT_PARAM)
  FLIGHT_MODE: 3,  // Flight mode (see FLIGHT_MODE)
  LC: 4,           // Logic Condition result (reference to another LC)
  GVAR: 5,         // Global variable (0-7)
  PID: 6,          // PID controller output
  WAYPOINTS: 7     // Waypoint mission data
}
```

**Usage in operands:**
- `{ type: 0, value: 100 }` → Literal value 100
- `{ type: 1, value: 5 }` → RC channel 5
- `{ type: 2, value: 12 }` → `flight.altitude` (FLIGHT_PARAM.ALTITUDE = 12)
- `{ type: 4, value: 3 }` → Result of Logic Condition 3
- `{ type: 5, value: 0 }` → `gvar[0]`

### Operation Codes (`OPERATION`)

Defines what operation a Logic Condition performs.

#### Condition Operations (return boolean)

```javascript
TRUE: 0           // Always true
EQUAL: 1          // operandA === operandB
GREATER_THAN: 2   // operandA > operandB
LOWER_THAN: 3     // operandA < operandB
LOW: 4            // RC channel is LOW
MID: 5            // RC channel is MID
HIGH: 6           // RC channel is HIGH
```

#### Logical Operations

```javascript
AND: 7            // operandA && operandB (rarely used, prefer activators)
OR: 8             // operandA || operandB
XOR: 9            // operandA XOR operandB
NAND: 10          // !(operandA && operandB)
NOR: 11           // !(operandA || operandB)
NOT: 12           // !operandA
```

#### Arithmetic Operations (return number)

```javascript
ADD: 14           // operandA + operandB
SUB: 15           // operandA - operandB
MUL: 16           // operandA * operandB
DIV: 17           // operandA / operandB
MODULUS: 40       // operandA % operandB
MIN: 43           // min(operandA, operandB)
MAX: 44           // max(operandA, operandB)
```

#### Variable Operations

```javascript
GVAR_SET: 18      // gvar[operandA.value] = operandB
GVAR_INC: 19      // gvar[operandA.value] += operandB
GVAR_DEC: 20      // gvar[operandA.value] -= operandB
```

#### Override Operations (actions)

```javascript
OVERRIDE_ARMING_SAFETY: 22
OVERRIDE_THROTTLE_SCALE: 23
OVERRIDE_THROTTLE: 29
SET_VTX_POWER_LEVEL: 25
SET_VTX_BAND: 30
SET_VTX_CHANNEL: 31
SET_OSD_LAYOUT: 32
RC_CHANNEL_OVERRIDE: 38
SET_HEADING_TARGET: 39
LOITER_OVERRIDE: 41
SET_PROFILE: 42
FLIGHT_AXIS_ANGLE_OVERRIDE: 45
FLIGHT_AXIS_RATE_OVERRIDE: 46
// ... and more (see inav_constants.js)
```

#### Special Operations

```javascript
STICKY: 13        // SR latch (set/reset)
EDGE: 47          // Edge detection
DELAY: 48         // Time delay
TIMER: 49         // On/off timer
DELTA: 50         // Rate of change
APPROX_EQUAL: 51  // Approximate equality
MAP_INPUT: 36     // Map input range
MAP_OUTPUT: 37    // Map output range
```

### Flight Parameters (`FLIGHT_PARAM`)

When `operandType = FLIGHT`, the `value` field indexes into flight parameters.

```javascript
FLIGHT_PARAM = {
  ARM_TIMER: 0,           // Time since arming (s)
  HOME_DISTANCE: 1,       // Distance to home (m)
  TRIP_DISTANCE: 2,       // Total distance traveled (m)
  RSSI: 3,                // Radio signal strength (0-99)
  VBAT: 4,                // Battery voltage (cV)
  CELL_VOLTAGE: 5,        // Cell voltage (cV)
  CURRENT: 6,             // Current draw (cA)
  MAH_DRAWN: 7,           // Battery consumed (mAh)
  GPS_SATS: 8,            // GPS satellite count
  GROUND_SPEED: 9,        // Ground speed (cm/s)
  SPEED_3D: 10,           // 3D speed (cm/s)
  AIR_SPEED: 11,          // Air speed (cm/s)
  ALTITUDE: 12,           // Altitude (cm)
  VERTICAL_SPEED: 13,     // Vertical speed (cm/s)
  THROTTLE_POS: 14,       // Throttle position (0-100)
  ROLL: 15,               // Roll angle (decideg)
  PITCH: 16,              // Pitch angle (decideg)
  YAW: 40,                // Yaw angle (decideg)
  IS_ARMED: 17,           // Armed state (0/1)
  IS_FAILSAFE: 24,        // Failsafe active (0/1)
  GPS_VALID: 31,          // GPS fix valid (0/1)
  LOITER_RADIUS: 32,      // Current loiter radius (cm)
  // ... 50 total parameters (see inav_constants.js)
}
```

### Flight Modes (`FLIGHT_MODE`)

When `operandType = FLIGHT_MODE`, the `value` field indexes flight modes.

```javascript
FLIGHT_MODE = {
  FAILSAFE: 0,
  MANUAL: 1,
  RTH: 2,              // Return to Home
  POSHOLD: 3,          // Position Hold
  CRUISE: 4,
  ALTHOLD: 5,          // Altitude Hold
  ANGLE: 6,
  HORIZON: 7,
  AIR: 8,
  ACRO: 14,
  WAYPOINT_MISSION: 15,
  // ... (see inav_constants.js)
}
```

---

## 5. API Variable Types

These are the JavaScript variable types available to users.

### Read-Only Flight Data

Accessed via `flight.*` property paths.

**Source:** `api/definitions/flight.js`

```javascript
flight.altitude        // Altitude in cm (FLIGHT:ALTITUDE)
flight.cellVoltage     // Cell voltage in cV (FLIGHT:CELL_VOLTAGE)
flight.groundSpeed     // Ground speed in cm/s (FLIGHT:GROUND_SPEED)
flight.isArmed         // Armed state 0/1 (FLIGHT:IS_ARMED)
flight.isFailsafe      // Failsafe active 0/1 (FLIGHT:IS_FAILSAFE)
flight.gpsSats         // GPS satellite count (FLIGHT:GPS_SATS)
flight.gpsValid        // GPS fix valid 0/1 (FLIGHT:GPS_VALID)
flight.rssi            // Radio signal 0-99 (FLIGHT:RSSI)
flight.vbat            // Battery voltage cV (FLIGHT:VBAT)
flight.current         // Current draw cA (FLIGHT:CURRENT)
flight.mahDrawn        // Battery consumed mAh (FLIGHT:MAH_DRAWN)
flight.roll            // Roll angle decideg (FLIGHT:ROLL)
flight.pitch           // Pitch angle decideg (FLIGHT:PITCH)
flight.yaw             // Yaw angle decideg (FLIGHT:YAW)
// ... ~50 total properties
```

### Read-Only Flight Modes

Accessed via `flight.mode.*` property paths.

```javascript
flight.mode.failsafe   // Failsafe mode active
flight.mode.manual     // Manual mode active
flight.mode.rth        // Return to Home active
flight.mode.angle      // Angle mode active
flight.mode.acro       // Acro mode active
// ... (see api/definitions/flight.js)
```

### RC Channels

Accessed via `rc[N]` array syntax, where N is 1-18.

**Source:** `api/definitions/rc.js`

```javascript
rc[1].value            // RC channel value (1000-2000 µs)
rc[1].high             // Channel is HIGH (> 1750 µs)
rc[1].mid              // Channel is MID (1250-1750 µs)
rc[1].low              // Channel is LOW (< 1250 µs)

// Example:
if (rc[5].high) {
  override.vtx.power = 4;
}
```

### Global Variables (GVAR)

Writable variables for storing state. 8 variables total (0-7).

```javascript
gvar[0] = 100          // Set gvar[0] to 100
gvar[1]++              // Increment gvar[1]
gvar[2] -= 5           // Decrement by 5

// Range: -1,000,000 to +1,000,000
// Default: 0 (uninitialized)
```

### Writable Overrides

Accessed via `override.*` property paths.

**Source:** `api/definitions/override.js`

```javascript
// Throttle control
override.throttleScale = 50    // Scale to 50% (OVERRIDE_THROTTLE_SCALE)
override.throttle = 1500       // Direct throttle µs (OVERRIDE_THROTTLE)

// VTX control
override.vtx.power = 4         // Power level 0-4 (SET_VTX_POWER_LEVEL)
override.vtx.band = 5          // Band 0-5 (SET_VTX_BAND)
override.vtx.channel = 1       // Channel 1-8 (SET_VTX_CHANNEL)

// Arming
override.armSafety = 1         // Override arm safety (OVERRIDE_ARMING_SAFETY)

// OSD
override.osdLayout = 2         // Set OSD layout 0-3 (SET_OSD_LAYOUT)

// Loiter
override.loiterRadius = 5000   // Loiter radius cm (LOITER_OVERRIDE)

// Profile
override.profile = 1           // Switch profile 0-2 (SET_PROFILE)

// Flight axis overrides
override.flight.roll.angle = 20     // Roll angle override (FLIGHT_AXIS_ANGLE_OVERRIDE)
override.flight.pitch.rate = 100    // Pitch rate override (FLIGHT_AXIS_RATE_OVERRIDE)

// ... and more (see api/definitions/override.js)
```

### Waypoint Data

Accessed via `waypoint.*` property paths.

**Source:** `api/definitions/waypoint.js`

```javascript
waypoint.isWaypoint         // Currently executing waypoint mission
waypoint.index              // Current waypoint index
waypoint.action             // Current waypoint action
waypoint.nextAction         // Next waypoint action
waypoint.distance           // Distance to waypoint (cm)
waypoint.user1              // User action 1 value
waypoint.user2              // User action 2 value
// ... (see api/definitions/waypoint.js)
```

### PID Output

Accessed via `pid.*` property paths.

**Source:** `api/definitions/pid.js`

```javascript
pid.roll         // Roll PID output
pid.pitch        // Pitch PID output
pid.yaw          // Yaw PID output
// (Rarely used in Logic Conditions)
```

### Local Variables (let/const/var)

User-defined variables in JavaScript. The transpiler handles these by:
- **Substitution:** For `let` with simple expressions
- **GVAR mapping:** For `var` with numeric values

```javascript
// Substitution (inline replacement)
let threshold = 1000;
if (flight.altitude > threshold) { ... }
// Transpiles as: if (flight.altitude > 1000)

// GVAR allocation
var counter = 0;
counter++;
// Transpiles to: gvar[N] = 0; gvar[N]++
```

---

## Summary

This document provides a complete type hierarchy for the INAV transpiler:

1. **Acorn AST** - JavaScript syntax parsed by Acorn (ES2020)
2. **Simplified AST** - INAV-specific intermediate representation
3. **Operators** - Comparison, arithmetic, logical, assignment
4. **Logic Conditions** - Binary INAV firmware format
5. **API Types** - User-facing JavaScript variables

### Key Relationships

```
User JavaScript Code
  ↓ (Acorn Parser)
Acorn AST (ES2020 standard)
  ↓ (parser.js transformation)
Simplified INAV AST
  ↓ (analyzer.js validation)
Validated AST
  ↓ (codegen.js generation)
Logic Condition Commands (binary)
  ↓ (MSP protocol)
INAV Flight Controller Firmware
```

### File References

- **Parser:** `transpiler/parser.js`
- **Expression utilities:** `transpiler/expression_utils.js`
- **Analyzer:** `transpiler/analyzer.js`
- **Code generator:** `transpiler/codegen.js`
- **Condition generator:** `transpiler/condition_generator.js`
- **Action generator:** `transpiler/action_generator.js`
- **Expression generator:** `transpiler/expression_generator.js`
- **Constants:** `transpiler/inav_constants.js` (auto-generated)
- **API definitions:** `api/definitions/*.js`

---

**End of Document**
