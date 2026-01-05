# AT32F43x Flash Recovery - Flash Protection / Lock Recovery

**INAV Branch:** `at32-sram-zw-flash-config`
**Related Document:** `claude/developer/AT32F43x_SRAM_ZW_Flash_Analysis.md`

## Problem Summary

After attempting to automatically configure EOPB0 (Extended Option Byte 0) during early boot initialization, the AT32F435 flash controller entered a protected/locked state that prevents DFU flashing operations.

**Symptoms:**
- `dfu-util: ERASE_PAGE not correctly executed`
- `dfu-util: MASS_ERASE not correctly executed`
- Flash status shows `dfuERROR, status = 11`
- Cannot flash any firmware via DFU

**Root Cause:**
The EOPB0 initialization code attempted to modify the USD (User System Data) area very early in `systemInit()` before all necessary subsystems were initialized. This operation either:
1. Failed and left the flash controller in an error state
2. Succeeded but triggered flash read/write protection
3. Caused incomplete flash operations that locked the flash controller

## What is EOPB0?

EOPB0 (Extended Option Byte 0) at address `0x1FFF_F810` controls the SRAM/Flash partitioning on AT32F435/437:

- Determines how much RAM is available (128K - 512K)
- Controls zero-wait (ZW) flash region size
- More SRAM = less ZW flash, and vice versa
- Optimal for INAV: 192KB SRAM → 448KB ZW flash + 560KB non-ZW flash

**Why we tried to configure it:**
Zero-wait flash runs at full CPU speed (288MHz), while non-zero-wait flash has 2-3 wait states and runs 3-4x slower. Optimizing the ZW/NZW split improves performance.

**Why automatic configuration failed:**
Attempting to write USD/EOPB0 during very early boot (`systemInit()`) before flash subsystems are fully initialized causes the flash controller to enter a protected state.

## Recovery Methods

### Method 1: STM32CubeProgrammer (Recommended - Easiest)

**Note:** AT32F43x chips are compatible with STM32 programming tools. Despite being from different manufacturers (Artery vs STMicroelectronics), they use the same ARM Cortex-M4 core and DFU protocol.

**Download:**
https://www.st.com/en/development-tools/stm32cubeprog.html

**Steps:**

1. **Install STM32CubeProgrammer**
   - Download for your platform (Windows/Linux/macOS)
   - Run installer
   - Launch STM32CubeProgrammer GUI

2. **Connect to Flight Controller**
   - Put FC into DFU mode (hold BOOT button while plugging USB)
   - In STM32CubeProgrammer:
     - Select "USB" connection type
     - Click "Refresh" to detect device
     - Device should show as `USB1` with VID: `2E3C`, PID: `DF11`
     - Click "Connect"

3. **Clear Flash Protection**
   - If connection fails with protection error:
     - Go to "OB" (Option Bytes) tab
     - Look for Read Protection (RDP) setting
     - If RDP is set to Level 1, change to Level 0
     - Click "Apply"
     - **Warning:** This will erase all flash content

   - For write protection:
     - In "OB" tab, check "Write Protection" settings
     - Disable all write protection bits
     - Click "Apply"

4. **Mass Erase Flash**
   - Go to "Erasing & Programming" tab
   - Select "Full chip erase"
   - Click "Start"
   - Wait for completion

5. **Flash New Firmware**
   - In "Erasing & Programming" tab:
     - Select your `.hex` file
     - Start address: `0x08000000`
     - Check "Verify programming"
     - Click "Start Programming"
   - Or use `.bin` file with explicit address `0x08000000`

6. **Disconnect and Test**
   - Click "Disconnect"
   - Unplug FC
   - Replug without holding BOOT button
   - FC should boot normally

### Method 2: ST-Link Hardware Debugger

**Hardware Required:**
- ST-Link V2 or compatible (e.g., ST-Link V3, J-Link)
- 4-pin SWD connection: SWDIO, SWCLK, GND, 3.3V

**Connection:**

```
ST-Link          AT32F435 (Flight Controller)
--------         ----------------------------
SWDIO       -->  SWDIO (SWD Data)
SWCLK       -->  SWCLK (SWD Clock)
GND         -->  GND
3.3V        -->  3.3V (optional - can power from USB)
```

**Check your flight controller pinout** - SWD pins are usually:
- Labeled on PCB silkscreen
- In a 4-pin or 6-pin debug header
- Sometimes shared with unused UART pads

**Using STM32CubeProgrammer with ST-Link:**

