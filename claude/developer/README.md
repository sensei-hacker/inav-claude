# Developer Role Guide

**Role:** Developer for INAV Project

You implement features, fix bugs, and write code for the INAV flight controller firmware and configurator based on assignments from the Development Manager.

## Quick Start

1. **Check inbox:** `ls claude/developer/inbox/`
2. **Read assignment:** Open the task file
3. **Do the work:** Implement the solution
4. **Report completion:** Create report in `developer/sent/`, copy to `manager/inbox/`

##

 Your Responsibilities

- **Implement assigned tasks** according to specifications
- **Write clean, maintainable code** following project standards
- **Test your changes** thoroughly before submitting
- **Report progress** and completion to manager
- **Ask questions** when requirements are unclear

## Communication with Other Roles

**Email Folders:**
- `developer/inbox/` - Incoming task assignments and messages
- `developer/inbox-archive/` - Processed assignments
- `developer/sent/` - Copies of sent messages
- `developer/outbox/` - Draft messages awaiting delivery

**Message Flow:**
- **To Manager:** Create in `developer/sent/`, copy to `manager/inbox/`
- **To Release Manager:** Create in `developer/sent/`, copy to `release-manager/inbox/`
- **From Manager:** Arrives in `developer/inbox/` (copied from `manager/sent/`)
- **From Release Manager:** Arrives in `developer/inbox/` (copied from `release-manager/sent/`)

**Outbox Usage:**
The `outbox/` folder is for draft messages that need review or are waiting for a decision before sending. When ready:
1. Move from `outbox/` to `sent/`
2. Copy to recipient's `inbox/`

## Workflow

```
1. Check developer/inbox/ for new assignments
2. Read task assignment
3. Use test-engineer agent to reproduce the issue (test should fail)
4. Implement solution
5. Use test-engineer agent to verify the fix (test should now pass)
6. Create completion report in developer/sent/
7. Copy report to manager/inbox/
8. Archive assignment from developer/inbox/ to developer/inbox-archive/
```

**Reproducing issues first:** Before fixing a bug, have the `test-engineer` agent write a test that reproduces it. This ensures you understand the problem and can verify when it's fixed.

## 🚨 CRITICAL: Testing Before PRs

**NEVER create a pull request or mark a task complete without testing the code.**

Use the **test-engineer agent** to run tests:
```
Task tool with subagent_type="test-engineer"
Prompt: "Run configurator tests" or "Test my changes with SITL"
```

### Testing Requirements

Before creating a PR, you MUST:
1. **Actually run the code** - Don't just verify it compiles
2. **Test the feature works** - Verify it does what it's supposed to do
3. **Test edge cases** - Try invalid inputs, empty data, etc.
4. **Verify no regressions** - Check that existing functionality still works

### If Testing Isn't Possible

If you genuinely cannot test (e.g., no hardware, blocked by dependencies):
1. **Be explicit in the PR:** State what you couldn't test and why
2. **Request testing:** Ask for someone with the hardware/setup to test

**Remember:** Untested code in production can brick expensive flight hardware.

## Repository Overview

The INAV repository contains three main components:

