#!/bin/bash
# Tests cmake/validate-pg-for-release.sh via --current-file hook against throwaway git repos.
# Usage: test_validate_pg.sh [path-to-validate-pg-for-release.sh]
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=${1:-$HERE/../../../../../inav3/cmake/validate-pg-for-release.sh}
[ -f "$SRC" ] || { echo "SETUP ERROR: script not found: $SRC"; exit 2; }
WORK=$(mktemp -d) || exit 2
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0

g() { git -C "$R" -c user.name=t -c user.email=t@t -c commit.gpgsign=false -c tag.gpgsign=false "$@" >/dev/null 2>&1; }
db() { # db line... -> write working DB
  : > "$R/cmake/pg_struct_sizes.reference.db"
  for l in "$@"; do set -- $l; printf "%-30s %3s %s\n" "$1" "$2" "$3" >> "$R/cmake/pg_struct_sizes.reference.db"; done; }
newrepo() { R="$WORK/$1"; mkdir -p "$R/cmake"; git -C "$R" init -q 2>/dev/null
  cp "$SRC" "$R/cmake/validate-pg-for-release.sh"; chmod +x "$R/cmake/validate-pg-for-release.sh"
  g config core.autocrlf false; }
commit() { g add -A; g commit -q -m "$1" --allow-empty; }
cur() { printf "%s\n" "$@" > "$R/current.txt"; }
check() { # name expected_exit
  local out rc
  out=$(cd "$R" && bash cmake/validate-pg-for-release.sh --current-file "$R/current.txt" 2>&1); rc=$?
  # Guard against coincidental exit codes: the --current-file hook must bypass toolchain/build.
  if echo "$out" | grep -qE 'Building reference target|Creating build directory|CMake Error|arm-none-eabi-gcc not found|Build failed'; then
    echo "FAIL  $1: script ignored --current-file and tried to build (exit $rc)"; FAIL=$((FAIL+1))
  elif [ "$rc" = "$2" ]; then echo "PASS  $1 (exit $rc)"; PASS=$((PASS+1))
  else echo "FAIL  $1: expected exit $2, got $rc"; echo "$out" | tail -4 | sed 's/^/        /'; FAIL=$((FAIL+1)); fi; }

# 1 wraparound
newrepo c1; db "fooConfig_t 8 15"; commit base; g tag 1.0.0; commit later
cur "fooConfig_t 12 0"; check "1 wraparound v15->v0 passes but DB at HEAD is stale" 3

# 2 dev-DB drift
newrepo c2; db "fooConfig_t 8 3"; commit base; g tag 1.0.0
db "fooConfig_t 12 4"; commit "dev auto-update"
cur "fooConfig_t 12 4"; check "2a drift: changed vs shipped, version differs" 0
db "fooConfig_t 12 3"; commit "dev drift 2"
cur "fooConfig_t 12 3"; check "2b drift: size changed vs shipped, same version" 1

# 3 size changed same version
newrepo c3; db "fooConfig_t 8 3"; commit base; g tag 1.0.0; commit later
cur "fooConfig_t 12 3"; check "3 size changed, same version" 1

# 4 negatives/positives
newrepo c4; db "fooConfig_t 8 3"; commit base; g tag 1.0.0; commit later
cur "fooConfig_t 8 3"; check "4a size unchanged" 0
cur "fooConfig_t 8 3" "barConfig_t 4 0"; check "4b new struct passes but DB at HEAD lacks it" 3

newrepo c4c; db "fooConfig_t 8 3"; commit base; g tag 1.0.0
db "fooConfig_t 12 4"; commit rc; g tag 1.1.0-RC1; commit later
cur "fooConfig_t 12 3"; check "4c RC tag ignored as baseline" 1

newrepo c4d; db "fooConfig_t 8 3"; commit base; g tag 1.0.0
db "fooConfig_t 12 3"; commit head; g tag 1.0.1
cur "fooConfig_t 12 3"; check "4d tag at HEAD skipped" 1

# 6 DB committed at HEAD matches the validated sizes
newrepo c6; db "fooConfig_t 8 15"; commit base; g tag 1.0.0
db "fooConfig_t 12 0"; commit "update PG db"
cur "fooConfig_t 12 0"; check "6a wraparound with DB committed" 0
# 6b: --current-file never rewrites the working DB
newrepo c6b; db "fooConfig_t 8 3"; commit base; g tag 1.0.0; commit later
cur "fooConfig_t 8 3" "barConfig_t 4 0"; check "6b new struct, DB stale" 3
if git -C "$R" diff --quiet -- cmake/pg_struct_sizes.reference.db; then echo "PASS  6c --current-file leaves DB untouched"; PASS=$((PASS+1)); else echo "FAIL  6c --current-file modified the DB"; FAIL=$((FAIL+1)); fi

# 6d committed DB in a different line order is not a difference
newrepo c6d; db "fooConfig_t 8 3" "barConfig_t 4 0"; commit base; g tag 1.0.0
printf "%-30s %3s %s\n" fooConfig_t 8 3 barConfig_t 4 0 > "$R/cmake/pg_struct_sizes.reference.db"; commit reorder
cur "fooConfig_t 8 3" "barConfig_t 4 0"; check "6d DB line order ignored" 0

# 5 baseline tag lacks DB
newrepo c5; echo x > "$R/README"; commit base; g tag 1.0.0
db "fooConfig_t 8 3"; commit later
cur "fooConfig_t 8 3"; check "5 baseline tag has no DB" 2

echo; echo "passed=$PASS failed=$FAIL"; [ $FAIL -eq 0 ]
