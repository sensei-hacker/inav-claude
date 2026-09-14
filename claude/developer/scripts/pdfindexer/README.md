# Generic PDF Indexer

A reusable tool for **building** keyword indexes from large PDF documents.

## Two-Tool Workflow

This tool (`pdfindexer.py`) is one half of a two-step process:

| Step | Tool | Purpose |
|------|------|---------|
| 1 — Build | `pdfindexer.py build-index` | Scans PDF with pdfgrep, creates static `search-index/*.txt` files |
| 2 — Search | Per-location `search_indexes.py` | Reads the static index files (instant), then extracts matched pages from PDF |

**Key point:** `pdfindexer.py search` and `find` commands re-run `pdfgrep` against the PDF every time — they do **not** read pre-built indexes. Once you have indexes built, use the per-location `search_indexes.py` instead. It's instant for Phase 1 (index lookup) and only calls pdftotext for the specific pages you need.

## Quick Start

### Step 1: Build the Index (one-time setup only)

> ⚠️ **Check first** — if the `search-index/` directory already exists and contains `.txt` files, the index is already built. Skip this step. Running `build-index` again will overwrite everything and take several minutes for nothing.

```bash
# Check whether the index already exists
ls search-index/*.txt

# Only run build-index if the directory is missing or empty
./pdfindexer.py --config mybook.yaml build-index
```

This creates `search-index/<keyword>.txt` files with page numbers and matched snippets.

### Step 2: Create a search_indexes.py for Your Document

Each indexed location gets its own `search_indexes.py`. See the reference implementation at `claude/developer/docs/targets/stm32h7/search_indexes.py` and the pattern guide at `claude/developer/workspace/js-minspace/stm32h7-index-changes.md`.

Minimal template:

```python
#!/usr/bin/env python3
# (copy from an existing search_indexes.py and update INDEXES dict)

INDEXES = {
    "My-Index": {
        "description": "Description of the document",
        "pdf": "relative/path/to/document.pdf",   # relative to script location
        "index_dir": "path/to/search-index",       # relative to script location
    },
}
```

### Step 3: Search Using search_indexes.py

```bash
cd /path/to/your/document/directory
./search_indexes.py keyword                  # full search + page extraction
./search_indexes.py --no-extract keyword     # index lookup only (instant)
./search_indexes.py --context 2 keyword      # extract with surrounding pages
./search_indexes.py --list                   # browse available keywords
./search_indexes.py --match substr           # find keywords by substring
```

## Config File Format

```yaml
# Path to PDF file (absolute or relative to config file)
pdf_file: path/to/document.pdf

# Directory name for search index (optional, default: "search-index")
index_dir: search-index

# List of keywords to index
keywords:
  - keyword 1
  - keyword 2
  - multi word keyword
```

## Example Configurations

See `example-crypto.yaml` and `example-stm32h7.yaml` for full keyword lists.

- **Crypto textbook (52 keywords):** `example-crypto.yaml` → output in `../../docs/encryption/Boneh-Shoup-Index/search-index/`
- **STM32H7 datasheet (100+ keywords):** `example-stm32h7.yaml` → output in `../../docs/targets/stm32h7/STM32H7-Index/search-index/`
- **M9 GPS interface (128 keywords):** `m9-gps.yaml` → output in `../../docs/gps/m9-interface-description/m9-search-index/`

## Commands

### build-index (one-time setup only)

Build a searchable index for all configured keywords. This is the main reason to use this tool — but **only run it once** per document. The output files are static and persist until you deliberately rebuild.

> ⚠️ **Check first:** `ls search-index/*.txt` — if files exist, the index is already built. Do not re-run.

```bash
./pdfindexer.py --config mybook.yaml build-index
```

Creates `search-index/<keyword>.txt` files. Can take several minutes depending on PDF size.

### search / find (direct PDF search — bypasses index)

These commands run `pdfgrep` against the PDF directly. They do **not** read pre-built indexes. Use them only for one-off searches on terms that aren't indexed, or for rebuilding indexes.

```bash
# Search for a term (runs pdfgrep, not index lookup)
./pdfindexer.py --config mybook.yaml search "keyword"

# Find with context pages (runs pdfgrep + pdftotext)
./pdfindexer.py --config mybook.yaml find "term" --context 2

# Case-sensitive search
./pdfindexer.py --pdf doc.pdf search "KeyWord" --case-sensitive
```

> **For pre-indexed keywords, use `search_indexes.py` instead** — it's instant and only extracts the pages you need.

### extract

Extract a page range to text. Useful for pulling specific sections.

```bash
./pdfindexer.py --config mybook.yaml extract 100 150 --output chapter5.txt

# Extract to stdout (no layout preservation)
./pdfindexer.py --pdf doc.pdf extract 50 75 --no-layout
```

## Configuration File Format

```yaml
# Path to PDF file (absolute or relative to config file)
pdf_file: path/to/document.pdf

# Directory name for search index (optional, default: "search-index")
index_dir: search-index

# List of keywords to index
keywords:
  - keyword 1
  - keyword 2
  - multi word keyword
  - keyword/with/slashes
```

**Notes:**
- `pdf_file` can be absolute or relative to the config file location
- Keywords are searched case-insensitively
- Multi-word keywords and keywords with special characters are supported
- Safe filenames are generated automatically (spaces → hyphens, slashes → hyphens)

## Command-Line Options

### Global Options

