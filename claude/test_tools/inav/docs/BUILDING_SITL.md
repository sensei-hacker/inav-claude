# Building INAV SITL

## Quick Reference

### Build from scratch (Recommended - Separate Directory)
```bash
cd inav
mkdir -p build_sitl
cd build_sitl
cmake -DSITL=ON ..
make -j4
```

The binary will be at: `build_sitl/bin/SITL.elf`

### Alternative - Shared Build Directory
```bash
cd inav
mkdir -p build
cd build
rm -f CMakeCache.txt  # If rebuilding
cmake -DSITL=ON ..
make SITL.elf -j4
```

The binary will be at: `build/bin/SITL.elf`

### Copy to test location
```bash
cp build/bin/SITL.elf build/inav_SITL_<version_name>
chmod +x build/inav_SITL_<version_name>
```

## Important Notes

1. **Use separate build directory (CRITICAL)**: Use `build_sitl/` for SITL builds to avoid conflicts with hardware target builds. Building SITL in the same directory as hardware builds will clean all hardware targets.

2. **NEVER run `make` without a target in shared build directory**: If using the shared `build/` directory, you MUST specify the target `make SITL.elf`. Running just `make` or `make -j4` will attempt to build ALL 281 hardware targets, which will fail and waste time.

3. **Use separate directory OR specify target explicitly**:
   - **Recommended**: Use `build_sitl/` and run `make` (builds only SITL)
   - **Alternative**: Use `build/` and run `make SITL.elf` (must specify target)

4. **Binary location**: The executable is created at `build_sitl/bin/SITL.elf` or `build/bin/SITL.elf`, not in the build root.

5. **Parallel builds**: Use `-j4` for faster compilation.

## Rebuild after code changes

### Using separate build_sitl directory (Recommended)
```bash
cd inav/build_sitl
make -j4
```

### Using shared build directory
```bash
cd inav/build
make SITL.elf -j4  # MUST specify target!
```

No need to run cmake again unless you changed CMakeLists.txt files.

## Switching branches

When switching git branches with code changes:
```bash
cd inav
git checkout <branch_name>
cd build
make SITL.elf -j4
cp bin/SITL.elf inav_SITL_<branch_name>
```

## Running the binary

```bash
cd inav/build
./inav_SITL_<version>
```

The SITL will:
- Bind to ports 5760 (UART1) and 5761 (UART2)
- Listen on all interfaces [::]
- Load/save eeprom.bin in current directory
- Display connection messages when clients connect

## Testing with benchmark

```bash
# Start SITL in background
./inav_SITL_<version> 2>&1 &

# Wait for initialization
sleep 2

# Run benchmark
python3 claude/test_tools/inav/msp_benchmark.py localhost 5761

# Kill SITL when done
pkill -9 inav_SITL
```

## Common Issues

### Build tries to compile all 281 hardware targets
**Symptom**: After running `cmake -DSITL=ON ..`, running `make -j4` starts building AIKONF4, AIKONF7, etc.
**Cause**: Running `make` without specifying a target in a directory configured with `-DSITL=ON` will still try to build all targets
**Fix**:
- **Option 1 (Recommended)**: Use a separate `build_sitl/` directory - then `make` works correctly
- **Option 2**: Always specify target: `make SITL.elf -j4

### CMake path errors
**Symptom**: `CMake Error: The source directory "/old/path" does not exist`
**Fix**: `rm CMakeCache.txt && cmake -DSITL=ON ..`

### Wrong toolchain
**Symptom**: Build tries to use ARM toolchain instead of host GCC
**Fix**: Ensure `-DSITL=ON` is specified in cmake command

### SITL build cleaned hardware targets
**Symptom**: Built hardware firmware (e.g., BLUEBERRYF435WING.hex) disappeared after SITL build
**Cause**: Building SITL in the same directory as hardware builds (`build/`) cleans those targets
**Prevention**: Always use separate `build_sitl/` directory for SITL builds

---

## Related Skills

- **build-sitl** - Complete SITL build workflow with troubleshooting
- **sitl-arm** - Arm SITL via MSP for automated testing
- **test-crsf-sitl** - Test CRSF telemetry with SITL
- **msp-protocol** - MSP protocol reference for SITL testing
