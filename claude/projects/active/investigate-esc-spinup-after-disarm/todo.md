# Todo List: Investigate ESC Motor Spinup After Disarm

## Phase 1: Issue Analysis

- [ ] Read Issue #10913
  - [ ] Read complete description
  - [ ] Note all symptoms
  - [ ] Check for video/log evidence
  - [ ] Note ESC type and protocol
  - [ ] Note timing (seconds after disarm)
  - [ ] Note trigger (switch, timeout, etc.)
  - [ ] Read all comments

- [ ] Read Issue #9441
  - [ ] Read Pawel's explanation
  - [ ] Understand EEPROM blocking
  - [ ] Note workarounds mentioned
  - [ ] Check if issue closed/fixed
  - [ ] Read related comments

- [ ] Search for related issues
  - [ ] "motor spin disarm"
  - [ ] "ESC reboot"
  - [ ] "EEPROM blocking"
  - [ ] Document findings

## Phase 2: EEPROM Investigation

- [ ] Find EEPROM save operations
  - [ ] Search for saveEEPROM
  - [ ] Search for writeEEPROM
  - [ ] Search for config_streamer
  - [ ] Document all save locations

- [ ] Analyze EEPROM timing
  - [ ] When does save occur on disarm?
  - [ ] What triggers save?
  - [ ] How long does save take?
  - [ ] Is it truly blocking?
  - [ ] Are interrupts disabled?

- [ ] Check what gets saved on disarm
  - [ ] Flight statistics?
  - [ ] Configuration?
  - [ ] Blackbox data?
  - [ ] Other data?

## Phase 3: Motor Output Investigation

- [ ] Find motor output code
  - [ ] Locate mixer code
  - [ ] Locate PWM output code
  - [ ] Locate DSHOT code
  - [ ] Document key functions

- [ ] Analyze disarm sequence
  - [ ] How is disarmed state set?
  - [ ] What happens to motor outputs?
  - [ ] Are outputs explicitly zeroed?
  - [ ] Are pins set to known state?

- [ ] Analyze output during EEPROM save
  - [ ] Does DSHOT signal continue?
  - [ ] What happens to PWM?
  - [ ] Are pins held in any state?
  - [ ] Check interrupt behavior

## Phase 4: Other Causes Investigation

- [ ] Check disarm timing
  - [ ] Delay between command and stop?
  - [ ] Arming state effect immediate?

- [ ] Check ESC protocol edge cases
  - [ ] DSHOT special commands?
  - [ ] ESC telemetry interactions?
  - [ ] Bidirectional DSHOT?

- [ ] Check interrupt/timing issues
  - [ ] High-priority interrupts?
  - [ ] Scheduler issues?
  - [ ] Task priorities?

- [ ] Check ESC-specific behavior
  - [ ] Motor spin on signal loss?
  - [ ] ESC reboot behavior?
  - [ ] ESC startup sequences?

- [ ] Check configuration issues
  - [ ] Motor idle settings
  - [ ] Min throttle settings
  - [ ] ESC protocol settings

## Phase 5: Code Analysis

- [ ] Analyze fc_core.c
  - [ ] Find disarm sequence
  - [ ] Check if EEPROM save in path
  - [ ] Document flow

- [ ] Analyze config_streamer.c
  - [ ] Understand blocking behavior
  - [ ] Check interrupt status
  - [ ] Measure save duration

- [ ] Analyze mixer.c
  - [ ] How disarm affects outputs
  - [ ] Check output zeroing
  - [ ] Verify pin states

- [ ] Analyze DSHOT driver
  - [ ] Frame generation during block
  - [ ] Special disarm commands
  - [ ] Signal continuity requirements

## Phase 6: Root Cause Determination

- [ ] Compile all findings
- [ ] Determine if EEPROM is cause
- [ ] Identify any other causes
- [ ] Document root cause analysis
- [ ] Create timing diagram if helpful

## Phase 7: Solution Design

- [ ] If EEPROM is cause:
  - [ ] Evaluate Option A (hold pins low)
  - [ ] Evaluate Option B (non-blocking)
  - [ ] Evaluate Option C (defer save)
  - [ ] Choose best option
  - [ ] Design implementation

- [ ] If other cause:
  - [ ] Design appropriate fix
  - [ ] Consider edge cases
  - [ ] Plan implementation

## Phase 8: Implementation (If Proceeding)

- [ ] Implement chosen fix
  - [ ] Write code
  - [ ] Add comments
  - [ ] Handle edge cases
  - [ ] Ensure compatibility

- [ ] Add safety measures
  - [ ] Explicit pin control
  - [ ] State verification
  - [ ] Error handling

## Phase 9: Testing (If Possible)

- [ ] Build firmware with fix
- [ ] Test on hardware
  - [ ] Disarm via switch
  - [ ] Disarm via timeout
  - [ ] After flight (stats save)
  - [ ] Without flight
  - [ ] Different ESC protocols

- [ ] Verify fix
  - [ ] No motor spinup
  - [ ] Pins stay low
  - [ ] DSHOT behavior correct
  - [ ] No new issues

## Phase 10: Documentation

- [ ] Create investigation report
  - [ ] Root cause analysis
  - [ ] Code locations
  - [ ] Timing analysis
  - [ ] Proposed fix
  - [ ] Safety considerations
  - [ ] Testing approach

- [ ] If fix implemented:
  - [ ] Document code changes
  - [ ] Create test plan
  - [ ] Write PR description

## Completion

- [ ] Investigation complete
- [ ] Root cause identified
- [ ] Fix proposed (or implemented)
- [ ] Report created
- [ ] Send completion report to manager