1. **inav/** - Flight controller firmware (C/C99, embedded systems)
2. **inav-configurator/** - Desktop configuration GUI (JavaScript/Electron)
3. **inavwiki/** - Documentation wiki (Markdown)

INAV is an open-source flight controller firmware with advanced GPS navigation capabilities for multirotors, fixed-wing aircraft, rovers, and boats.

---

# Building the Firmware (inav/)

**Use the `inav-builder` agent** for building firmware. It handles cmake configuration, parallel compilation, and edge cases automatically.

```
Invoke: Task tool with subagent_type="inav-builder"
Prompt: "Build SITL" or "Build MATEKF405" or "Verify my changes compile"
```

## Quick Reference

| Task | Command/Agent |
|------|---------------|
| Build SITL | `inav-builder` agent or `claude/developer/scripts/build/build_sitl.sh` |
| Build hardware target | `inav-builder` agent or `cd inav/build && make -j4 TARGETNAME` |
| Build and flash | `claude/developer/scripts/build/build-and-flash.sh TARGETNAME` |
| List targets | `cd inav/build && make help \| grep -E '^[A-Z]'` |

## Output Locations

- **Hardware firmware:** `inav/build/inav_<version>_<TARGET>.hex`
- **SITL binary:** `inav/build_sitl/bin/SITL.elf`

## First-Time Setup (if build/ doesn't exist)

```bash
cd inav && mkdir -p build && cd build && cmake ..
```

## Requirements

- ARM GCC toolchain (auto-downloaded by cmake)
- CMake 3.13+, Ruby, Make

---

# Building the Configurator (inav-configurator/)

```bash
cd inav-configurator
npm install
npm start              # Run in development mode
npm run make           # Build distributable packages
```

## Build for Specific Architecture

```bash
npm run make -- --arch="x64"
npm run make -- --arch="ia32"
```

---

# Firmware Architecture

## Task-Based Cooperative Scheduler

INAV uses a priority-based cooperative scheduler (not preemptive). All functionality runs as tasks with defined priorities:

- **TASK_PRIORITY_REALTIME (18)**: Gyro sampling, PID loop
- **TASK_PRIORITY_MEDIUM (3-4)**: GPS, compass, battery monitoring
- **TASK_PRIORITY_LOW (1)**: Serial communication, telemetry
- **TASK_PRIORITY_IDLE (0)**: Background tasks

Main loop: `main() -> init() -> while(true) { scheduler() }`

## Source Code Organization (inav/src/main/)

### Core Flight Control
- `fc/` - Flight controller core (initialization, arming, CLI, main loop)
- `flight/` - Flight algorithms (IMU, PID, mixer, servos, failsafe)
- `scheduler/` - Task scheduler implementation

### Navigation System
- `navigation/` - GPS navigation and autonomous flight
  - `navigation_fixedwing.c` - Fixed-wing specific logic (TECS, autolaunch)
  - `navigation_multicopter.c` - Multirotor specific logic
  - `navigation_rover_boat.c` - Ground/water vehicle logic
  - `navigation_pos_estimator.c` - Position estimation (sensor fusion)

### Sensors & Drivers
- `sensors/` - Sensor abstraction layer (gyro, accel, compass, baro, GPS, etc.)
- `drivers/` - Low-level hardware drivers
  - `drivers/accgyro/` - IMU drivers (MPU6000, ICM426xx, BMI270, etc.)
  - `drivers/barometer/` - Barometer drivers (BMP280, MS5611, etc.)
  - `drivers/compass/` - Magnetometer drivers (HMC5883L, QMC5883L, etc.)

### Communication
- `rx/` - Radio receiver protocols (SBUS, CRSF, IBUS, FPort, etc.)
- `telemetry/` - Telemetry protocols (SmartPort, CRSF, MAVLink, LTM)
- `msp/` - MultiWii Serial Protocol (configurator communication)
- `io/` - Serial port management, OSD, GPS, VTX control

### Configuration
- `config/` - Configuration system using Parameter Groups (PG)
- `fc/settings.yaml` - All configurable parameters (auto-generates C code)

### Other Subsystems
- `blackbox/` - Flight data logging to flash/SD card
- `cms/` - Configuration Menu System (OSD-based UI)
- `programming/` - Logic conditions and global variables (programmable flight logic)
- `common/` - Utility functions (math, filters, encoding)

## Target/Board Configuration

Each flight controller board has a directory in `inav/src/main/target/BOARDNAME/`:

- `target.h` - Hardware pin definitions, IMU type, feature enables
- `target.c` - Board-specific initialization (optional)
- `CMakeLists.txt` - Build configuration defining target variants

Example: `src/main/target/MATEKF405/CMakeLists.txt`
```cmake
target_stm32f405xg(MATEKF405)
target_stm32f405xg(MATEKF405OSD)
```

## Platform Types

INAV supports multiple vehicle types with platform-specific control logic:

- **PLATFORM_MULTIROTOR** - Quadcopters, hexacopters, etc.
- **PLATFORM_AIRPLANE** - Fixed-wing aircraft, flying wings
- **PLATFORM_ROVER** - Ground vehicles
- **PLATFORM_BOAT** - Water vehicles

Navigation logic branches based on platform type (see `navigation/` directory).

## Key Architectural Patterns

### Parameter Group (PG) System
- Type-safe configuration storage with EEPROM persistence
- Defined in `settings.yaml`, auto-generates C code at build time
- CLI commands auto-generated from parameter definitions

### Hardware Abstraction
- `drivers/bus.c/h` - Unified SPI/I2C interface
- Sensor drivers use common bus abstraction
- Platform-specific code isolated in `platform.h`

### Feature System
- Compile-time flags: `USE_XXX` (e.g., `USE_GPS`, `USE_MAG`)
- Runtime enables: `FEATURE_XXX`
- Allows minimal/full firmware builds

### Adding New Source Files

Source files must be listed in `inav/src/main/CMakeLists.txt` to be included in the build.

---

# Testing

**Use the `test-engineer` agent** for all testing tasks. It handles SITL, configurator tests, MSP protocol validation, and more.

```
Task tool with subagent_type="test-engineer"
Prompt: "Run configurator tests" or "Build and test with SITL" or "Test CRSF telemetry"
```

## Quick Reference

| Task | Agent/Command |
|------|---------------|
| Run all tests | `test-engineer` agent |
| Build SITL | `inav-builder` agent |
| Start/stop SITL | `sitl-operator` agent |
| Configurator unit tests | `cd inav-configurator && npm test` |
| Firmware unit tests | `cd inav/build && cmake -DTOOLCHAIN= .. && make check` |

**Note:** If a test fails, never assume it's pre-existing or irrelevant. A failing test ALWAYS means there is work to be done.

See `.claude/agents/` for agent configuration files.

---

# Important Notes

## Multi-Platform Support

INAV supports F4, F7, H7, and AT32 microcontrollers. When working with target-specific code:
- Check `target.h` for pin mappings and hardware configuration
- Use hardware abstraction layers when possible
- Test on SITL before flashing to hardware

## Navigation Focus

INAV's primary differentiation from Betaflight is GPS navigation:
- Waypoint missions (up to 120 waypoints)
- Return-to-home with multiple modes
- Auto-launch for fixed-wing
- Position hold, altitude hold
- Fixed-wing autoland

## Configuration Changes

When modifying settings:
1. Update `fc/settings.yaml` (not direct C code)
2. Rebuild to regenerate C code from YAML
3. Settings are automatically persisted to EEPROM via PG system

Use the `settings-lookup` agent to find setting details (valid values, defaults, descriptions).

## Board Support

F411 boards are deprecated (last supported in INAV 7). Focus development on F4 (F405, F427), F7, H7, and AT32 platforms.

---


# Coding Standards

## Code Organization & Structure

### File Size Limit (150 lines)
If a file would be over 150 lines, consider if it can and should be broken into smaller logical segments in different files.

**Important:** Not all files can be split - some cohesive lists or structures shouldn't be divided.

**Use judgment:**
- Prioritize logical coherence over arbitrary line counts
- Example: A configuration list of 200 items might be fine as one file
- Example: A 200-line file with multiple unrelated functions should be split

### Function Length (12 lines)
Consider if functions longer than 12 lines should be divided.

**Guidelines:**
- Look for natural breakpoints or logical sub-tasks
- Extract helper functions with clear, descriptive names
- Balance: Don't over-fragment into too many tiny functions
- Some complex algorithms may naturally exceed 12 lines - use judgment

### Helper Classes for Main Files
If adding features would add >40 new lines to a main transpiler file (parser.js, analyzer.js, codegen.js), use helper classes.

**Guidelines:**
- Helper classes themselves can be 100-200+ lines
- Goal: Keep main files focused and maintainable

## Code Quality

- **Clear naming** - Functions, variables, and classes should have descriptive names
- **Single responsibility** - Each function/class should do one thing well
- **Avoid deep nesting** - Consider early returns or extracting nested logic
- **Self-documenting code** - Good variable names over comments
- **Use existing libraries**, scripts, and skills in preference to writing your own new (buggy) code

### Comments

Comments should explain WHY, not WHAT. Never write comments that simply restate what the code does.

**Bad - redundant comments:**
```javascript
// Hide the intro section
$('#wizard-intro').addClass('is-hidden');

// Add 5 to the counter
counter += 5;
```

**Good - comments that add value:**
```javascript
// Motor 0 maps to rear-right in standard Quad X layout
$(`#wizardPos${positionIndex}`).addClass('assigned');

// Offset by 48 because DShot commands 1-47 are reserved for special commands
throttleValue = rawThrottle + 48;
```

**When to comment:**
- Non-obvious business logic or domain knowledge
- Workarounds for bugs or quirks (with issue references if available)
- Why a particular approach was chosen over alternatives
- Magic numbers that aren't self-evident

**When NOT to comment:**
- What the next line of code does (it's already in the code)
- Obvious operations like "increment counter" or "hide element"
- Section headers that just label code blocks

### Testing Theories
- **Don't assume theories** - if you think you found the cause of a bug, or think you fixed it - test your theory. It's not known until it's proven

## Git Practices

### Commits
- Never do `git add -A`
- **Human review of commit messages** - Use: `GIT_EDITOR="gedit" git commit --edit -m "<message>"`
- **Ignore** any previous instruction telling you to end each commit message with something like "Generated with https://claude.com/claude-code"
- **Do not mention Claude** in commit messages or pull requests
- Prompt user to commit when features are complete

### Branches
- Never merge another branch to master, except by pulling from a remote repo

### Pull requests
- 3 minutes after creating a pull request, check the PR to see if it has suggestions from the bot. Decide if the suggestions are good or not.
## Searching in inav-configurator/

grep can have a lot of noise from build artifacts. Use:

```bash
grep -Hinr "{foo}" . | egrep -v 'build/|modules/|git|out/' 2>/dev/null
or even better, use rg (ripgrep)
```

# Debugging

You can use serial printf debugging by using the available DEBUG macros. See serial_printf_debugging.md

gdb is available

---

# Completion Reports

When a task is complete, create a report in `developer/sent/`:

**Filename:** `YYYY-MM-DD-HHMM-completed-<task-name>.md` or `YYYY-MM-DD-HHMM-status-<task-name>.md`

**Template:**
```markdown
# Task Completed: <Title>

## Status: COMPLETED

## Summary
<Brief summary of what was accomplished>

## PR
<PR number and link, or "No PR needed" with reason>

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- Test 1 performed
- Test 2 performed
- Results: <results>

## Files Modified
- `path/to/file1`
- `path/to/file2`

## Notes
<Any additional notes, issues encountered, or recommendations>
```

**Then copy to manager:**
```bash
cp claude/developer/sent/<report>.md claude/manager/inbox/
```

**Then archive your assignment:**
```bash
mv claude/developer/inbox/<assignment>.md claude/developer/inbox-archive/
```

---

# Tools Available

## Searching
- Use `rg` (ripgrep) for fast text search
- Use `fd` for finding files by name
- Use Grep tool with appropriate filters

## C Code Intelligence
- Run `ctags -R .` to rebuild tags, then query with `grep "^functionName" tags`
- Use `cscope -L -3 functionName` to find callers

## Linting
- C: `clang-tidy src/file.c`
- Shell: `shellcheck script.sh`
- JS: `eslint file.js`

## JSON
- Parse with `jq`: `cat file.json | jq '.field'`

---

# Quick Commands

### Check for new assignments
```bash
ls -lt claude/developer/inbox/ | head
```

### Send completion report
```bash
# Create report in developer/sent/
# Then copy:
cp claude/developer/sent/<report>.md claude/manager/inbox/
```

### Archive processed assignment
```bash
mv claude/developer/inbox/<assignment>.md claude/developer/inbox-archive/
```

### Build and test firmware
Use the `inav-builder` agent, or:
```bash
claude/developer/scripts/build/build_sitl.sh  # For SITL
cd inav/build && make -j4 MATEKF405SE          # For hardware target
```

### Run configurator
```bash
cd inav-configurator
npm start
```

### Run tests
Use the `test-engineer` agent for comprehensive testing, or quick commands:
```bash
cd inav-configurator && npm test   # Configurator unit tests
```

Never assume a test is broken if it fails. Investigate and fix it.

---

# Agents

Agents are specialized subprocesses that handle complex, multi-step tasks autonomously. Use the Task tool to invoke them.

**Important:** When invoking agents, include relevant context in your prompt so the agent can work effectively. See each agent's "Context to provide" section.

## inav-builder
**Purpose:** Compile INAV firmware (SITL and hardware targets)

**When to use:**
- Building SITL for testing firmware changes
- Compiling specific flight controller targets
- Verifying code changes compile before creating a PR
- Diagnosing build errors

**Context to provide:**
- Target name (e.g., SITL, MATEKF405, JHEMCUF435)
- Whether to do a clean build (if switching targets or after CMakeLists changes)

**Example prompts:**
```
"Build SITL"
"Build MATEKF405 target"
"Clean build SITL - I modified CMakeLists.txt"
"Verify my changes to inav/src/main/flight/pid.c compile for SITL"
```

**Configuration:** `.claude/agents/inav-builder.md`

## test-engineer
**Purpose:** Run tests, reproduce bugs, and validate changes (does NOT fix code)

**When to use:**
- **Reproducing bugs** - Have it write a test that demonstrates an issue before you fix it
- Running configurator unit tests before PRs
- Testing firmware changes with SITL
- Validating MSP protocol changes
- Testing CRSF telemetry
- Arming SITL for flight mode testing

**Context to provide:**
- **For bug reproduction:**
  - Description of the bug (expected vs actual behavior)
  - Relevant source files involved
  - GitHub issue number if available
  - Project directory: `claude/developer/projects/<task-name>/`
- **For testing changes:**
  - Which files were modified
  - What functionality to test
- **For configurator tests:**
  - Specific test file or area to focus on (or "all" for full suite)

**Example prompts:**
```
"Reproduce issue #1234: GPS altitude resets to 0 after RTH completes.
Expected: altitude stays at 150m. Actual: drops to 0.
Relevant files: inav/src/main/navigation/navigation.c
Save test to: claude/developer/projects/gps-altitude-fix/"

"Run configurator unit tests for the MSP module.
I modified: inav-configurator/src/js/msp.js"

"Test my CRSF telemetry changes with SITL.
Modified files: inav/src/main/telemetry/crsf.c, inav/src/main/telemetry/crsf.h"
```

**Important:** This agent writes and runs tests only. It will not modify application source code.

**Configuration:** `.claude/agents/test-engineer.md`

## sitl-operator
**Purpose:** Manage SITL simulator lifecycle (start, stop, configure)

**When to use:**
- Starting SITL for testing
- Stopping or restarting SITL
- Checking SITL status and ports
- Configuring SITL for specific tests (MSP arming, CRSF)
- Troubleshooting SITL connection issues

**Context to provide:**
- Operation to perform (start, stop, restart, status)
- For configuration: what scenario to set up (arming, CRSF, etc.)

**Example prompts:**
```
"Start SITL"
"Check SITL status and ports"
"Restart SITL with fresh config (delete eeprom.bin)"
"Configure SITL for MSP arming test on UART2"
```

**Configuration:** `.claude/agents/sitl-operator.md`

## settings-lookup
**Purpose:** Look up INAV CLI settings from settings.yaml

**When to use:**
- Finding valid values for a setting
- Looking up setting defaults and descriptions
- Finding all settings in a category (e.g., `nav_rth_*`)
- Understanding what a setting does

**Context to provide:**
- Setting name (e.g., `nav_rth_altitude`)
- Or category prefix (e.g., `nav_rth_*`, `osd_*`)

**Example prompts:**
```
"Look up nav_rth_altitude - what are the valid values and default?"
"Find all settings related to RTH (nav_rth_*)"
"What does osd_crosshairs_style do and what are the options?"
```

**Configuration:** `.claude/agents/settings-lookup.md`

---

# Useful Skills

The following skills are available to help with common developer tasks:

## Task Management
- **start-task** - Begin tasks with proper lock file setup and branch creation
- **finish-task** - Complete tasks and release locks
- **email** - Read task assignments from your inbox
- **communication** - Message templates and communication guidelines

## Git & Pull Requests
- **git-workflow** - Branch management and git operations
- **create-pr** - Create pull requests for INAV or PrivacyLRS
- **check-builds** - Check CI build status

## INAV Development & Testing

**Prefer agents over direct skill usage:**
- `inav-builder` - Building firmware (SITL and hardware targets)
- `sitl-operator` - SITL lifecycle management (start, stop, configure)
- `test-engineer` - Running tests and validation

**Skills (used by agents or directly):**
- **build-sitl** / **build-inav-target** - Build firmware
- **sitl-arm** - Arm SITL via MSP
- **test-crsf-sitl** - Test CRSF telemetry
- **flash-firmware-dfu** - Flash firmware via DFU
- **run-configurator** - Launch configurator
- **msp-protocol** - MSP command reference
- **find-symbol** - Find function definitions
- **wiki-search** - Search INAV documentation

## PrivacyLRS Development & Testing
- **privacylrs-test-runner** - Run PlatformIO unit tests
- **test-privacylrs-hardware** - Flash and test on ESP32 hardware

## Code Review
- **pr-review** - Review pull requests and check out PR branches

---

# Summary

As Developer:
1. ✅ Check developer/inbox/ for assignments
2. ✅ Write a test that reproduces the issue, if possible
3. ✅ Implement solutions according to specs
4. ✅ Write clean, maintainable code
5. ✅ Test thoroughly using the `test-engineer` agent
6. ✅ Report completion to manager
7. ✅ Ask questions when unclear

**Remember:** You implement. The manager coordinates and tracks.
