# Todo List: Update MSP Library Documentation to mspapi2

## Phase 1: Research mspapi2

- [ ] Find mspapi2 GitHub repository
  - [ ] Get repository URL
  - [ ] Review README and documentation
  - [ ] Check installation instructions
  - [ ] Review API examples
- [ ] Compare with uNAVlib
  - [ ] Identify API differences
  - [ ] Note any breaking changes
  - [ ] Check if usage patterns are similar
- [ ] Document installation
  - [ ] pip install command
  - [ ] Dependencies
  - [ ] Any setup requirements

## Phase 2: Update CLAUDE.md Files

- [ ] Update `claude/developer/CLAUDE.md`
  - [ ] Change "uNAVlib/" to "mspapi2" as primary
  - [ ] Add note about uNAVlib as older alternative
  - [ ] Update description
- [ ] Update `claude/manager/CLAUDE.md`
  - [ ] Change "uNAVlib/" to "mspapi2" as primary
  - [ ] Add note about uNAVlib as older alternative

## Phase 3: Update Skills

- [ ] Update `.claude/skills/msp-protocol/SKILL.md`
  - [ ] Change primary library recommendation to mspapi2
  - [ ] Update installation instructions
  - [ ] Update code examples if needed
  - [ ] Add note: "PRs welcome to mspapi2 for improvements"
  - [ ] Keep uNAVlib mention as older alternative
- [ ] Update `.claude/skills/sitl-arm/SKILL.md`
  - [ ] Update MSP library references
  - [ ] Update import statements in examples
  - [ ] Update installation instructions
  - [ ] Keep uNAVlib as fallback option
- [ ] Update `.claude/skills/test-crsf-sitl/SKILL.md`
  - [ ] Update MSP configuration examples
  - [ ] Update library imports
  - [ ] Update installation section

## Phase 4: Update Developer Documentation

- [ ] Review `claude/developer/crsf-telemetry-msp-config-guide.md`
  - [ ] Update library imports
  - [ ] Update code examples
  - [ ] Update installation instructions
  - [ ] Note uNAVlib compatibility
- [ ] Check for other MSP-related docs
  - [ ] Search for uNAVlib references in claude/developer/
  - [ ] Update any test scripts or examples
  - [ ] Update pattern documentation if needed

## Phase 5: Verify and Test

- [ ] Check all references
  - [ ] Search for remaining "uNAVlib" hard references
  - [ ] Ensure "older alternative" notes are in place
  - [ ] Verify installation instructions are correct
- [ ] Review changes
  - [ ] All CLAUDE.md files updated
  - [ ] All skills updated
  - [ ] Documentation consistent
  - [ ] Note about PRs to mspapi2 included

## Completion

- [ ] All documentation updated
- [ ] mspapi2 is primary recommendation
- [ ] uNAVlib preserved as older alternative
- [ ] Send completion report to manager