1. Connect ST-Link to FC via SWD
2. Power FC via USB
3. In STM32CubeProgrammer:
   - Select "ST-LINK" connection type
   - Click "Connect"
4. Follow same procedure as Method 1 (steps 3-6)

**Using OpenOCD (Command Line):**

```bash
# Install OpenOCD
sudo apt install openocd    # Ubuntu/Debian
brew install openocd        # macOS

# Create openocd.cfg
cat > openocd.cfg << 'EOF'
source [find interface/stlink.cfg]
source [find target/at32f435_437.cfg]

init
reset halt
at32f4x unlock 0
reset halt
flash erase_sector 0 0 last
reset
shutdown
EOF

# Run recovery
openocd -f openocd.cfg

# Flash new firmware
openocd -f openocd.cfg -c "program inav_9.0.0_BLUEBERRYF435WING.hex verify reset exit"
```

**Note:** You may need to create `at32f435_437.cfg` if OpenOCD doesn't have it:

```tcl
# target/at32f435_437.cfg
source [find target/stm32f4x.cfg]

# AT32F43x is compatible with STM32F4 configuration
```

### Method 3: Commercial Programmers

If ST-Link is unavailable:

**J-Link (Segger):**
- More expensive but very robust
- Excellent vendor support
- Use J-Link Commander or J-Flash software

**Black Magic Probe:**
- Open source debugger/programmer
- Uses GDB protocol
- Good alternative to ST-Link

### Method 4: Serial Bootloader (if SWD unavailable)

AT32F43x has a ROM bootloader accessible via UART (if not locked out).

**Requirements:**
- UART connection (TX, RX, GND)
- Boot0 pin pulled HIGH at power-on

**Tools:**
- **stm32flash** (Linux command-line)
- **Flash Loader Demonstrator** (Windows GUI from ST)

**Steps:**

```bash
# Install stm32flash
sudo apt install stm32flash

# Connect FC with BOOT0 = HIGH
# Identify serial port
ls /dev/ttyUSB* /dev/ttyACM*

# Unlock and erase
stm32flash -k /dev/ttyUSB0
stm32flash -o /dev/ttyUSB0

# Flash firmware
stm32flash -w inav_9.0.0_BLUEBERRYF435WING.bin -v -g 0x08000000 /dev/ttyUSB0
```

**Limitations:**
- Some FC boards don't expose BOOT0 pin
- May not work if bootloader is disabled via option bytes

## Prevention - EOPB0 Configuration Status

**⚠️ CRITICAL: No safe EOPB0 configuration method has been verified yet.**

### Attempts Made:

All attempts to modify EOPB0 programmatically have resulted in flash protection:

1. **❌ Early boot (systemInit before system_clock_config)** - Bricked FC
   ```c
   void systemInit(void) {
       init_sram_config();  // ← Tried here - FAILED
       system_clock_config();
   }
   ```

2. **❌ Early boot (systemInit after system_clock_config)** - Bricked FC

3. **❓ Late boot (after flashInit/readEEPROM)** - NOT TESTED (never implemented)

4. **❓ CLI command (full boot, idle state)** - NOT TESTED

### Theoretical Approach - Requires Testing

**Manual CLI Command (UNVERIFIED):**

A CLI command *might* be safer because it runs after full boot initialization:

```c
// In cli.c - THEORETICAL implementation (NOT TESTED)
static void cliEopb0Config(char *cmdline)
{
    uint16_t sram_kb;
    if (isEmpty(cmdline)) {
        // Show current config
        uint8_t eopb0 = (USD->eopb0) & 0x7;
        cliPrintf("Current EOPB0: 0x%02x\r\n", eopb0);
        // Print SRAM/ZW flash split
        return;
    }

    sram_kb = atoi(cmdline);

    if (sram_kb != 192 && sram_kb != 256 && /* ... valid values */) {
        cliPrintError("Invalid SRAM size");
        return;
    }

    flash_usd_eopb0_type cfg = /* convert sram_kb to EOPB0 value */;

    cliPrint("WARNING: This will reset the flight controller!\r\n");
    cliPrint("Continue? (y/n): ");

    // Only proceed if user confirms
    flash_unlock();
    flash_user_system_data_erase();
    flash_eopb0_config(cfg);
    systemReset();
}
```

**Theoretical benefits:**
- User has control
- Can backup config first (`diff all` command)
- Clear warning about reset
- Only runs when explicitly requested
- Flash operations happen after full boot, not during early init

**⚠️ WARNING: This approach MUST be tested on recovered hardware before deployment.**

