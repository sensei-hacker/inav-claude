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

- [ ] Update documentation
  - [ ] Find GPS documentation (docs/Gps.md or similar)
  - [ ] Add note about Galileo enabled by default
  - [ ] Explain benefits
  - [ ] Document how to disable if needed

## Phase 3: GPS Update Rate Decision (45-60 minutes)

### Research-Based Decision

- [ ] Document Jetrell's findings
  - [ ] What hardware was tested?
  - [ ] What rates were compared?
  - [ ] What metrics improved at 8Hz?
  - [ ] Any downsides noted?

- [ ] Analyze evidence
  - [ ] Is 8Hz better universally or hardware-specific?
  - [ ] What is community consensus?
  - [ ] What do experienced users run?
  - [ ] Any known issues with 10Hz?

- [ ] Choose implementation path
  - [ ] Option A: Change default to 8Hz for all M7+
  - [ ] Option B: Keep 10Hz, document 8Hz option
  - [ ] Option C: Hardware-specific rates (8Hz M8/M9, 10Hz M10)
  - [ ] Document decision rationale

### If Implementing Rate Change

- [ ] Modify rate configuration code
  - [ ] Edit inav/src/main/io/gps_ublox.c
  - [ ] Update configureRATE() calls
  - [ ] Add comments explaining choice
  - [ ] Handle hardware detection properly

- [ ] Test build
  - [ ] Verify compilation
  - [ ] Check rate is applied correctly
  - [ ] Test with multiple targets

- [ ] Update documentation
  - [ ] Document new default rate
  - [ ] Explain rationale
  - [ ] Note how to change if needed
  - [ ] Add to GPS documentation

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
  - [ ] Monitor GPS fix quality
  - [ ] Check for any issues

- [ ] Documentation review
  - [ ] CLI help text accurate
  - [ ] Documentation reflects changes
  - [ ] Examples are correct
  - [ ] No outdated information

## Phase 5: Pull Request

- [ ] Commit changes
  - [ ] Stage all modified files
  - [ ] Write clear commit message
  - [ ] Reference analysis document
  - [ ] Cite Jetrell's testing
  - [ ] Explain rationale

- [ ] Create PR
  - [ ] Write comprehensive description
  - [ ] Reference analysis document
  - [ ] Include Jetrell's findings
  - [ ] Explain benefits
  - [ ] Note backward compatibility
  - [ ] Request community testing

- [ ] PR quality check
  - [ ] All files included
  - [ ] No unrelated changes
  - [ ] Documentation updated
  - [ ] Build succeeds in CI

## Phase 6: Completion Report

- [ ] Document findings
  - [ ] Summarize Jetrell's testing
  - [ ] Document decisions made
  - [ ] Note any trade-offs
  - [ ] Record testing performed

- [ ] Report to manager
  - [ ] Completion email with summary
  - [ ] Link to PR
  - [ ] Note any follow-up needed
  - [ ] Request feedback if uncertain

- [ ] Update project status
  - [ ] Mark todos complete
  - [ ] Archive project notes
  - [ ] Clean up working files

## Key Questions to Answer

- [ ] What did Jetrell test specifically?
- [ ] Why is 8Hz potentially better than 10Hz?
- [ ] Is this universal or hardware-specific?
- [ ] What does u-blox documentation recommend?
- [ ] What do experienced users run?
- [ ] Are there any risks to changing the rate?

## Notes

**Priority:**
1. Galileo enable - clear win, do it
2. GPS rate - research first, then decide

**Don't guess on GPS rate** - find evidence, make informed decision

**Both changes maintain backward compatibility** - users can revert via CLI
