# Task Assignment: Document GPS Testing Tools

**Date:** 2025-12-27
**Project:** inav (firmware) - GPS Testing Infrastructure
**Priority:** Medium
**Estimated Effort:** 2-3 hours

## Task

Create comprehensive documentation (`README.md`) for the GPS testing tools in `claude/test_tools/inav/gps/` that serves as the main entry point for understanding and using all the scripts and tools in that directory.

## Objectives

### 1. Create Main README.md

**Location:** `claude/test_tools/inav/gps/README.md`

**Purpose:** Provide comprehensive overview and quick reference for all GPS testing scripts and tools

**Structure:**

```markdown
# GPS Testing Tools

[Overview paragraph - what this directory contains and what it's used for]

## Quick Start Guide

[Most common workflows and use cases]

## Tools and Scripts Overview

### Motion Simulation
- test_motion_simulator.sh
- simulate_gps_fluctuation_issue_11202.py
- simulate_altitude_motion.py
- inject_gps_altitude.py

### GPS Testing Scripts
- gps_recovery_test.py
- gps_rth_bug_test.py
- gps_rth_test.py
- gps_test_v6.py
- gps_with_naveph_logging.py
- gps_with_naveph_logging_mspapi2.py
- gps_with_rc_keeper.py

### Configuration Scripts
- configure_fc_blackbox.py
- configure_fc_msp_rx.py
- configure_sitl_blackbox_file.py
- configure_sitl_blackbox_serial.py
- configure_sitl_for_arming.py
- configure_sitl_gps.py
- enable_blackbox_feature.py
- enable_blackbox.py

### Monitoring and Utilities
- monitor_gps_status.py
- check_gps_config.py
- test_gps_read.py
- set_gps_provider_msp.py
- benchmark_msp2_debug_rate.py

### Test Runners
- run_gps_blackbox_test.sh

## Detailed Tool Documentation

[Detailed documentation for each tool...]

## Related Documentation

[Links to other README files in this directory]
```

### 2. Pay Special Attention to test_motion_simulator.sh

**Current file:** `claude/test_tools/inav/gps/test_motion_simulator.sh`

**What it does:**
- Orchestrates motion simulation testing
- Starts CRSF RC sender (keeps SITL active + receives telemetry)
- Starts GPS altitude injection via MSP (separate script)
- Waits for both processes to complete
- Displays telemetry results

**Document:**
- Purpose and workflow
- How it coordinates multiple processes
- Dependencies (crsf_rc_sender.py, inject_gps_altitude.py)
- Usage examples with different profiles
- How to interpret the results
- Log file locations and contents
- What the telemetry output means

**Example usage:**
```bash
# Run with default climb profile for 20 seconds
./test_motion_simulator.sh

# Run descent profile for 30 seconds
./test_motion_simulator.sh descent 30

# Available profiles:
# - climb: 0m to 100m at 5 m/s
# - descent: 100m to 0m at 2 m/s
# - hover: constant 50m
# - sine: oscillating ±30m around 50m
```

### 3. Reference Existing Documentation

**Existing documentation files:**
- `README_GPS_BLACKBOX_TESTING.md` - Comprehensive blackbox testing workflow
- `BLACKBOX_SERIAL_WORKFLOW.md` - Serial blackbox logging
- `HIGH_FREQUENCY_LOGGING_STATUS.md` - High-frequency logging status
- `MSP2_INAV_DEBUG_FIX.md` - MSP2 debug fixes
- `MSP_QUERY_RATE_ANALYSIS.md` - Query rate analysis

**The new README.md should:**
- Reference these existing docs where appropriate
- Not duplicate their content
- Provide overview of what each covers
- Help users find the right documentation for their use case

### 4. Organize by Use Case

**Example use cases to document:**

1. **Testing GPS navigation (RTH, position hold)**
   - Which scripts to use
   - Typical workflow
   - Expected results

