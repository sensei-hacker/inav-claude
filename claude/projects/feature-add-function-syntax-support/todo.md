# TODO: Add Transpiler Support for Function Syntax

## Phase 1: Research & Analysis

### Review Current Implementation
- [ ] Read parser code (`js/transpiler/transpiler/parser.js`)
- [ ] Read analyzer code (`js/transpiler/transpiler/analyzer.js`)
- [ ] Read codegen code (`js/transpiler/transpiler/codegen.js`)
- [ ] Read arrow function helper (`js/transpiler/transpiler/arrow_function_helper.js`)
- [ ] Understand current arrow function handling

### Test Current Behavior
- [ ] Try anonymous function: `on.always(function() { ... })`
- [ ] Try named function: `function fn() { ... }; edge(fn, ...)`
- [ ] Try function expression: `const fn = function() { ... }`
- [ ] Document current errors/failures
- [ ] Identify exactly what doesn't work

### Analyze Requirements
- [ ] List all places arrow functions are currently used
- [ ] Determine which function features to support
- [ ] Decide on limitations (parameters, closures, nesting)
- [ ] Plan error messages for unsupported features
- [ ] Document decision rationale

### Create Test Cases
- [ ] Write test case: Anonymous function in `on.always()`
- [ ] Write test case: Anonymous function in `edge()`
- [ ] Write test case: Named function declaration + reference
- [ ] Write test case: Function expression
- [ ] Write test case: Multiple references to same function
- [ ] Write test case: Function with parameters (should error)
- [ ] Write test case: Nested function (should error?)
- [ ] Write test case: Closure (should error?)

## Phase 2: Parser Updates

### Verify Acorn Configuration
- [ ] Check Acorn parser options
- [ ] Ensure function syntax is enabled
- [ ] Test Acorn parsing of function declarations
- [ ] Test Acorn parsing of function expressions
- [ ] Verify AST structure for functions

### Update Parser Code
- [ ] Identify where to handle `FunctionDeclaration` nodes
- [ ] Identify where to handle `FunctionExpression` nodes
- [ ] Ensure function nodes are preserved in AST
- [ ] Handle named vs anonymous functions
- [ ] Preserve function bodies for codegen

### Test Parser
- [ ] Parse: `function() { gvar[0] = 1; }`
- [ ] Parse: `function name() { gvar[0] = 1; }`
- [ ] Parse: `const fn = function() { ... }`
- [ ] Verify correct AST structure
- [ ] Check that body is captured
- [ ] Verify function name is captured (if named)

## Phase 3: Analyzer Updates

### Function Declaration Handling
- [ ] Detect `FunctionDeclaration` nodes
- [ ] Extract function name
- [ ] Add function name to symbol table/scope
- [ ] Store function AST node for later lookup
- [ ] Handle hoisting (or require forward declaration)

### Function Expression Handling
- [ ] Detect `FunctionExpression` nodes
- [ ] Handle as part of variable declaration (if applicable)
- [ ] Handle as direct argument to helper functions
- [ ] Ensure function body is validated

### Function Reference Handling
- [ ] Detect when identifier refers to function
- [ ] Look up function in symbol table
- [ ] Verify function exists (error if not declared)
- [ ] Retrieve function AST node for transpilation
- [ ] Handle forward references (if supporting hoisting)

### Validation
- [ ] Validate function body (same as arrow functions)
- [ ] Error on functions with parameters
- [ ] Error on closures (if not supporting)
- [ ] Error on nested functions (if not supporting)
- [ ] Error on recursive functions
- [ ] Validate return statement usage

### Error Messages
- [ ] "Function 'X' referenced but not declared"
- [ ] "Function parameters are not supported"
- [ ] "Closures are not supported"
- [ ] "Nested functions are not supported"
- [ ] "Recursive functions are not supported"

## Phase 4: Code Generator Updates

### Function Declaration Processing
- [ ] Detect `FunctionDeclaration` nodes
- [ ] Store function name → body mapping
- [ ] Don't generate logic conditions yet (wait for references)
- [ ] Handle function declarations at top level

### Function Expression Processing
- [ ] Detect `FunctionExpression` nodes in helper calls
- [ ] Extract function body
- [ ] Transpile body to logic conditions
- [ ] Generate same output as arrow functions

### Function Reference Processing
- [ ] Detect identifier references to functions
- [ ] Look up function body from stored mapping
- [ ] Inline function body at call site
- [ ] Generate logic conditions from inlined body

### Return Statement Handling
- [ ] Extract return value from function body
- [ ] Handle implicit vs explicit return
- [ ] Convert to condition/action as appropriate
- [ ] Validate return statement placement

