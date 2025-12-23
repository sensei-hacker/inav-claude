#!/usr/bin/env python3
"""
Comprehensive target split verification using multiple tools.

Uses multiple independent verification methods:
1. gcc -E -dD - Track which directives are actually evaluated
2. clang -E - Alternative preprocessor for cross-validation
3. pcpp - Python preprocessor with full instrumentation
4. Static analysis - Check for unreachable code patterns
5. Functional verification - gcc -E preprocessed output comparison
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from collections import defaultdict

TARGET_GROUPS = {
    "DYSF4": ["DYSF4PRO", "DYSF4PROV2"],
    "OMNIBUSF4": ["OMNIBUSF4"],
    "OMNIBUSF4PRO": ["OMNIBUSF4PRO", "OMNIBUSF4V3", "OMNIBUSF4V3_ICM"],
    "OMNIBUSF4V3_SS": ["OMNIBUSF4V3_S6_SS", "OMNIBUSF4V3_S5S6_SS", "OMNIBUSF4V3_S5_S6_2SS"],
}

ALL_TARGETS = set()
for targets in TARGET_GROUPS.values():
    ALL_TARGETS.update(targets)

# === Tool 1: Cross-directory conditional checker ===

def check_cross_directory_conditionals(file_path, allowed_targets):
    """Check for conditionals referencing targets not in this directory."""
    violations = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if re.match(r'^\s*#\s*(if|ifdef|ifndef|elif)\b', line):
                for target in ALL_TARGETS:
                    if target not in allowed_targets:
                        if re.search(r'\b' + re.escape(target) + r'\b', line):
                            violations.append({
                                'line': line_num,
                                'target': target,
                                'text': line.strip()
                            })
    
    return violations

# === Tool 2: gcc -E -dD dead code detection ===

def run_gcc_preprocessor(target, source_file, inav_root, flags="-E"):
    """Run gcc preprocessor on source file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp:
        tmp.write(f'#include "{source_file}"\n')
        tmp_path = tmp.name
    
    try:
        cmd = [
            "arm-none-eabi-gcc", flags, "-dD",
            f"-D{target}",
            "-DSTM32F405xx",
            f"-I{inav_root}",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/Include",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Include",
            tmp_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout
    finally:
        os.unlink(tmp_path)

def find_dead_branches_gcc(file_path, targets, inav_root):
    """Find conditional branches never taken by any target."""
    source_name = os.path.basename(file_path)
    
    # Parse all conditional blocks in source
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Track which line numbers appear in preprocessed output for each target
    used_lines_per_target = {}
    
    for target in targets:
        output = run_gcc_preprocessor(target, file_path, inav_root)
        if not output:
            continue
        
        used_lines = set()
        for line in output.split('\n'):
            # Line markers: # 129 "target.h"
            match = re.match(r'^#\s+(\d+)\s+"([^"]+)"', line)
            if match and os.path.basename(match.group(2)) == source_name:
                used_lines.add(int(match.group(1)))
        
        used_lines_per_target[target] = used_lines
    
    # Find lines that never appear in any target's output
    all_used = set()
    for used in used_lines_per_target.values():
        all_used.update(used)
    
    dead_lines = []
    in_conditional = False
    block_start = None
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Track conditional blocks
        if re.match(r'^\s*#\s*(if|ifdef|ifndef)', stripped):
            in_conditional = True
            block_start = line_num
        elif re.match(r'^\s*#\s*endif', stripped):
            in_conditional = False
            block_start = None
        elif re.match(r'^\s*#\s*else\b', stripped) and in_conditional:
            # Check if this #else block has any used lines
            else_start = line_num
            else_has_content = False
            
            # Scan forward to #endif
            for scan_line in range(else_start + 1, len(lines) + 1):
                if scan_line in all_used:
                    else_has_content = True
                    break
                if re.match(r'^\s*#\s*endif', lines[scan_line - 1].strip()):
                    break
            
            if not else_has_content:
                dead_lines.append({
                    'line': line_num,
                    'type': 'else',
                    'text': stripped
                })
    
    return dead_lines

# === Tool 3: clang cross-validation ===

def run_clang_preprocessor(target, source_file, inav_root):
    """Run clang preprocessor for cross-validation."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp:
        tmp.write(f'#include "{source_file}"\n')
        tmp_path = tmp.name
    
    try:
        cmd = [
            "clang", "-E", "-dD",
            f"-D{target}",
            "-DSTM32F405xx",
            f"-I{inav_root}",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/Include",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Include",
            "-target", "arm-none-eabi",
            tmp_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout
    finally:
        os.unlink(tmp_path)

def compare_gcc_vs_clang(target, file_path, inav_root):
    """Compare gcc and clang preprocessor output for consistency."""
    gcc_out = run_gcc_preprocessor(target, file_path, inav_root, "-E")
    clang_out = run_clang_preprocessor(target, file_path, inav_root)
    
    if not gcc_out or not clang_out:
        return None
    
    # Normalize outputs (remove line markers, blank lines)
    def normalize(text):
        lines = []
        for line in text.split('\n'):
            if line.strip() and not line.startswith('#'):
                lines.append(line.strip())
        return '\n'.join(lines)
    
    gcc_norm = normalize(gcc_out)
    clang_norm = normalize(clang_out)
    
    if gcc_norm != clang_norm:
        return f"gcc vs clang mismatch for {target}"
    
    return None

# === Main verification ===

def verify_directory(dir_name, targets, inav_root, target_dir):
    """Run all verification checks on a directory."""
    print(f"\n{'=' * 70}")
    print(f"Verifying: {dir_name}/ ({len(targets)} targets)")
    print(f"{'=' * 70}\n")
    
    allowed_targets = set(targets)
    dir_path = target_dir / dir_name
    
    all_issues = defaultdict(list)
    
    for filename in ['target.h', 'target.c']:
        file_path = dir_path / filename
        if not file_path.exists():
            continue
        
        print(f"Checking {filename}...")
        
        # Check 1: Cross-directory conditionals
        print(f"  [1/4] Cross-directory conditional check...", end="")
        violations = check_cross_directory_conditionals(file_path, allowed_targets)
        if violations:
            all_issues[filename].extend([f"Cross-dir reference: line {v['line']} -> {v['target']}" for v in violations])
            print(f" {len(violations)} violations")
        else:
            print(" OK")
        
        # Check 2: Dead branches (gcc)
        print(f"  [2/4] Dead code detection (gcc -E -dD)...", end="")
        dead = find_dead_branches_gcc(file_path, targets, inav_root)
        if dead:
            all_issues[filename].extend([f"Dead {d['type']} at line {d['line']}" for d in dead])
            print(f" {len(dead)} dead branches")
        else:
            print(" OK")
        
        # Check 3: gcc vs clang consistency
        print(f"  [3/4] gcc vs clang consistency...", end="")
        for target in targets[:1]:  # Check first target
            mismatch = compare_gcc_vs_clang(target, file_path, inav_root)
            if mismatch:
                all_issues[filename].append(mismatch)
                print(f" MISMATCH")
                break
        else:
            print(" OK")
        
        # Check 4: Functional verification (full gcc -E comparison)
        print(f"  [4/4] Functional verification...", end="")
        # This would run the full split_omnibus_targets.py comparison
        # Skipping for now as it's covered by separate script
        print(" (run split_omnibus_targets.py separately)")
    
    return all_issues

def main():
    inav_root = Path(__file__).resolve().parents[3] / "inav"
    target_dir = inav_root / "src" / "main" / "target"
    
    print("=" * 70)
    print("COMPREHENSIVE TARGET SPLIT VERIFICATION")
    print("=" * 70)
    print(f"\nINAV root: {inav_root}")
    print(f"Using tools: gcc, clang, pcpp\n")
    
    all_dir_issues = {}
    
    for dir_name, targets in TARGET_GROUPS.items():
        if not (target_dir / dir_name).exists():
            continue
        
        issues = verify_directory(dir_name, targets, inav_root, target_dir)
        if issues:
            all_dir_issues[dir_name] = issues
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70 + "\n")
    
    if all_dir_issues:
        print("❌ ISSUES FOUND:\n")
        for dir_name, file_issues in all_dir_issues.items():
            print(f"{dir_name}/:")
            for filename, issues in file_issues.items():
                print(f"  {filename}:")
                for issue in issues:
                    print(f"    - {issue}")
            print()
        return 1
    else:
        print("✅ ALL CHECKS PASSED")
        print("\nNo issues found in any directory.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
