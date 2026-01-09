# Todo List: Setup Code Indexes for Claude Code

## PHASE 1: ctags Setup & Evaluation (START HERE)

**Complete Phase 1 entirely before considering Phase 2.**

### Installation & Setup

- [ ] Verify ctags installation
  - [ ] Run `ctags --version`
  - [ ] Confirm Universal Ctags (preferred) or Exuberant Ctags

### Generate ctags Indexes

- [ ] Generate tags for inav-configurator
  - [ ] Navigate to inav-configurator directory
  - [ ] Run: `ctags -R --fields=+niazS --extras=+q -f tags .`
  - [ ] Verify tags file created
  - [ ] Check file size and sample contents

- [ ] Generate tags for inav (firmware)
  - [ ] Navigate to inav directory
  - [ ] Run: `ctags -R --fields=+niazS --extras=+q -f tags .`
  - [ ] Verify tags file created
  - [ ] Check file size and sample contents

### Test Generated Tags

- [ ] Test inav-configurator tags
  - [ ] Pick 3-5 known JavaScript functions/classes
  - [ ] Verify they appear in tags file
  - [ ] Check tag format is correct

- [ ] Test inav firmware tags
  - [ ] Pick 3-5 known C functions/structures
  - [ ] Verify they appear in tags file
  - [ ] Check tag format is correct

### Research Claude Code Integration

- [ ] Read Claude Code documentation
  - [ ] Search for "ctags" support
  - [ ] Look for code navigation features
  - [ ] Find configuration documentation

- [ ] Check for ctags support
  - [ ] Does Claude Code support ctags natively?
  - [ ] Are there MCP servers for ctags?
  - [ ] What configuration is required?
  - [ ] Find examples or tutorials

- [ ] Investigate alternatives if no native support
  - [ ] Can tags be provided via context?
  - [ ] Custom MCP server feasibility?
  - [ ] Other integration methods?

### Configure Claude Code

- [ ] Locate Claude Code configuration
  - [ ] Find config file location
  - [ ] Understand config format
  - [ ] Backup existing config

- [ ] Add ctags configuration
  - [ ] Add paths to tags files
  - [ ] Configure any required settings
  - [ ] Set options/preferences

- [ ] Verify configuration
  - [ ] Check config syntax
  - [ ] Restart Claude Code if needed
  - [ ] Test config loads correctly

### Test with Claude Code

- [ ] Test JavaScript navigation
  - [ ] Ask Claude Code to find specific functions in configurator
  - [ ] Test jump-to-definition (if supported)
  - [ ] Try cross-file navigation
  - [ ] Test class/method lookups

- [ ] Test C/C++ navigation
  - [ ] Ask Claude Code to find specific functions in firmware
  - [ ] Test jump-to-definition (if supported)
  - [ ] Try cross-file navigation
  - [ ] Test struct/typedef lookups

- [ ] Document what works
  - [ ] List features that work
  - [ ] Note features that don't work
  - [ ] Identify limitations
  - [ ] Record any issues

### Evaluate Effectiveness

- [ ] Assess improvements
  - [ ] Is code navigation better?
  - [ ] Does Claude Code use the tags?
  - [ ] Is there noticeable benefit?
  - [ ] Are responses more accurate?

- [ ] Identify limitations
  - [ ] What doesn't work well?
  - [ ] Any performance issues?
  - [ ] Configuration difficulties?
  - [ ] Missing features?

- [ ] Make recommendation
  - [ ] Worth continuing to Phase 2?
  - [ ] Stop here if no benefit?
  - [ ] Document reasoning

### Cleanup & Documentation

- [ ] Add tags to .gitignore
  - [ ] Add "tags" to inav-configurator/.gitignore
  - [ ] Add "TAGS" to inav-configurator/.gitignore
  - [ ] Add "tags" to inav/.gitignore
  - [ ] Add "TAGS" to inav/.gitignore

- [ ] Create INDEXING.md
  - [ ] Overview of ctags setup
  - [ ] Installation instructions
  - [ ] Generation commands
  - [ ] Claude Code configuration
  - [ ] Regeneration procedure
  - [ ] Troubleshooting tips

