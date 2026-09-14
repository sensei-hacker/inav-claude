#!/usr/bin/env python3
"""
Search pre-built indexes across all four AT32F435 documentation indexes,
then extract the matched pages from the source PDF for full context.

Phase 1 — Index lookup (instant, no PDF tools needed):
  Reads static search-index/*.txt files to find which pages mention a keyword.

Phase 2 — Page extraction (uses pdftotext from poppler-utils):
  Extracts only the relevant pages from the PDF so you can read the
  surrounding content.

Each index covers a different document:
  AT32F435-RefMan-Index           → reference-manaul-RM_AT32F435_437_EN_V2.06.pdf (Reference Manual: registers, per-pin IOMUX tables)
  AT32F435-Datasheet-Index        → AT32F437VGT7-datasheet.pdf (datasheet: pinouts, electrical specs)
  AT32F435-DMA-Index              → AN0103_AT32F435_437_DMA_Application_Note_EN_V2.0.1.pdf (DMA details)
  AT32F435-ADC-Index              → AN0093_AT32F435_437_ADC_Application_Note_EN_V2.0.1.pdf (ADC details)
  AT32F435-Performance-Index      → AN0092_AT32F435_437_Performance_Improve_V2.0.1_EN.pdf (Optimization)

Note: for MUX/alternate-function *numbers*, don't search the PDF — use
alternate-functions.tsv / af-by-function.txt, pre-extracted from the RM's own
per-pin tables by parse_refman_iomux.py + parse_af_table.py.

Usage:
    # Search all indexes, extract matched pages
    ./search_indexes.py DMA

    # Search one index only
    ./search_indexes.py --index AT32F435-Datasheet-Index SPI
    ./search_indexes.py --index AT32F435-DMA-Index channel

    # Index lookup only — no PDF extraction (fast listing of pages)
    ./search_indexes.py --no-extract timer

    # Extract with extra context pages around each match
    ./search_indexes.py --context 2 --index AT32F435-ADC-Index conversion

    # Raise the per-index result cap (default 20; extraction skipped above cap)
    ./search_indexes.py --max 50 interrupt

    # List available keywords
    ./search_indexes.py --list
    ./search_indexes.py --list --index AT32F435-Performance-Index

    # Fuzzy-match keyword names by substring
    ./search_indexes.py --match timer
"""

import argparse
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

# Gracefully handle broken pipe (e.g. when piped to head)
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

BASE = Path(__file__).parent
DATA_DIR = BASE / "datasheets_application_notes"

# Each index directory mapped to its source PDF (relative to DATA_DIR)
INDEXES = {
    "AT32F435-RefMan-Index": {
        "description": "Reference Manual (registers, peripheral operation, per-pin IOMUX tables)",
        "pdf": "reference-manaul-RM_AT32F435_437_EN_V2.06.pdf",
    },
    "AT32F435-Datasheet-Index": {
        "description": "Datasheet (pinouts, electrical specs, alternate functions)",
        "pdf": "AT32F437VGT7-datasheet.pdf",
    },
    "AT32F435-DMA-Index": {
        "description": "DMA Application Note (DMA channels, configuration, examples)",
        "pdf": "AN0103_AT32F435_437_DMA_Application_Note_EN_V2.0.1.pdf",
    },
    "AT32F435-ADC-Index": {
        "description": "ADC Application Note (ADC setup, calibration, conversion)",
        "pdf": "AN0093_AT32F435_437_ADC_Application_Note_EN_V2.0.1.pdf",
    },
    "AT32F435-Performance-Index": {
        "description": "Performance Improvement Note (optimization techniques, benchmarking)",
        "pdf": "AN0092_AT32F435_437_Performance_Improve_V2.0.1_EN.pdf",
    },
}


def index_path(index_name: str) -> Path:
    return DATA_DIR / index_name / "search-index"


def pdf_path(index_name: str) -> Path:
    return DATA_DIR / INDEXES[index_name]["pdf"]


def available_keywords(index_name: str) -> list:
    """Return sorted keyword names (without .txt) for an index."""
    p = index_path(index_name)
    if not p.is_dir():
        return []
    return sorted(f.stem for f in p.glob("*.txt"))


def parse_index_file(filepath: Path):
    """Parse an index file into (keyword, occurrence_count, [(page, line), ...])."""
    keyword = ""
    count = 0
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("Keyword: "):
                keyword = line[len("Keyword: "):]
            elif line.startswith("Occurrences: "):
                count = int(line[len("Occurrences: "):])
            elif line.startswith("=" * 10):
                continue
            else:
                m = re.match(r"Page\s+(\d+):\s*(.*)", line)
                if m:
                    entries.append((int(m.group(1)), m.group(2)))
    return keyword, count, entries


def search_keyword(index_name: str, keyword: str):
    """Look up a keyword in one index (case-insensitive). Returns None if not found."""
    idx_dir = index_path(index_name)
    p = idx_dir / f"{keyword}.txt"
    if p.is_file():
        return parse_index_file(p)
    kw_lower = keyword.lower()
    for candidate in idx_dir.glob("*.txt"):
        if candidate.stem.lower() == kw_lower:
            return parse_index_file(candidate)
    return None