- `--config`, `-c` - Path to YAML config file
- `--pdf` - PDF file path (if not using config)
- `--keywords` - Keywords to index (if not using config)
- `--index-dir` - Index directory name (default: "search-index")

### search Options

- `term` - Term to search for (required)
- `--case-sensitive`, `-s` - Enable case-sensitive search

### find Options

- `term` - Term to find (required)
- `--context`, `-C` - Number of pages of context (default: 0)
- `--max-pages`, `-m` - Maximum pages to show (default: 5)

### extract Options

- `start_page` - First page to extract (required)
- `end_page` - Last page to extract (required)
- `--output`, `-o` - Output file (default: stdout)
- `--no-layout` - Don't preserve PDF layout

## Requirements

- Python 3.6+
- `pdftotext` (from poppler-utils)
- `pdfgrep`
- `pyyaml` (for config file support)

### Installation

Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils pdfgrep python3-yaml
```

macOS (with Homebrew):
```bash
brew install poppler pdfgrep
pip3 install pyyaml
```

## Use Cases

### Security Analysis — Crypto Textbook

> Index already exists at `../../docs/encryption/Boneh-Shoup-Index/search-index/` — skip build, go straight to search:

```bash
cd ../../docs/encryption
./search_indexes.py timing-attack
./search_indexes.py --no-extract AES
```

### Hardware Development — Microcontroller Datasheet

> Index already exists at `../../docs/targets/stm32h7/STM32H7-Index/search-index/` — skip build, go straight to search:

```bash
cd ../../docs/targets/stm32h7
./search_indexes.py DMA
./search_indexes.py --index STM32H7-Index SPI
```

### New Document — Full Workflow

Only needed when adding a **new** document that hasn't been indexed yet:

```yaml
# rfc8439.yaml
pdf_file: rfc8439-chacha20-poly1305.pdf
index_dir: search-index
keywords:
  - ChaCha20
  - Poly1305
  - AEAD
  - nonce
  - authentication tag
```

```bash
# 1. Check if index already exists
ls search-index/*.txt

# 2. Only build if missing
./pdfindexer.py --config rfc8439.yaml build-index

# 3. Create search_indexes.py (copy template, update INDEXES dict)
# 4. Search
./search_indexes.py ChaCha20
```

## Output Format

### Index Files

Each keyword gets an index file in `search-index/`:

```
Keyword: DMA channel
Occurrences: 247
================================================================================

Page   42: DMA channel selection is controlled by the DMAREQ_ID field
Page   43: Each DMA channel can be configured for memory-to-memory transfers
Page   87: The DMA channel priority is configured in the DMA_CCR register
...
```

### search_indexes.py Output (recommended)

```
======================================================================
  My-Index — Description of the document
  Keyword: DMA channel  |  247 occurrences  |  PDF: document.pdf
======================================================================
  Page   42: DMA channel selection is controlled by the DMAREQ_ID field
  Page   43: Each DMA channel can be configured for memory-to-memory transfers
  Page   87: The DMA channel priority is configured in the DMA_CCR register

  --- Extracting 3 page(s) from PDF ---

--- Pages 42–43 ---
[Full text of pages 42-43 with layout preserved]
...
```

## Directory Structure

After building an index:

```
project/
├── pdfindexer.py
├── myconfig.yaml
├── document.pdf
└── search-index/
    ├── keyword-1.txt
    ├── keyword-2.txt
    ├── multi-word-keyword.txt
    └── ...
```

## Tips

- **Build indexes once** with `pdfindexer.py build-index`, then search with `search_indexes.py` forever
- **Use config files** for documents you reference frequently
- **Use meaningful keywords** — choose terms you'll actually look up
- **For one-off searches** on non-indexed terms, `pdfgrep -n "term" document.pdf` is faster than `pdfindexer.py search`
- **Page numbers** in index output make it easy to reference the original PDF
- **Extracting a borderless per-row/per-column table (not just keyword search)?**
  Don't reconstruct it from `pdftotext -layout` — a table with multi-line wrapped
  cells commonly renders a cell's first text line *above* the row label it belongs
  to (confirmed while extracting the AT32F435 Reference Manual's per-pin IOMUX
  tables), silently misattributing data to the wrong row. Use `pdfplumber.extract_words()`
  instead: get each word's real `(x0, top)` position, cluster words into row anchors
  by whichever label word (e.g. a pin name) sits nearest vertically, and assign
  columns by nearest header `x0`. See `claude/developer/docs/targets/at32f435/parse_refman_iomux.py`
  for a working example, including guards for trailing note/heading text bleeding
  into the last row (filter cell tokens to only accept plausible-looking values,
  and never let a row label go "backwards" except at a genuine table/header boundary).

## See Also

**Per-location search scripts (use these for searching):**
- `../../docs/targets/stm32h7/search_indexes.py` — STM32H7 (3 indexes, 300+ keywords)
- `../../docs/aerodynamics/search_indexes.py` — Houghton & Carpenter (1 index, 20 keywords)
- `../../docs/encryption/search_indexes.py` — Boneh & Shoup (1 index, 52 keywords)
- `../../docs/gps/m9-interface-description/search_indexes.py` — u-blox M9 (1 index, 128 keywords)

**Pattern guide for adding new indexes:**
- `claude/developer/workspace/js-minspace/stm32h7-index-changes.md` — full checklist and template

**Config examples (for building indexes):**
- `example-crypto.yaml`, `example-stm32h7.yaml`, `m9-gps.yaml`

## License

This tool is part of the INAV project developer utilities.
Use freely for documentation indexing and search tasks.
