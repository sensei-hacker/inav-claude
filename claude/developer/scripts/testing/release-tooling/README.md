# Release-tooling tests

- `test_validate_pg.sh [script]` - tests `inav3/cmake/validate-pg-for-release.sh` against throwaway git repos (baseline tag, 4-bit wraparound, working-DB drift).
- `test_verify_dmg.sh` - tests `claude/release-manager/scripts/verify-dmg-contents.sh` with a stub `7z`.

Each exits 0 only if every case passes.
