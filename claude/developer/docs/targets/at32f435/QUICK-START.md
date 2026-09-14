# Quick Start Guide - AT32F435 Documentation Tools

## What You Have

✅ **Five indexed AT32F435 documents** (Reference Manual, datasheet, DMA, ADC, and performance notes)
✅ **`search_indexes.py`** — unified search across all five indexes
✅ **100+ pre-indexed keywords per index**
✅ **Two-phase lookup:** index first (instant), then PDF page extraction (pdftotext)
✅ **`alternate-functions.tsv`/`af-by-function.txt`** — per-pin MUX ground truth
  extracted directly from the Reference Manual's own tables (not a PDF search —
  see `parse_refman_iomux.py` / `parse_af_table.py` and `CLAUDE.md`)

## How It Works

`search_indexes.py` operates in two phases:

1. **Index lookup** — reads pre-built `search-index/*.txt` files to identify which pages mention your keyword. No PDF tools needed, instant results.
2. **Page extraction** — uses `pdftotext` to pull only the matched pages from the source PDF, so you can read the full surrounding content.

Use `--no-extract` to skip phase 2 when you only need the page listing.

## Basic Usage

```bash
cd claude/developer/docs/targets/at32f435

# Search all four indexes (index lookup + page extraction)
./search_indexes.py DMA

# Search one index only
./search_indexes.py --index AT32F435-RefMan-Index register
./search_indexes.py --index AT32F435-Datasheet-Index SPI
./search_indexes.py --index AT32F435-DMA-Index channel
./search_indexes.py --index AT32F435-ADC-Index conversion

# Index lookup only — fast page listing, no PDF extraction
./search_indexes.py --no-extract timer

# Add context pages around each match
./search_indexes.py --context 2 --index AT32F435-ADC-Index sampling

# Find keywords by substring
./search_indexes.py --match timer
./search_indexes.py --match gpio

# List all available keywords
./search_indexes.py --list
./search_indexes.py --list --index AT32F435-Performance-Index
```

## Most Relevant Topics for Flight Controller Development

| Topic | Relevance | Index to Search | Use in Flight Controller |
|-------|-----------|-----------------|-------------------------|
| DMA | CRITICAL | AT32F435-DMA-Index, AT32F435-Datasheet-Index | High-speed sensor data, motor output |
| SPI | CRITICAL | AT32F435-Datasheet-Index, AT32F435-DMA-Index | IMU, barometer, flash memory |
| Timer | CRITICAL | AT32F435-Datasheet-Index | PWM generation, input capture |
| GPIO | CRITICAL | AT32F435-Datasheet-Index | Pin configuration, alternate functions |
| ADC | HIGH | AT32F435-ADC-Index, AT32F435-Datasheet-Index | Battery voltage, current sensing |
| UART/USART | HIGH | AT32F435-Datasheet-Index | GPS, telemetry, debug console |
| I2C | HIGH | AT32F435-Datasheet-Index | Magnetometer, secondary sensors |
| Interrupts (NVIC) | CRITICAL | AT32F435-Datasheet-Index | Real-time event handling |
| Clock config (RCC) | CRITICAL | AT32F435-Datasheet-Index, AT32F435-Performance-Index | System performance tuning |
| CAN | HIGH | AT32F435-Datasheet-Index | ESC communication |
| DFU / Boot mode | HIGH | AT32F435-Datasheet-Index | Firmware update entry |
| Performance | HIGH | AT32F435-Performance-Index | Code optimization, benchmarking |

## Pre-Indexed Keywords

Use `--list` to see all available keywords, or `--match` to find by substring:

```bash
./search_indexes.py --list                              # all indexes
./search_indexes.py --list --index AT32F435-DMA-Index  # one index
./search_indexes.py --match dma                         # fuzzy match
./search_indexes.py --match timer                       # finds timer, TIM1-TIM11, ...
```

**Common keywords across AT32F435-Datasheet-Index:**
`DMA`, `SPI`, `I2C`, `UART`, `timer`, `PWM`, `GPIO`, `alternate-function`, `ADC`, `CAN`, `NVIC`, `RCC`, `flash`, `SRAM`, `Cortex-M4`, `FPU`

**DMA-Index keywords:**
`DMA`, `DMA-channel`, `channel`, `SPI`, `UART`, `ADC`, `timing`, `trigger`, `request`, `configuration`

**ADC-Index keywords:**
`ADC`, `conversion`, `calibration`, `sampling`, `channel`, `trigger`, `DMA`, `interrupt`, `configuration`

**Performance-Index keywords:**
`performance`, `optimization`, `clock`, `memory`, `cache`, `compiler`, `benchmark`, `efficiency`

## Usage in Target Configuration

### When Creating a New Target

```bash
cd claude/developer/docs/targets/at32f435

# 1. Identify peripherals you need — search datasheet
./search_indexes.py --index AT32F435-Datasheet-Index SPI
./search_indexes.py --index AT32F435-Datasheet-Index alternate-function

# 2. Get DMA channel assignments — search DMA note
./search_indexes.py --index AT32F435-DMA-Index DMA-channel

# 3. Get ADC details if using ADC — search ADC note
./search_indexes.py --index AT32F435-ADC-Index conversion

# 4. Optimize if needed — search performance note
./search_indexes.py --index AT32F435-Performance-Index optimization

# 5. Configure target.h with page references from the output
# 6. Document timer and DMA assignments
```

### Example Workflow: Adding SPI1 for the Gyro

```bash
cd claude/developer/docs/targets/at32f435

# Find SPI pinout and alternate functions in the datasheet
./search_indexes.py --index AT32F435-Datasheet-Index SPI

# Find SPI DMA channel assignments in the DMA note
./search_indexes.py --context 1 --index AT32F435-DMA-Index DMA-channel

# Configure in target.h with page reference:
# "SPI1 on AF5 (see AT32F437VGT7 datasheet p.XXX)"
```

### Example Workflow: Setting Up ADC for Battery Voltage

```bash
cd claude/developer/docs/targets/at32f435

# Find ADC channel configuration
./search_indexes.py --index AT32F435-ADC-Index conversion

# Find sampling time information
./search_indexes.py --index AT32F435-ADC-Index sampling

# Find calibration requirements
./search_indexes.py --index AT32F435-ADC-Index calibration

# Find DMA integration for continuous ADC
./search_indexes.py --context 1 --index AT32F435-DMA-Index ADC
```

## Tips

- **Start with `search_indexes.py`** — it searches all four indexes and extracts the relevant PDF pages automatically
- **Use `--no-extract`** for a quick page listing without waiting for PDF extraction
- **Use `--index`** to narrow to one document when you know which one you need
- **Use `--max`** to see more results for broad keywords
- **Reference page numbers** from the output in your target.h comments
- **Use `--match`** to discover available keywords (e.g. `--match dma`, `--match timer`)
- **For SPI/DMA configuration**, search both the datasheet and the DMA application note
- **For ADC setup**, use the dedicated ADC application note for detailed examples
- **For performance tuning**, check the performance improvement note

## Troubleshooting

**"pdftotext not found"**
```bash
sudo apt-get install poppler-utils
```

**"Keyword not found"**
Try `--match` to find similar keywords or `--list` to browse all available keywords:
```bash
./search_indexes.py --match timer
./search_indexes.py --list --index AT32F435-Datasheet-Index
```

**Too many results for extraction**
Use a more specific keyword or raise the limit with `--max`:
```bash
./search_indexes.py --max 50 timer
```

**Just want page numbers, not extraction**
Use `--no-extract` for instant results:
```bash
./search_indexes.py --no-extract DMA
```
