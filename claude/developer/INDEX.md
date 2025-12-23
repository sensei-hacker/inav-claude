# Developer Directory Index

This document describes the organization of the `claude/developer/` workspace.

---

## Directory Structure

```
claude/developer/
│
├── CLAUDE.md                 # Developer role guide
├── README.md                 # Detailed developer documentation
├── INDEX.md                  # This file - directory organization
│
├── docs/                     # Documentation and guides (tracked in git)
│   ├── testing/              # Testing guides and results
│   ├── debugging/            # Debugging techniques and tools
│   ├── transpiler/           # Transpiler documentation
│   ├── patterns/             # Code patterns and best practices
│   └── mspapi2/              # MSP API documentation
│
├── scripts/                  # Reusable scripts (tracked in git)
│   ├── testing/              # Test scripts and utilities
│   ├── build/                # Build and flash helpers
│   └── analysis/             # Code analysis and verification tools
│
├── investigations/           # Project-specific investigations (GITIGNORED)
│   ├── crsf-telemetry/       # CRSF telemetry testing
│   ├── h743-msc/             # H743 USB MSC regression
│   ├── blueberry-pid/        # PID performance investigation
│   ├── gps/                  # GPS-related investigations
│   ├── websocket/            # WebSocket/PWA analysis
│   └── target-split/         # Target directory split verification
│
├── reports/                  # Analysis reports (GITIGNORED)
│
├── archive/                  # Old/completed work (GITIGNORED)
│   ├── completed-tasks/      # Completed task assignments
│   ├── data/                 # Test logs, profiling data
│   └── legacy/               # Legacy scripts, old documents
│
├── builds/                   # Build artifacts (GITIGNORED)
│
├── work-in-progress/         # Active WIP documents (GITIGNORED)
│
└── inbox/outbox/sent/        # Email directories (GITIGNORED)
    inbox-archive/
```

---

## What Goes Where

### `docs/` - Documentation (Tracked)

General-purpose documentation that applies across projects:

| Subdirectory | Contents |
|--------------|----------|
| `testing/` | Testing guides, approaches, configurator testing |
| `debugging/` | Serial printf, GCC techniques, USB/MSC, performance, target splitting |
| `transpiler/` | Transpiler AST types, implementation notes |
| `patterns/` | Code patterns (e.g., MSP async data access) |
| `mspapi2/` | MSP API library documentation |

**Key debugging docs:**
- `debugging/usb-msc-debugging.md` - USB mass storage issues
- `debugging/performance-debugging.md` - PID loop performance
- `debugging/target-split-verification.md` - Target directory splitting
- `debugging/gcc-preprocessing-techniques.md` - GCC preprocessing

### `scripts/` - Reusable Scripts (Tracked)

Scripts that can be reused across multiple projects:

| Subdirectory | Contents |
|--------------|----------|
| `testing/` | CRSF test scripts, configurator startup tests |
| `build/` | Build and flash helpers |
| `analysis/` | Target verification, dead code detection, preprocessing tools |

### `investigations/` - Project-Specific (Gitignored)

Detailed investigation notes for specific issues. These are gitignored because:
- They contain session-specific data
- Key lessons are extracted to `docs/LESSONS-LEARNED.md`
- Useful scripts are moved to `scripts/`

### `reports/` - Analysis Reports (Gitignored)

Code review reports, qodo analysis, PR reviews.

### `archive/` - Completed Work (Gitignored)

Historical data that might be useful for reference:
- `completed-tasks/` - Old task assignments
- `data/` - Test logs, profiling output, eeprom dumps
- `legacy/` - Old scripts, superseded documents

---

## Finding Things

### Need a test script?
Look in `scripts/testing/`

### Need to understand a past investigation?
1. Check `docs/LESSONS-LEARNED.md` for key insights
2. Look in `investigations/` for full details

### Need to verify a target split?
Use scripts in `scripts/analysis/`:
- `comprehensive_verification.py`
- `verify_target_conditionals.py`
- `split_omnibus_targets.py`

### Need debugging techniques?
Look in `docs/debugging/`

---

## Adding New Content

### New investigation?
Create a subdirectory in `investigations/`:
```
investigations/my-investigation/
├── README.md
├── findings/
└── test-data/
```

When complete, extract lessons to `docs/LESSONS-LEARNED.md`.

### New reusable script?
Add to appropriate `scripts/` subdirectory.

### New documentation?
Add to appropriate `docs/` subdirectory.

### Temporary work?
Use `work-in-progress/` for session-specific notes.

---

## Gitignored Directories

The following are excluded from version control (`.gitignore`):

- `investigations/` - Project-specific data
- `reports/` - Analysis reports
- `archive/` - Old work
- `builds/` - Binary artifacts
- `work-in-progress/` - Session notes
- `inbox/`, `outbox/`, `sent/`, `inbox-archive/` - Email

**Why?** These contain session-specific data. Reusable content is extracted to tracked directories (`docs/`, `scripts/`).

---

## Related Files

- **Developer guide:** `README.md`
- **Lessons learned:** `docs/LESSONS-LEARNED.md`
- **Skills:** `.claude/skills/*/SKILL.md`
- **Root CLAUDE.md:** `../CLAUDE.md`
