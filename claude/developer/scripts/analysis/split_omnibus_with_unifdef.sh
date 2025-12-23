#!/bin/bash
# Split OMNIBUSF4 targets into 4 directories using unifdef
# This preserves exact functionality while removing irrelevant #ifdef blocks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INAV_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TARGET_DIR="$INAV_ROOT/src/main/target"

echo "=== OMNIBUSF4 Target Split using unifdef (4-way) ==="
echo ""

# Step 1: Copy original files to all 4 directories
echo "Step 1: Copying original OMNIBUSF4 files to target directories..."

# DYSF4 - copy from OMNIBUSF4
mkdir -p "$TARGET_DIR/DYSF4"
cp "$TARGET_DIR/OMNIBUSF4/target.h" "$TARGET_DIR/DYSF4/target.h"
cp "$TARGET_DIR/OMNIBUSF4/target.c" "$TARGET_DIR/DYSF4/target.c"

# OMNIBUSF4PRO - copy from OMNIBUSF4
mkdir -p "$TARGET_DIR/OMNIBUSF4PRO"
cp "$TARGET_DIR/OMNIBUSF4/target.h" "$TARGET_DIR/OMNIBUSF4PRO/target.h"
cp "$TARGET_DIR/OMNIBUSF4/target.c" "$TARGET_DIR/OMNIBUSF4PRO/target.c"

# OMNIBUSF4V3_SS - copy from OMNIBUSF4
mkdir -p "$TARGET_DIR/OMNIBUSF4V3_SS"
cp "$TARGET_DIR/OMNIBUSF4/target.h" "$TARGET_DIR/OMNIBUSF4V3_SS/target.h"
cp "$TARGET_DIR/OMNIBUSF4/target.c" "$TARGET_DIR/OMNIBUSF4V3_SS/target.c"

# OMNIBUSF4 will be edited in place

echo "✓ Files copied"
echo ""

# Step 2: Use unifdef to remove irrelevant code from each directory
echo "Step 2: Removing irrelevant #ifdef blocks with unifdef..."
echo ""

# DYSF4 - Keep only DYSF4PRO, DYSF4PROV2
echo "Processing DYSF4/..."
unifdef -k \
  -UOMNIBUSF4 \
  -UOMNIBUSF4PRO \
  -UOMNIBUSF4PRO_LEDSTRIPM5 \
  -UOMNIBUSF4V3 \
  -UOMNIBUSF4V3_S6_SS \
  -UOMNIBUSF4V3_S5S6_SS \
  -UOMNIBUSF4V3_S5_S6_2SS \
  -UOMNIBUSF4V3_ICM \
  "$TARGET_DIR/DYSF4/target.h" > "$TARGET_DIR/DYSF4/target.h.new" && mv "$TARGET_DIR/DYSF4/target.h.new" "$TARGET_DIR/DYSF4/target.h"

unifdef -k \
  -UOMNIBUSF4 \
  -UOMNIBUSF4PRO \
  -UOMNIBUSF4PRO_LEDSTRIPM5 \
  -UOMNIBUSF4V3 \
  -UOMNIBUSF4V3_S6_SS \
  -UOMNIBUSF4V3_S5S6_SS \
  -UOMNIBUSF4V3_S5_S6_2SS \
  -UOMNIBUSF4V3_ICM \
  "$TARGET_DIR/DYSF4/target.c" > "$TARGET_DIR/DYSF4/target.c.new" && mv "$TARGET_DIR/DYSF4/target.c.new" "$TARGET_DIR/DYSF4/target.c"

echo "✓ DYSF4 processed"

# OMNIBUSF4 - Keep only OMNIBUSF4 (base variant)
echo "Processing OMNIBUSF4/..."
unifdef -k \
  -DDYSF4PRO=0 \
  -DDYSF4PROV2=0 \
  -DOMNIBUSF4PRO=0 \
  -DOMNIBUSF4PRO_LEDSTRIPM5=0 \
  -DOMNIBUSF4V3=0 \
  -DOMNIBUSF4V3_S6_SS=0 \
  -DOMNIBUSF4V3_S5S6_SS=0 \
  -DOMNIBUSF4V3_S5_S6_2SS=0 \
  -DOMNIBUSF4V3_ICM=0 \
  "$TARGET_DIR/OMNIBUSF4/target.h" > "$TARGET_DIR/OMNIBUSF4/target.h.new" && mv "$TARGET_DIR/OMNIBUSF4/target.h.new" "$TARGET_DIR/OMNIBUSF4/target.h"

unifdef -k \
  -DDYSF4PRO=0 \
  -DDYSF4PROV2=0 \
  -DOMNIBUSF4PRO=0 \
  -DOMNIBUSF4PRO_LEDSTRIPM5=0 \
  -DOMNIBUSF4V3=0 \
  -DOMNIBUSF4V3_S6_SS=0 \
  -DOMNIBUSF4V3_S5S6_SS=0 \
  -DOMNIBUSF4V3_S5_S6_2SS=0 \
  -DOMNIBUSF4V3_ICM=0 \
  "$TARGET_DIR/OMNIBUSF4/target.c" > "$TARGET_DIR/OMNIBUSF4/target.c.new" && mv "$TARGET_DIR/OMNIBUSF4/target.c.new" "$TARGET_DIR/OMNIBUSF4/target.c"

