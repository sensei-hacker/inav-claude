# Repository Separation Analysis

**Question:** Should we separate the generic context engineering structure from INAV-specific content?

**Date:** 2026-01-12

---

## Current State

**Repository:** `github.com/iNavFlight/inav` (forked/extended at `github.com/sensei-hacker/inav-claude`)

**Structure:**
```
inavflight/
├── .claude/              # Generic structure + INAV-specific agents
│   ├── agents/           # Mix of generic concepts + INAV-specific
│   ├── skills/           # Mix of generic + INAV-specific
│   └── hooks/            # Mostly generic
│
├── claude/               # Role-specific workspaces
│   ├── manager/          # Generic structure
│   ├── developer/        # Generic structure + INAV-specific guides
│   ├── release-manager/  # Generic structure + INAV-specific
│   └── projects/         # Generic structure, INAV content
│
├── inav/                 # INAV firmware (external project)
├── inav-configurator/    # INAV configurator (external project)
└── CLAUDE.md             # Entry point (generic pattern)
```

---

## What's Generic vs. INAV-Specific

### Generic (Reusable Structure)

**Directory Structure:**
- `claude/manager/`, `claude/developer/`, `claude/release-manager/` directories
- `claude/projects/` project tracking system
- `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` directories
- Email-based communication pattern
- Lock file pattern

**Workflow:**
- 12-step developer workflow
- Role separation pattern
- Just-in-time documentation loading
- Agent spawning pattern
- Hook enforcement pattern

**Files:**
- `CLAUDE.md` entry point structure
- `claude/projects/INDEX.md` and `completed/INDEX.md` format
- Email template formats
- Project summary.md and todo.md templates

### INAV-Specific (Must Stay Here)

**Content:**
- All agent implementations (`inav-builder`, `test-engineer`, `msp-expert`, etc.)
- All skill implementations (except maybe `/start-task` and `/finish-task` patterns)
- CRITICAL-BEFORE-* guide **content** (not structure)
- Developer README **content** (not structure)
- Project tracking **content**
- Lock file **content** (file paths, task names)

---

## Option 1: Monorepo (Current State)

**Keep everything in one repository.**

### Pros
- ✅ Simple - everything in one place
- ✅ Easy updates - change both structure and content together
- ✅ Works as-is - no migration needed
- ✅ Complete example - shows working system
- ✅ Context clear - can see how generic applies to specific

### Cons
- ❌ Hard to extract for other projects
- ❌ INAV-specific content mixed with generic patterns
- ❌ Harder to maintain "clean" generic version
- ❌ Can't separately version structure vs content

### Best For
- Projects that want to fork the whole thing
- Projects similar to INAV (embedded systems, C/JavaScript)
- Users who want to see complete working example first

---

## Option 2: Two Repos (Template + Instance)

**Create `claude-code-template` repo with generic structure, keep INAV-specific content here.**

### Structure

**Repo 1: `claude-code-template`** (Generic)
```
claude-code-template/
├── .claude/
│   ├── agents/
│   │   └── README.md            # How to create agents
│   ├── skills/
│   │   ├── start-task/          # Generic workflow
│   │   └── finish-task/         # Generic workflow
│   └── hooks/
│       └── subagent_hooks.py    # Generic hook script
│
├── claude/
│   ├── manager/
│   │   ├── README.md            # Generic manager guide
│   │   └── email/               # Directory structure only
│   ├── developer/
│   │   ├── README.md            # Generic developer guide
│   │   ├── guides/
│   │   │   ├── CRITICAL-BEFORE-CODE.md      # Template
│   │   │   ├── CRITICAL-BEFORE-TEST.md      # Template
│   │   │   ├── CRITICAL-BEFORE-COMMIT.md    # Template
│   │   │   └── CRITICAL-BEFORE-PR.md        # Template
│   │   └── email/               # Directory structure only
│   ├── projects/
│   │   ├── INDEX.md             # Template
│   │   └── README.md            # Project system docs
│   └── README.md                # System overview
│
├── CLAUDE.md                    # Entry point template
├── INSTALL.md                   # Installation guide
└── README.md                    # "Clone and customize"
```

**Repo 2: `sensei-hacker/inav-claude`** (INAV Instance)
```
(Same as current, but references claude-code-template as upstream)
```

### Pros
- ✅ Clean separation of concerns
- ✅ Easy to adapt for new projects
- ✅ Can version template separately
- ✅ Template improvements benefit all users
- ✅ Clear "what to customize" vs "what stays"

### Cons
- ❌ More complex - two repos to maintain
- ❌ Sync issues - need to pull template updates
- ❌ Setup harder - clone template, customize, maintain
- ❌ Template might drift from real-world usage

### Best For
- Users starting fresh projects
- Projects very different from INAV
- Long-term maintenance of multiple projects

---

## Option 3: Subtree/Submodule (Hybrid)

**Use git subtree or submodule to embed template in INAV repo.**

### Structure

**Repo 1: `claude-code-template`** (as in Option 2)

