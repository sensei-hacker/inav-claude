# Performance Debugging

Techniques for investigating PID loop and task performance issues.

## Key Insight: Excessive Update Rates

Functions in high-frequency loops may not need every-cycle updates.

**Example:** `updateArmingStatus()` was running at 2 kHz when 100 Hz is sufficient.

**Result:** 13% PID loop improvement by rate-limiting:

```c
static uint32_t lastUpdate = 0;
if (millis() - lastUpdate < 10) return; // 100 Hz limit
lastUpdate = millis();
```

**Lesson:** Audit high-frequency loops for functions that don't need every-cycle updates.

## Measuring Task Performance

Use the CLI `tasks` command to see execution times:

```bash
# Via fc-cli.py
.claude/skills/flash-firmware-dfu/fc-cli.py tasks

# Or in CLI directly
tasks
```

Output shows:
- Task name
- Rate (Hz)
- Max execution time (us)
- Average execution time (us)

## GPIO Constraints: Backup Domain Pins

PC13/PC14 on AT32 (and STM32) are backup domain pins with limits:
- Max 2 MHz speed
- Max 3mA current
- Max 30 pF capacitive load

**Lesson:** Don't use `GPIO_DRIVE_STRENGTH_STRONGER` on backup domain pins.

**Symptoms:** LEDs don't behave correctly, unexpected GPIO behavior.

**Fix:** Use `GPIO_DRIVE_STRENGTH_MODERATE` or weaker.

## Serial Printf Debugging

For detailed printf debugging techniques, see: `serial_printf_debugging.md`

Quick reference:
```c
#include "build/debug.h"

// SITL-only debug output
SD(fprintf(stderr, "[DEBUG] value=%d\n", value));
```

## Build with Debug Logging

```bash
make CPPFLAGS="-DUSE_BOOTLOG=1024 -DUSE_LOG" TARGETNAME
```

This enables `LOG_DEBUG` output over serial.

## Related

- Serial debugging: `serial_printf_debugging.md`
- GCC techniques: `gcc-preprocessing-techniques.md`
- Full investigation: `../investigations/blueberry-pid/` (gitignored)