def extract_pages(pdf: Path, pages: list, context: int = 0) -> str:
    """Extract specific pages from a PDF using pdftotext.

    Groups nearby pages (within context distance) into single extractions
    to avoid redundant subprocess calls.
    """
    if not pdf.exists():
        return f"[PDF not found: {pdf}]"

    # Sort and deduplicate pages, then expand by context
    expanded = set()
    for p in pages:
        for offset in range(-context, context + 1):
            expanded.add(max(1, p + offset))

    # Group consecutive pages into ranges
    sorted_pages = sorted(expanded)
    ranges = []
    start = sorted_pages[0]
    end = start
    for p in sorted_pages[1:]:
        if p <= end + 1:
            end = p
        else:
            ranges.append((start, end))
            start = p
            end = p
    ranges.append((start, end))

    # Extract each range
    chunks = []
    for start, end in ranges:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as tmp:
                tmp_path = tmp.name
            subprocess.run(
                [
                    "pdftotext", "-layout",
                    "-f", str(start), "-l", str(end),
                    str(pdf), tmp_path,
                ],
                check=True,
                capture_output=True,
            )
            with open(tmp_path) as f:
                text = f.read()
            chunks.append(f"--- Pages {start}–{end} ---\n{text}")
        except FileNotFoundError:
            return "[pdftotext not found — install poppler-utils]"
        except subprocess.CalledProcessError as e:
            return f"[pdftotext error: {e.stderr.decode(errors='replace')}]"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    return "\n".join(chunks)


def rg_fallback(keyword: str, search_dir: Path) -> bool:
    """Fall back to rg -i when keyword not found in any pre-built index."""
    try:
        result = subprocess.run(
            ["rg", "-i", "--glob", "!*.pdf", "-n", keyword, str(search_dir)],
            capture_output=True, text=True,
        )
        if not result.stdout.strip():
            return False
        lines = result.stdout.strip().split("\n")
        print(f"\n--- rg fallback: {len(lines)} match(es) for '{keyword}' ---")
        for line in lines[:50]:
            print(f"  {line}")
        if len(lines) > 50:
            print(f"  ... ({len(lines) - 50} more matches)")
        return True
    except FileNotFoundError:
        return False


MAX_RESULTS = 20  # Default cap; use --max to override


def search_all(keyword: str, indexes: list, extract: bool = True, context: int = 0, max_results: int = MAX_RESULTS):
    """Search for a keyword across indexes. Optionally extract matched pages.

    If an index has more than max_results entries, only the first max_results
    are shown and PDF extraction is skipped for that index to keep output
    manageable. Use --max to raise the limit.
    """
    found_any = False
    for idx in indexes:
        result = search_keyword(idx, keyword)
        if result is None:
            continue
        found_any = True
        kw, count, entries = result
        pdf = pdf_path(idx)
        truncated = len(entries) > max_results

        print(f"\n{'=' * 70}")
        print(f"  {idx} — {INDEXES[idx]['description']}")
        print(f"  Keyword: {kw}  |  {count} occurrences  |  PDF: {pdf.name}")
        if truncated:
            print(f"  ⚠  Too many results ({len(entries)}) — showing first {max_results}.")
            print(f"     Use --max N to raise the limit, or a more specific keyword.")
        print('=' * 70)

        # Phase 1: print index summary (page + matched line)
        pages = []
        for page, text in entries[:max_results]:
            print(f"  Page {page:4d}: {text}")
            pages.append(page)

        # Phase 2: extract matched pages from PDF (skip if truncated)
        if extract and pages and not truncated:
            unique_pages = sorted(set(pages))
            print(f"\n  --- Extracting {len(unique_pages)} page(s) from PDF ---\n")
            extracted = extract_pages(pdf, unique_pages, context=context)
            print(extracted)
        elif extract and truncated:
            print(f"\n  (PDF extraction skipped — refine your keyword or use --max)\n")

    if not found_any:
        if not rg_fallback(keyword, DATA_DIR):
            print(f"Keyword '{keyword}' not found in any index or text file.", file=sys.stderr)
            print("Use --match to fuzzy-search keyword names, or --list to browse.", file=sys.stderr)
            sys.exit(1)


def list_keywords(indexes: list):
    """Print available keywords for the given indexes."""
    for idx in indexes:
        kws = available_keywords(idx)
        print(f"\n{idx} — {INDEXES[idx]['description']}  ({len(kws)} keywords)")
        print("-" * 60)
        for kw in kws:
            print(f"  {kw}")


def match_keywords(substring: str, indexes: list):
    """Find keywords whose name contains the given substring (case-insensitive)."""
    sub = substring.lower()
    found_any = False
    for idx in indexes:
        kws = [k for k in available_keywords(idx) if sub in k.lower()]
        if not kws:
            continue
        found_any = True
        print(f"\n{idx} — {INDEXES[idx]['description']}")
        print("-" * 60)
        for kw in kws:
            print(f"  {kw}")

    if not found_any:
        print(f"No keywords matching '{substring}' found.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Search AT32F435 documentation indexes and extract PDF pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("keyword", nargs="?", help="Keyword to search for")
    parser.add_argument(
        "--index", "-i",
        choices=list(INDEXES.keys()),
        help="Search only this index (default: all four)",
    )
    parser.add_argument(
        "--no-extract", "-n",
        action="store_true",
        help="Skip PDF extraction — show only the index page listing",
    )
    parser.add_argument(
        "--context", "-C",
        type=int, default=0,
        help="Extra context pages to extract around each match (default: 0)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available keywords instead of searching",
    )
    parser.add_argument(
        "--match", "-m",
        metavar="SUBSTR",
        help="Find keywords whose name contains SUBSTR (case-insensitive)",
    )
    parser.add_argument(
        "--max",
        type=int, default=MAX_RESULTS,
        help=f"Max index entries to show per keyword (default: {MAX_RESULTS}). "
             "PDF extraction is skipped when this limit is hit.",
    )

    args = parser.parse_args()
    indexes = [args.index] if args.index else list(INDEXES.keys())

    if args.list:
        list_keywords(indexes)
    elif args.match:
        match_keywords(args.match, indexes)
    elif args.keyword:
        search_all(
            args.keyword, indexes,
            extract=not args.no_extract,
            context=args.context,
            max_results=args.max,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
