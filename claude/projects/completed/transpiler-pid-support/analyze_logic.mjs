import { OPERATION, OPERAND_TYPE } from "./js/transpiler/transpiler/inav_constants.js";

const logicLines = `
logic 0 1 -1 1 2 31 0 1 0
logic 1 1 0 2 2 9 0 1000 0
logic 2 1 0 13 4 1 4 3 0
logic 3 1 -1 1 2 17 0 0 0
logic 4 1 2 14 2 11 0 0 0
logic 5 1 2 14 2 10 0 0 0
logic 12 1 -1 1 2 31 0 0 0
logic 20 1 -1 16 0 50 0 28 0
logic 21 1 33 2 4 5 4 4 0
logic 22 1 21 3 4 4 4 20 0
logic 23 1 22 15 4 20 4 4 0
logic 24 1 23 19 0 0 4 23 0
logic 25 1 27 13 4 24 4 26 0
logic 26 1 25 2 4 4 4 20 0
logic 27 1 53 2 1 11 0 1480 0
logic 28 1 -1 47 4 27 0 100 0
logic 29 1 -1 50 1 4 0 90 0
logic 30 1 -1 1 2 23 0 1 0
logic 31 1 -1 8 4 12 4 29 0
logic 32 1 -1 8 4 31 4 30 0
logic 33 1 27 13 4 28 4 32 0
logic 34 1 33 12 4 25 0 0 0
logic 35 1 34 15 1 12 0 1000 0
logic 36 1 35 37 4 35 0 110 0
logic 37 1 36 16 4 36 0 28 0
logic 38 1 37 18 0 0 4 37 0
logic 39 1 33 14 6 3 0 3000 0
logic 40 1 33 17 4 39 0 2 0
logic 41 1 33 43 0 1800 4 40 0
logic 42 1 33 44 0 1250 4 41 0
logic 43 1 33 44 4 41 4 42 0
logic 44 1 33 29 4 43 0 0 0
logic 45 1 33 17 4 43 0 10 0
logic 46 1 33 15 4 45 0 100 0
logic 47 1 -1 1 3 3 0 1 0
logic 48 1 33 6 1 11 0 0 0
logic 49 1 33 8 4 47 4 48 0
logic 50 1 49 18 0 1 4 4 0
logic 51 1 33 12 4 50 0 0 0
logic 52 1 51 18 0 1 4 5 0
logic 53 1 2 1 2 18 0 0 0
`.trim().split("\n");

const opNames = {
  0: "TRUE", 1: "EQUAL", 2: "GT", 3: "LT", 4: "LOW", 5: "MID", 6: "HIGH",
  7: "AND", 8: "OR", 9: "XOR", 10: "NAND", 11: "NOR", 12: "NOT", 13: "STICKY",
  14: "ADD", 15: "SUB", 16: "MUL", 17: "DIV", 18: "GVAR_SET", 19: "GVAR_INC",
  20: "GVAR_DEC", 21: "PORT_SET", 22: "OVERRIDE_ARM", 23: "OVERRIDE_THROTTLE_SCALE",
  24: "SWAP_ROLL_YAW", 25: "VTX_POWER", 26: "INVERT_ROLL", 27: "INVERT_PITCH",
  28: "INVERT_YAW", 29: "OVERRIDE_THROTTLE", 30: "VTX_BAND", 31: "VTX_CHANNEL",
  32: "OSD_LAYOUT", 33: "SIN", 34: "COS", 35: "TAN", 36: "MAP_IN", 37: "MAP_OUT",
  38: "RC_OVERRIDE", 39: "HEADING_TARGET", 40: "MOD", 41: "LOITER_OVERRIDE",
  42: "SET_PROFILE", 43: "MIN", 44: "MAX", 45: "AXIS_ANGLE", 46: "AXIS_RATE",
  47: "EDGE", 48: "DELAY", 49: "TIMER", 50: "DELTA", 51: "APPROX_EQ"
};

const typeNames = {
  0: "VAL", 1: "RC", 2: "FLT", 3: "MODE", 4: "LC", 5: "GVAR", 6: "PID", 7: "WP"
};

console.log("Idx | Act | Operation        | OpA          | OpB          | Notes");
console.log("----|-----|------------------|--------------|--------------|------");

for (const line of logicLines) {
  const parts = line.split(" ");
  if (parts[0] !== "logic") continue;

  const idx = parts[1].padStart(3);
  const act = parts[3].padStart(3);
  const op = opNames[parts[4]] || parts[4];
  const opAType = typeNames[parts[5]] || parts[5];
  const opAVal = parts[6];
  const opBType = typeNames[parts[7]] || parts[7];
  const opBVal = parts[8];

  let opA = opAType + ":" + opAVal;
  let opB = opBType + ":" + opBVal;

  const actionOps = [18, 19, 20, 21, 22, 23, 29, 38, 41, 45, 46];
  const isAction = actionOps.includes(parseInt(parts[4]));

  console.log(idx + " | " + act + " | " + op.padEnd(16) + " | " + opA.padEnd(12) + " | " + opB.padEnd(12) + " | " + (isAction ? "ACTION" : ""));
}
