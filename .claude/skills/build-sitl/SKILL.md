---
description: Build INAV SITL (Software In The Loop) firmware for testing without hardware
triggers:
  - build SITL
  - compile SITL
  - compile SITL.elf
  - build SITL.elf
  - make SITL
  - create SITL build
  - SITL build
  - build sitl firmware
  - build simulator
---

# Building INAV SITL

SITL (Software In The Loop) allows testing the full firmware on your host system without hardware.

## Quick Build (Recommended - Separate Directory)

Use a separate build directory to avoid conflicts with hardware target builds:

```bash
cd inav
mkdir -p build_sitl
cd build_sitl
cmake -DSITL=ON ..
make -j4
```

The binary will be at: `build_sitl/bin/SITL.elf`

## Rebuild After Code Changes

```bash
cd inav/build_sitl
make -j4
```

No need to run cmake again unless CMakeLists.txt files changed.

## Alternative - Shared Build Directory

If you must use the shared `build/` directory:

```bash
cd inav/build
rm -f CMakeCache.txt  # If switching from hardware build
cmake -DSITL=ON ..
make SITL.elf -j4     # MUST specify target!
```

**WARNING:** Running `make` without `SITL.elf` target will attempt to build all 281 hardware targets.

## Running SITL

```bash
cd inav/build_sitl
./bin/SITL.elf
```

SITL will:
- Bind TCP to ports 5761-5768 (UART1-8)
- Bind WebSocket to ports 5771-5778 (UART1-8) [if WebSocket support compiled in]
- Listen on all interfaces [::]
- Load/save eeprom.bin in current directory

## Common Issues

| Problem | Solution |
|---------|----------|
| Build tries to compile all 281 targets | Use separate `build_sitl/` dir OR specify `make SITL.elf` |
| CMake path errors | `rm CMakeCache.txt && cmake -DSITL=ON ..` |
| Wrong toolchain (ARM instead of host) | Ensure `-DSITL=ON` in cmake command |
| Hardware builds disappeared | Use separate `build_sitl/` directory |
| Linker error: `unrecognized option '--no-warn-rwx-segments'` | Older ld versions don't support this flag. Comment out lines 69-72 in `cmake/sitl.cmake` |

## Full Documentation

```bash
cat claude/test_tools/inav/BUILDING_SITL.md
```

## Related Skills

- **sitl-arm** - Arming SITL via MSP for automated testing
- **test-crsf-sitl** - Complete CRSF telemetry testing workflow with SITL
- **run-configurator** - Using INAV Configurator with SITL
- **msp-protocol** - MSP protocol reference for SITL testing
- **pr-review** - Build SITL to test firmware PRs
