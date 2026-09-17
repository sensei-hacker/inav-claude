# Check PR Documentation Skill

## Overview

This skill checks pull requests for documentation compliance. It verifies that PRs include appropriate documentation updates and identifies PRs that may need documentation but don't have it.

## Key Features

- ✅ Checks PRs from the last 7 days (configurable)
- ✅ Independently verifies wiki **and docs-site** commits (doesn't rely on PR mentions)
- ✅ Matches wiki commits by PR reference, author, and time
- ✅ Matches `iNavFlight.github.io` (Docusaurus docs site) commits the same way
- ✅ Assesses whether documentation is needed based on file changes
- ✅ Interactive tagging of PRs needing documentation
- ✅ Supports both inav and inav-configurator repositories

## Files

- **SKILL.md** - Skill documentation and workflow guide
- **check_pr_docs.sh** - Main shell script for automated checking
- **tag_pr_docs.py** - Interactive Python script for tagging PRs
- **README.md** - This file

## Usage

### Quick Check (Automated Report)

Run the shell script to get a comprehensive report:

```bash
cd .claude/skills/check-pr-docs
./check_pr_docs.sh
```

This will:
1. Update wiki repositories
2. Extract recent wiki commits
3. Check all PRs from the last 7 days
4. Generate a summary report

**Output:**
- PRs with documentation ✅
- PRs needing review ⚠️
- PRs not needing documentation ℹ️

### Interactive Tagging

After reviewing the report, use the Python script to tag PRs:

```bash
cd .claude/skills/check-pr-docs
python3 tag_pr_docs.py
```

For specific repository or time period:

```bash
# Check only inav repository
python3 tag_pr_docs.py inav

# Check last 14 days
python3 tag_pr_docs.py inav 14

# Check both repos, last 14 days
python3 tag_pr_docs.py "" 14
```

The script will:
1. Find PRs likely needing documentation
2. Check wiki for related commits
3. Show you each PR and ask if you want to tag it
4. Apply "documentation needed" label if you approve

### Interactive Options

When reviewing a PR, you can:
- **[y]** - Yes, tag this PR with "documentation needed"
- **[n]** - No, skip this PR
- **[v]** - View PR in browser first (opens in default browser)
- **[q]** - Quit the script

## How It Works

### Documentation Detection

The skill looks for documentation in multiple ways:

#### 1. Files Modified in PR
- Files in `docs/` directory
- README files
- Markdown files

#### 2. PR Description References
- Links to wiki updates
- References to other PRs (e.g., "Docs in #1234")
- Mentions of "documentation" or "wiki"

#### 3. Wiki Commits with PR References
- Wiki commit messages containing "#1234"
- **HIGH CONFIDENCE** - Direct link

#### 4. Wiki Commits by Author (Time-Based)
- Same author as PR
- Within ±2 days of PR merge
- **MEDIUM CONFIDENCE** - Likely related

#### 5. Wiki Commits by Topic
- Wiki commits mentioning similar keywords
- **LOW CONFIDENCE** - Needs manual review

#### 6. Docs-Site Commits (iNavFlight.github.io)

The Docusaurus docs site is checked with the same logic as the wikis (PR-reference
match and author/time match). A PR whose documentation landed on the docs site instead
of the wiki is treated as documented, not flagged as missing docs.

### Assessment Logic

#### Likely Needs Documentation:
- New features or modes
- New CLI commands or settings
- New MSP messages
- Changes to flight behavior
- New UI features or tabs
- New settings/configuration options

#### Likely Doesn't Need Documentation:
- Internal refactoring
- Code cleanup or formatting
- Dependency updates (internal)
- Build system changes
- Test additions/fixes
- Minor bug fixes
- CI/workflow updates

## Requirements

### System Requirements
- Bash shell
- Python 3.6+
- Git
- GitHub CLI (`gh`)

### Repository Setup

The skill expects this directory structure:

```
inavflight/
├── inav/                    # Main firmware repo
├── inav-configurator/       # Configurator repo
├── inav.wiki/              # Wiki (cloned automatically)
├── inav-configurator.wiki/ # Wiki (cloned automatically)
├── iNavFlight.github.io/   # Docs site (cloned automatically)
└── .claude/
    └── skills/
        └── check-pr-docs/
            ├── SKILL.md
            ├── check_pr_docs.sh
            ├── tag_pr_docs.py
            └── README.md
```

The wiki repositories will be cloned automatically on first run.

## Example Workflow

### Manager Workflow

As the development manager, run this skill periodically (e.g., weekly):

```bash
# 1. Run the automated check
cd .claude/skills/check-pr-docs
./check_pr_docs.sh > /tmp/pr_docs_report.txt

# 2. Review the report
cat /tmp/pr_docs_report.txt

# 3. Interactively tag PRs that need docs
python3 tag_pr_docs.py

# 4. Follow up with developers
# - Send email to authors of tagged PRs
# - Request documentation updates
```

### Output Example

```
=== PR Documentation Compliance Check ===
Date: Sat Dec 28 10:30:00 PST 2025
Checking PRs from last 7 days

=== Step 1: Updating Wiki Repositories ===
Updating inav.wiki...
Already up to date.

=== Step 2: Extracting Recent Wiki Commits ===
## inav.wiki commits (last 7 days):
abc123|John Doe|john@example.com|2025-12-22 14:30:00|Updated Navigation.md for #1234
Total: 5 commits

=== Step 3: Checking Repository: inav ===
Found 8 PRs to check

----------------------------------------
Checking PR #1234
Title: Add GPS altitude hold feature
Author: johndoe
State: MERGED
✅ Wiki commit directly references PR #1234:
  - [abc123] 2025-12-22 14:30:00 - Updated Navigation.md for #1234
📝 Documentation status: FOUND (wiki PR ref; )

----------------------------------------
Checking PR #1235
Title: Add new CLI command for telemetry
Author: janesmith
State: MERGED
⚠️  Documentation status: MISSING - likely needed

==========================================
=== SUMMARY REPORT ===
==========================================

Period: Last 7 days (since 2025-12-21)
Total PRs checked: 8

📊 Results:
  ✅ PRs with documentation: 5
  ⚠️  PRs needing review: 2
  ℹ️  PRs not needing docs: 1

⚠️  ACTION REQUIRED: 2 PR(s) may need documentation
```

## Configuration

### Adjust Time Period

Edit `check_pr_docs.sh` to change the default time period:

```bash
DAYS_BACK=14  # Check last 14 days instead of 7
```

### Customize Assessment Logic

Edit `tag_pr_docs.py` to adjust which changes are considered user-facing:

```python
# In get_prs_needing_docs() function
has_user_changes = any(
    'src/main/cli' in f['path'] or
    'src/main/your_module' in f['path']  # Add your patterns
    for f in files
)
```

### Change Label Name

Edit `tag_pr_docs.py` to use a different label:

```python
def tag_pr(repo: str, pr_number: int, label: str = "needs-documentation"):
    # Changed from "documentation needed"
```

## Tips

1. **Run Weekly** - Check PRs every week to catch missing docs early
2. **Review Wiki Independently** - Authors may update wiki but not mention it
3. **Check Author + Time** - Wiki commits by same author around PR time are often related
4. **Use Interactive Mode** - Always review PRs before tagging
5. **Follow Up** - Send email to PR authors when tagging their PRs

## Troubleshooting

### Wiki/docs-site repositories not found

If wiki or docs-site repos don't exist, they'll be cloned automatically. To manually clone:

```bash
cd ~/Documents/planes/inavflight
git clone https://github.com/iNavFlight/inav.wiki.git
git clone https://github.com/iNavFlight/inav-configurator.wiki.git
git clone https://github.com/iNavFlight/iNavFlight.github.io.git
```

### Date command errors

The script supports both Linux and macOS date commands. If you get errors:

```bash
# Test your date command
date -d '7 days ago' +%Y-%m-%d    # Linux
date -v-7d +%Y-%m-%d              # macOS
```

### GitHub CLI not authenticated

Ensure you're logged in:

```bash
gh auth status
gh auth login  # If not logged in
```

### Permission denied

Make scripts executable:

```bash
chmod +x check_pr_docs.sh
chmod +x tag_pr_docs.py
```

## Related Skills

- **pr-review** - Review PR code and comments
- **git-workflow** - Manage git operations
- **wiki-search** - Search wiki for documentation
- **check-builds** - Verify PR builds pass
- **email** - Send messages to developers

## Future Enhancements

Potential improvements:
- [ ] Check for specific wiki pages (e.g., CLI.md for CLI changes)
- [ ] Analyze PR diff for documentation keywords
- [ ] Generate suggested wiki content
- [ ] Automatic PR commenting when docs missing
- [ ] Integration with GitHub Projects for tracking
- [ ] Weekly automated reports via email
