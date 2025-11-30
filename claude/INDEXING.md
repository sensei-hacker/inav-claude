# Code Indexing for INAV Projects

This document describes how to generate and use ctags indexes for the INAV firmware and configurator codebases.

## Quick Start

### Generate ctags for inav-configurator

```bash
cd inav-configurator
ctags -R --fields=+niazS --extras=+q \
  --exclude=node_modules --exclude=.git --exclude=out --exclude=.vite --exclude=dist \
  -f tags .
```

### Generate ctags for inav firmware

```bash
cd inav
ctags -R --fields=+niazS --extras=+q \
  --exclude=lib --exclude=build --exclude=tools --exclude=.git \
  -f tags .
```

## Using ctags

### Slash command

Use `/find-symbol symbolName` to search both codebases:

```
/find-symbol pidController
/find-symbol navConfig
```

### Manual lookups

```bash
# Find a function definition
grep "^functionName\b" tags

# Find all functions in a file
grep "filename.c" tags | grep "kind:f"

# Find structs
grep "kind:s" tags | head -20
```

### Example output

```
pidController	src/main/flight/pid.c	/^void FAST_CODE pidController(float dT)$/;"	kind:f	line:1178	typeref:typename:void FAST_CODE	signature:(float dT)
```

This tells you:
- Function name: `pidController`
- File: `src/main/flight/pid.c`
- Line: 1178
- Kind: function (`f`)
- Signature: `(float dT)`

## Kind codes

| Code | Meaning |
|------|---------|
| f | function |
| v | variable |
| s | struct |
| t | typedef |
| d | macro definition |
| e | enum value |
| g | enum name |
| m | struct/class member |
| c | class |

## File sizes (typical)

| Project | Size | Entries |
|---------|------|---------|
| inav-configurator | ~5 MB | ~40K |
| inav firmware | ~95 MB | ~460K |

## Limitations

1. **JavaScript indexing is limited** - ctags doesn't parse modern ES6+ syntax well. For JS code, Claude's built-in Grep tool often works better.

2. **Large firmware index** - The firmware tags file includes vendor headers. Excluding `lib/` and `tools/` reduces size significantly.

3. **Not committed to git** - Tags files are in `.gitignore` and must be regenerated locally.

## Regeneration

Regenerate indexes when:
- New source files are added
- Major refactoring occurs
- After pulling significant changes

## Phase 1 Evaluation

**Conclusion:** ctags provides value for C firmware symbol lookup but limited value for JavaScript. Claude Code's built-in Grep tool is often sufficient without pre-generated indexes.

**Recommendation:** Keep ctags for firmware navigation. Do not proceed to Phase 2 (cscope, custom JS indexer) unless specific needs arise.
