#!/usr/bin/env python3
"""
check_blackbox_integrity.py

Automated integrity checker for INAV blackbox .TXT/.BBL logs. Wraps the
existing `blackbox_decode` tool (do not reimplement frame parsing) and adds
raw byte-level checks that the decoder does not do on its own, specifically
aimed at symptoms of a flaky/corrupting SD-card write path:

  - zero-filled 512-byte-aligned blocks in the MIDDLE of the file (a dropped/
    silently-failed SD write typically leaves a block of NULs where log data
    should be, since FAT preallocates/zeroes clusters)
  - truncation: absence of the "End of log (disarm reason:N)" event that
    INAV writes on clean blackbox shutdown (blackbox.c: blackboxPrintf("End
    of log (disarm reason:%d)", ...))
  - unparsed trailing bytes (file continues after the point blackbox_decode
    stopped being able to make sense of it, and no clean end marker follows)

...and combines them with the frame/iteration accounting blackbox_decode
already computes internally (see printStats() in blackbox_decode.c):

  - corrupt/desynced I/P frames (stats->totalCorruptFrames)
  - missing loop iterations (gaps in the iteration counter -- this is the
    single strongest signal of dropped data, since it only increments when
    the sequence itself has a hole, not just when decode had to skip a
    frame it could still bound)
  - iterations intentionally not logged due to blackbox_rate_denom (must be
    subtracted out, these are NOT corruption)
  - missing expected metadata (short/torn header)

IMPORTANT baseline finding (established empirically against a real, cleanly
terminated SITL log): blackbox_decode's own frame parser routinely reports
1-2 "frames failed to decode" at completely healthy end-of-file, because it
probes for one more frame header past the last real frame before hitting
EOF/the end-of-log event. This is NOT corruption. A `--corrupt-frame-baseline`
(default 3) suppresses false positives from this effect; anything above the
baseline, or ANY missing iteration, mid-file zero block, or missing end
marker, is treated as real corruption.

USAGE
    # Single file, human-readable + JSON to stdout
    python3 check_blackbox_integrity.py flight.TXT

    # JSON only (for scripting / diffing)
    python3 check_blackbox_integrity.py flight.TXT --json-only > result.json

    # Whole directory (e.g. all logs from an A or B test run), one JSON
    # object per file plus an aggregate summary
    python3 check_blackbox_integrity.py --dir logs_before/ --json-only > before.json
    python3 check_blackbox_integrity.py --dir logs_after/  --json-only > after.json

    # Diff two previously-generated summaries (or two dirs directly) for an
    # objective A/B comparison
    python3 check_blackbox_integrity.py --compare before.json after.json

EXIT CODE
    0 if all logs are CLEAN or SUSPECT, 1 if any log is CORRUPT (so this is
    safe to use as a CI-style gate / shell && chain).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

END_OF_LOG_EVENT = b"\x45\xffEnd of log"  # 'E' frame marker + event-type 0xFF (FLIGHT_LOG_EVENT_LOG_END)
# followed by ASCII "End of log". NOTE: INAV appends "(disarm reason:N)\0" after
# this (see blackbox.c: blackboxPrintf("End of log (disarm reason:%d)", ...)), so
# do NOT require an immediate trailing NUL as blackbox-tools' own fixed-11-byte
# comparison does internally -- that comparison actually never matches a real INAV
# log for this reason, it only matches bare Betaflight-style "End of log\0".
ZERO_BLOCK_SIZE = 512  # SD sector size; dropped writes leave whole sectors of NULs
MIN_ZERO_RUN_TO_FLAG = 512  # ignore anything smaller than one sector


def find_blackbox_decode():
    exe = shutil.which("blackbox_decode")
    if exe:
        return exe
    # Common fallback locations used in this workspace
    candidates = [
        os.path.expanduser("~/.local/bin/blackbox_decode"),
        os.path.expanduser("~/Documents/planes/inavflight/blackbox-tools-9.0.0-rc1/bin/blackbox_decode"),
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def run_decoder(path, debug_csv_path):
    """Run blackbox_decode --debug --stdout, capturing CSV to a file and
    stats text from stderr. Returns (stats_text, decoder_returncode)."""
    exe = find_blackbox_decode()
    if not exe:
        raise RuntimeError(
            "blackbox_decode not found on PATH or in known locations. "
            "Install INAV's blackbox-tools (see claude/developer docs) before running this checker."
        )
    with open(debug_csv_path, "wb") as csv_out:
        proc = subprocess.run(
            [exe, "--debug", "--stdout", path],
            stdout=csv_out,
            stderr=subprocess.PIPE,
        )
    return proc.stderr.decode("utf-8", errors="replace"), proc.returncode


def parse_stats_text(stats_text):
    """Parse the human-readable stderr block from blackbox_decode's
    printStats() into structured fields. Field names/regexes are anchored to
    src/blackbox_decode.c printStats() format strings; keep in sync if that
    changes."""
    result = {
        "frame_counts": {},
        "frame_bytes": {},
        "good_frames": None,
        "good_bytes": None,
        "corrupt_frames": 0,
        "unreadable_iterations": 0,
        "missing_iterations": 0,
        "missing_iterations_ms": 0,
        "missing_iterations_pct": 0.0,
        "intentionally_absent_iterations": 0,
        "intentionally_absent_pct": 0.0,
        "metadata_warnings": [],
        "duration_ms": None,
        "raw_stats_text": stats_text,
    }

    m = re.search(r"duration (\d+):(\d+)\.(\d+)", stats_text)
    if m:
        mins, secs, ms = int(m.group(1)), int(m.group(2)), int(m.group(3))
        result["duration_ms"] = (mins * 60 + secs) * 1000 + ms

    for m in re.finditer(r"^([IPSGHE]) frames\s+(\d+)\s+[\d.]+ bytes avg\s+(\d+) bytes total$", stats_text, re.M):
        ftype, count, total_bytes = m.group(1), int(m.group(2)), int(m.group(3))
        result["frame_counts"][ftype] = count
        result["frame_bytes"][ftype] = total_bytes

    m = re.search(r"^Frames\s+(\d+)\s+[\d.]+ bytes avg\s+(\d+) bytes total$", stats_text, re.M)
    if m:
        result["good_frames"] = int(m.group(1))
        result["good_bytes"] = int(m.group(2))
    else:
        m = re.search(r"^Frames\s+(\d+)$", stats_text, re.M)
        if m:
            result["good_frames"] = int(m.group(1))
            result["good_bytes"] = 0

    m = re.search(r"(\d+) frames failed to decode, rendering (\d+) loop iterations unreadable", stats_text)
    if m:
        result["corrupt_frames"] = int(m.group(1))
        result["unreadable_iterations"] = int(m.group(2))

    m = re.search(r"(\d+) iterations are missing in total \((\d+)ms, ([\d.]+)%\)", stats_text)
    if m:
        result["missing_iterations"] = int(m.group(1))
        result["missing_iterations_ms"] = int(m.group(2))
        result["missing_iterations_pct"] = float(m.group(3))

    m = re.search(r"(\d+) loop iterations weren't logged because of your blackbox_rate settings \((\d+)ms, ([\d.]+)%\)", stats_text)
    if m:
        result["intentionally_absent_iterations"] = int(m.group(1))
        result["intentionally_absent_pct"] = float(m.group(3))

    if "Missing expected metadata" in stats_text:
        for m in re.finditer(r"^\s*(?:Warning|Error): (.+)$", stats_text, re.M):
            result["metadata_warnings"].append(m.group(1))
        if not result["metadata_warnings"]:
            result["metadata_warnings"].append("Missing expected metadata (unspecified)")

    return result


def scan_raw_file(path):
    """Byte-level scan independent of the frame decoder:
      - locate the clean 'End of log' event marker (if any), and how close
        to true EOF it is
      - find runs of NUL bytes >= ZERO_BLOCK_SIZE, excluding a single
        trailing run that immediately precedes the end-of-log marker (that
        is normal FAT/sector padding, not corruption)
    """
    with open(path, "rb") as f:
        data = f.read()

    file_size = len(data)
    end_marker_offset = data.rfind(END_OF_LOG_EVENT)
    has_clean_end_marker = end_marker_offset != -1
    # bytes after the marker + its fixed message body; message is variable
    # length ("End of log (disarm reason:N)\0") so just report offset info
    trailing_bytes_after_marker = 0
    if has_clean_end_marker:
        # message continues until the terminating NUL after "reason:N)" (or
        # immediately, for a bare "End of log\0" with no disarm reason)
        msg_end = data.find(b"\x00", end_marker_offset + len(END_OF_LOG_EVENT))
        if msg_end == -1:
            msg_end = file_size
        else:
            msg_end += 1
        trailing_bytes_after_marker = file_size - msg_end

    # Find all runs of zero bytes >= MIN_ZERO_RUN_TO_FLAG
    zero_runs = []
    i = 0
    n = file_size
    while i < n:
        if data[i] == 0:
            j = i
            while j < n and data[j] == 0:
                j += 1
            run_len = j - i
            if run_len >= MIN_ZERO_RUN_TO_FLAG:
                zero_runs.append((i, run_len))
            i = j
        else:
            i += 1

    # A single zero run that ends exactly where the end-of-log marker begins
    # is normal trailing sector padding before a clean shutdown -- exclude it.
    mid_file_zero_blocks = []
    for offset, length in zero_runs:
        is_trailing_pad_before_marker = (
            has_clean_end_marker and (offset + length == end_marker_offset)
        )
        is_trailing_pad_at_eof = (offset + length == file_size) and not has_clean_end_marker
        if is_trailing_pad_before_marker:
            continue
        mid_file_zero_blocks.append({"offset": offset, "length": length, "at_eof": is_trailing_pad_at_eof})

    return {
        "file_size_bytes": file_size,
        "has_clean_end_marker": has_clean_end_marker,
        "end_marker_offset": end_marker_offset if has_clean_end_marker else None,
        "trailing_bytes_after_marker": trailing_bytes_after_marker,
        "mid_file_zero_blocks": mid_file_zero_blocks,
        "mid_file_zero_block_total_bytes": sum(b["length"] for b in mid_file_zero_blocks),
    }


def check_file(path, corrupt_frame_baseline=3, keep_csv=False, csv_out_dir=None):
    if not os.path.isfile(path):
        return {
            "file": path,
            "verdict": "ERROR",
            "verdict_reasons": [f"File not found: {path}"],
        }

    raw = scan_raw_file(path)

    csv_path = None
    try:
        if csv_out_dir:
            os.makedirs(csv_out_dir, exist_ok=True)
            csv_path = os.path.join(csv_out_dir, os.path.basename(path) + ".debug.csv")
        else:
            csv_path = path + ".debug.csv.tmp"

        try:
            stats_text, decoder_rc = run_decoder(path, csv_path)
        except RuntimeError as e:
            return {
                "file": path,
                "file_size_bytes": raw["file_size_bytes"],
                "verdict": "ERROR",
                "verdict_reasons": [str(e)],
            }

        stats = parse_stats_text(stats_text)
        stats["decoder_return_code"] = decoder_rc

        result = {
            "file": path,
            "file_size_bytes": raw["file_size_bytes"],
            "has_clean_end_marker": raw["has_clean_end_marker"],
            "end_marker_offset": raw["end_marker_offset"],
            "trailing_bytes_after_marker": raw["trailing_bytes_after_marker"],
            "mid_file_zero_blocks": raw["mid_file_zero_blocks"],
            "mid_file_zero_block_total_bytes": raw["mid_file_zero_block_total_bytes"],
            "duration_ms": stats["duration_ms"],
            "frame_counts": stats["frame_counts"],
            "frame_bytes": stats["frame_bytes"],
            "good_frames": stats["good_frames"],
            "good_bytes": stats["good_bytes"],
            "corrupt_frames": stats["corrupt_frames"],
            "unreadable_iterations": stats["unreadable_iterations"],
            "missing_iterations": stats["missing_iterations"],
            "missing_iterations_ms": stats["missing_iterations_ms"],
            "missing_iterations_pct": stats["missing_iterations_pct"],
            "intentionally_absent_iterations": stats["intentionally_absent_iterations"],
            "intentionally_absent_pct": stats["intentionally_absent_pct"],
            "metadata_warnings": stats["metadata_warnings"],
            "decoder_return_code": decoder_rc,
        }

        reasons = []
        verdict = "CLEAN"

        if stats["good_frames"] is None:
            verdict = "ERROR"
            reasons.append("blackbox_decode produced no parseable frame statistics (header missing/corrupt?)")
        else:
            if stats["missing_iterations"] > 0:
                verdict = "CORRUPT"
                reasons.append(
                    f"{stats['missing_iterations']} loop iterations missing "
                    f"({stats['missing_iterations_pct']:.2f}% of log, {stats['missing_iterations_ms']}ms) "
                    "-- real data loss, not explained by blackbox_rate_denom"
                )

            if raw["mid_file_zero_blocks"]:
                verdict = "CORRUPT"
                total = raw["mid_file_zero_block_total_bytes"]
                reasons.append(
                    f"{len(raw['mid_file_zero_blocks'])} zero-filled block(s) in the middle of the file "
                    f"totalling {total} bytes -- looks like dropped/silently-failed SD write(s)"
                )

            if not raw["has_clean_end_marker"]:
                if verdict != "CORRUPT":
                    verdict = "CORRUPT"
                reasons.append(
                    "No 'End of log' clean-shutdown marker found -- log is truncated "
                    "(file ends mid-write or FC reset before blackboxFinish() ran)"
                )
            elif raw["trailing_bytes_after_marker"] > 0:
                # Bytes after the end-of-log message -- e.g. a second overlapping
                # session's data, or garbage appended after logging stopped.
                if verdict == "CLEAN":
                    verdict = "SUSPECT"
                reasons.append(
                    f"{raw['trailing_bytes_after_marker']} byte(s) found after the 'End of log' marker "
                    "(unexpected trailing data)"
                )

            if stats["metadata_warnings"]:
                verdict = "CORRUPT"
                reasons.append("Missing expected header metadata: " + "; ".join(stats["metadata_warnings"]))

            if stats["corrupt_frames"] > corrupt_frame_baseline:
                if verdict == "CLEAN":
                    verdict = "SUSPECT"
                reasons.append(
                    f"{stats['corrupt_frames']} frames failed to decode "
                    f"(baseline for a healthy EOF is <= {corrupt_frame_baseline}); "
                    f"{stats['unreadable_iterations']} iterations rendered unreadable"
                )

        if not reasons:
            reasons.append("No corruption indicators found")

        result["verdict"] = verdict
        result["verdict_reasons"] = reasons
        return result
    finally:
        if csv_path and not keep_csv and os.path.isfile(csv_path) and not csv_out_dir:
            os.remove(csv_path)


def print_human(result):
    print(f"\n=== {result['file']} ===")
    print(f"Verdict: {result['verdict']}")
    for r in result.get("verdict_reasons", []):
        print(f"  - {r}")
    if "file_size_bytes" in result:
        print(f"File size: {result['file_size_bytes']} bytes")
    if result.get("duration_ms") is not None:
        print(f"Duration: {result['duration_ms']/1000:.2f}s")
    if result.get("good_frames") is not None:
        print(f"Good frames: {result['good_frames']} ({result.get('good_bytes', 0)} bytes)")
    if result.get("missing_iterations"):
        print(f"Missing iterations: {result['missing_iterations']} ({result.get('missing_iterations_pct', 0):.2f}%)")
    if result.get("mid_file_zero_blocks"):
        print(f"Mid-file zero blocks: {len(result['mid_file_zero_blocks'])} totalling {result['mid_file_zero_block_total_bytes']} bytes")
        for b in result["mid_file_zero_blocks"][:10]:
            print(f"    offset={b['offset']} length={b['length']}")


def aggregate(results):
    agg = {
        "total_files": len(results),
        "clean": sum(1 for r in results if r["verdict"] == "CLEAN"),
        "suspect": sum(1 for r in results if r["verdict"] == "SUSPECT"),
        "corrupt": sum(1 for r in results if r["verdict"] == "CORRUPT"),
        "error": sum(1 for r in results if r["verdict"] == "ERROR"),
        "total_missing_iterations": sum(r.get("missing_iterations", 0) or 0 for r in results),
        "total_mid_file_zero_bytes": sum(r.get("mid_file_zero_block_total_bytes", 0) or 0 for r in results),
        "total_corrupt_frames": sum(r.get("corrupt_frames", 0) or 0 for r in results),
        "files_missing_end_marker": sum(1 for r in results if r.get("has_clean_end_marker") is False),
    }
    return agg


def do_compare(a_path, b_path):
    def load(p):
        with open(p) as f:
            data = json.load(f)
        # accept either {"results": [...], "aggregate": {...}} or a bare list
        if isinstance(data, dict) and "aggregate" in data:
            return data["aggregate"]
        if isinstance(data, dict) and "results" in data:
            return aggregate(data["results"])
        if isinstance(data, list):
            return aggregate(data)
        raise ValueError(f"Unrecognized JSON structure in {p}")

    a = load(a_path)
    b = load(b_path)

    print(f"\n=== A/B Comparison: {a_path} (BEFORE) vs {b_path} (AFTER) ===\n")
    keys = [
        "total_files", "clean", "suspect", "corrupt", "error",
        "total_missing_iterations", "total_mid_file_zero_bytes",
        "total_corrupt_frames", "files_missing_end_marker",
    ]
    print(f"{'metric':<32}{'before':>12}{'after':>12}{'delta':>12}")
    for k in keys:
        av, bv = a.get(k, 0), b.get(k, 0)
        delta = bv - av
        marker = ""
        if k in ("corrupt", "total_missing_iterations", "total_mid_file_zero_bytes",
                 "total_corrupt_frames", "files_missing_end_marker"):
            if delta < 0:
                marker = "  IMPROVED"
            elif delta > 0:
                marker = "  WORSE"
        print(f"{k:<32}{av:>12}{bv:>12}{delta:>+12}{marker}")

    print()
    if b.get("corrupt", 0) == 0 and a.get("corrupt", 0) > 0:
        print("RESULT: AFTER build has zero corrupt logs where BEFORE had corruption -- fix looks effective.")
    elif b.get("corrupt", 0) < a.get("corrupt", 0):
        print("RESULT: AFTER build shows fewer corrupt logs than BEFORE -- improvement, but not fully eliminated.")
    elif b.get("corrupt", 0) == a.get("corrupt", 0) == 0:
        print("RESULT: Neither run showed corruption. Increase repetitions/duration before concluding the fix works "
              "(this bug is probabilistic/timing-dependent).")
    else:
        print("RESULT: AFTER build did NOT show fewer corrupt logs than BEFORE -- fix not confirmed effective by this data.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="Blackbox .TXT/.BBL file(s) to check")
    ap.add_argument("--dir", help="Check all .TXT/.BBL files in a directory")
    ap.add_argument("--json-only", action="store_true", help="Suppress human-readable output, print JSON only")
    ap.add_argument("--out", help="Write JSON result to this file instead of stdout")
    ap.add_argument("--corrupt-frame-baseline", type=int, default=3,
                     help="Number of 'failed to decode' frames tolerated as normal EOF-probe noise (default 3)")
    ap.add_argument("--keep-csv", action="store_true", help="Keep the intermediate --debug CSV output")
    ap.add_argument("--csv-out-dir", help="Directory to save debug CSVs into (implies --keep-csv)")
    ap.add_argument("--compare", nargs=2, metavar=("BEFORE_JSON", "AFTER_JSON"),
                     help="Compare two previously-saved JSON summaries and print an A/B verdict")
    args = ap.parse_args()

    if args.compare:
        do_compare(args.compare[0], args.compare[1])
        return 0

    targets = list(args.files)
    if args.dir:
        for fn in sorted(os.listdir(args.dir)):
            if fn.upper().endswith(".TXT") or fn.upper().endswith(".BBL"):
                targets.append(os.path.join(args.dir, fn))

    if not targets:
        ap.error("No input files given. Pass file(s), or --dir, or --compare.")

    results = []
    for t in targets:
        r = check_file(
            t,
            corrupt_frame_baseline=args.corrupt_frame_baseline,
            keep_csv=args.keep_csv or bool(args.csv_out_dir),
            csv_out_dir=args.csv_out_dir,
        )
        results.append(r)
        if not args.json_only:
            print_human(r)

    agg = aggregate(results)
    output = {"results": results, "aggregate": agg}

    if not args.json_only:
        print("\n=== Aggregate ===")
        print(json.dumps(agg, indent=2))

    json_text = json.dumps(output, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(json_text)
        if not args.json_only:
            print(f"\nJSON written to {args.out}")
    else:
        if args.json_only:
            print(json_text)

    return 1 if agg["corrupt"] > 0 or agg["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
