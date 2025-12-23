# USB MSC Debugging

Debugging USB Mass Storage (MSC) and CDC (serial) issues on flight controllers.

## Key Insight: Composite USB Devices

When INAV creates composite USB (CDC + MSC), the USB library may require `USE_USBD_COMPOSITE` flag:

```c
// Without USE_USBD_COMPOSITE:
// - MSC uses standalone descriptors
// - But device was initialized with CDC descriptors
// - Windows sees conflicting descriptors → fails
```

**Lesson:** USB library updates can break composite device behavior. Check conditional compilation flags when USB stops working after library updates.

## Symptoms of MSC Issues

**Windows:**
- Device Manager shows "Virtual COM Port in FS Mode"
- Missing drivers (Code 28)
- No storage drive appears in MSC mode

**Linux:**
- MSC may still work (different enumeration handling)
- Check `dmesg` for USB errors

## Debugging Commands

```bash
# Check USB device enumeration
lsusb -v | grep -A20 "STM"

# Check kernel messages
dmesg | tail -50

# Check USB device modes
cat /sys/bus/usb/devices/*/product

# List all USB devices with details
lsusb -t
```

## H743-Specific Issues

H743 boards typically use SDIO for SD card access. After USB library updates (v2.5.3 → v2.11.3), composite device handling changed.

**Affected:** H743 boards (MATEK H743, AET H743-Wing, Holybro Kakute H743, GEPRC TAKER H743)

**Working:** F405, AT32, F765 boards (often use SPI for SD card)

## USB Library Changes to Watch

When USB libraries are updated, check for:
- `USE_USBD_COMPOSITE` flag requirements
- API changes (`DEP0CTL_MPS_64` → `EP_MPS_64`)
- Function signature changes (`uint16_t` → `uint32_t`)
- Descriptor handling differences

## Related Files

INAV USB implementation:
- `src/main/drivers/usb_msc_h7xx.c` - H7 MSC implementation
- `src/main/vcp_hal/usbd_desc.c` - USB descriptors
- `lib/main/STM32H7/Middlewares/ST/STM32_USB_Device_Library/` - USB library

## Related

- Full investigation: `../investigations/h743-msc/` (gitignored)
