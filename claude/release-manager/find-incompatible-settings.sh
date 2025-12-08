#!/bin/bash
# Find incompatible settings between two INAV releases
# Usage: ./find-incompatible-settings.sh 8.0.1 9.0.0-RC3

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <old-version> <new-version>"
    echo ""
    echo "Examples:"
    echo "  $0 8.0.1 9.0.0-RC3"
    echo "  $0 8.0.1 upstream/maintenance-9.x"
    echo ""
    exit 1
fi

OLD=$1
NEW=$2

echo "=========================================="
echo "Incompatible Settings: $OLD → $NEW"
echo "=========================================="
echo ""

# Check if we're in the inav directory
if [ ! -d ".git" ] || [ ! -f "src/main/fc/settings.yaml" ]; then
    echo "❌ Error: Must run this script from the inav repository root"
    exit 1
fi

# Check if versions exist
if ! git rev-parse "$OLD" >/dev/null 2>&1; then
    echo "❌ Error: Version '$OLD' not found"
    echo "Available tags:"
    git tag | grep "^8\." | tail -5
    exit 1
fi

if ! git rev-parse "$NEW" >/dev/null 2>&1; then
    echo "❌ Error: Version '$NEW' not found"
    exit 1
fi

echo "📋 Analyzing settings.yaml changes..."
echo ""

# Extract removed/renamed settings
REMOVED=$(git diff $OLD..$NEW -- src/main/fc/settings.yaml | \
  grep -E "^[\-].*- name:" | \
  grep -v "^\-\-\-" | \
  sed 's/^-.*- name: //' | \
  sort -u)

if [ -z "$REMOVED" ]; then
    echo "✅ No settings were removed or renamed"
    echo ""
    exit 0
fi

echo "⚠️  REMOVED or RENAMED Settings:"
echo "================================"
echo ""
echo "$REMOVED" | while read setting; do
    echo "  - $setting"
done

echo ""
echo "📝 Next Steps:"
echo "=============="
echo ""
echo "1. Review the full diff to determine if settings were:"
echo "   - RENAMED (old name removed, new name added)"
echo "   - REMOVED (functionality deprecated)"
echo ""
echo "2. Run this command to see context:"
echo "   git diff $OLD..$NEW -- src/main/fc/settings.yaml | less"
echo ""
echo "3. Create incompatibility report:"
echo "   - Document renamed settings (old → new)"
echo "   - Explain why settings were removed"
echo "   - Provide migration instructions"
echo ""
echo "4. Add to release notes:"
echo "   - \"Incompatible Settings Changes\" section"
echo "   - Migration examples"
echo ""

# Try to identify some obvious renames
echo "🔍 Checking for common rename patterns..."
echo ""

git diff $OLD..$NEW -- src/main/fc/settings.yaml | \
  grep -E "^[\+\-].*- name:" | \
  grep -v "^\-\-\-\|^\+\+\+" | \
  awk '
    /^-.*- name:/ {
      old = $0
      sub(/^-.*- name: /, "", old)
      removed[old] = 1
    }
    /^\+.*- name:/ {
      new = $0
      sub(/^\+.*- name: /, "", new)
      added[new] = 1

      # Check for similar names (potential renames)
      for (r in removed) {
        if (index(new, r) > 0 || index(r, new) > 0) {
          print "  POSSIBLE RENAME: " r " → " new
        }
      }
    }
  '

echo ""
echo "✅ Analysis complete"
echo ""
