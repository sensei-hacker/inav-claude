# Incompatible Settings Workflow - Added to Release Process

**Date Added:** 2025-12-07
**First Used:** 9.0.0-RC3 release

## Overview

Added automated workflow to identify and document CLI settings that have been renamed or removed between INAV releases. This prevents users from being surprised by RED errors when loading their old `diff all` into new firmware.

## Why This Matters

When users upgrade major versions (e.g., 8.x → 9.x):
1. They export configuration with `diff all` from old version
2. Flash new firmware
3. Load their old diff into new CLI
4. **Any renamed/removed settings show in RED and fail**

Without documentation, users don't know:
- Which settings changed
- What to rename them to
- Why they were removed

## What Was Added

### 1. Detection Script
**File:** `claude/release-manager/find-incompatible-settings.sh`

**Usage:**
```bash
./find-incompatible-settings.sh 8.0.1 9.0.0-RC3
```

**Output:**
- List of removed/renamed settings
- Suggestions for next steps
- Attempts to identify renames automatically

### 2. Documentation Section
**Added to:** `claude/release-manager/README.md`

**Sections:**
- "Identifying Incompatible Settings Changes" - Full workflow explanation
- "Release Notes Template for Incompatibilities" - Copy-paste template
- Updated "Release Workflow" - Added step 4c: Identify incompatible settings
- Updated "Pre-Release Checklist" - Added checkbox for incompatibility check

### 3. Release Notes Template

**Where to add:** Both firmware AND configurator release notes

**Template:**
```markdown
## ⚠️ Incompatible Settings Changes

The following CLI settings have been renamed or removed in INAV X.0. When loading an older `diff all`, these will show in RED:

**Renamed Settings:**
- `old_name` → `new_name` - Brief explanation

**Removed Settings:**
- `removed_setting` - Reason / replacement

**Migration Instructions:**
1. Export configuration from old version
2. Flash new firmware with Full Chip Erase
3. Edit saved diff and update renamed settings
4. Load edited diff into new CLI
```

## Workflow for Future Releases

### During Release Preparation

1. **Run detection script:**
   ```bash
   cd claude/release-manager
   ./find-incompatible-settings.sh <previous-version> <new-version>
   ```

2. **Review diff for context:**
   ```bash
   git diff 8.0.1..9.0.0-RC3 -- src/main/fc/settings.yaml | less
   ```

3. **Determine renames vs removals:**
   - If old name removed AND new name added = **RENAME**
   - If old name removed with no similar new name = **REMOVED**

4. **Create incompatibility section:**
   - Copy template from README.md
   - Fill in renamed settings (old → new)
   - Fill in removed settings with explanations
   - Add to both firmware and configurator release notes

5. **Optional: Create reference doc:**
   - Like `9.0.0-INCOMPATIBLE-SETTINGS.md`
   - For detailed migration instructions
   - For user support reference

### Checklist Items

**Pre-Release Checklist:**
- [ ] Incompatible settings changes identified and added to release notes

**Release Workflow Step 4:**
- Generate changelog
  - ├── List PRs since last tag
  - ├── Categorize changes
  - ├── **Identify incompatible settings** (./find-incompatible-settings.sh)
  - ├── Add incompatibility section to release notes
  - └── Format release notes

## Example: 9.0.0-RC3

### Settings Found
- 3 renamed settings (controlrate_profile, mixer_pid_profile_linking, osd_pan_servo_pwm2centideg)
- 3 removed settings (reboot_character, PG_CONTROL_RATE_PROFILES, PG_SERIAL_CONFIG)

### Documents Created
1. `9.0.0-INCOMPATIBLE-SETTINGS.md` - Detailed reference
2. `9.0.0-RC3-SETTINGS-REVIEW.md` - Summary and recommendations
3. Release notes updated manually with incompatibility section

### Time Taken
- Script execution: ~5 seconds
- Manual review and categorization: ~10 minutes
- Documentation creation: ~15 minutes
- **Total: ~30 minutes** (one-time, reusable for RC1/RC2/Final)

## Benefits

1. **User Experience:** Users know what to expect when upgrading
2. **Support Reduction:** Fewer questions about "why is this RED in CLI?"
3. **Professional:** Shows attention to detail and user needs
4. **Automated:** Script does the hard work, just need manual review
5. **Documented:** Clear migration path for users

## Maintenance

The script and templates should work for all future releases with minimal changes. Only update if:
- settings.yaml file location changes
- Git workflow changes significantly
- Better automation becomes available

## Related Files

- `claude/release-manager/find-incompatible-settings.sh` - Detection script
- `claude/release-manager/README.md` - Full documentation
- `claude/release-manager/9.0.0-INCOMPATIBLE-SETTINGS.md` - Example reference doc
- `claude/release-manager/9.0.0-RC3-SETTINGS-REVIEW.md` - Example summary

---

**For next release manager:** Just run the script, review the output, and fill in the template. It's now a standard part of the process!
