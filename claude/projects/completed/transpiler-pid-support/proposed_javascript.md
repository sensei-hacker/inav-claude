const { flight, override, rc, gvar, edge, sticky, pid } = inav;

// Variable declarations
let latch1; // logicCondition[2] - sticky/timer state
let latch2; // logicCondition[25] - sticky/timer state
let latch3; // logicCondition[33] - sticky/timer state

if (flight.gpsValid === 1) {
  latch1 = sticky({
    on: () => flight.groundSpeed > 1000,
    off: () => flight.isArmed === 0
  });
  if (latch1) {
    if (flight.isAutoLaunch === 0) {
      if (rc[11] > 1480) {
        latch2 = sticky({
          on: () => gvar[0],
          off: () => flight.airSpeed > (50 * 28)
        });
        latch3 = sticky({
          on: () => edge(rc[11] > 1480, 100),
          off: () => flight.gpsValid === 0 || delta(rc[4], 90) || flight.isLanding === 1
        });
        if (latch3) {
          if (flight.speed3d > flight.airSpeed) {
            if (flight.airSpeed < (50 * 28)) {
              gvar[0] = gvar[0] + ((50 * 28) - flight.airSpeed);
            }
          }
          if (!latch2) {
            gvar[0] = (Math.min(110, Math.max(0, Math.round((rc[12] - 1000) * 110 / 1000))) * 28);
          }
          override.throttle = Math.max(Math.min(1800, ((pid[3].output + 3000) / 2)), Math.max(1250, Math.min(1800, ((pid[3].output + 3000) / 2))));
          if (flight.mode.poshold === 1 || rc[11].high) {
            gvar[1] = flight.airSpeed;
          }
          if (!gvar[1]) {
            gvar[1] = flight.speed3d;
          }
        }
      }
    }
  }
}