- [ ] Document configuration
  - [ ] Claude Code config steps
  - [ ] File locations
  - [ ] Settings used
  - [ ] Examples

### Phase 1 Completion Report

- [ ] Write completion report
  - [ ] Summarize what was done
  - [ ] Report ctags setup results
  - [ ] Document Claude Code integration
  - [ ] Describe effectiveness
  - [ ] List what works/doesn't work
  - [ ] Provide recommendation

- [ ] **DECISION POINT:**
  - [ ] Recommend proceeding to Phase 2? (Yes/No)
  - [ ] Justification for recommendation
  - [ ] Send report to manager
  - [ ] **STOP HERE until manager responds**

---

## PHASE 2: Additional Tools (CONDITIONAL)

**DO NOT START PHASE 2 without manager approval after Phase 1 evaluation.**

### Option A: Configurator Indexer (If Proceeding)

- [ ] Locate indexer scripts
  - [ ] Navigate to test_tools/configurator_indexer/
  - [ ] List files in directory
  - [ ] Identify indexer script
  - [ ] Identify lookup script

- [ ] Understand indexer
  - [ ] Read indexer script source
  - [ ] Understand what it indexes
  - [ ] Note output format
  - [ ] Check dependencies

- [ ] Check dependencies
  - [ ] Identify required packages
  - [ ] Install if needed
  - [ ] Verify installation

- [ ] Run indexer
  - [ ] Execute indexer on inav-configurator
  - [ ] Note runtime
  - [ ] Verify index created
  - [ ] Check index format

- [ ] Test lookup script
  - [ ] Run lookup for known symbols
  - [ ] Verify results are correct
  - [ ] Test multiple queries
  - [ ] Note performance

- [ ] Evaluate benefit
  - [ ] Does it provide value beyond ctags?
  - [ ] Is it faster/better for JavaScript?
  - [ ] Worth integrating with Claude Code?

- [ ] Configure Claude Code (if beneficial)
  - [ ] Determine integration method
  - [ ] Update configuration
  - [ ] Test functionality

### Option B: cscope (If Proceeding)

- [ ] Verify cscope installation
  - [ ] Run `cscope --version`
  - [ ] Confirm installation

- [ ] Generate cscope database
  - [ ] Navigate to inav directory
  - [ ] Run: `find . -name "*.c" -o -name "*.h" > cscope.files`
  - [ ] Run: `cscope -b -q`
  - [ ] Verify database files created

- [ ] Test cscope database
  - [ ] Run `cscope -d` (interactive mode)
  - [ ] Search for known functions
  - [ ] Verify results
  - [ ] Exit cscope

- [ ] Evaluate benefit
  - [ ] Does it provide value beyond ctags for C?
  - [ ] Is call graph info useful?
  - [ ] Worth integrating with Claude Code?

- [ ] Configure Claude Code (if beneficial)
  - [ ] Research cscope integration
  - [ ] Update configuration
  - [ ] Test functionality

- [ ] Add to .gitignore
  - [ ] Add cscope.out
  - [ ] Add cscope.in.out
  - [ ] Add cscope.po.out
  - [ ] Add cscope.files

### Phase 2 Documentation

- [ ] Update INDEXING.md
  - [ ] Add sections for implemented tools
  - [ ] Document generation procedures
  - [ ] Update Claude Code config
  - [ ] Add tool comparison

- [ ] Create update script (optional)
  - [ ] Script to regenerate all indexes
  - [ ] Add error handling
  - [ ] Make executable
  - [ ] Test script

- [ ] Document Phase 2 results
  - [ ] What tools were implemented?
  - [ ] How do they integrate?
  - [ ] Benefits over ctags alone?
  - [ ] Maintenance procedures

### Phase 2 Completion

- [ ] Send Phase 2 completion report
  - [ ] Summarize additional tools
  - [ ] Document integration
  - [ ] Provide maintenance guide
  - [ ] Note any issues

---

## Notes

- **Priority:** Complete Phase 1 first, evaluate, then decide on Phase 2
- **Focus:** Making ctags work with Claude Code is the primary goal
- **Pragmatic:** Only add complexity if it provides clear benefit
- **Report:** Keep manager informed at decision points
