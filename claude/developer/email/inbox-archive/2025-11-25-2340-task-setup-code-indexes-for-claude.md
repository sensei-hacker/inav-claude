# Task Assignment: Setup Code Indexes for Claude Code

**Date:** 2025-11-25 23:40
**Project:** setup-code-indexes-for-claude
**Priority:** Medium
**Estimated Effort:** 3-5 hours (Phase 1 only)
**Branch:** Not applicable (tooling setup)

## Task

Set up code navigation indexes to improve Claude Code's ability to understand and navigate the INAV codebase. This is a **two-phase project** - complete Phase 1 first, evaluate effectiveness, then decide whether Phase 2 is worthwhile.

## Background

User mentioned three potential indexing tools from a Claude chat:
1. **ctags** - Universal code indexing (JavaScript + C/C++)
2. **cscope** - C/C++ specific indexing (firmware)
3. **configurator_indexer** - Custom JavaScript indexer (configurator)

However, we don't want to implement all three without first verifying that Claude Code can actually use them. This is a pragmatic, phased approach.

## PHASE 1: ctags Setup & Evaluation (START HERE)

**Complete Phase 1 entirely before considering Phase 2.**

### Objectives

1. Generate ctags indexes for both codebases
2. Research and configure Claude Code to use ctags
3. Test and evaluate effectiveness
4. Report results and make recommendation

### Commands Provided by User

**Generate ctags:**
```bash
ctags -R --fields=+niazS --extras=+q -f tags .
```

Run this in both:
- `inav-configurator/` (JavaScript code)
- `inav/` (C/C++ firmware)

### Implementation Steps

#### 1. Verify Installation (5 min)

```bash
ctags --version
```

Tools are "probably" already installed per user.

#### 2. Generate Indexes (15-30 min)

```bash
# In inav-configurator/
cd inav-configurator
ctags -R --fields=+niazS --extras=+q -f tags .

# In inav/
cd ../inav
ctags -R --fields=+niazS --extras=+q -f tags .
```

Verify both tags files were created and contain entries.

#### 3. Research Claude Code Integration (1-2 hours)

**Critical step:** Determine if/how Claude Code uses ctags.

- Read Claude Code documentation
- Search for "ctags" or "code navigation" features
- Check for native support or MCP servers
- Find configuration examples
- Document what you find

#### 4. Configure Claude Code (30-60 min)

If Claude Code supports ctags:
- Locate configuration file(s)
- Add tags file paths
- Configure any required settings
- Test configuration

If no native support:
- Document this finding
- Investigate alternatives (MCP server, context injection, etc.)
- Attempt basic integration if feasible

#### 5. Test with Claude Code (1-2 hours)

**Test JavaScript navigation:**
- Ask Claude Code to find specific functions in configurator
- Test cross-file navigation
- Try class/method lookups

**Test C/C++ navigation:**
- Ask Claude Code to find specific functions in firmware
- Test cross-file navigation
- Try struct/typedef lookups

**Document results:**
- What works?
- What doesn't work?
- Is there noticeable improvement?
- Are responses more accurate?

#### 6. Evaluate & Report (30-60 min)

**Key questions:**
- Does Claude Code actually use the ctags?
- Is code navigation noticeably better?
- Is this worth the maintenance overhead?
- Should we proceed to Phase 2 (additional tools)?

**Create Phase 1 Report:**
- Summarize setup process
- Document Claude Code integration
- Describe what works/doesn't work
- **Provide clear recommendation:** Proceed to Phase 2 or stop here?

#### 7. Cleanup (15 min)

```bash
# Add to .gitignore
echo "tags" >> inav-configurator/.gitignore
echo "TAGS" >> inav-configurator/.gitignore
echo "tags" >> inav/.gitignore
echo "TAGS" >> inav/.gitignore
```

Create `INDEXING.md` with ctags setup instructions.

### Phase 1 Deliverables

1. **Generated Indexes:**
   - `inav-configurator/tags`
   - `inav/tags`

2. **Configuration:**
   - Claude Code configured for ctags (if supported)
   - Configuration documented

3. **Documentation:**
   - INDEXING.md with setup instructions
   - Regeneration commands
   - Claude Code configuration steps

4. **Phase 1 Report:**
   - Does Claude Code support ctags?
   - How well does it work?
   - Recommendation: Proceed to Phase 2 or stop?

### Decision Gate

**STOP after Phase 1 and send report to manager.**

Do NOT proceed to Phase 2 without manager approval.

---

## PHASE 2: Additional Tools (CONDITIONAL)

**DO NOT start Phase 2 without manager approval.**

Phase 2 would involve investigating two additional tools:

### Option A: Configurator Indexer

**Location:** `test_tools/configurator_indexer/`

Contains indexer and lookup scripts for JavaScript/configurator code.

**Tasks:**
- Locate and examine scripts
- Run indexer on inav-configurator
- Test lookup functionality
- Evaluate if it provides value beyond ctags
- Configure Claude Code if beneficial

### Option B: cscope

**Commands:**
```bash
find . -name "*.c" -o -name "*.h" > cscope.files
cscope -b -q
```

C/C++ specific indexing with call graph analysis.

**Tasks:**
- Generate cscope database for firmware
- Test functionality
- Evaluate if it provides value beyond ctags for C code
- Configure Claude Code if beneficial

### Phase 2 Decision

Phase 2 will only proceed if:
1. Phase 1 shows clear benefit
2. Manager approves continuation
3. Additional tools appear to add value beyond ctags

---

## Success Criteria

### Phase 1 (Complete first):
- [ ] ctags indexes generated for both codebases
- [ ] Claude Code integration researched and documented
- [ ] Claude Code configured (if supported)
- [ ] Effectiveness tested and evaluated
- [ ] INDEXING.md created
- [ ] Phase 1 report sent to manager
- [ ] Decision made: proceed to Phase 2 or stop

### Phase 2 (Only if approved):
- [ ] Additional tools evaluated
- [ ] Beneficial tools integrated
- [ ] Complete documentation updated
- [ ] Maintenance procedures documented

## Estimated Time

**Phase 1:** 3-5 hours
**Phase 2:** 4-6 hours (only if proceeding)

**Focus on Phase 1.** This gives us:
- Quick validation of concept
- Data to make informed decision
- Minimal wasted effort if not beneficial

## Priority Justification

**Medium Priority:**
- Could improve Claude Code capabilities
- Not urgent - no blocking issues
- Worth investigating but pragmatically
- Start small, expand if beneficial

## Notes

**Pragmatic Approach:**
- Don't blindly implement all three tools
- Verify Claude Code can actually use indexes first
- Only add complexity if it provides clear benefit
- Report results before expanding scope

**Tools Target Different Code:**
- ctags: Universal (both JavaScript & C)
- cscope: C/C++ only (firmware)
- configurator_indexer: JavaScript only (configurator)

They're not redundant for *different* codebases, but may be redundant for the *same* codebase (e.g., cscope vs. ctags for C code).

**User indicated:**
- Tools are "probably" installed
- Commands provided for ctags and cscope
- Configurator indexer scripts at `test_tools/configurator_indexer/`

## Questions?

**If you find:**
- Claude Code doesn't support ctags → Document finding, investigate alternatives
- ctags works great → Complete Phase 1, recommend Phase 2
- ctags doesn't help → Complete Phase 1, recommend stopping

**Most important:** Focus on evaluating whether this actually helps Claude Code, not just generating indexes.

---

**Manager**
