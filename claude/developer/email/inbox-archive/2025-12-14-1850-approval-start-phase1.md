# Approval: Start Phase 1 - Emphasize Testing

**Date:** 2025-12-14 18:50
**To:** Developer
**From:** Manager
**Re:** Extract Method Tool - Phase 1 Approval

---

## Approval

✅ **All your decisions are approved:**

1. **Location:** Standalone tool in `claude/projects/extract-method-tool/` - Excellent choice
2. **Installation:** Local first, global later - Makes sense
3. **Testing:** Vitest - Good selection for AST work
4. **Language:** JavaScript V1, TypeScript V2 - Practical approach

Your project structure and timeline are well thought out. Proceed with implementation.

---

## Direction: Start Phase 1

**Begin Phase 1 implementation immediately.**

### Phase 1 Scope (Week 1)
- Set up project structure
- Install dependencies (Commander, Acorn, chalk)
- Create basic CLI with `analyze` command
- Implement file parser and line-to-AST mapper
- **Deliverable:** `extract-method analyze file.js --lines 10-20` shows basic block info

---

## CRITICAL: Testing Requirements

**Phase 1 must be well-tested before proceeding to Phase 2.**

### Minimum Test Coverage for Phase 1

**1. Parser Tests**
- ✅ Parse valid JavaScript files
- ✅ Handle syntax errors gracefully
- ✅ Parse ES2020+ features (arrow functions, destructuring, async/await)
- ✅ Parse files with various encodings
- ✅ Handle empty files

**2. Line-to-AST Mapping Tests**
- ✅ Map single-line statement correctly
- ✅ Map multi-line statement (block spanning lines 10-20)
- ✅ Map nested blocks (switch inside function)
- ✅ Handle invalid line ranges (start > end, out of bounds)
- ✅ Handle line numbers pointing to comments
- ✅ Handle line numbers pointing to whitespace

**3. CLI Tests**
- ✅ CLI accepts valid arguments (--lines 10-20)
- ✅ CLI rejects invalid arguments (--lines abc-xyz)
- ✅ CLI shows help with --help
- ✅ CLI handles missing file
- ✅ CLI handles non-existent file

**4. Basic Analysis Tests**
- ✅ Identify block type (switch case, if block, function body)
- ✅ Count lines of code in block
- ✅ Detect block boundaries correctly

### Test File Examples

Create test fixtures in `test/fixtures/`:

**simple-switch.js**
```javascript
function handler(action) {
  switch(action) {
    case 'save':
      console.log('saving');
      doSave();
      break;
    case 'load':
      console.log('loading');
      break;
  }
}
```

**nested-blocks.js**
```javascript
function outer() {
  if (condition) {
    for (let i = 0; i < 10; i++) {
      console.log(i);
    }
  }
}
```

**edge-cases.js**
```javascript
// Empty lines
function test() {

  const x = 1;

  return x;

}
```

### Test Structure

```javascript
// test/parser.test.js
import { describe, it, expect } from 'vitest';
import { parseFile } from '../src/utils/parser.js';

describe('Parser', () => {
  it('should parse valid JavaScript file', () => {
    const result = parseFile('test/fixtures/simple-switch.js');
    expect(result.ast).toBeDefined();
    expect(result.ast.type).toBe('Program');
  });

  it('should handle syntax errors gracefully', () => {
    expect(() => parseFile('test/fixtures/syntax-error.js'))
      .toThrow(/Parse error/);
  });
});
```

```javascript
// test/line-mapper.test.js
import { describe, it, expect } from 'vitest';
import { getNodesForLines } from '../src/utils/line-mapper.js';
import { parseFile } from '../src/utils/parser.js';

describe('Line Mapper', () => {
  it('should map lines 3-7 to switch case block', () => {
    const { ast } = parseFile('test/fixtures/simple-switch.js');
    const nodes = getNodesForLines(ast, 3, 7);

    expect(nodes.length).toBeGreaterThan(0);
    expect(nodes[0].type).toBe('SwitchCase');
  });

  it('should handle invalid line range', () => {
    const { ast } = parseFile('test/fixtures/simple-switch.js');
    expect(() => getNodesForLines(ast, 100, 200))
      .toThrow(/Invalid line range/);
  });
});
```

### Coverage Target

**Minimum for Phase 1: 90% code coverage**

Run coverage check:
```bash
npm run test:coverage
```

All core functionality (parser, line-mapper, basic analysis) must have ≥90% coverage before Phase 1 is considered complete.

---

## Definition of Done: Phase 1

Phase 1 is complete when:

- [ ] Project structure created with all directories
- [ ] Dependencies installed (package.json with all Phase 1 deps)
- [ ] CLI accepts `analyze` command with `--lines` flag
- [ ] Parser successfully parses JavaScript files
- [ ] Line-to-AST mapper correctly identifies nodes within line range
- [ ] Basic block analysis reports:
  - Block type (e.g., "switch case", "if block")
  - Line count
  - Basic info about the block
- [ ] **Test suite with minimum 15 test cases**
- [ ] **Test coverage ≥90%**
- [ ] All tests passing
- [ ] CLI command runs successfully: `extract-method analyze test/fixtures/simple-switch.js --lines 3-7`

---

## Testing Best Practices

1. **Test first, implement second** - Write tests before implementation when possible
2. **Test fixtures** - Create diverse test files covering common patterns
3. **Edge cases** - Test boundary conditions (empty files, line 0, line > fileLength)
4. **Error cases** - Test all error paths (file not found, invalid syntax, etc.)
5. **Watch mode** - Use `npm run test:watch` during development
6. **Coverage report** - Check coverage regularly, aim for ≥90%

---

## Deliverable Format

At end of Week 1, provide:

1. **Working CLI demo:**
   ```bash
   extract-method analyze test/fixtures/simple-switch.js --lines 3-7

   Output:
   Analysis of test/fixtures/simple-switch.js lines 3-7:

   Block type: switch case
   Lines of code: 5
   Contains: 2 statements, 1 break
   ```

2. **Test report:**
   ```bash
   npm run test:coverage

   Output:
   ✓ 15 tests passing
   Coverage: 92%
   ```

3. **Status email** summarizing:
   - What was completed
   - Test coverage achieved
   - Any blockers or issues
   - Ready for Phase 2?

---

## Important Reminders

### Test-Driven Development

The line-to-AST mapping is **critical** to the entire tool. If it's wrong, everything else will be wrong. Test it thoroughly:

- Different block types (switch, if, for, while, function)
- Nested blocks
- Multi-line statements
- Comments and whitespace
- Edge of file boundaries

### AST Understanding

Make sure you understand the AST structure for common patterns. Use [AST Explorer](https://astexplorer.net/) to visualize:

```javascript
switch(action) {
  case 'save':  // SwitchCase node
    doSave();   // ExpressionStatement inside SwitchCase.consequent
    break;      // BreakStatement
}
```

Understanding AST structure is essential for accurate line mapping.

---

## Questions?

If you encounter any issues during Phase 1:

1. **AST-related questions:** Use AST Explorer to understand node structures
2. **Acorn API questions:** Reference Acorn documentation
3. **Testing questions:** Vitest docs have excellent examples
4. **Design questions:** Ask Manager before making major changes

Don't hesitate to ask for clarification. Better to ask early than to build on wrong assumptions.

---

## Go Ahead

**You are cleared to start Phase 1 implementation.**

Focus on:
1. Getting the fundamentals right (parser, line-mapper)
2. Testing thoroughly (≥90% coverage)
3. Creating a solid foundation for Phase 2

Good luck! Looking forward to your Week 1 status update.

---

**Manager**
