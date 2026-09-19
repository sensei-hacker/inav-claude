# Coding Standards

These are the coding standards for INAV firmware and configurator development.

## Code Organization & Structure

### File Size Limit (150 lines)

If a file would be over 150 lines, consider if it can and should be broken into smaller logical segments in different files.

**Important:** Not all files can be split - some cohesive lists or structures shouldn't be divided.

**Use judgment:**
- Prioritize logical coherence over arbitrary line counts
- Example: A configuration list of 200 items might be fine as one file
- Example: A 200-line file with multiple unrelated functions should be split

### Function Length (12 lines)

Consider if functions longer than 12 lines should be divided.

**Guidelines:**
- Look for natural breakpoints or logical sub-tasks
- Extract helper functions with clear, descriptive names
- Balance: Don't over-fragment into too many tiny functions
- Some complex algorithms may naturally exceed 12 lines - use judgment

### Helper Classes for Main Files

If adding features would add >40 new lines to a main transpiler file (parser.js, analyzer.js, codegen.js), use helper classes.

**Guidelines:**
- Helper classes themselves can be 100-200+ lines
- Goal: Keep main files focused and maintainable

---

## Code Quality

- **Clear naming** - Functions, variables, and classes should have descriptive names
- **Single responsibility** - Each function/class should do one thing well
- **Avoid deep nesting** - Consider early returns or extracting nested logic
- **Self-documenting code** - Good variable names over comments
- **Use existing libraries**, scripts, and skills in preference to writing your own new (buggy) code

---

## Comments

The purpose of comments is to explain code that would otherwise be confusing. Do not add a comment that is redundant to perfectly clear code.
Comments should explain WHY, not WHAT. Never write comments that simply restate what the code does.

### Bad - Redundant Comments

```javascript
// Hide the intro section
$('#wizard-intro').addClass('is-hidden');

// Add 5 to the counter
counter += 5;
```

### Good - Comments That Add Value

```javascript
// Motor 0 maps to rear-right in standard Quad X layout
$(`#wizardPos${positionIndex}`).addClass('assigned');

// Offset by 48 because DShot commands 1-47 are reserved for special commands
throttleValue = rawThrottle + 48;
```

### When to Comment

- Non-obvious business logic or domain knowledge
- Workarounds for bugs or quirks (with issue references if available)
- Why a particular approach was chosen over alternatives
- Magic numbers that aren't self-evident

### When NOT to Comment

- What the next line of code does (it's already in the code)
- Obvious operations like "increment counter" or "hide element"
- Section headers that just label code blocks
- Why something was **changed from** a previous version — that belongs in the commit message and PR description. Code comments are read without access to git history; they are not changelogs.
  - **Exception:** "use X instead of Y because Z" IS an appropriate comment when Y is what a reader of the *current* code would naturally reach for — the comment saves them from wondering "why not Y?" For example, when comparing distances a reader would naturally expect `sqrt(a*a + b*b) > other_distance` — so `// skip sqrt, comparing squares is equivalent and cheaper` is a useful comment. But "changed from sqrt to squared comparison in this PR" is a changelog entry that belongs in the commit message.

---

## Testing

### Testing Theories

**Don't assume theories** - if you think you found the cause of a bug, or think you fixed it - test your theory. It's not known until it's proven.

---

## Avoiding Over-Engineering

- **Don't add features, refactor code, or make "improvements" beyond what was asked**
  - A bug fix doesn't need surrounding code cleaned up
  - A simple feature doesn't need extra configurability
  - Don't add docstrings, comments, or type annotations to code you didn't change
  - Only add comments where the logic isn't self-evident

- **Don't add error handling, fallbacks, or validation for scenarios that can't happen**
  - Trust internal code and framework guarantees
  - Only validate at system boundaries (user input, external APIs)
  - Don't use feature flags or backwards-compatibility shims when you can just change the code

- **Don't create helpers, utilities, or abstractions for one-time operations**
  - Don't design for hypothetical future requirements
  - Three similar lines of code is better than a premature abstraction

- **Avoid backwards-compatibility hacks** like:
  - Renaming unused `_vars`
  - Re-exporting types that are no longer used
  - Adding `// removed` comments for removed code
  - If something is unused, delete it completely

---

## INAV-Specific Guidelines

### Multi-Platform Support

INAV supports F4, F7, H7, and AT32 microcontrollers. When working with target-specific code:
- Check `target.h` for pin mappings and hardware configuration
- Use hardware abstraction layers when possible
- Test on SITL before flashing to hardware

### Configuration Changes

When modifying settings:
**Use a task list tool to track these steps.**
1. Update `fc/settings.yaml` (not direct C code)
2. Rebuild to regenerate C code from YAML
3. Settings are automatically persisted to EEPROM via PG system

Use the `settings-lookup` agent to find setting details (valid values, defaults, descriptions).

### Board Support

F411 boards are deprecated (last supported in INAV 7). Focus development on F4 (F405, F427), F7, H7, and AT32 platforms.

---

## References

- **For architecture patterns:** Use `inav-architecture` agent
- **For testing approach:** See `CRITICAL-BEFORE-TEST.md`
- **For git practices:** See `git-workflow.md`

---

## Self-Improvement: Lessons

Add concise, actionable one-liners (see `guides/README.md` Capture Rubric). State the
rule, not the story.

- **Docs and comments describe the current state, not its history** — "used to be X" belongs in the commit message, not the doc/code.
- **Lead with what IS true, not what isn't** — state the actual fact/behavior; reserve negatives for genuinely surprising cases.
- **`str.split("\n")` on a trailing-newline file yields a phantom trailing `""`** — drop it before joining/merging.
- **A file "overlaps" itself at k = its full length** — self-overlap/loop detection needs a *proper* overlap (k < total non-empty lines).
- **Configurator `i18n` replaces the element's entire inner HTML** — put `i18n` on the text leaf span, not structure-bearing wrappers or JS-managed counters.
- **jBox modals don't auto-size to content** — bump the fixed `height` when adding content, and re-check live.
- **Floats must end in `f` to avoid promotion to double** — `2.0` pulls in double math on embedded targets.
- **A `SYSTEM` include dir silences `-Werror=switch` too** — prefer `#pragma GCC diagnostic ignored "-Wxxx"` around the one `#include`.
- **A promise rejection is only as good as its callers** — before making a function reject, audit callers for a catch-all `.catch` that swallows it and still runs the success callback (defeats the fix), and for callers that never attached a rejection handler (now-unhandled rejection).

<!-- Add new lessons above this line -->
