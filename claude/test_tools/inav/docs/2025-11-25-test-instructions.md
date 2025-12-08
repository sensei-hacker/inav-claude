# SITL Test Instructions: Faster MSP When Disarmed

## Quick Test Plan

### Build Both Binaries

```bash
cd inav

# Build baseline (master)
git checkout master
mkdir -p build_baseline && cd build_baseline
cmake -DSITL=ON ..
make -j4
cp inav_SITL ../inav_SITL_baseline
cd ..

# Build optimized (faster_msp_when_disarmed)
git checkout faster_msp_when_disarmed
mkdir -p build_optimized && cd build_optimized
cmake -DSITL=ON ..
make -j4
cp inav_SITL ../inav_SITL_optimized
cd ..

# Verify
ls -lh inav_SITL_baseline inav_SITL_optimized
```

### Run Test

**Terminal 1 - SITL:**
```bash
cd inav
./inav_SITL_baseline
# Look for "Listening on port 5761"
```

**Terminal 2 - Configurator:**
```bash
cd inav-configurator
npm start
# Connect to localhost:5761
# Time tab loads: OSD, Advanced Tuning, Magnetometer
# Disconnect
```

**Terminal 1 - Switch:**
```bash
# Ctrl+C to stop baseline
./inav_SITL_optimized
# Repeat configurator test
```

### Measure

Use browser DevTools Console:
```javascript
// Before switching tab
console.time('tabload');
// After tab loads
console.timeEnd('tabload');
```

### Expected Results

- Baseline: 2-5 seconds per tab
- Optimized: 1-2.5 seconds per tab (~50% improvement)
