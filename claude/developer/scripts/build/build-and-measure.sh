#!/bin/bash
#
# Brief: Build INAV firmware targets at a given commit with the CI size-diff
#        recipe and print the canonical flash/RAM usage.
# Usage: build-and-measure.sh <sha> <branch-name> <build-dir-suffix> [TARGETS...]
# Example: build-and-measure.sh 939cfb8 measure-pr11656-head pr MATEKF405 MATEKF722
#
# What problem this solves: measuring a PR's flash/RAM footprint requires
# identical toolchain + flags on both the PR head and its base. This script
# reproduces the exact CI size-diff build (inav/.github/workflows/ci.yml) and
# the canonical measurement (.github/scripts/extract-size-report.sh), so the
# numbers match the project's own size bot.
# When to use it: any "how much flash/RAM does branch/commit X use vs Y" task.
#
# Must be run from an inav checkout root (repo lock held by caller).
# Recipe matches CI exactly: cmake -DWARNINGS_AS_ERRORS=ON -DMAIN_COMPILE_OPTIONS=-pipe -G Ninja ..
#   (default build type, no -DCMAKE_BUILD_TYPE), then ninja <targets>.
# Measurement: flash = text + data ; ram = data + bss (arm-none-eabi-size -B).

set -euo pipefail

SHA=${1:?usage: build-and-measure.sh <sha> <branch-name> <build-dir-suffix> [TARGETS...]}
BRANCH=${2:?usage: build-and-measure.sh <sha> <branch-name> <build-dir-suffix> [TARGETS...]}
SUFFIX=${3:?usage: build-and-measure.sh <sha> <branch-name> <build-dir-suffix> [TARGETS...]}
shift 3
TARGETS=("$@")
[ ${#TARGETS[@]} -gt 0 ] || TARGETS=(MATEKF405 MATEKF722)  # CI representative F405/F722 pair

SIZE_TOOL=${SIZE_TOOL:-$(compgen -G 'tools/arm-gnu-toolchain-*/bin/arm-none-eabi-size' | head -n1)}
[ -n "$SIZE_TOOL" ] || SIZE_TOOL=arm-none-eabi-size

echo "==> checking out $BRANCH @ $SHA"
git checkout -f -B "$BRANCH" "$SHA"
git status --short --branch | head -3

BUILD_DIR="build-size-$SUFFIX"
echo "==> configuring $BUILD_DIR (CI recipe)"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
( cd "$BUILD_DIR" && cmake -DWARNINGS_AS_ERRORS=ON -DMAIN_COMPILE_OPTIONS=-pipe -G Ninja .. > cmake-config.log 2>&1 )

echo "==> building ${TARGETS[*]}"
( cd "$BUILD_DIR" && ninja -j"$(nproc)" "${TARGETS[@]}" )

echo "==> size report"
for T in "${TARGETS[@]}"; do
    ELF="$BUILD_DIR/bin/$T.elf"
    read -r text data bss _dec _hex _name < <("$SIZE_TOOL" -B "$ELF" | tail -n1)
    flash=$((text + data))
    ram=$((data + bss))
    printf '%-12s flash=%10d  ram=%10d  (text=%d data=%d bss=%d)\n' "$T" "$flash" "$ram" "$text" "$data" "$bss"
done