echo "✓ OMNIBUSF4 processed"

# OMNIBUSF4PRO - Keep OMNIBUSF4PRO, OMNIBUSF4V3, OMNIBUSF4V3_ICM (no softserial variants)
echo "Processing OMNIBUSF4PRO/..."
unifdef -k \
  -UDYSF4PRO \
  -UDYSF4PROV2 \
  -UOMNIBUSF4 \
  -UOMNIBUSF4V3_S6_SS \
  -UOMNIBUSF4V3_S5S6_SS \
  -UOMNIBUSF4V3_S5_S6_2SS \
  "$TARGET_DIR/OMNIBUSF4PRO/target.h" > "$TARGET_DIR/OMNIBUSF4PRO/target.h.new" && mv "$TARGET_DIR/OMNIBUSF4PRO/target.h.new" "$TARGET_DIR/OMNIBUSF4PRO/target.h"

unifdef -k \
  -UDYSF4PRO \
  -UDYSF4PROV2 \
  -UOMNIBUSF4 \
  -UOMNIBUSF4V3_S6_SS \
  -UOMNIBUSF4V3_S5S6_SS \
  -UOMNIBUSF4V3_S5_S6_2SS \
  "$TARGET_DIR/OMNIBUSF4PRO/target.c" > "$TARGET_DIR/OMNIBUSF4PRO/target.c.new" && mv "$TARGET_DIR/OMNIBUSF4PRO/target.c.new" "$TARGET_DIR/OMNIBUSF4PRO/target.c"

echo "✓ OMNIBUSF4PRO processed"

# OMNIBUSF4V3_SS - Keep softserial variants only
echo "Processing OMNIBUSF4V3_SS/..."
unifdef -k \
  -UDYSF4PRO \
  -UDYSF4PROV2 \
  -UOMNIBUSF4 \
  -UOMNIBUSF4PRO \
  -UOMNIBUSF4PRO_LEDSTRIPM5 \
  -UOMNIBUSF4V3_ICM \
  -DOMNIBUSF4V3=1 \
  "$TARGET_DIR/OMNIBUSF4V3_SS/target.h" > "$TARGET_DIR/OMNIBUSF4V3_SS/target.h.new" && mv "$TARGET_DIR/OMNIBUSF4V3_SS/target.h.new" "$TARGET_DIR/OMNIBUSF4V3_SS/target.h"

unifdef -k \
  -UDYSF4PRO \
  -UDYSF4PROV2 \
  -UOMNIBUSF4 \
  -UOMNIBUSF4PRO \
  -UOMNIBUSF4PRO_LEDSTRIPM5 \
  -UOMNIBUSF4V3_ICM \
  -DOMNIBUSF4V3=1 \
  "$TARGET_DIR/OMNIBUSF4V3_SS/target.c" > "$TARGET_DIR/OMNIBUSF4V3_SS/target.c.new" && mv "$TARGET_DIR/OMNIBUSF4V3_SS/target.c.new" "$TARGET_DIR/OMNIBUSF4V3_SS/target.c"

echo "✓ OMNIBUSF4V3_SS processed"
echo ""

# Step 3: Create CMakeLists.txt files
echo "Step 3: Creating CMakeLists.txt files..."

cat > "$TARGET_DIR/DYSF4/CMakeLists.txt" <<'EOF'
target_stm32f405xg(DYSF4PRO)
target_stm32f405xg(DYSF4PROV2)
EOF

cat > "$TARGET_DIR/OMNIBUSF4/CMakeLists.txt" <<'EOF'
target_stm32f405xg(OMNIBUSF4)
EOF

cat > "$TARGET_DIR/OMNIBUSF4PRO/CMakeLists.txt" <<'EOF'
# OMNIBUSF4PRO has SD card, BMP280 baro
target_stm32f405xg(OMNIBUSF4PRO)
# OMNIBUSF4V3 is similar to PRO but with UART6 inverter
target_stm32f405xg(OMNIBUSF4V3)
target_stm32f405xg(OMNIBUSF4V3_ICM SKIP_RELEASES)
EOF

cat > "$TARGET_DIR/OMNIBUSF4V3_SS/CMakeLists.txt" <<'EOF'
# OMNIBUSF4V3 softserial variants with different S5/S6 timer configurations
target_stm32f405xg(OMNIBUSF4V3_S6_SS)
target_stm32f405xg(OMNIBUSF4V3_S5S6_SS)
target_stm32f405xg(OMNIBUSF4V3_S5_S6_2SS)
EOF

echo "✓ CMakeLists.txt files created"
echo ""

echo "=== Split Complete! ==="
echo ""
echo "Next step: Run verification script"
echo "  python3 split_omnibus_targets.py"
