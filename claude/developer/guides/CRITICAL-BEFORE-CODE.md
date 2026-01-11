# ⚠️ CRITICAL CHECKLIST - Read Before Modifying Any Code

**STOP! Complete this checklist before making ANY code changes:**

## 1. Check Lock Files

```bash
# Check if repo is locked by another session
cat claude/locks/inav.lock 2>/dev/null || echo "No lock"
cat claude/locks/inav-configurator.lock 2>/dev/null || echo "No lock"
```

**If locked:** STOP. Report to manager that repo is locked. Do NOT proceed.

## 2. Acquire Lock (if unlocked)

Use the `/start-task` skill - it handles lock acquisition and branch creation automatically.

OR manually:
```bash
# Create lock file with session info
echo "Locked by: [task-name] at $(date)" > claude/locks/inav.lock
# (or inav-configurator.lock depending on which repo)
```

## 3. Create Git Branch

```bash
cd inav  # or inav-configurator
git checkout master && git pull
git checkout -b fix/issue-XXXX-description
```

## 4. Use Agents - NEVER Direct Commands

**❌ NEVER:**
- `cmake ..`
- `make TARGETNAME`
- `npm start` (for builds)

**✅ ALWAYS:**
- Use `inav-builder` agent for ALL builds
- Use `test-engineer` agent for ALL testing
- Use `inav-architecture` agent BEFORE searching firmware code

## 5. Before Searching Firmware Code

**❌ NEVER:** Start with `Grep` or `Explore` on `inav/src/`

**✅ ALWAYS:** Ask `inav-architecture` agent first:
```
"Where is [functionality I need to find]?"
```

The agent will tell you exactly which files/directories to look at. THEN use Grep/Read on those specific locations.

## 6. Debugging Tools Available

When investigating bugs or understanding code behavior:

1. **Serial printf debugging** - Use DEBUG macros in firmware code (via `/mwptools` for CLI)
2. **Chrome DevTools MCP** - For configurator debugging (via `/test-configurator`)
3. **GDB** - For SITL debugging (`gdb inav/build_sitl/bin/SITL.elf`)

See `guides/debugging-guide.md` for detailed usage instructions.

---

**Once this checklist is complete, proceed with your task.**

---

## Self-Improvement: Lessons Learned

When you discover something important about PRE-CODING SETUP that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future pre-coding setup, not one-off situations
- **About setup/preparation** - lock files, branches, agent usage, search strategy
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

<!-- Add new lessons above this line -->