### Code Generation Unification
- [ ] Ensure functions generate same logic as arrow functions
- [ ] Reuse existing codegen logic where possible
- [ ] Test that `function() {}` and `() => {}` are equivalent
- [ ] Verify optimization works on both syntaxes

## Phase 5: Testing

### Unit Tests

Create test file: `js/transpiler/transpiler/tests/function_syntax_tests.js`

**Parser Tests:**
- [ ] Parse anonymous function
- [ ] Parse named function
- [ ] Parse function expression
- [ ] Verify AST structure
- [ ] Handle syntax errors

**Analyzer Tests:**
- [ ] Analyze function declaration
- [ ] Analyze function reference
- [ ] Detect undeclared function error
- [ ] Detect parameter usage error
- [ ] Detect closure usage error
- [ ] Validate function body

**Codegen Tests:**
- [ ] Generate logic from anonymous function
- [ ] Generate logic from named function reference
- [ ] Verify same output as arrow function
- [ ] Handle multiple references to same function
- [ ] Inline function body correctly

### Integration Tests

Test with full transpiler:

- [ ] Test Case 1: Anonymous in `on.always()`
```javascript
on.always(function() {
  gvar[0] = 100;
});
```

- [ ] Test Case 2: Named function + reference
```javascript
function check() {
  return flight.yaw > 1800;
}
edge(check, function() { gvar[0] = 1; }, function() { gvar[0] = 0; });
```

- [ ] Test Case 3: Function expression
```javascript
const resetGvar = function() {
  gvar[0] = 0;
};
on.always(resetGvar);
```

- [ ] Test Case 4: Multiple references
```javascript
function highAlt() {
  return flight.altitude > 100;
}
edge(highAlt, ...);
sticky(highAlt, ...);
```

- [ ] Test Case 5: Mix arrow and traditional
```javascript
on.always(() => { gvar[0] = 1; });
on.always(function() { gvar[1] = 2; });
```

- [ ] Test Case 6: All helper functions
```javascript
edge(function() { ... }, function() { ... }, function() { ... });
sticky(function() { ... }, function() { ... }, function() { ... });
delay(function() { ... }, 100, function() { ... });
timer(function() { ... }, 100, 200);
whenChanged(function() { ... }, 10, function() { ... });
```

### Error Case Tests

- [ ] Function with parameters
```javascript
function setValue(x) { gvar[0] = x; }  // Should error
```

- [ ] Undeclared function reference
```javascript
edge(undefinedFunc, ...);  // Should error
```

- [ ] Closure usage
```javascript
const threshold = 1800;
function check() { return flight.yaw > threshold; }  // Should error?
```

- [ ] Nested function
```javascript
function outer() {
  function inner() { ... }  // Should error?
}
```

- [ ] Recursive function
```javascript
function recursive() {
  return recursive();  // Should error
}
```

### Manual Testing

- [ ] Open configurator JavaScript Programming tab
- [ ] Test each syntax variant
- [ ] Verify transpilation succeeds
- [ ] Check generated logic conditions
- [ ] Test with SITL/real FC
- [ ] Verify logic behavior is correct

### Regression Testing

- [ ] All existing arrow function examples still work
- [ ] No performance degradation
- [ ] Error reporting still works
- [ ] Documentation examples still valid

## Phase 6: Arrow Function Helper Refactoring

### Review arrow_function_helper.js
- [ ] Understand current functionality
- [ ] Determine if it needs updating
- [ ] Consider renaming to `function_helper.js`
- [ ] Update to handle both arrow and traditional functions

### Refactor if Needed
- [ ] Extract common function processing logic
- [ ] Handle both AST node types uniformly
- [ ] Update function names to be generic
- [ ] Add tests for helper

## Phase 7: Documentation

### Code Documentation
- [ ] Add JSDoc for function handling functions
- [ ] Document AST node types handled
- [ ] Explain function inlining approach
- [ ] Note limitations (no parameters, etc.)
- [ ] Add inline comments for complex logic

### User Documentation
- [ ] Update transpiler docs with function syntax examples
- [ ] Show both arrow and traditional syntax
- [ ] Document limitations clearly
- [ ] Add "Function Syntax" section
- [ ] Update all examples to show both options

### Update Examples
- [ ] Update built-in examples (optional)
- [ ] Add example using named functions
- [ ] Show function reusability pattern
- [ ] Add comments explaining syntax choice

### API Documentation
- [ ] Update API definitions if needed
- [ ] Note that both syntaxes work identically
- [ ] Document best practices

## Phase 8: Error Handling & UX