**Repo 2: `sensei-hacker/inav-claude`**
```
inavflight/
├── .claude/
│   ├── template/                # Git subtree from claude-code-template
│   ├── agents/                  # INAV-specific
│   └── skills/                  # INAV-specific
│
├── claude/
│   ├── template/                # Git subtree from claude-code-template
│   ├── manager/                 # INAV-specific content
│   └── developer/               # INAV-specific content
│
└── CLAUDE.md
```

### Pros
- ✅ Template separate but embedded
- ✅ Can pull template updates
- ✅ Single repo for users
- ✅ Clear separation in filesystem

### Cons
- ❌ Git subtree/submodule complexity
- ❌ Risk of editing template accidentally
- ❌ Merge conflicts when pulling updates
- ❌ Not intuitive for non-git experts

### Best For
- Advanced git users
- Projects that need frequent template updates
- Organizations managing multiple instances

---

## Option 4: Documentation Only (Lightest)

**Keep structure in INAV repo, publish guide "How to Adapt for Your Project"**

### What to Create

**Document:** `claude/ADAPTATION-GUIDE.md`

Sections:
1. **Clone These Directories:** List what to copy
2. **Keep Structure, Replace Content:** Explain what stays, what changes
3. **Agent Examples:** Show Python/Rust/JS agent patterns
4. **Common Customizations:** Build systems, test frameworks, etc.
5. **Week-by-Week Setup:** Incremental adoption guide

### Pros
- ✅ Simplest - no repo split needed
- ✅ Users see complete working example
- ✅ Documentation-driven adaptation
- ✅ No maintenance overhead

### Cons
- ❌ Users must manually extract structure
- ❌ No "clean template" to start from
- ❌ Risk of copying INAV-specific content by mistake
- ❌ Hard to track "template version" users based on

### Best For
- Small number of adaptors
- Projects wanting to fork and modify heavily
- Documentation-focused approach

---

## Recommendation

**Recommended: Option 2 (Two Repos) + Option 4 (Documentation)**

### Phase 1: Documentation First
1. Create `ADAPTATION-GUIDE.md` in current repo
2. Document generic vs specific clearly
3. Add examples for Python/Rust/JS projects
4. Get feedback from early adaptors

### Phase 2: Extract Template (If Demand Exists)
1. Create `claude-code-template` repository
2. Extract generic structure and patterns
3. Provide installation script that:
   - Clones template
   - Prompts for project details
   - Generates customized structure
4. Maintain INAV instance as reference

### Why This Approach

**Start Simple:**
- Current repo is working example
- Documentation helps early adoptors
- Low overhead to maintain

**Scale Up If Needed:**
- If 5+ projects want to adapt, extract template
- Template repo becomes "upstream" for improvements
- Each project maintains instance

**Best of Both:**
- Users can see complete example (INAV)
- Template repo available for clean starts
- Documentation bridges the gap

---

## Implementation Checklist (If Going with Option 2)

### Create Template Repo

- [ ] Create `github.com/sensei-hacker/claude-code-template`
- [ ] Extract generic structure (directories, templates)
- [ ] Write comprehensive README with examples
- [ ] Add installation script: `./install.sh --project-name MyProject --language python`
- [ ] Create example agents for Python/Rust/JS
- [ ] Document customization points clearly

### Update INAV Repo

- [ ] Add reference to template repo in README
- [ ] Document INAV-specific customizations
- [ ] Add "upstream" git remote to pull template updates
- [ ] Create guide "Syncing Template Updates"

### Ongoing Maintenance

- [ ] Template improvements in separate repo
- [ ] Pull template updates to INAV instance periodically
- [ ] Document any INAV-specific overrides

---

## Questions to Answer

Before deciding:

1. **How many people want to adapt this?**
   - If <5 → Documentation only (Option 4)
   - If 5-20 → Two repos (Option 2)
   - If 20+ → Consider framework/library approach

2. **How different are target projects from INAV?**
   - Very similar → Fork INAV instance
   - Different language/domain → Need clean template

3. **How often will template improve?**
   - Rarely → Documentation sufficient
   - Frequently → Need separate versioning

4. **Who's maintaining?**
   - Just you → Keep simple (Option 1 or 4)
   - Community → Separate template (Option 2)

---

## Next Steps

**Immediate:**
1. Create `ADAPTATION-GUIDE.md` in current repo
2. Add section to presentation about adaptation
3. Get feedback from potential users

**If Demand Exists:**
1. Create `claude-code-template` repository
2. Extract generic structure
3. Provide migration path for existing users

**Long Term:**
1. Collect lessons learned from adaptors
2. Improve template based on real-world usage
3. Consider additional language examples

---

## Files Referenced

- Presentation Slide 13: Discusses universal workflow and adaptation
- `claude/README.md`: System overview
- `claude/developer/README.md`: Developer guide (237 lines, some generic)
- `.claude/agents/*.md`: Agent definitions (INAV-specific but pattern is generic)

---

**Decision:** Document for now, extract template if demand warrants it.

**Rationale:** Start simple, prove value, scale up if needed. Users can fork INAV repo as-is and customize.
