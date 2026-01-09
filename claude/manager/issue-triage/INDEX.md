# GitHub Issue Triage Index

**Repository:** iNavFlight/inav
**Last Updated:** 2026-01-08

## Quick Lookup

| Issue | Category | Title |
|-------|----------|-------|
| #11233 | [needs-investigation](needs-investigation.md) | Multi-frame MSP responses over CRSF lose first frame |
| #11216 | [enhancement-simple](enhancement-simple.md) | Include APA parameters in Adjustments tab |
| #11209 | [readily-solvable](readily-solvable.md) | Integer overflow in CRSF MSP handling (security) |
| #11184 | [enhancement-complex](enhancement-complex.md) | Add support for SRXL2 as ESC protocol |
| #11156 | [needs-investigation](needs-investigation.md) | ADSB Warning Message not showing in OSD |
| #11141 | [hardware-dependent](hardware-dependent.md) | Speedybee F7 V3 servo fix |
| #11135 | [hardware-dependent](hardware-dependent.md) | HAKRCH743 OSD issue |
| #11128 | [enhancement-complex](enhancement-complex.md) | DroneCAN/CANBus support |
| #10848 | [enhancement-complex](enhancement-complex.md) | Wind Speed Estimator for Multicopters |
| #10778 | [documentation](documentation.md) | Unclear documentation regarding fw_d_level |
| #10754 | [enhancement-simple](enhancement-simple.md) | Add support for W25N02K flash |
| #10674 | [readily-solvable](readily-solvable.md) | SPI busWriteBuf wrong register masking |
| #10660 | [readily-solvable](readily-solvable.md) | Climb rate deadband applied twice |
| #9633 | [needs-investigation](needs-investigation.md) | LED strip RED color shows as pink |
| #9195 | [needs-investigation](needs-investigation.md) | Altitude/speed scroll bars move wrong direction |

## Categories

| File | Description | Count |
|------|-------------|-------|
| [readily-solvable.md](readily-solvable.md) | Clear problem, known solution, reasonable effort | 3 |
| [needs-investigation.md](needs-investigation.md) | Promising but needs more analysis | 4 |
| [documentation.md](documentation.md) | Documentation fixes or improvements | 1 |
| [enhancement-simple.md](enhancement-simple.md) | Simple feature additions | 2 |
| [enhancement-complex.md](enhancement-complex.md) | Larger feature work | 3 |
| [hardware-dependent.md](hardware-dependent.md) | Requires specific hardware | 2 |
| [no-action.md](no-action.md) | Reviewed, no action needed | 0 |

## Tools

```bash
# Refresh issue cache from GitHub
python3 fetch_issues.py --refresh

# View specific issue details
python3 fetch_issues.py --issue 11156

# Search issues by keyword
python3 fetch_issues.py --search "overflow"

# List cached issues
python3 fetch_issues.py
```
