# Debugging Guide

Tools and techniques for debugging INAV firmware and configurator.

---

## 1. Serial Printf Debugging (Firmware)

**Best for:** Embedded firmware debugging, understanding real-time behavior

**How to use:**
```c
// In firmware code, use DEBUG macros
DEBUG_SET(DEBUG_GYRO, 0, gyroData.x);
DEBUG_SET(DEBUG_GYRO, 1, gyroData.y);
DEBUG_SET(DEBUG_GYRO, 2, gyroData.z);
```

**Configuration:**
- Enable debug mode using `/mwptools` skill for CLI access
- CLI command: `set debug_mode = GYRO`
- View output in configurator or via serial console
- See firmware documentation for available DEBUG slots

**Finding debug modes:**
- Use `inav-architecture` agent: "Where are debug modes defined?"
- Check `src/main/fc/fc_debug.h` for full list

**Common debug modes:**
- `DEBUG_GYRO` - Gyroscope data
- `DEBUG_PIDLOOP` - PID loop timing
- `DEBUG_NAV_YAW` - Navigation yaw control
- Many more available

---

## 2. Chrome DevTools MCP (Configurator)

**Best for:** JavaScript debugging, UI issues, network requests

**How to use:**
```bash
# Launch configurator with debugging enabled
/test-configurator

# Or use MCP tools directly via Task tool
```

**Capabilities:**
- Set breakpoints in JavaScript code
- Inspect DOM and network requests
- Console logging and error tracking
- Performance profiling
- Take screenshots for bug reports

**See also:**
- `.claude/skills/test-configurator/SKILL.md`
- MCP chrome-devtools tools (mcp__chrome-devtools__*)

---

## 3. GDB (SITL Debugging)

**Best for:** Low-level firmware debugging, crash investigation

**Prerequisites:**
- Build SITL using `inav-builder` agent (includes debug symbols)
- Start SITL using `sitl-operator` agent if needed for testing

**How to use:**
```bash
# Start SITL under GDB
gdb inav/build_sitl/bin/SITL.elf

# Common GDB commands
(gdb) break navigationInit        # Set breakpoint
(gdb) run                         # Start SITL
(gdb) next                        # Step to next line
(gdb) step                        # Step into function
(gdb) print variable              # Inspect variable
(gdb) backtrace                   # Show call stack
(gdb) continue                    # Continue execution
```

**Tips:**
- Use `inav-architecture` agent to find function names for breakpoints
- Use breakpoints at key functions to understand flow
- Inspect variables to verify state
- Backtrace helpful for crash debugging

---

## When to Use Each Tool

| Scenario | Recommended Tool |
|----------|-----------------|
| Understanding sensor data flow | Serial printf debugging |
| Investigating navigation logic | Serial printf or GDB |
| UI not responding correctly | Chrome DevTools MCP |
| JavaScript errors in configurator | Chrome DevTools MCP |
| SITL crashes or segfaults | GDB |
| Performance issues (firmware) | Serial printf with timing |
| Performance issues (configurator) | Chrome DevTools profiler |
| Need CLI access to flight controller | `/mwptools` skill |

---

## General Debugging Approach

1. **Reproduce the bug reliably** - Use `test-engineer` agent to create reproduction test
2. **Isolate the problem** - Narrow down which component/function is involved
   - Use `inav-architecture` agent to find relevant files
3. **Use appropriate tool** - Serial printf for most firmware, Chrome DevTools for configurator
4. **Verify your theory** - Test that your understanding is correct before fixing
5. **Fix and verify** - Implement fix, run reproduction test again (should pass)

---

## References

- **CLI access:** `/mwptools` skill
- **Build SITL:** `inav-builder` agent
- **Start SITL:** `sitl-operator` agent
- **Find code locations:** `inav-architecture` agent
- **MSP debugging:** `msp-expert` agent
- **Test creation:** `test-engineer` agent
- **Configurator testing:** `/test-configurator` skill

---

## Self-Improvement: Lessons Learned

When you discover something important about DEBUGGING TECHNIQUES that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future debugging tasks, not one-off situations
- **About debugging** - tools, techniques, when to use each, debugging approaches
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

<!-- Add new lessons above this line -->
