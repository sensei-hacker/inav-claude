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
- Bind to ports 5760 (UART1) and 5761 (UART2)
- Listen on all interfaces [::]
- Load/save eeprom.bin in current directory

## Common Issues

| Problem | Solution |
|---------|----------|
| Build tries to compile all 281 targets | Use separate `build_sitl/` dir OR specify `make SITL.elf` |
| CMake path errors | `rm CMakeCache.txt && cmake -DSITL=ON ..` |
| Wrong toolchain (ARM instead of host) | Ensure `-DSITL=ON` in cmake command |
| Hardware builds disappeared | Use separate `build_sitl/` directory |

## Full Documentation

```bash
cat claude/test_tools/inav/BUILDING_SITL.md
```
