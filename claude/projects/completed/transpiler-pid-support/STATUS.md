# Transpiler PID Support - Status

## Branch
`decompiler-pid` in inav-configurator

## Commits Made
1. `638525f8e` - Add PID operand support for transpiler compile/decompile
2. `1fac90a72` - Fix decompiler handling of value computations vs boolean conditions

## Uncommitted Changes
Major refactor to tree-based decompilation in `decompiler.js`:
- Added `buildConditionTree()`, `decompileTree()`, `decompileWithTrees()`
- Added `detectSpecialPatternForNode()`, `renderSpecialPattern()`, `renderSpecialPatternWithCode()`
- Added `getDirectChildren()`, `describeActionForCondition()`
- Proper nested if statements instead of one giant if
- Fixed empty special pattern blocks (sticky with no meaningful children)
- Fixed NOT operator precedence for complex operands
- Simplified arithmetic (`+ 0`, `- 0`, `* 1`, `/ 1`)
- EDGE/DELAY operations inline with timing comments
- GVAR action refs show variable names instead of `logicCondition[N]`

## Current Output (jetrell-logic.txt)
```javascript
if (flight.gpsValid === 1) {
  sticky(() => flight.groundSpeed > 1000, () => flight.isArmed === 0, () => {
    if (flight.isAutoLaunch === 0) {
      if (rc[11] > 1480) {
        sticky(() => rc[11] > 1480 /* edge 100ms */, () => flight.gpsValid === 0 || /* delta(...) */ true || flight.isLanding === 1, () => {
          if (flight.speed3d > flight.airSpeed) {
            if (flight.airSpeed < (50 * 28)) {
              gvar[0] = gvar[0] + ((50 * 28) - flight.airSpeed);
            }
          }
          if (!logicCondition[25]) {
            gvar[0] = (Math.min(110, Math.max(0, Math.round((rc[12] - 1000) * 110 / 1000))) * 28);
          }
          override.throttle = Math.max(Math.min(1800, ((pid[3].output + 3000) / 2)), ...);
          if (flight.mode.poshold === 1 || rc[11].high) {
            gvar[1] = flight.airSpeed;
          }
          if (!gvar[1]) {
            gvar[1] = flight.speed3d;
          }
        });
      }
    }
  });
}
```

## What Works
- PID operands compile/decompile correctly: `pid[0]` through `pid[3]`
- Tree-based nesting produces proper nested if/sticky blocks
- Value computations (ADD, MUL, etc.) properly inlined
- OVERRIDE_THROTTLE uses correct operand (operandA)
- Boolean vs value operation distinction
- Empty special pattern blocks skipped
- Arithmetic simplification (`+ 0` etc.)
- EDGE/DELAY inlining with timing comments
- GVAR action references show variable names
- NOT operator properly parenthesizes complex operands

## Remaining Issues
1. **`logicCondition[25]`** - STICKY refs can't be inlined (state-based, acceptable)
2. **`/* delta(...) */ true`** - DELTA shows as comment+true (acceptable workaround)

## Test Files
- `inav-configurator/test_jetrell_decompile.mjs` - Test runner
- `inav-configurator/analyze_logic.mjs` - Parses and displays LC structure
- `claude/projects/transpiler-pid-support/jetrell-logic.txt` - Test data

## Next Steps
1. Commit tree-based decompiler changes
2. Optional: Better DELTA rendering
3. Optional: Add comments explaining what `logicCondition[N]` references
