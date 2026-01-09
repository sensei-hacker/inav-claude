# JavaScript Function Hoisting Tool - Evaluation of Existing Tools

**Date:** 2025-12-14
**Evaluator:** Manager
**Status:** Research Complete

---

## Executive Summary

After researching existing JavaScript refactoring tools, I found **two viable approaches**:

1. **Use/Extend Existing Plugin:** [babel-plugin-transform-hoist-nested-functions](https://github.com/motiz88/babel-plugin-transform-hoist-nested-functions)
2. **Build Custom Codemod:** Use [jscodeshift](https://github.com/facebook/jscodeshift) to build a tailored solution

**Recommendation:** Build a custom codemod using jscodeshift. The existing Babel plugin doesn't guarantee 100% semantic equivalence (changes function identity), which violates our core requirement.

---

## Option 1: babel-plugin-transform-hoist-nested-functions

### Overview
- **Type:** Babel plugin
- **Purpose:** Automatically hoist nested functions to outermost possible scope
- **Maturity:** Experimental
- **License:** (Not specified in available docs)
- **Last Update:** Unknown (GitHub repo exists)

### Installation
```bash
npm install --save-dev babel-plugin-transform-hoist-nested-functions
```

### Configuration
```json
{
  "plugins": ["transform-hoist-nested-functions"]
}
```

### How It Works

Analyzes nested functions and moves them to outer scopes when they don't reference variables from enclosing scopes.

**Example:**
```javascript
// Before
function renderApp() {
  return renderStateContainer(({value}) => renderValue(value));
}

// After
var _hoistedAnonymousFunc = ({value}) => renderValue(value);
function renderApp() {
  return renderStateContainer(_hoistedAnonymousFunc);
}
```

### Pros ✅

1. **Ready to use** - Can install and use immediately
2. **Babel ecosystem** - Well-integrated with existing Babel pipelines
3. **Performance focus** - Designed for optimization (React render callbacks)
4. **Method hoisting** - Supports class methods with `methods: true` option

### Cons ❌

1. **❌ NOT semantically equivalent** - Changes function identity
   - Function equality comparisons (`fn === fn`) will fail
   - Functions are now shared instances instead of new instances per call

2. **❌ Experimental status** - Not production-ready, per documentation

3. **Scope escape issues** - "References to hoisted inner functions are allowed to escape their enclosing scopes"

4. **Limited control** - All-or-nothing transformation, can't selectively hoist

5. **Unknown maintenance** - Project activity unclear

### Verdict for Our Use Case

**NOT SUITABLE** - Violates the core requirement of 100% semantic equivalence. The plugin explicitly states it's "not fully transparent" and changes function identity semantics.

---

## Option 2: jscodeshift (Custom Codemod)

### Overview
- **Type:** Codemod toolkit
- **Maintainer:** Facebook (Meta)
- **Maturity:** Production-ready, widely used
- **License:** MIT
- **Active:** Yes, actively maintained

### Installation
```bash
npm install -g jscodeshift
```

### How It Works

Provides AST manipulation toolkit to build custom transformations:

1. Parse JavaScript to AST (using recast)
2. Traverse and modify AST nodes
3. Generate transformed code

**Basic structure:**
```javascript
module.exports = function(fileInfo, api, options) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  // Find functions
  root.find(j.FunctionDeclaration)
    .forEach(path => {
      // Custom hoisting logic
    });

  return root.toSource();
};
```

### Pros ✅

1. **Full control** - We control the transformation logic completely
2. **Semantic guarantees** - We can implement 100% equivalence checks
3. **Selective hoisting** - Can hoist specific functions or validate safety first
4. **Production-ready** - Widely used in industry (React, Next.js, etc.)
5. **Well-documented** - Good docs, large community
6. **Acorn compatible** - Works with same AST structure we already use
7. **Safety-first** - We can implement our edge case checks
8. **jQuery-like API** - Easy to learn and use

### Cons ❌

1. **Development time** - Need to write the transformation logic
2. **Testing required** - Need to create comprehensive test suite
3. **Maintenance** - We own the code

### Verdict for Our Use Case

**RECOMMENDED** - Gives us full control to implement 100% semantic equivalence while leveraging a battle-tested transformation framework.

---

## Option 3: Other Tools Considered

### JS CodeFormer / JS Refactor
- **Type:** VS Code extension
- **Verdict:** UI-focused, not suitable for automated/programmatic use

### OpenRewrite (Moderne)
- **Type:** Commercial refactoring platform
- **Verdict:** Added JS/TS support recently, but commercial/cloud-based

### WebStorm / IntelliJ IDEA
- **Type:** IDE refactoring features
- **Verdict:** Not available as standalone CLI tools

---

## Recommended Approach

### Strategy: Build Custom Codemod with jscodeshift

**Why this is the best option:**

1. **Meets all requirements:**
   - ✅ 100% semantic equivalence (we control the logic)
   - ✅ Safety-first (refuse unsafe hoisting)
   - ✅ Comprehensive edge case handling
   - ✅ Both CLI and programmatic API

2. **Leverages existing tech:**
   - Uses jscodeshift (proven, maintained)
   - Can integrate with Acorn (already in our deps)
   - Reuses AST patterns from INAV transpiler

3. **Manageable scope:**
   - jscodeshift handles parsing/generation
   - We only write transformation logic
   - Can reuse safety analysis patterns from transpiler

### Hybrid Approach (Alternative)

**Option A:** Use babel-plugin as reference implementation
- Study its logic for identifying hoistable functions
- Reimplement the safe parts in jscodeshift
- Add our stricter semantic equivalence checks

**Option B:** Wrap babel-plugin with validation
- Run babel-plugin transformation
- Verify semantic equivalence before/after
- Reject transformation if not equivalent
- **Risk:** May reject most transformations due to identity changes

---

## Implementation Plan Update

### Phase 1: Setup & Learning (3-5 days)
1. Install jscodeshift and dependencies
2. Study jscodeshift API and examples
3. Create basic "hello world" transformation
4. Set up test framework for transformations

### Phase 2: Core Transformation (1 week)
1. Implement function finder (identify hoistable functions)
2. Implement safety analyzer:
   - Variable shadowing detection
   - Temporal Dead Zone detection
   - Closure variable analysis
   - `this` binding analysis
3. Implement basic hoisting transformation

### Phase 3: Edge Cases & Validation (1 week)
1. Handle all edge cases from spec
2. Implement AST-based equivalence verification
3. Add comprehensive test suite (50+ cases)

### Phase 4: Polish & Integration (3-5 days)
1. CLI wrapper
2. Documentation
3. Integration examples
4. Performance testing

**Total Estimate:** 3-4 weeks (vs 5 weeks for from-scratch approach)

---

## Code Size Estimate

Using jscodeshift reduces implementation complexity:

**From-scratch approach (original estimate):**
- Parser wrapper: ~100 lines
- Function finder: ~200 lines
- Safety analyzer: ~400 lines
- Code generator: ~300 lines
- Verifier: ~200 lines
- CLI: ~100 lines
- **Total: ~1,300 lines**

**jscodeshift approach (new estimate):**
- Transform function: ~400 lines (includes safety checks)
- Verifier: ~150 lines
- CLI wrapper: ~50 lines
- **Total: ~600 lines** (54% reduction!)

---

## Dependencies Update

### Minimal Dependencies
```json
{
  "dependencies": {
    "jscodeshift": "^0.15.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "c8": "^8.0.0"
  }
}
```

**Notes:**
- Don't need separate parser (jscodeshift includes recast/esprima)
- Don't need code generator (jscodeshift handles it)
- Can remove: escodegen, estraverse, acorn wrapper
- Acorn still available for INAV transpiler if needed

---

## Examples of jscodeshift Codemods

To demonstrate feasibility, here are real-world jscodeshift codemods:

1. **React Codemod** - [react-codemod](https://github.com/reactjs/react-codemod)
   - Updates React code across versions
   - Handles complex transformations
   - Production-tested on massive codebases

2. **JS Codemods** - [js-codemod](https://github.com/cpojer/js-codemod)
   - Various JS transformations
   - Arrow functions, template literals, etc.
   - Shows patterns we can adapt

3. **ESLint Auto-fix** - Uses similar AST transformation
   - Reliable, production-ready
   - Handles edge cases well

---

## Risk Analysis Update

| Risk | Original | With jscodeshift | Mitigation |
|------|----------|------------------|------------|
| Parser bugs | Medium | **Low** | jscodeshift battle-tested |
| Codegen bugs | Medium | **Low** | recast handles generation |
| Edge cases missed | Medium | Medium | Still need thorough testing |
| Performance | Low | **Very Low** | jscodeshift optimized |
| Maintenance | High | **Medium** | Less code to maintain |

---

## Questions for Developer

Before proceeding with jscodeshift approach:

1. **Comfort level:** Familiar with jscodeshift or willing to learn?
2. **Integration:** Standalone tool or integrate into INAV transpiler?
3. **Testing:** Preference for test framework? (Vitest, Jest, Node test runner)
4. **Scope:** Start with simple cases and expand, or implement all edge cases upfront?
5. **Timeline:** 3-4 weeks acceptable? Or need faster delivery?

---

## Recommended Next Steps

1. **✅ APPROVED:** Proceed with jscodeshift approach
2. **Task:** Developer installs jscodeshift and runs basic examples
3. **Task:** Developer reviews jscodeshift docs and API
4. **Task:** Create initial transform for simple function hoisting
5. **Task:** Set up test framework with first 10 test cases
6. **Milestone:** Working prototype with basic hoisting (Week 1)

---

## References

### Tools Evaluated

- [jscodeshift](https://github.com/facebook/jscodeshift) - Facebook's codemod toolkit
- [babel-plugin-transform-hoist-nested-functions](https://github.com/motiz88/babel-plugin-transform-hoist-nested-functions) - Experimental Babel plugin
- [JS CodeFormer](https://github.com/cmstead/js-codeformer) - VS Code refactoring extension
- [OpenRewrite](https://sdtimes.com/softwaredev/moderne-adds-support-for-javascript-and-typescript-to-its-code-refactoring-tool/) - Commercial refactoring platform

### Learning Resources

- [Refactoring with Codemods and jscodeshift](https://www.toptal.com/javascript/write-code-to-rewrite-your-code) - Comprehensive tutorial
- [Automated Refactoring with JSCodeShift](https://bacarybruno.substack.com/p/automated-refactoring-with-jscodeshift) - Getting started guide
- [Mastering jscodeshift with TypeScript](https://www.xjavascript.com/blog/jscodeshift-typescript/) - Advanced patterns
- [AST Explorer](https://astexplorer.net/) - Essential tool for understanding AST structure

### Community Examples

- [react-codemod](https://github.com/reactjs/react-codemod) - Production codemods from React team
- [js-codemod](https://github.com/cpojer/js-codemod) - Collection of JS transformations
- [Automating Code Transformation](https://engineering.widen.com/blog/Automating-Code-Transformation-With-jscodeshift/) - Real-world case study

---

## Conclusion

**Decision:** Build custom function hoisting tool using jscodeshift

**Rationale:**
- Existing plugins don't meet semantic equivalence requirement
- jscodeshift provides robust foundation
- Reduces implementation effort by ~54%
- Maintains full control over safety guarantees
- Production-ready, well-supported framework

**Next Action:** Developer begins Phase 1 (Setup & Learning)
