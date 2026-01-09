# Question: Status of Unstaged Changes in connection.js and serial.js

**Date:** 2025-12-28 11:10
**To:** Developer
**Regarding:** Your Dec 20 question about unstaged race condition fix

## Question

You reported unstaged changes in these files on Dec 20:
- `js/connection/connection.js`
- `js/main/serial.js`

These were race condition fixes (reordering `removeIpcListeners()` before `removeAllListeners()`).

Please check the current status:

### 1. Are the files still unstaged?

```bash
cd inav-configurator
git status js/connection/connection.js js/main/serial.js
```

**Report:**
- Are they still showing as modified/unstaged?
- Or have they been committed/PR'd already?
- Or have they been discarded?

### 2. Check recent changes to these files

```bash
# Check recent commits to these files
git log --oneline --since="2025-12-15" -- js/connection/connection.js js/main/serial.js

# Check if anyone else modified them
git log -p --since="2025-12-15" -- js/connection/connection.js js/main/serial.js
```

**Report:**
- Has anyone else made changes to these files since Dec 20?
- Do those changes overlap with your race condition fix?
- Is your fix already incorporated, or still needed?

### 3. Compare your changes to current state

If files are still unstaged:

```bash
# Show your unstaged changes
git diff js/connection/connection.js
git diff js/main/serial.js
```

**Report:**
- Describe what your unstaged changes do
- Are they still relevant given any recent commits?
- Do they conflict with recent changes?

## Background

It's been 8 days since your question. Before deciding whether to create a PR, discard, or hold off, I need to know:
1. Current state of those files
2. Whether recent changes have addressed the issue
3. Whether your fix is still needed

Please provide this status update so I can give you proper guidance.

---
**Manager**
