# New Skill Created: check-pr-docs

**Date:** 2025-12-28 10:30
**Type:** Skill Implementation
**Status:** Complete

## Summary

Created a comprehensive skill for checking pull request documentation compliance. The skill automatically checks PRs from the last week, independently verifies wiki commits, and helps tag PRs that need documentation.

## What Was Built

### Files Created

1. **.claude/skills/check-pr-docs/SKILL.md**
   - Complete skill documentation
   - Workflow guides
   - Usage examples
   - Command references

2. **.claude/skills/check-pr-docs/check_pr_docs.sh**
   - Automated shell script for PR checking
   - Updates wiki repositories
   - Extracts recent commits
   - Generates comprehensive reports

3. **.claude/skills/check-pr-docs/tag_pr_docs.py**
   - Interactive Python script for tagging PRs
   - Asks user before applying labels
   - Checks wiki commits independently
   - Supports multiple repositories

4. **.claude/skills/check-pr-docs/README.md**
   - User guide
   - Configuration options
   - Troubleshooting tips
   - Example workflows

## Key Features

### Automated Checking ✅
- Lists PRs from last 7 days (configurable)
- Checks both inav and inav-configurator repos
- Identifies PRs with/without documentation

### Independent Wiki Verification ✅
- **Critical Feature:** Doesn't rely on PR mentions
- Clones/updates wiki repositories automatically
- Matches wiki commits by:
  - Direct PR reference (#1234)
  - Author + time window (±2 days)
  - Topic/keyword matching

### Documentation Detection ✅
Checks multiple sources:
- Files in docs/ directory
- README updates
- PR description links
- PR comments
- Wiki commits referencing PR
- Wiki commits by same author

### Smart Assessment ✅
Determines if docs are needed based on:
- User-facing changes (CLI, MSP, OSD, navigation)
- Feature additions (new, add, implement)
- Excludes internal changes (refactor, cleanup, tests)

### Interactive Tagging ✅
- Shows PR details and analysis
- Asks user before tagging
- Option to view PR in browser
- Applies "documentation needed" label

## Usage

### Quick Check
```bash
cd .claude/skills/check-pr-docs
./check_pr_docs.sh
```

### Interactive Tagging
```bash
python3 tag_pr_docs.py              # Both repos, last 7 days
python3 tag_pr_docs.py inav         # Only inav repo
python3 tag_pr_docs.py inav 14      # Last 14 days
```

### Skill Invocation
```
/check-pr-docs
```

## Output Example

The script generates reports showing:
- PRs with documentation ✅ (with reasons: docs files, wiki refs, author match)
- PRs needing review ⚠️ (user-facing changes, no docs found)
- PRs not needing docs ℹ️ (internal changes only)
- Wiki activity summary

## How It Matches Wiki Commits

### Priority 1: Direct PR Reference
Wiki commit message contains "#1234" → HIGH CONFIDENCE

### Priority 2: Author + Time Window
Same author, within ±2 days of PR merge → MEDIUM CONFIDENCE

### Priority 3: Topic/Keyword Match
Wiki commit mentions related keywords from PR → LOW CONFIDENCE (needs review)

## Manager Workflow

1. **Weekly Review**
   ```bash
   ./check_pr_docs.sh > /tmp/weekly_pr_docs.txt
   ```

2. **Review Report**
   ```bash
   cat /tmp/weekly_pr_docs.txt
   ```

3. **Tag PRs Interactively**
   ```bash
   python3 tag_pr_docs.py
   ```

4. **Follow Up**
   - Send emails to PR authors
   - Request documentation updates
   - Track in project management

## Testing Status

- ✅ Shell script syntax validated
- ✅ Python script syntax validated
- ✅ Scripts made executable
- ⚠️ Not yet run against live data (ready for first run)

## Requirements Met

All requested features implemented:
- ✅ Check PRs from last week for each repo
- ✅ Detect docs/ file modifications
- ✅ Detect PR links to documentation PRs
- ✅ Detect PR links to wiki updates
- ✅ **Independently fetch and check wiki commits**
- ✅ Match wiki commits to PRs (even without mentions)
- ✅ Assess if documentation is likely needed
- ✅ Report PRs needing documentation
- ✅ Ask user whether to tag PRs

## Next Steps

1. **Test the skill** with a real run:
   ```bash
   cd .claude/skills/check-pr-docs
   ./check_pr_docs.sh
   ```

2. **Review the output** to verify accuracy

3. **Try interactive tagging** if any PRs need attention:
   ```bash
   python3 tag_pr_docs.py
   ```

4. **Establish weekly routine** for documentation compliance

5. **Optional:** Customize thresholds and patterns in scripts

## Notes

- Wiki repositories are cloned automatically on first run
- Supports both Linux and macOS date commands
- Requires GitHub CLI (`gh`) authentication
- Interactive mode allows viewing PRs in browser before tagging

---
**Manager**
