#!/usr/bin/env python3
"""
Detect dead code using gcc -E -dD.

Strategy:
- gcc -E -dD outputs preprocessor directives that were actually evaluated
- Dead branches don't have their directives in the output
- Compare all source #defines vs. those that appear in ANY target's output
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TARGET_GROUPS = {
    "DYSF4": ["DYSF4PRO", "DYSF4PROV2"],
    "OMNIBUSF4": ["OMNIBUSF4"],
    "OMNIBUSF4PRO": ["OMNIBUSF4PRO", "OMNIBUSF4V3", "OMNIBUSF4V3_ICM"],
    "OMNIBUSF4V3_SS": ["OMNIBUSF4V3_S6_SS", "OMNIBUSF4V3_S5S6_SS", "OMNIBUSF4V3_S5_S6_2SS"],
}

def run_preprocessor_dD(target_name, source_file, inav_root):
    """Run gcc -E -dD to get preprocessed output with directives."""
    # Create wrapper to avoid #pragma once issues
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp:
        tmp.write(f'#include "{source_file}"\n')
        tmp_path = tmp.name
    
    try:
        gcc_cmd = [
            "arm-none-eabi-gcc", "-E", "-dD",
            f"-D{target_name}",
            "-DSTM32F405xx",
            f"-I{inav_root}",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/Include",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Include",
            tmp_path
        ]
        
        result = subprocess.run(gcc_cmd, capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        print(f"Error preprocessing {target_name}: {e}", file=sys.stderr)
        return None
    finally:
        os.unlink(tmp_path)

def extract_defines_from_preprocessed(output, source_filename):
    """
    Extract #define directives from preprocessed output for our source file.
    Returns set of (line_num, macro_name, value)
    """
    defines = set()
    current_file = None
    
    for line in output.split('\n'):
        # Track which file we're in
        file_marker = re.match(r'^#\s+\d+\s+"([^"]+)"', line)
        if file_marker:
            current_file = os.path.basename(file_marker.group(1))
        
        # Extract #define directives from our source file
        if current_file == source_filename:
            define_match = re.match(r'^#define\s+(\S+)(?:\s+(.+))?$', line)
            if define_match:
                macro_name = define_match.group(1)
                value = define_match.group(2) or ""
                defines.add((macro_name, value.strip()))
    
    return defines

def get_source_defines(source_file):
    """Get all #define directives from source (with line numbers)."""
    defines = []
    
    with open(source_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # Match #define directive
            match = re.match(r'^\s*#define\s+(\S+)(?:\s+(.+))?$', line)
            if match:
                macro_name = match.group(1)
                value = match.group(2) or ""
                defines.append((line_num, macro_name, value.strip()))
    
    return defines

def check_file(source_file, directory_name, targets, inav_root):
    """Check a file for dead #define directives."""
    source_filename = os.path.basename(source_file)
    
    # Get all #defines from source
    source_defines = get_source_defines(source_file)
    
    if not source_defines:
        return []
    
    print(f"  Checking {source_filename}: {len(source_defines)} #defines in source...", end="")
    
    # Collect #defines that appear in preprocessed output for ANY target
    all_used_defines = set()
    
    for target in targets:
        output = run_preprocessor_dD(target, source_file, inav_root)
        if output:
            used = extract_defines_from_preprocessed(output, source_filename)
            all_used_defines.update(used)
    
    # Find dead #defines (in source but never in preprocessed output)
    dead_defines = []
    for line_num, macro_name, value in source_defines:
        # Check if this macro appeared in any target's output
        found = False
        for used_macro, used_value in all_used_defines:
            if used_macro == macro_name:
                found = True
                break
        
        if not found:
            dead_defines.append((line_num, macro_name, value))
    
    print(f" {len(dead_defines)} dead")
    return dead_defines

def main():
    inav_root = Path(__file__).resolve().parents[3] / "inav"
    target_dir = inav_root / "src" / "main" / "target"
    
    print("=== Dead Code Detection (gcc -E -dD) ===\n")
    
    found_dead = False
    
    for dir_name, targets in TARGET_GROUPS.items():
        dir_path = target_dir / dir_name
        
        if not dir_path.exists():
            continue
        
        print(f"{dir_name}/ ({len(targets)} targets)")
        
        for filename in ['target.h', 'target.c']:
            file_path = dir_path / filename
            if not file_path.exists():
                continue
            
            dead_defines = check_file(file_path, dir_name, targets, inav_root)
            
            if dead_defines:
                found_dead = True
                print(f"\n    Dead #defines in {filename}:")
                for line_num, macro, value in dead_defines[:10]:
                    print(f"      Line {line_num}: #define {macro} {value}")
                if len(dead_defines) > 10:
                    print(f"      ... and {len(dead_defines) - 10} more")
                print()
        
        print()
    
    print("=" * 70)
    if found_dead:
        print("❌ Dead #define directives found")
        print("=" * 70)
        return 1
    else:
        print("✅ No dead code detected")
        print("=" * 70)
        return 0

if __name__ == "__main__":
    sys.exit(main())
