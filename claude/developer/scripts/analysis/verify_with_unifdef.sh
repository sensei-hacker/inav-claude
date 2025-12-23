#!/bin/bash
# Use unifdef -s to verify target directories don't reference wrong targets

set -e

INAV_ROOT="${1:-/home/raymorris/Documents/planes/inavflight/inav}"
TARGET_DIR="$INAV_ROOT/src/main/target"

# Define which targets belong in which directories
declare -A GROUPS
GROUPS[DYSF4]="DYSF4PRO DYSF4PROV2"
GROUPS[OMNIBUSF4]="OMNIBUSF4"
GROUPS[OMNIBUSF4PRO]="OMNIBUSF4PRO OMNIBUSF4V3 OMNIBUSF4V3_ICM OMNIBUSF4PRO_LEDSTRIPM5"
GROUPS[OMNIBUSF4V3_SS]="OMNIBUSF4V3_S6_SS OMNIBUSF4V3_S5S6_SS OMNIBUSF4V3_S5_S6_2SS"

echo "=== Target Directory Verification (unifdef -s) ==="
echo ""

# Build set of all valid targets
ALL_TARGETS=()
for targets in "${GROUPS[@]}"; do
    ALL_TARGETS+=($targets)
done

FOUND_VIOLATIONS=0

for dir_name in "${!GROUPS[@]}"; do
    dir_path="$TARGET_DIR/$dir_name"
    
    if [ ! -d "$dir_path" ]; then
        continue
    fi
    
    # Get allowed targets for this directory
    allowed_targets=(${GROUPS[$dir_name]})
    
    echo "$dir_name/ (allowed: ${allowed_targets[*]})"
    
    for file in target.h target.c; do
        file_path="$dir_path/$file"
        
        if [ ! -f "$file_path" ]; then
            continue
        fi
        
        # Get controlling macros from file
        controlling_macros=$(unifdef -s "$file_path" 2>&1 | sort -u)
        
        # Check each controlling macro
        violations=""
        for macro in $controlling_macros; do
            # Is this macro allowed in this directory?
            is_allowed=0
            for allowed in "${allowed_targets[@]}"; do
                if [ "$macro" == "$allowed" ]; then
                    is_allowed=1
                    break
                fi
            done
            
            # If not allowed, is it a known target macro from another directory?
            if [ $is_allowed -eq 0 ]; then
                for check_target in "${ALL_TARGETS[@]}"; do
                    if [ "$macro" == "$check_target" ]; then
                        violations="$violations\n    ❌ $macro (belongs in different directory)"
                        FOUND_VIOLATIONS=1
                        break
                    fi
                done
            fi
        done
        
        if [ -n "$violations" ]; then
            echo "  $file:"
            echo -e "$violations"
        else
            echo "  $file: ✅ OK"
        fi
    done
    echo ""
done

echo "=========================================="
if [ $FOUND_VIOLATIONS -eq 0 ]; then
    echo "✅ NO VIOLATIONS FOUND"
    exit 0
else
    echo "❌ VIOLATIONS FOUND"
    exit 1
fi
