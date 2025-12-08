#!/bin/bash
# DMG Verification Script for Linux
# Verifies macOS DMG files for cross-platform contamination and architecture
# Uses 7z to extract DMG contents without modifying the original file

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <dmg-file> [dmg-file ...]"
    echo "Example: $0 *.dmg"
    exit 1
fi

for dmg_file in "$@"; do
    if [ ! -f "$dmg_file" ]; then
        echo "❌ File not found: $dmg_file"
        continue
    fi

    echo "========================================="
    echo "Verifying: $dmg_file"
    echo "========================================="

    # Create temporary directory for extraction
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf '$TEMP_DIR'" EXIT

    # Extract DMG to temp directory (does not modify original)
    echo "  Extracting DMG to temporary directory..."
    7z x -o"$TEMP_DIR" "$dmg_file" >/dev/null 2>&1 || {
        echo "  ❌ Failed to extract DMG"
        rm -rf "$TEMP_DIR"
        continue
    }

    # Check for Windows executables
    echo "  Checking for .exe files..."
    EXE_COUNT=$(find "$TEMP_DIR" -name "*.exe" -o -name "*.dll" 2>/dev/null | wc -l)
    if [ "$EXE_COUNT" -gt 0 ]; then
        echo "  ❌ ERROR: Found Windows files in macOS DMG!"
        find "$TEMP_DIR" -name "*.exe" -o -name "*.dll"
    else
        echo "  ✅ No .exe or .dll files found"
    fi

    # Check for .msi files
    MSI_COUNT=$(find "$TEMP_DIR" -name "*.msi" 2>/dev/null | wc -l)
    if [ "$MSI_COUNT" -gt 0 ]; then
        echo "  ❌ ERROR: Found .msi files in macOS DMG!"
        find "$TEMP_DIR" -name "*.msi"
    else
        echo "  ✅ No .msi files found"
    fi

    # Find the app bundle
    APP_PATH=$(find "$TEMP_DIR" -name "*.app" -type d | head -1)
    if [ -n "$APP_PATH" ]; then
        echo "  ✅ Found app bundle: $(basename "$APP_PATH")"

        # Check for binary (7z doesn't preserve execute permissions on Linux)
        BINARY=$(find "$APP_PATH/Contents/MacOS" -type f 2>/dev/null | head -1)
        if [ -n "$BINARY" ]; then
            echo "  ✅ Found executable: $(basename "$BINARY")"

            # Check if 'file' command can identify it as Mach-O
            FILE_TYPE=$(file "$BINARY" 2>/dev/null)
            if echo "$FILE_TYPE" | grep -q "Mach-O"; then
                echo "  ✅ Binary is Mach-O (macOS format)"

                # Try to identify architecture from file output
                if echo "$FILE_TYPE" | grep -q "arm64"; then
                    echo "  Architecture: arm64 (Apple Silicon)"
                elif echo "$FILE_TYPE" | grep -q "x86_64"; then
                    echo "  Architecture: x86_64 (Intel)"
                else
                    echo "  Architecture: $FILE_TYPE"
                fi
            else
                echo "  ⚠️  Binary type: $FILE_TYPE"
            fi
        else
            echo "  ⚠️  No executable found in app bundle"
        fi
    else
        echo "  ❌ No .app bundle found in DMG"
    fi

    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    echo ""
done

echo "========================================="
echo "Verification complete"
echo "========================================="
