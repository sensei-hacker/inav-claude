#!/bin/bash
# Generic firmware hex file renaming script for INAV releases
# Removes CI build suffix and adds release version

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version> [directory]"
    echo ""
    echo "Examples:"
    echo "  $0 9.0.0-RC3              # Rename files in current directory"
    echo "  $0 9.0.0-RC3 /path/to/hex # Rename files in specified directory"
    echo "  $0 9.0.0                  # For final releases (no RC suffix)"
    echo "  $0 9.0.1                  # For patch releases"
    exit 1
fi

VERSION="$1"
DIRECTORY="${2:-.}"

# Change to target directory
cd "$DIRECTORY"

# Count files before renaming
BEFORE_COUNT=$(ls inav_*_ci-*.hex 2>/dev/null | wc -l)

if [ "$BEFORE_COUNT" -eq 0 ]; then
    echo "❌ No hex files matching pattern 'inav_*_ci-*.hex' found in: $DIRECTORY"
    exit 1
fi

echo "Found $BEFORE_COUNT hex files to rename"
echo "Version: $VERSION"
echo ""

# Rename files
RENAMED=0
for f in inav_*_ci-*.hex; do
    # Extract target name (between version number and _ci-)
    # Pattern: inav_X.Y.Z_TARGETNAME_ci-YYYYMMDD-hash.hex
    target=$(echo "$f" | sed -E 's/inav_[0-9]+\.[0-9]+\.[0-9]+_(.*)_ci-.*/\1/')

    # Extract base version (X.Y.Z) from filename
    base_version=$(echo "$f" | sed -E 's/inav_([0-9]+\.[0-9]+\.[0-9]+)_.*/\1/')

    # Create new name: inav_VERSION_TARGET.hex
    newname="inav_${VERSION}_${target}.hex"

    # Rename file
    mv "$f" "$newname"
    RENAMED=$((RENAMED + 1))
done

echo "✅ Successfully renamed $RENAMED files"
echo ""
echo "Sample renamed files:"
ls inav_${VERSION}_*.hex | head -5
echo ""
echo "Total files after renaming: $(ls inav_${VERSION}_*.hex | wc -l)"
