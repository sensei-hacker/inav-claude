# Project: Setup Code Indexes for Claude Code

**Status:** ✉️ ASSIGNED
**Priority:** Medium
**Type:** Development Tooling / Infrastructure
**Created:** 2025-11-25
**Assignee:** Developer

## Overview

Set up code navigation and search indexes to improve Claude Code's ability to understand and navigate the INAV codebase. This involves configuring ctags for general code navigation and setting up a custom configurator indexer for enhanced search capabilities.

## Problem

Claude Code currently lacks structured indexes for code navigation:
- No ctags index for jump-to-definition
- No custom index for configurator-specific code search
- Reduced efficiency in code exploration and understanding
- Slower response times when searching codebase

## Objectives

**Phase 1 (High Priority - Start Here):**
1. **Generate ctags Index:** Create comprehensive tags file for both codebases (configurator + firmware)
2. **Configure Claude Code for ctags:** Enable Claude Code to use the tags file
3. **Evaluate Effectiveness:** Test and measure improvement in code navigation
4. **Document ctags Setup:** Provide instructions for maintaining ctags

**Phase 2 (Conditional - Only if Phase 1 proves beneficial):**
5. **Evaluate Additional Tools:** Determine if cscope and configurator_indexer add value
6. **Implement if Beneficial:** Set up additional tools only if they provide clear additional benefit
7. **Document Complete Setup:** Update documentation for all tools in use

## Scope

**This project is divided into TWO PHASES:**

### PHASE 1: ctags Setup & Validation (MANDATORY)

Start here. Only proceed to Phase 2 if ctags integration with Claude Code proves beneficial.

**Generate ctags Index:**
```bash
ctags -R --fields=+niazS --extras=+q -f tags .
```

**What this does:**
- `-R`: Recursive indexing of all files
- `--fields=+niazS`: Include name, input file, access, signature, kind
- `--extras=+q`: Include qualified tags
- `-f tags`: Output to file named "tags"

**Target directories:**
- `inav-configurator/` - Configurator codebase (JavaScript)
- `inav/` - Firmware codebase (C/C++)

**Configure Claude Code:**
- Research Claude Code documentation for ctags support
- Determine how Claude Code consumes ctags files
- Configure paths to tags file(s)
- Test jump-to-definition functionality
- **Measure effectiveness:** Does it actually help Claude Code navigate code better?

**Decision Gate:** If ctags integration works and provides clear benefit, proceed to Phase 2. If not, stop here and report findings.

---

### PHASE 2: Additional Tools (CONDITIONAL)

**Only proceed if Phase 1 proves beneficial.** These tools may be redundant or not supported by Claude Code.

#### Option A: Configurator Indexer Setup

**Location:** `test_tools/configurator_indexer/`

**Components:**
- Indexer script (creates index)
- Lookup script (queries index)

**Tasks:**
1. Locate/verify indexer scripts exist
2. Understand indexer functionality
3. Run indexer on inav-configurator/ codebase
4. Generate index file(s)
5. Test lookup script functionality
6. **Evaluate:** Does this provide value beyond ctags for JavaScript code?
7. Configure Claude Code to use the index (only if beneficial)

#### Option B: cscope Setup

**Generate cscope Database:**
```bash
find . -name "*.c" -o -name "*.h" > cscope.files
cscope -b -q
```

**What this does:**
- `find . -name "*.c" -o -name "*.h"`: Find all C source and header files
- `> cscope.files`: Save file list to cscope.files
- `cscope -b -q`: Build database in batch mode with quick symbol lookup
  - `-b`: Build database only (no interactive mode)
  - `-q`: Build inverted index for faster lookups

**Target directory:**
- `inav/` - Firmware codebase (C/C++ code)

**Output files:**
- `cscope.out` - Main database
- `cscope.in.out` - Inverted index (from -q flag)
- `cscope.po.out` - Pointer index (from -q flag)
- `cscope.files` - List of indexed files

**Purpose:** C/C++ call graph analysis, caller/callee relationships

