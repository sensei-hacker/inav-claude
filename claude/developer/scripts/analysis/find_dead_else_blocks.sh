#!/bin/bash
# Simple script to find #else blocks containing cross-directory conditionals

TARGET_DIR="$1"

if [ -z "$TARGET_DIR" ]; then
    echo "Usage: $0 <target_directory>"
    echo "Example: $0 src/main/target/OMNIBUSF4PRO"
    exit 1
fi

echo "Searching for #else blocks in $TARGET_DIR..."
echo ""

for file in "$TARGET_DIR/target.h" "$TARGET_DIR/target.c"; do
    if [ ! -f "$file" ]; then
        continue
    fi
    
    echo "=== $file ==="
    
    # Find #else followed by comments mentioning other target families
    grep -n -A 3 "^#else" "$file" | grep -E "(OMNIBUSF4PRO|OMNIBUSF4V3|DYSF4|pad labelled)"
    
    echo ""
done
