# Todo List: Enable Galileo and Optimize GPS Rate

## Phase 1: Research (30 minutes)

- [ ] Find Jetrell's GPS testing results
  - [ ] Search INAV GitHub issues for "jetrell", "gps rate", "8hz"
  - [ ] Search INAV Discord if accessible
  - [ ] Check RC Groups INAV thread
  - [ ] Check INAV pull requests related to GPS
  - [ ] Document findings in project notes

- [ ] Review current GPS rate implementation
  - [ ] Read gps_ublox.c rate configuration code
  - [ ] Understand how gps_ublox_nav_hz setting works
  - [ ] Note any existing comments about rate selection
  - [ ] Check if there are hardware-specific rates already

- [ ] Understand the trade-offs
  - [ ] Why would 8Hz be better than 10Hz?
  - [ ] Is this hardware-specific? (M8 vs M9 vs M10)
  - [ ] What metrics matter? (CPU, accuracy, reliability)
  - [ ] Check u-blox documentation for rate recommendations

## Phase 2: Enable Galileo (45 minutes)

- [ ] Modify default setting
  - [ ] Edit inav/src/main/fc/settings.yaml
  - [ ] Find gps_ublox_use_galileo setting (around line 1730-1786)
  - [ ] Change default_value from OFF to ON
  - [ ] Update description if needed

- [ ] Verify implementation
  - [ ] Check if code handles Galileo enable correctly
  - [ ] Review gps_ublox.c GNSS configuration code
  - [ ] Ensure M8+ detection works properly
  - [ ] Verify backward compatibility (CLI can disable)

- [ ] Test build
  - [ ] Build test target: ./build.sh MATEKF405
  - [ ] Verify compilation succeeds
  - [ ] Check generated defaults file
  - [ ] Build second target to verify consistency

## Phase 3: GPS Update Rate Decision (45-60 minutes)

### Research-Based Decision

- [ ] Document Jetrell's findings
  - [ ] What hardware was tested?
  - [ ] What rates were compared?
  - [ ] What metrics improved at 8Hz?
  - [ ] Any downsides noted?

- [ ] Choose implementation path
  - [ ] Option A: Change default to 8Hz for all M7+
  - [ ] Option B: Keep 10Hz, document 8Hz option
  - [ ] Option C: Hardware-specific rates (8Hz M8/M9, 10Hz M10)
  - [ ] Document decision rationale

## Phase 4: Testing (30 minutes)

- [ ] Build verification
  - [ ] Build at least 2 targets successfully
  - [ ] Check defaults are correct (Galileo ON)
  - [ ] Verify GPS rate setting if changed
  - [ ] No compilation warnings

- [ ] Hardware testing (if available)
  - [ ] Flash to board with M8+ GPS
  - [ ] Verify Galileo enabled automatically
  - [ ] Check satellite count increases
  - [ ] Verify GPS rate via CLI

## Phase 5: Pull Request

- [ ] Commit changes
  - [ ] Stage all modified files
  - [ ] Write clear commit message
  - [ ] Reference analysis document
  - [ ] Explain rationale

- [ ] Create PR
  - [ ] Write comprehensive description
  - [ ] Include testing results
  - [ ] Request community testing

## Completion

- [ ] Code compiles successfully
- [ ] Documentation updated
- [ ] PR created
- [ ] Completion report sent to manager
