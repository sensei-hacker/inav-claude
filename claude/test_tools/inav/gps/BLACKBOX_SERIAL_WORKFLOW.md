# Blackbox Serial Logging Workflow for High-Frequency navEPH Capture

**Purpose:** Capture navEPH data at 500 Hz to investigate 198 Hz GPS fluctuation (Issue #11202)

**Method:** Serial blackbox logging with `blackbox_rate_denom = 2`

---

## Why Serial Blackbox Instead of MSP?

**MSP Limitations:**
- Maximum query rate: ~20 Hz (limited by TASK_SERIAL at 100 Hz)
- Cannot capture signals > 10 Hz (Nyquist limit)
- 198 Hz signal requires ≥396 Hz sampling (Nyquist theorem)

**Blackbox Advantages:**
- Logs at PID rate (1000 Hz) / blackbox_rate_denom
- With denom=2: **500 Hz logging** (2.5× the 198 Hz signal)
- Captures debug[] array directly without MSP overhead
- Proper high-frequency data acquisition

---

## Quick Start

```bash
cd ~/Documents/planes/inavflight

# 1. Start SITL (fresh config)
cd inav/build_sitl
pkill -9 SITL.elf
rm -f eeprom.bin
./bin/SITL.elf > /tmp/sitl.log 2>&1 &
sleep 10

# 2. Configure SITL for blackbox serial logging
cd ~/Documents/planes/inavflight
python3 claude/test_tools/inav/gps/configure_sitl_blackbox_serial.py

# 3. Enable BLACKBOX feature (via configurator or CLI)
# See "Feature Enable" section below

# 4. Run GPS test with blackbox capture
# TODO: Create wrapper script
```

---

## Detailed Workflow

### Step 1: SITL Setup

```bash
cd ~/Documents/planes/inavflight/inav/build_sitl

# Clean start (fresh EEPROM)
pkill -9 SITL.elf 2>/dev/null
rm -f eeprom.bin

# Start SITL
./bin/SITL.elf > /tmp/sitl.log 2>&1 &
sleep 10
```

### Step 2: Configure Blackbox

```bash
python3 ~/Documents/planes/inavflight/claude/test_tools/inav/gps/configure_sitl_blackbox_serial.py
```

**What this does:**
- Sets `blackbox_device = SERIAL (0)`
- Sets `blackbox_rate_num = 1`
- Sets `blackbox_rate_denom = 2` → **500 Hz logging**
- Sets `debug_mode = DEBUG_POS_EST (20)` → navEPH in debug[7]
- Saves to EEPROM and reboots

### Step 3: Enable BLACKBOX Feature

**Option A: Via INAV Configurator**
1. Connect configurator to localhost:5760
2. Go to Configuration tab
3. Enable "BLACKBOX" feature
4. Click "Save and Reboot"

**Option B: Via CLI (mspapi2)**
```python
# TODO: Create feature enable script
# Requires reading current feature mask and ORing bit 19
```

**Option C: Manual CLI (if configurator unavailable)**
```bash
# Feature bit 19 = BLACKBOX = 2^19 = 524288
# If no other features: feature 524288
# If other features exist: add 524288 to current value
```

### Step 4: Configure Arming (if not already done)

```bash
# Use existing SITL arm configuration script
python3 claude/test_tools/inav/sitl/sitl_arm_test.py 5760
```

**This configures:**
- MSP receiver
- ARM mode on AUX1
- HITL mode
- Tests arming

### Step 5: Determine Blackbox Serial Port

**Challenge:** SITL may map serial blackbox to different outputs.

**Possible locations:**
1. **TCP port:** SITL may expose serial ports as TCP (e.g., 5761, 5762)
2. **Stdout/stderr:** Mixed with SITL debug output
3. **Separate log file:** SITL may create blackbox file
4. **Unix socket:** Some SITL configs use sockets

**Investigation needed:**
```bash
# Check SITL stdout for blackbox data
tail -f /tmp/sitl.log | xxd | head

# Check for new TCP connections
netstat -an | grep 576

# Check SITL help/docs
./bin/SITL.elf --help
```

### Step 6: Capture Blackbox Data

**Method depends on Step 5 results:**

**If TCP port available:**
```bash
# Capture raw data
nc localhost 5761 > blackbox_raw.bin

# Or use socat
socat TCP:localhost:5761 - > blackbox_raw.bin
```

**If stdout/stderr:**
```bash
# SITL may need to be started differently
./bin/SITL.elf --blackbox-serial-stdout > blackbox_raw.bin 2>&1
```

**If file output:**
```bash
# Check build_sitl/ for .TXT or .BBL files
ls -lh *.TXT *.BBL 2>/dev/null
```

### Step 7: Run GPS Injection Test

```bash
# Use existing GPS injection script
# This sends GPS altitude + RC to keep armed
python3 claude/test_tools/inav/gps/gps_with_rc_keeper.py \
    --profile climb \
    --duration 60 \
    --port 5760
```

**While this runs, blackbox should be logging navEPH at 500 Hz.**

### Step 8: Decode Blackbox Log

```bash
# Decode to CSV
blackbox_decode blackbox_raw.bin

# This creates: blackbox_raw.01.csv (or similar)
```

### Step 9: Analyze navEPH

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('blackbox_raw.01.csv')

# Extract time and navEPH
# Time might be in 'time (us)' column
# navEPH is in debug[7] - need to decode bit-packed value

# Decode debug[7]:
# Bits 10-19: navEPH (cm)
# Bits 0-9: navEPV (cm)
df['navEPH_cm'] = (df['debug[7]'] >> 10) & 0x3FF
df['navEPV_cm'] = df['debug[7]'] & 0x3FF

# Convert time to seconds
df['time_s'] = df['time (us)'] / 1e6

# Plot navEPH over time
plt.figure(figsize=(14, 6))
plt.plot(df['time_s'], df['navEPH_cm'], label='navEPH', linewidth=0.5)
plt.xlabel('Time (s)')
plt.ylabel('navEPH (cm)')
plt.title('navEPH at 500 Hz')
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('navEPH_500hz.png', dpi=150)
print("Plot saved to navEPH_500hz.png")

# Check for 198 Hz oscillation
from scipy import signal
from scipy.fft import fft, fftfreq

# FFT to find frequency components
sample_rate = 500  # Hz
fft_vals = fft(df['navEPH_cm'].values)
fft_freq = fftfreq(len(fft_vals), 1/sample_rate)

# Plot frequency spectrum
plt.figure(figsize=(14, 6))
plt.plot(fft_freq[:len(fft_freq)//2],
         np.abs(fft_vals[:len(fft_vals)//2]))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('navEPH Frequency Spectrum')
plt.axvline(x=198, color='r', linestyle='--', label='198 Hz')
plt.axvline(x=10, color='g', linestyle='--', label='10 Hz (GPS)')
plt.xlim(0, 250)
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('navEPH_spectrum.png', dpi=150)
print("Spectrum saved to navEPH_spectrum.png")

# Find dominant frequencies
peak_indices = signal.find_peaks(np.abs(fft_vals[:len(fft_vals)//2]),
                                 height=1000)[0]
peak_freqs = fft_freq[peak_indices]
print(f"\nDominant frequencies:")
for freq in peak_freqs[:10]:
    if freq > 0:
        print(f"  {freq:.1f} Hz")
```

---

## Configuration Summary

| Setting | Value | Purpose |
|---------|-------|---------|
| blackbox_device | SERIAL (0) | Output to serial port |
| blackbox_rate_num | 1 | Numerator of rate fraction |
| blackbox_rate_denom | 2 | Log every 2nd cycle → 500 Hz |
| debug_mode | DEBUG_POS_EST (20) | navEPH in debug[7] |
| PID loop rate | 1000 Hz | Base rate |
| **Effective log rate** | **500 Hz** | 1000 / 2 = 500 Hz |

**Nyquist Analysis:**
- Signal frequency: 198 Hz
- Sampling rate: 500 Hz
- Nyquist factor: 500 / 198 = **2.5×** ✓ (adequate)
- Recommended minimum: 2× (Nyquist theorem)

---

## Troubleshooting

### Issue: Can't find blackbox serial output

**Check SITL serial port configuration:**
```bash
# Look for serial port args in SITL startup
./bin/SITL.elf --help | grep -i serial

# Check SITL source code for serial mapping
grep -r "blackbox" inav/src/main/target/SITL/
```

**Try FILE device instead:**
```bash
# Reconfigure for FILE output
set blackbox_device = FILE
save

# Check for .TXT files in build_sitl/
ls -lh build_sitl/*.TXT
```

### Issue: Blackbox log is empty or corrupted

**Verify feature is enabled:**
```bash
# Via configurator or check feature mask
# BLACKBOX = bit 19 = 524288
```

**Check if armed:**
- Blackbox only logs when armed
- Use sitl_arm_test.py to verify arming

**Check log rate:**
```bash
# If blackbox_rate_denom too high, may miss data
# denom=2 should be safe (500 Hz)
```

### Issue: Cannot decode blackbox file

**Try different decoder:**
```bash
# Use INAV blackbox-tools
# https://github.com/iNavFlight/blackbox-tools

# Clone and build
git clone https://github.com/iNavFlight/blackbox-tools
cd blackbox-tools
make

# Decode
./blackbox_decode /path/to/log.BBL
```

---

## Alternative: Use Hardware Flight Controller

If SITL serial blackbox proves problematic:

1. **Use real hardware:**
   - Flight controller with SD card or flash
   - Guaranteed working blackbox
   - Same configuration (blackbox_rate_denom=2, debug_mode=20)

2. **Connect via USB:**
   - Run GPS injection via MSP
   - Blackbox logs to SD card
   - Decode after test

3. **Advantages:**
   - Proven blackbox implementation
   - No SITL quirks
   - Real-world timing

---

## Expected Results

**If 198 Hz cycle exists:**
- FFT will show peak at 198 Hz
- Time-domain plot shows oscillation period of ~5ms
- navEPH varies cyclically

**If 198 Hz is artifact:**
- No 198 Hz peak in spectrum
- May see 10 Hz (GPS update rate)
- May see other frequencies (scheduler, estimator)

**Either way, 500 Hz logging will reveal truth.**

---

## Files

- **configure_sitl_blackbox_serial.py:** SITL blackbox configuration
- **BLACKBOX_SERIAL_WORKFLOW.md:** This document
- **MSP_QUERY_RATE_ANALYSIS.md:** Why MSP can't capture 198 Hz

---

## Next Steps

1. **Investigate SITL serial port mapping**
   - How does SITL expose serial ports?
   - Is there a TCP port for blackbox?

2. **Test FILE device workaround**
   - May work better than SERIAL in SITL
   - Check if 15ms bug is fixed

3. **Create end-to-end script**
   - Automate: configure → arm → inject GPS → capture → decode → analyze

4. **Hardware testing**
   - If SITL proves difficult, use real FC
   - Validate findings on hardware

---

## References

- Blackbox docs: https://github.com/iNavFlight/inav/blob/master/docs/Blackbox.md
- Blackbox tools: https://github.com/iNavFlight/blackbox-tools
- Issue #11202: https://github.com/iNavFlight/inav/issues/11202
- MSP rate analysis: `MSP_QUERY_RATE_ANALYSIS.md`
