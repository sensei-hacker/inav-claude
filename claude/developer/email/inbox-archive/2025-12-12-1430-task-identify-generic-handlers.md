# Task Assignment: Identify Transpiler Generic Handler Opportunities

**Date:** 2025-12-12 14:30
**Project:** identify-transpiler-generic-handlers
**Priority:** Medium
**Estimated Effort:** 3-5 hours
**Depends On:** document-transpiler-ast-types (do that first)

## Task

Using `transpiler-ast-types.md` and the transpiler source code, identify cases where specific handling for each subtype could be simplified by handling the supertype generically.

## What to Look For

### Report These (genuine improvements)

**Example:** Separate handlers for ">", "<", "===" that duplicate logic
```javascript
// BEFORE: repetitive
if (op === '>') { return handleGreaterThan(left, right); }
if (op === '<') { return handleLessThan(left, right); }
if (op === '===') { return handleEquals(left, right); }

// AFTER: generic
if (isComparisonOp(op)) { return handleComparison(op, left, right); }
```

**Look for:**
- Switch statements with many similar cases → lookup table
- Repeated patterns across subtypes → single generic handler
- Adding new subtype requires touching multiple places → centralize
- Duplicate validation/transformation logic across types

### DON'T Report These

- Several short, clear functions that happen to handle related types (that's fine)
- Cases where subtypes genuinely need different logic
- Combining would just make one long function instead of several short ones
- Abstractions that would obscure rather than clarify

## Key Question

For each candidate, ask: **"Would a generic handler make this simpler to understand and maintain, or just different?"**

Only report if the answer is genuinely "simpler."

## Deliverable

Create `claude/developer/reports/transpiler-generic-handler-opportunities.md`:

```markdown
# Transpiler Generic Handler Opportunities

## 1. [Brief Description]

**Location:** `file.js:123-145`

**Current:** Separate handling for X, Y, Z subtypes

**Problem:** [Why this is suboptimal - duplication, maintenance burden, etc.]

**Proposed:** Generic handler for supertype

**Why Better:** [Concrete benefit - fewer lines, single point of change, clearer logic]

**Effort:** ~X hours

---

## 2. [Next opportunity...]
```

## Success Criteria

- [ ] Code reviewed with type hierarchy in mind
- [ ] Only genuine simplification opportunities listed
- [ ] Clear "why it's better" for each
- [ ] No "combine for combining's sake" suggestions

## Sequence

1. First complete: `document-transpiler-ast-types`
2. Then do this task using that document as reference

---
**Manager**
