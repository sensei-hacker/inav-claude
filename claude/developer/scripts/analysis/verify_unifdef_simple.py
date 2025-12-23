#!/usr/bin/env python3
"""
Simple verification using unifdef -s to extract controlling macros.
Much simpler than parsing #if directives ourselves!
"""

import subprocess
import sys
from pathlib import Path

TARGET_GROUPS = {
    "DYSF4": ["DYSF4PRO", "DYSF4PROV2"],
    "OMNIBUSF4": ["OMNIBUSF4"],
    "OMNIBUSF4PRO": ["OMNIBUSF4PRO", "OMNIBUSF4V3", "OMNIBUSF4V3_ICM", "OMNIBUSF4PRO_LEDSTRIPM5"],
    "OMNIBUSF4V3_SS": ["OMNIBUSF4V3_S6_SS", "OMNIBUSF4V3_S5S6_SS", "OMNIBUSF4V3_S5_S6_2SS"],
}

ALL_TARGETS = set()
for targets in TARGET_GROUPS.values():
    ALL_TARGETS.update(targets)

def get_controlling_macros(file_path):
    """Use unifdef -s to extract controlling macros."""
    result = subprocess.run(
        ["unifdef", "-s", str(file_path)],
        capture_output=True,
        text=True
    )
    return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()

def main():
    inav_root = Path(__file__).resolve().parents[3] / "inav"
    target_dir = inav_root / "src" / "main" / "target"
    
    print("=== Target Verification (unifdef -s) ===\n")
    
    found_issues = False
    
    for dir_name, allowed_targets in TARGET_GROUPS.items():
        dir_path = target_dir / dir_name
        
        if not dir_path.exists():
            continue
        
        allowed_set = set(allowed_targets)
        print(f"{dir_name}/ (allowed: {', '.join(allowed_targets)})")
        
        for filename in ['target.h', 'target.c']:
            file_path = dir_path / filename
            
            if not file_path.exists():
                continue
            
            macros = get_controlling_macros(file_path)
            
            # Find violations
            violations = []
            for macro in macros:
                if macro not in allowed_set and macro in ALL_TARGETS:
                    violations.append(macro)
            
            if violations:
                found_issues = True
                print(f"  {filename}: ❌ {len(violations)} violation(s)")
                for v in violations:
                    print(f"    - {v} (not allowed here)")
            else:
                print(f"  {filename}: ✅ OK")
        
        print()
    
    print("=" * 60)
    if found_issues:
        print("❌ VIOLATIONS FOUND")
        return 1
    else:
        print("✅ ALL CHECKS PASSED")
        return 0

if __name__ == "__main__":
    sys.exit(main())
