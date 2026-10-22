#!/bin/bash
# Sequential A/B of test_sdcard_fragmentation.py over several SITL variants (never run in parallel: false stalls).
# Usage: run_frag_ab.sh ELF_DIR WORKDIR "fix4 fix3" [seed] [flights] [min_dur] [max_dur] [img_MB]
# Needs >=3 laps to be conclusive: with a 36MB card use max_dur ~40, flights ~115 (about 40 min per variant).
# Writes WORKDIR/summary.txt (one line per variant, ALLDONE at the end) and WORKDIR/<variant>_<seed>.log
ELF_DIR=$1; W=$2; VARS=${3:-"fix4 fix3"}; seed=${4:-1}; flights=${5:-115}; mind=${6:-1}; maxd=${7:-40}; mb=${8:-36}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$W"; rm -f "$W/summary.txt"
for v in $VARS; do
  img=$W/${v}_$seed.img; rm -f "$img"
  truncate -s ${mb}M "$img" && echo 'start=2048, type=c' | sfdisk -q "$img" && mkfs.vfat -F32 -s1 --offset 2048 "$img" >/dev/null || { echo "$v image creation FAILED" >> "$W/summary.txt"; continue; }
  python3 "$HERE/test_sdcard_fragmentation.py" "$ELF_DIR/SITL-$v.elf" "$img" --seed $seed --flights $flights \
      --min-dur $mind --max-dur $maxd --workdir "$W" > "$W/${v}_$seed.log" 2>&1
  echo "$v seed$seed rc=$?" >> "$W/summary.txt"
done
echo ALLDONE >> "$W/summary.txt"