**Evaluate:**
- Does Claude Code support cscope?
- Does cscope provide value beyond ctags for C code navigation?
- Is the call graph functionality useful for Claude Code?

**Configure Claude Code** (only if beneficial):
- Determine how Claude Code consumes cscope databases
- Configure paths to cscope files
- Test symbol lookup functionality

---

## Implementation Strategy

**Start with Phase 1 ONLY.** Complete ctags setup, test with Claude Code, and evaluate effectiveness before considering Phase 2.

## Technical Details

### ctags Overview

**What ctags provides:**
- Symbol definitions (functions, classes, variables)
- File locations for each symbol
- Jump-to-definition capability
- Code navigation in editors

**Supported languages:**
- JavaScript (configurator)
- C/C++ (firmware)
- Python (build tools)
- And many more

**Output format:**
Standard tags file with entries like:
```
functionName	file.js	/^function functionName()/;"	f
className	file.js	/^class className {/;"	c
```

### Configurator Indexer

**Purpose:** (To be determined by examining scripts)
Likely provides:
- Configurator-specific code indexing
- Enhanced search capabilities
- Custom metadata extraction
- Faster lookup than grep

**Expected workflow:**
1. Run indexer script: `./indexer.py` (or similar)
2. Generates index file(s) in specific format
3. Use lookup script: `./lookup.py <query>` (or similar)
4. Integrate with Claude Code

### cscope Overview

**What cscope provides:**
- C/C++ symbol database
- Find function definitions and callers
- Find where variables/symbols are used
- Find files including a header
- Navigate C codebase efficiently

**Optimized for C code:**
- Understanding function call graphs
- Tracing code execution paths
- Finding all references to symbols
- Analyzing C codebases

**Output format:**
Binary database files:
- `cscope.out` - Main symbol database
- `cscope.in.out` - Inverted index (for faster symbol lookups)
- `cscope.po.out` - Pointer symbol index
- `cscope.files` - List of indexed files

**Use cases:**
- "Where is this function defined?"
- "What functions call this function?"
- "Where is this variable used?"
- "What files include this header?"

## Implementation Steps

### PHASE 1: ctags Setup & Integration (MANDATORY - 3-5 hours)

1. **Verify ctags installation:**
   ```bash
   ctags --version
   ```

2. **Generate tags for inav-configurator:**
   ```bash
   cd inav-configurator
   ctags -R --fields=+niazS --extras=+q -f tags .
   cd ..
   ```

3. **Generate tags for inav (firmware):**
   ```bash
   cd inav
   ctags -R --fields=+niazS --extras=+q -f tags .
   cd ..
   ```

4. **Verify tags files created:**
   ```bash
   ls -lh inav-configurator/tags inav/tags
   head -20 inav-configurator/tags
   head -20 inav/tags
   ```

5. **Test tags files:**
   - Pick known functions/classes from both codebases
   - Verify they appear in respective tags files
   - Check tag format is correct

6. **Research Claude Code ctags support:**
   - Read Claude Code documentation
   - Check for native ctags support
   - Investigate MCP servers for ctags
   - Look for configuration options
   - Find examples if available

7. **Configure Claude Code for ctags:**
   - Locate Claude Code configuration files
   - Add tags file paths for both projects
   - Configure any required settings
   - Test functionality

8. **Test with Claude Code:**
   - Ask Claude Code to find specific functions
   - Test jump-to-definition (if supported)
   - Verify improved code navigation
   - Document what works and what doesn't

9. **Evaluate effectiveness:**
   - Does Claude Code use the tags?
   - Is code navigation noticeably better?
   - Are there any issues or limitations?
   - **DECISION POINT:** Is this worth continuing with Phase 2?

10. **Add tags to .gitignore:**
    ```bash
    echo "tags" >> inav-configurator/.gitignore
    echo "TAGS" >> inav-configurator/.gitignore
    echo "tags" >> inav/.gitignore
    echo "TAGS" >> inav/.gitignore
    ```

11. **Document Phase 1 results:**
    - Create INDEXING.md with ctags setup
    - Document configuration process
    - Note effectiveness and limitations
    - Provide regeneration instructions

