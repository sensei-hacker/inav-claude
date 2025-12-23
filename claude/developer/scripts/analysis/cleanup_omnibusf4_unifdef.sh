#!/bin/bash
# Script to clean up OMNIBUSF4 directory using unifdef
# This removes all conditional compilation blocks for targets that don't belong in OMNIBUSF4/
#
# The OMNIBUSF4 directory contains only the OMNIBUSF4 target, so we:
# - Undefine all other targets (they're never defined when building OMNIBUSF4)
# - Keep only the code paths that apply to OMNIBUSF4

set -e

TARGET_DIR="src/main/target/OMNIBUSF4"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: $TARGET_DIR does not exist"
    exit 1
fi

echo "Cleaning up OMNIBUSF4 directory with unifdef..."
echo ""

# Backup original files
echo "Creating backups..."
cp "$TARGET_DIR/target.h" "$TARGET_DIR/target.h.backup"
cp "$TARGET_DIR/target.c" "$TARGET_DIR/target.c.backup"
echo "  - target.h.backup"
echo "  - target.c.backup"
echo ""

# Run unifdef on target.h
# We undefine all targets that are NOT OMNIBUSF4
echo "Running unifdef on target.h..."
unifdef \
    -UOMNIBUSF4PRO \
    -UOMNIBUSF4PRO_LEDSTRIPM5 \
    -UOMNIBUSF4V3 \
    -UOMNIBUSF4V3_ICM \
    -UOMNIBUSF4V3_S6_SS \
    -UOMNIBUSF4V3_S5S6_SS \
    -UOMNIBUSF4V3_S5_S6_2SS \
    -UDYSF4PRO \
    -UDYSF4PROV2 \
    -k \
    "$TARGET_DIR/target.h" > "$TARGET_DIR/target.h.tmp" || true

# unifdef returns exit code 1 if it made changes, which is what we want
# So we use || true to prevent script from exiting

if [ -f "$TARGET_DIR/target.h.tmp" ]; then
    mv "$TARGET_DIR/target.h.tmp" "$TARGET_DIR/target.h"
    echo "  ✓ target.h cleaned"
else
    echo "  ✗ Error processing target.h"
    exit 1
fi

# Run unifdef on target.c
echo "Running unifdef on target.c..."
unifdef \
    -UOMNIBUSF4PRO \
    -UOMNIBUSF4PRO_LEDSTRIPM5 \
    -UOMNIBUSF4V3 \
    -UOMNIBUSF4V3_ICM \
    -UOMNIBUSF4V3_S6_SS \
    -UOMNIBUSF4V3_S5S6_SS \
    -UOMNIBUSF4V3_S5_S6_2SS \
    -UDYSF4PRO \
    -UDYSF4PROV2 \
    -k \
    "$TARGET_DIR/target.c" > "$TARGET_DIR/target.c.tmp" || true

if [ -f "$TARGET_DIR/target.c.tmp" ]; then
    mv "$TARGET_DIR/target.c.tmp" "$TARGET_DIR/target.c"
    echo "  ✓ target.c cleaned"
else
    echo "  ✗ Error processing target.c"
    exit 1
fi

echo ""
echo "Cleanup complete!"
echo ""
echo "Summary of changes:"
echo "  - Removed all conditionals for OMNIBUSF4PRO, OMNIBUSF4V3, DYSF4PRO, DYSF4PROV2"
echo "  - Kept only code paths that apply to OMNIBUSF4 target"
echo ""
echo "Verification:"
echo "  Remaining conditionals in target.h:"
grep -c "^#if\|^#elif\|^#else" "$TARGET_DIR/target.h" || echo "  0 (perfect!)"
echo "  Remaining conditionals in target.c:"
grep -c "^#if\|^#elif\|^#else" "$TARGET_DIR/target.c" || echo "  0 (perfect!)"
echo ""
echo "To restore backups if needed:"
echo "  mv $TARGET_DIR/target.h.backup $TARGET_DIR/target.h"
echo "  mv $TARGET_DIR/target.c.backup $TARGET_DIR/target.c"
echo ""
echo "To view changes:"
echo "  diff -u $TARGET_DIR/target.h.backup $TARGET_DIR/target.h | less"
echo "  diff -u $TARGET_DIR/target.c.backup $TARGET_DIR/target.c | less"
