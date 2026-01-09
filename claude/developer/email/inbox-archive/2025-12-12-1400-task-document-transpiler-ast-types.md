# Task Assignment: Document Transpiler AST Types

**Date:** 2025-12-12 14:00
**Project:** document-transpiler-ast-types
**Priority:** Medium
**Estimated Effort:** 4-6 hours

## Task

Analyze `inav-configurator/js/transpiler/` and document the types of objects manipulated by that code, including Acorn AST node types. Produce a document with a tree showing categories and subcategories.

## What to Document

### 1. Acorn AST Node Types
The transpiler parses JavaScript using Acorn. Document all AST node types used:
- Expression types (BinaryExpression, UnaryExpression, CallExpression, MemberExpression, etc.)
- Statement types (IfStatement, BlockStatement, ExpressionStatement, etc.)
- Literals, Identifiers
- How these map to transpiler processing

### 2. Operators
Expressions have operators and operands. Categorize:
- **Comparison operators:** ==, !=, <, >, <=, >=
- **Arithmetic operators:** +, -, *, /, %
- **Logical operators:** &&, ||, !
- **Assignment operators:** =, +=, -=, ++, --
- **Other operators?**

### 3. Transpiler Internal Types
- Logic Condition (LC) structure
- Operand types (what can be an operand?)
- Operation codes
- Variable types (gvar[], rc[], flight.*, etc.)

## Deliverable

Create `claude/developer/docs/transpiler-ast-types.md` containing:
- Tree structure showing type hierarchy
- You may use BNF notation (https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) or any other convenient format
- Examples where helpful

## Example Structure (rough idea)

```
Expression
├── BinaryExpression
│   ├── operator: ComparisonOp | ArithmeticOp | LogicalOp
│   ├── left: Expression
│   └── right: Expression
├── UnaryExpression
│   ├── operator: "!" | "-" | "++"
│   └── argument: Expression
├── CallExpression
│   ├── callee: Identifier | MemberExpression
│   └── arguments: Expression[]
...
```

Or BNF:
```
<expression> ::= <binary-expr> | <unary-expr> | <call-expr> | <literal> | <identifier>
<binary-expr> ::= <expression> <binary-op> <expression>
<binary-op> ::= <comparison-op> | <arithmetic-op> | <logical-op>
...
```

## Success Criteria

- [ ] All major AST node types documented
- [ ] Operators categorized
- [ ] Internal transpiler types included
- [ ] Clear hierarchy structure
- [ ] Useful as ongoing developer reference

## Directory to Analyze

`inav-configurator/js/transpiler/`

---
**Manager**