**STOP HERE and report results to manager before proceeding to Phase 2.**

---

### PHASE 2: Additional Tools (CONDITIONAL - Only if Phase 1 beneficial)

**Do NOT start Phase 2 without manager approval after Phase 1 evaluation.**

#### Option A: Configurator Indexer Investigation (2-3 hours)

1. **Locate indexer scripts:**
   ```bash
   ls -la test_tools/configurator_indexer/
   ```

2. **Examine scripts:**
   - Read indexer script source
   - Read lookup script source
   - Understand index format
   - Note dependencies

3. **Install dependencies (if needed):**
   ```bash
   # Example: pip install -r requirements.txt
   ```

4. **Run indexer:**
   ```bash
   cd test_tools/configurator_indexer
   ./indexer.py ../../inav-configurator/
   # Or whatever the actual command is
   ```

5. **Verify index created:**
   - Check output files
   - Examine index format
   - Note file locations

6. **Test lookup script:**
   ```bash
   ./lookup.py "some_function_name"
   ./lookup.py "MSP_STATUS"
   ```

7. **Document indexer:**
   - What it indexes
   - How to run it
   - Output format
   - How to query it

#### Option B: cscope Investigation (1-2 hours)

1. **Verify cscope installation:**
   ```bash
   cscope --version
   ```

2. **Generate cscope database for firmware:**
   ```bash
   cd inav
   find . -name "*.c" -o -name "*.h" > cscope.files
   cscope -b -q
   ```

3. **Verify database created:**
   ```bash
   ls -lh cscope.out cscope.in.out cscope.po.out cscope.files
   ```

4. **Test cscope (optional interactive test):**
   ```bash
   cscope -d  # Opens interactive mode
   # Test searching for a known function
   ```

5. **Add cscope files to .gitignore:**
   ```bash
   echo "cscope.out" >> .gitignore
   echo "cscope.in.out" >> .gitignore
   echo "cscope.po.out" >> .gitignore
   echo "cscope.files" >> .gitignore
   ```

**If implementing Phase 2 tools:**
- Configure Claude Code for additional tools
- Update INDEXING.md with full tool documentation
- Create comprehensive update script

## Claude Code Integration Research

**Need to investigate:**

1. **Does Claude Code support ctags natively?**
   - Check Claude Code documentation
   - Look for configuration options
   - Test functionality

2. **Does Claude Code support cscope natively?**
   - Check for cscope integration
   - Configuration requirements
   - Symbol lookup capabilities

3. **How to provide custom indexes to Claude Code?**
   - MCP (Model Context Protocol) servers?
   - Custom tool definitions?
   - Configuration files?
   - Context providers?

4. **Best practices for large codebases:**
   - Index file size limits
   - Search optimization
   - Update frequency
   - Memory usage considerations

## Success Criteria

### Phase 1 (MANDATORY):
- [ ] ctags installed and verified
- [ ] ctags index generated for inav-configurator
- [ ] ctags index generated for inav (firmware)
- [ ] ctags files properly formatted and complete
- [ ] Claude Code ctags support researched and documented
- [ ] Claude Code configured to use ctags (if supported)
- [ ] Effectiveness tested and evaluated
- [ ] tags files added to .gitignore
- [ ] INDEXING.md created with ctags setup
- [ ] Phase 1 results reported to manager
- [ ] **Decision made:** Proceed to Phase 2 or stop?

### Phase 2 (CONDITIONAL - Only if Phase 1 beneficial):

**Only implement if manager approves after Phase 1 evaluation.**

**If implementing cscope:**
- [ ] cscope database generated for inav (firmware)
- [ ] cscope.files list created
- [ ] Inverted indexes created (-q flag)
- [ ] Claude Code configured to use cscope
- [ ] cscope files added to .gitignore

**If implementing configurator_indexer:**
- [ ] Indexer scripts located and understood
- [ ] Configurator index generated successfully
- [ ] Lookup script tested and working
- [ ] Claude Code configured to use custom index