## Technical Details

### AT32F43x Flash Memory Map

```
0x0800_0000 - 0x0800_27FF  (10KB)   Vector table + bootloader space
0x0800_2800 - 0x0800_3FFF  (6KB)    Custom defaults
0x0800_4000 - 0x0800_7FFF  (16KB)   Configuration storage
0x0800_8000 - 0x080F_FFFF  (992KB)  Main firmware code
0x1FFF_0000 - 0x1FFF_3FFF  (16KB)   ROM bootloader
0x1FFF_C000 - 0x1FFF_C1FF  (512B)   User System Data (USD)
```

### EOPB0 Values

| SRAM Size | EOPB0 Value | ZW Flash | NZW Flash |
|-----------|-------------|----------|-----------|
| 512K      | 0x00        | 128K     | 864K      |
| 448K      | 0x01        | 192K     | 800K      |
| 384K      | 0x02        | 256K     | 736K      |
| 320K      | 0x03        | 320K     | 672K      |
| 256K      | 0x04        | 384K     | 608K      |
| **192K**  | **0x05**    | **448K** | **560K**  |
| 128K      | 0x06        | 512K     | 480K      |

**Recommended:** 192K SRAM (EOPB0=0x05) provides good balance for INAV workloads.

### Why USD Write Triggers Flash Protection

**Observed behavior:**
- EOPB0 writes during early boot (before OR after system_clock_config) trigger flash protection
- FC becomes unbootable
- Flash controller locks, preventing all erase/program operations
- DFU recovery fails with "ERASE_PAGE not correctly executed"

**Root cause unclear:**
The exact timing requirements and failure mechanisms are not fully understood. Possible causes:
1. Flash controller not fully initialized
2. Clock system timing issues
3. Power supply instability
4. Flash operation sequencing requirements
5. Hardware-specific protection mechanisms

**Betaflight observation:**
Betaflight places EOPB0 config at the very start of `systemInit()` (before `system_clock_config()`), but:
- We tested this approach - it bricked our FC
- Betaflight may have additional initialization or different hardware
- The approach is not reliable across all AT32F43x boards

**Unknown:**
- Would placement after `flashInit()`/`readEEPROM()` work? (Never tested)
- Would CLI command execution work? (Never tested)
- Are there specific flash unlock sequences required?
- Do different AT32F43x variants behave differently?

## Current Status of INAV Implementation

**Branch:** `inav/at32-sram-zw-flash-config`
**Commit:** `7b541080f` - AT32F43x: Add EOPB0 SRAM configuration (currently disabled)

**Code location:** `src/main/drivers/system_at32f43x.c`

**Current state:**
- EOPB0 configuration code exists but is **disabled** (commented out)
- Called in `systemInit()` but performs no operations (read-only check)
- Phase 1 linker script committed (single FLASH1 region, 192KB SRAM config)
- **BLOCKED**: Cannot proceed until safe EOPB0 write timing is verified
- Requires FC recovery and controlled testing before re-enabling

**Phase 2 Future Work:**
- Split linker script into explicit FLASH_ZW / FLASH_NZW regions
- Add `.fast_code` and `.nzw_code` sections
- Use `FAST_CODE` and `SLOW_CODE` macros to optimize critical paths
- Add build-time checks to ensure fast code fits in ZW region

## Lessons Learned

1. **USD/EOPB0 writes are extremely risky** - All attempted timings during boot triggered flash protection
2. **Betaflight's approach doesn't work universally** - What works on their hardware bricked our FC
3. **Flash protection is catastrophic** - Requires hardware debugger to recover, DFU cannot help
4. **Test incrementally with recovery plan** - Have ST-Link BEFORE attempting risky operations
5. **Document recovery procedures FIRST** - This guide should have existed before first flash attempt
6. **Never assume "later is safer"** - Testing is required; theoretical safety is not real safety
7. **Verify claims before documenting them** - Don't claim an approach is safe without testing it

## References

- AT32F435/437 Datasheet: https://www.arterychip.com/en/product/AT32F435.jsp
- AT32F435/437 Reference Manual: Flash Controller chapter
- STM32CubeProgrammer: https://www.st.com/en/development-tools/stm32cubeprog.html
- INAV EOPB0 implementation: `inav/src/main/drivers/system_at32f43x.c`
- Linker script: `inav/src/main/target/link/at32_flash_f43xG.ld`

---

**Date:** 2026-01-04
**Author:** Developer (with Claude Code assistance)
**Status:** Flash protection incident, recovery procedure documented
