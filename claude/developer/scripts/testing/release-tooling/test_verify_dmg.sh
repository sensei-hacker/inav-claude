#!/bin/bash
# Tests verify-dmg-contents.sh using a stub `7z` that mimics wrapper-error exits.
SCRIPT=$(cd "$(dirname "$0")/../../../../release-manager/scripts" && pwd)/verify-dmg-contents.sh
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/bin"
touch "$WORK/fake.dmg"

# Stub: STUB_MODE = full_ok | full_headers_err | full_exe_headers_err | empty_fail | partial_noapp
cat > "$WORK/bin/7z" <<'STUB'
#!/bin/bash
out=""; for a in "$@"; do case "$a" in -o*) out="${a#-o}";; esac; done
mkapp() { mkdir -p "$out/INAV.app/Contents/MacOS"; printf '\xcf\xfa\xed\xfe' > "$out/INAV.app/Contents/MacOS/inav"; }
case "$STUB_MODE" in
  full_ok) mkapp; exit 0;;
  full_headers_err) mkapp; echo "ERROR: Headers Error : outer wrapper" >&2; exit 2;;
  full_exe_headers_err) mkapp; touch "$out/INAV.app/Contents/Resources.exe"; echo "ERROR: Headers Error" >&2; exit 2;;
  empty_fail) echo "ERROR: Can not open the file as archive" >&2; exit 2;;
  partial_noapp) mkdir -p "$out/junk"; touch "$out/junk/a.txt"; echo "ERROR: Headers Error" >&2; exit 2;;
esac
STUB
chmod +x "$WORK/bin/7z"

fail=0
run() { # name mode expect_rc expect_grep [absent_grep]
    local name=$1 mode=$2 erc=$3 egrep=$4 absent=$5 out rc
    out=$(PATH="$WORK/bin:$PATH" STUB_MODE=$mode "$SCRIPT" "$WORK/fake.dmg" 2>&1); rc=$?
    local ok=1
    [ "$rc" -eq "$erc" ] || ok=0
    echo "$out" | grep -q -- "$egrep" || ok=0
    [ -z "$absent" ] || ! echo "$out" | grep -q -- "$absent" || ok=0
    if [ $ok -eq 1 ]; then echo "PASS $name"; else echo "FAIL $name (rc=$rc, wanted rc=$erc and /$egrep/)"; echo "$out" | sed 's/^/    /'; fail=1; fi
}
run "clean DMG passes"                    full_ok             0 "Found app bundle"
run "wrapper error still inspected"       full_headers_err    0 "Found app bundle" "Failed to extract"
run "wrapper error output is shown"       full_headers_err    0 "Headers Error"
run "exe found after wrapper error fails" full_exe_headers_err 1 "Found Windows files"
run "nothing extracted fails loudly"      empty_fail          1 "Failed to extract"
run "extracted but no app fails loudly"   partial_noapp       1 "No .app bundle"
exit $fail