### Implement Error Messages
- [ ] Clear error for function parameters
- [ ] Clear error for undeclared functions
- [ ] Clear error for unsupported features
- [ ] Include line numbers
- [ ] Suggest arrow function alternative if appropriate

### Edge Cases
- [ ] Empty function body
- [ ] Function with only return statement
- [ ] Function with multiple return statements
- [ ] Function with no return (for action functions)
- [ ] Function declared multiple times (error)
- [ ] Function shadowing (outer/inner scope)

### User Experience
- [ ] Ensure transpilation time doesn't increase significantly
- [ ] Verify error messages are helpful
- [ ] Test with novice JavaScript code
- [ ] Ensure examples are clear

## Phase 9: Performance & Optimization

### Performance Testing
- [ ] Benchmark transpilation time before/after
- [ ] Test with large code samples
- [ ] Verify no memory leaks
- [ ] Check function inlining overhead

### Optimization Opportunities
- [ ] Cache inlined function bodies
- [ ] Detect equivalent functions (same logic)
- [ ] Eliminate unused functions
- [ ] Optimize repeated inlining

### Code Review
- [ ] Remove debug logging
- [ ] Clean up commented code
- [ ] Verify code quality
- [ ] Check for code duplication

## Phase 10: Release Preparation

### Final Testing
- [ ] Full regression test suite
- [ ] Test all examples
- [ ] Test error cases
- [ ] Verify documentation accuracy
- [ ] Test with SITL
- [ ] Test with real FC (if possible)

### Pre-Commit Checklist
- [ ] All tests pass
- [ ] No console errors
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] No regressions
- [ ] Performance acceptable

### Commit & PR
- [ ] Write descriptive commit message
- [ ] Explain motivation (user flexibility)
- [ ] Show before/after examples
- [ ] Note limitations clearly
- [ ] Link to project documentation

## Implementation Patterns

### Pattern 1: Detect Function Node
```javascript
function isFunctionNode(node) {
  return node.type === 'FunctionDeclaration' ||
         node.type === 'FunctionExpression' ||
         node.type === 'ArrowFunctionExpression';
}
```

### Pattern 2: Extract Function Body
```javascript
function extractFunctionBody(node) {
  if (node.type === 'ArrowFunctionExpression' && node.body.type !== 'BlockStatement') {
    // Arrow function with implicit return: () => expr
    return { type: 'ReturnStatement', argument: node.body };
  }
  // Traditional function or arrow with block
  return node.body;
}
```

### Pattern 3: Store Function Declaration
```javascript
// In analyzer
const functionMap = new Map();

function visitFunctionDeclaration(node) {
  const name = node.id.name;
  if (functionMap.has(name)) {
    throw new Error(`Function '${name}' already declared`);
  }
  functionMap.set(name, node);
  // Validate function body
  this.visit(node.body);
}
```

### Pattern 4: Inline Function Reference
```javascript
// In codegen
function generateFromFunctionReference(identifier) {
  const functionNode = this.analyzer.lookupFunction(identifier.name);
  if (!functionNode) {
    throw new Error(`Function '${identifier.name}' not declared`);
  }
  // Generate logic from function body
  return this.generateFromFunction(functionNode);
}
```

### Pattern 5: Unified Function Processing
```javascript
function generateFromFunction(node) {
  // Handle both arrow and traditional functions uniformly
  const body = extractFunctionBody(node);
  const statements = body.type === 'BlockStatement' ? body.body : [body];

  for (const stmt of statements) {
    this.generateStatement(stmt);
  }
}
```

## Questions for Manager

- Should we support function parameters? (Recommendation: No, too complex)
- Should we support closures? (Recommendation: No, too complex)
- Should we support nested functions? (Recommendation: No, too complex)
- Should we support hoisting? (Recommendation: No, require forward declarations)
- Should function declarations generate warnings if unused?
- What's the priority - high enough to start before ESM refactor completes?

## Notes

- Keep implementation simple - error on advanced features
- Focus on common use cases (anonymous functions, basic named functions)
- Ensure equivalence with arrow functions (same logic conditions)
- Add comprehensive tests - this is core functionality
- Consider what JavaScript beginners expect to work

## Success Checklist

Final verification:
- [ ] Anonymous functions work in all helper contexts
- [ ] Named functions can be declared and referenced
- [ ] Function expressions work
- [ ] Generated logic is identical to arrow function equivalent
- [ ] Clear errors for unsupported features
- [ ] No regression in arrow function support
- [ ] Documentation shows both syntaxes
- [ ] Examples demonstrate function reusability
- [ ] Performance is acceptable
- [ ] All tests pass