**Phase 2 completion:**
- [ ] INDEXING.md updated with Phase 2 tools
- [ ] Comprehensive update script created
- [ ] All Phase 2 tools documented

## Estimated Time

### Phase 1 (Complete this first):
- **ctags generation:** 15-30 minutes
- **Claude Code research:** 1-2 hours
- **Claude Code configuration:** 30-60 minutes
- **Testing & evaluation:** 1-2 hours
- **Documentation:** 30-60 minutes

**Phase 1 Total:** 3-5 hours

### Phase 2 (Only if approved after Phase 1):
- **Configurator indexer investigation:** 2-3 hours (if implemented)
- **cscope setup:** 1-2 hours (if implemented)
- **Additional documentation:** 1 hour (if implemented)

**Phase 2 Total:** 4-6 hours (only if proceeding)

**Maximum Total:** 9-11 hours (if both phases completed)

## Deliverables

### Phase 1 (Mandatory):
1. **Generated ctags Indexes:**
   - `inav-configurator/tags` (JavaScript/configurator code)
   - `inav/tags` (C/C++ firmware code)

2. **Configuration:**
   - Claude Code configured for ctags (if supported)
   - Configuration documented

3. **Documentation:**
   - INDEXING.md with ctags setup instructions
   - Regeneration procedure
   - Claude Code configuration steps
   - Effectiveness evaluation report

4. **Maintenance:**
   - tags files added to .gitignore
   - Simple regeneration commands documented

5. **Phase 1 Report:**
   - Does Claude Code support ctags?
   - How well does it work?
   - Recommendation: proceed to Phase 2 or stop?

### Phase 2 (Conditional - only if implemented):
1. **Additional Indexes** (if implemented):
   - cscope database (if beneficial)
   - configurator_indexer output (if beneficial)

2. **Extended Documentation:**
   - INDEXING.md updated with all tools
   - Comprehensive update script
   - Tool comparison and use cases

3. **Complete Configuration:**
   - All tools integrated with Claude Code
   - Full maintenance procedures

## Priority Justification

**Medium Priority:**
- Improves developer productivity
- Enhances Claude Code capabilities
- Not urgent but valuable
- Foundation for better code navigation
- One-time setup with minimal maintenance

## Notes

**User-Provided Commands:**
- ctags: `ctags -R --fields=+niazS --extras=+q -f tags .`
- cscope: `find . -name "*.c" -o -name "*.h" > cscope.files` then `cscope -b -q`
- Configurator indexer scripts at: `test_tools/configurator_indexer/`

**Tool Installation:**
- User indicated tools are "probably" already installed
- Verify installation during Phase 1

**Primary Goal:**
- Focus on making all indexes accessible to Claude Code
- Improve code navigation and search capabilities
- Enable better understanding of INAV codebase

**Tool Coverage:**
- ctags: Universal (JavaScript + C/C++)
- cscope: C/C++ specific (firmware)
- configurator_indexer: JavaScript specific (configurator)

## Questions to Investigate

1. **Configurator indexer scripts:**
   - Do they exist at specified path?
   - What language are they written in?
   - What dependencies do they have?
   - What format is the index?

2. **Claude Code integration:**
   - Does Claude Code natively support ctags?
   - How to configure custom indexes?
   - Are MCP servers needed?
   - Best practices for large codebases?

3. **Maintenance:**
   - How often should indexes be regenerated?
   - Can regeneration be automated?
   - Git hooks for auto-update?

## Related Work

- **Active:** implement-configurator-test-suite (testing infrastructure)
- This project complements testing by improving code navigation

## Resources

**ctags:**
- Universal Ctags: https://github.com/universal-ctags/ctags
- Documentation: https://docs.ctags.io/

**Claude Code:**
- Documentation: (research during project)
- MCP: https://modelcontextprotocol.io/

## Future Enhancements

- Automated index updates (git hooks, cron jobs)
- Index multiple directories (inav/, inav-configurator/, docs/)
- Integration with other development tools
- Custom MCP server for enhanced search