2. **Investigating GPS signal issues (Issue #11202)**
   - simulate_gps_fluctuation_issue_11202.py
   - How to reproduce GPS fluctuation
   - What to look for in logs

3. **Motion simulation and telemetry testing**
   - test_motion_simulator.sh
   - inject_gps_altitude.py
   - CRSF telemetry validation

4. **Blackbox logging GPS data**
   - Reference README_GPS_BLACKBOX_TESTING.md
   - Quick start example
   - Common issues

5. **Configuring SITL for GPS testing**
   - Configuration scripts overview
   - One-time setup vs per-test configuration
   - EEPROM persistence

## Investigation Steps

### Step 1: Read Existing Documentation

Read all existing README files to understand:
- What's already documented
- Documentation style and format
- Level of detail provided
- What gaps exist

### Step 2: Analyze Scripts

For each script in the directory:
- Read the script to understand its purpose
- Identify dependencies
- Document usage patterns
- Note command-line options
- Identify related scripts (workflows)

### Step 3: Identify Script Categories

Group scripts by:
- **Purpose:** Motion simulation, configuration, testing, monitoring
- **Target:** SITL vs hardware FC
- **Dependencies:** What other scripts/tools they require
- **Workflow:** Which scripts work together

### Step 4: Create Main README.md

Write comprehensive documentation that:
- Provides quick start examples
- Explains the overall testing infrastructure
- Documents each tool/script
- Shows common workflows
- References specialized documentation
- Includes troubleshooting section

## Expected Deliverables

### 1. Main README.md

**Location:** `claude/test_tools/inav/gps/README.md`

**Content:**
- Overview of GPS testing infrastructure
- Quick start guide with common examples
- Comprehensive tool/script reference
- Use case workflows
- Dependencies and prerequisites
- Troubleshooting section
- Links to related documentation

### 2. Enhanced test_motion_simulator.sh Documentation

Include in the main README:
- Detailed explanation of the orchestration workflow
- How the two processes (CRSF RC + GPS injection) coordinate
- Timing considerations (why 3-second delay for connection)
- How to interpret telemetry results
- Log file analysis
- Examples with each profile type

### 3. Quick Reference Table

Create a table summarizing all scripts:

| Script | Purpose | Dependencies | Usage |
|--------|---------|--------------|-------|
| test_motion_simulator.sh | Motion simulation orchestrator | crsf_rc_sender.py, inject_gps_altitude.py | `./test_motion_simulator.sh climb 30` |
| simulate_gps_fluctuation_issue_11202.py | Reproduce GPS fluctuation issue | mspapi2 | `python3 simulate_gps_fluctuation_issue_11202.py` |
| ... | ... | ... | ... |

## Success Criteria

- [ ] Created comprehensive README.md as main entry point
- [ ] Documented all scripts in the directory
- [ ] Special attention given to test_motion_simulator.sh with detailed workflow explanation
- [ ] Referenced existing specialized documentation appropriately
- [ ] Organized by use case for easy navigation
- [ ] Included quick start examples
- [ ] Added script reference table
- [ ] Provided troubleshooting guidance
- [ ] Documentation is clear and accessible to new users
- [ ] No duplication of content from existing READMEs

## Documentation Style Guidelines

**Clarity:**
- Write for users who may be unfamiliar with the tools
- Provide context for why tools exist
- Explain workflows, not just individual scripts

**Examples:**
- Include working examples with expected output
- Show common use cases
- Demonstrate how scripts work together

**Organization:**
- Logical structure (overview → quick start → detailed docs)
- Clear headings and sections
- Easy to scan and find information

**Completeness:**
- Document all scripts (don't skip any)
- Include dependencies and prerequisites
- Note SITL vs hardware FC usage
- Explain configuration persistence (EEPROM)

## Resources

**Existing Documentation:**
- `README_GPS_BLACKBOX_TESTING.md` - 300+ lines of comprehensive blackbox workflow
- `BLACKBOX_SERIAL_WORKFLOW.md` - Serial logging specifics
- `HIGH_FREQUENCY_LOGGING_STATUS.md` - Performance analysis
- `MSP2_INAV_DEBUG_FIX.md` - Debugging information
- `MSP_QUERY_RATE_ANALYSIS.md` - Rate analysis

**Scripts to Document (40+ files):**
```bash
cd claude/test_tools/inav/gps
ls -1 *.py *.sh | wc -l
# Result: Many scripts for various testing purposes
```

**Key Dependencies:**
- **mspapi2:** Modern MSP Python library
- **uNAVlib:** Legacy MSP Python library (used by some scripts)
- **SITL:** Software-in-the-loop simulator
- **CRSF protocol:** For RC and telemetry

## Notes

**Focus Areas:**

1. **test_motion_simulator.sh** - The orchestrator script
   - How it coordinates two separate MSP connections
   - Why CRSF RC sender must start first
   - 3-second delay for connection establishment
   - Process management and error handling
   - Log file locations and interpretation

2. **Workflow Clarity**
   - How scripts work together
   - What runs in what order
   - When to use which script
   - Common pitfalls and solutions

3. **Entry Point**
   - README.md should be THE starting point
   - Quick wins for new users
   - Progressive detail (overview → detailed)
   - Don't make users hunt through multiple files

**Avoid:**
- Duplicating content from existing READMEs
- Just listing scripts without context
- Assuming users know MSP/SITL internals
- Creating another specialized doc instead of main overview

## Why This Matters

**Current State:**
- 40+ scripts in the directory
- Several specialized READMEs
- No main entry point or overview
- Hard to find the right tool for the job

**After This Task:**
- Clear entry point (README.md)
- Organized by use case
- Easy to find the right script
- Comprehensive reference
- Highlights important tools (test_motion_simulator.sh)

**User Impact:**
- Easier onboarding for GPS testing
- Less time hunting for the right script
- Better understanding of available tools
- Clearer workflows and examples

---
**Manager**
