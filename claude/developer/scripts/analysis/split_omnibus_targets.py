#!/usr/bin/env python3
"""
Script to split OMNIBUSF4 targets into 4 directories and verify correctness.
Uses gcc -E to compare preprocessed output before and after split.

Updated 2025-12-22:
- Uses -P flag to suppress line markers (reduces output by 50-70%)
- Uses -w flag to suppress warnings
- Filters blank lines with grep
- Improved progress reporting with counters
- See: claude/developer/docs/gcc-preprocessing-techniques.md

CRITICAL: After splitting, you MUST add target aliasing for variants!
See: claude/developer/investigations/target-split/README-target-aliasing.md
Example: OMNIBUSF4V3_ICM must be aliased to OMNIBUSF4V3 at top of target.h
"""

import os
import subprocess
import sys
import difflib

# Configuration
INAV_ROOT = "/home/raymorris/Documents/planes/inavflight/inav"
TARGET_DIR = f"{INAV_ROOT}/src/main/target"
BEFORE_DIR = "/tmp/omnibus-preprocess-before"
AFTER_DIR = "/tmp/omnibus-preprocess-after"

# Group definitions
GROUPS = {
    "DYSF4": ["DYSF4PRO", "DYSF4PROV2"],
    "OMNIBUSF4": ["OMNIBUSF4"],
    "OMNIBUSF4PRO": ["OMNIBUSF4PRO", "OMNIBUSF4V3", "OMNIBUSF4V3_ICM"],
    "OMNIBUSF4V3_SS": ["OMNIBUSF4V3_S6_SS", "OMNIBUSF4V3_S5S6_SS", "OMNIBUSF4V3_S5_S6_2SS"]
}

ALL_TARGETS = []
for targets in GROUPS.values():
    ALL_TARGETS.extend(targets)

def run_cmd(cmd, cwd=None):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def preprocess_target(target_name, target_dir, output_dir):
    """Preprocess target.h and target.c for a specific target."""
    os.makedirs(output_dir, exist_ok=True)

    # Use -P to suppress line markers, -w to suppress warnings
    # This dramatically reduces output size and noise
    gcc_cmd_base = f"arm-none-eabi-gcc -E -P -w -D{target_name} -DSTM32F405xx -I{INAV_ROOT}/src/main -I{INAV_ROOT}/lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/Include -I{INAV_ROOT}/lib/main/STM32F4/Drivers/CMSIS/Include"

    # Preprocess target.h - redirect stderr to suppress warnings
    ret_h, out, err = run_cmd(
        f"{gcc_cmd_base} {target_dir}/target.h 2>/dev/null | grep -v '^[[:space:]]*$' > {output_dir}/{target_name}_target.h",
        cwd=INAV_ROOT
    )

    # Preprocess target.c
    ret_c, out, err = run_cmd(
        f"{gcc_cmd_base} {target_dir}/target.c 2>/dev/null | grep -v '^[[:space:]]*$' > {output_dir}/{target_name}_target.c",
        cwd=INAV_ROOT
    )

    # Check if output files were created (warnings return non-zero but still produce output)
    h_exists = os.path.exists(f"{output_dir}/{target_name}_target.h") and os.path.getsize(f"{output_dir}/{target_name}_target.h") > 0
    c_exists = os.path.exists(f"{output_dir}/{target_name}_target.c") and os.path.getsize(f"{output_dir}/{target_name}_target.c") > 0

    return h_exists and c_exists

def normalize_preprocessed_line(line):
    """Normalize preprocessor output by removing path-specific info."""
    # Since we use -P flag, there are no line markers to normalize
    # Just remove any remaining path-specific info in error messages (unlikely)
    import re

    # Match lines like: /full/path/OMNIBUSF4/target.h:18:9: warning
    line = re.sub(r'[^:]+/(?:OMNIBUSF4|DYSF4|OMNIBUSF4PRO|OMNIBUSF4V3_SS)/([^:]+):', r'\1:', line)

    return line

def compare_files(file1, file2):
    """Compare two files and return diff if different (ignoring path differences)."""
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            content1 = [normalize_preprocessed_line(line) for line in f1.readlines()]
            content2 = [normalize_preprocessed_line(line) for line in f2.readlines()]

        if content1 == content2:
            return None

        diff = list(difflib.unified_diff(content1, content2, fromfile=file1, tofile=file2, lineterm=''))
        return '\n'.join(diff[:100])  # Limit diff output
    except Exception as e:
        return f"Error comparing files: {e}"

def verify_split():
    """Compare preprocessed output before and after split."""
    print("\n=== Verifying Split ===\n")

    all_match = True
    for target in ALL_TARGETS:
        print(f"Checking {target}...")

        # Compare target.h
        before_h = f"{BEFORE_DIR}/{target}_target.h"
        after_h = f"{AFTER_DIR}/{target}_target.h"
        diff_h = compare_files(before_h, after_h)

        # Compare target.c
        before_c = f"{BEFORE_DIR}/{target}_target.c"
        after_c = f"{AFTER_DIR}/{target}_target.c"
        diff_c = compare_files(before_c, after_c)

        if diff_h:
            print(f"  ❌ target.h DIFFERS")
            print(f"     First 50 lines of diff:")
            print(diff_h[:2000])
            all_match = False
        else:
            print(f"  ✅ target.h matches")

        if diff_c:
            print(f"  ❌ target.c DIFFERS")
            print(f"     First 50 lines of diff:")
            print(diff_c[:2000])
            all_match = False
        else:
            print(f"  ✅ target.c matches")

    return all_match

def main():
    print("OMNIBUSF4 Target Split Verification")
    print("=" * 50)

    # Check that before files exist
    if not os.path.exists(BEFORE_DIR):
        print(f"ERROR: {BEFORE_DIR} doesn't exist!")
        print("Run preprocessing on original targets first.")
        return 1

    # Step 1: Preprocess after-split targets
    print("\n=== Preprocessing Split Targets ===\n")
    total_targets = sum(len(targets) for targets in GROUPS.values())
    current = 0

    for group_name, targets in GROUPS.items():
        group_dir = f"{TARGET_DIR}/{group_name}"
        if not os.path.exists(group_dir):
            print(f"ERROR: {group_dir} doesn't exist!")
            return 1

        for target in targets:
            current += 1
            print(f"[{current}/{total_targets}] Preprocessing {target} from {group_name}/...", end=' ', flush=True)
            success = preprocess_target(target, group_dir, AFTER_DIR)
            if not success:
                print(f"❌ FAILED")
                return 1
            print(f"✅")

    # Step 2: Compare
    if verify_split():
        print("\n" + "=" * 50)
        print("✅ SUCCESS! All targets match exactly.")
        print("=" * 50)
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ FAILURE! Some targets differ.")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())
