# Project: Document Transpiler AST Types

**Status:** TODO
**Priority:** Medium
**Type:** Documentation / Research
**Created:** 2025-12-12
**Estimated Time:** 4-6 hours

## Overview

Document the types of objects and AST nodes manipulated by the transpiler code in `inav-configurator/js/transpiler/`. Produce a structured reference showing categories and subcategories of all data types.

## Objective

Create a comprehensive type reference document that shows:
1. Acorn AST node types used by the transpiler
2. Internal transpiler data structures
3. Category hierarchy (e.g., Expression → BinaryExpression → operators)

## Scope

### Acorn AST Nodes
- Expression types (BinaryExpression, UnaryExpression, CallExpression, etc.)
- Statement types (IfStatement, BlockStatement, etc.)
- Literal types
- Identifier handling
- MemberExpression (property access)

### Operators
- Comparison operators (==, !=, <, >, <=, >=)
- Arithmetic operators (+, -, *, /, %)
- Logical operators (&&, ||, !)
- Assignment operators (=, +=, -=, ++, --)

### Transpiler Internal Types
- Logic Conditions (LC) structure
- Operand types
- Operation types
- Variable mappings (gvar, rc, flight, etc.)

## Deliverable

A document (`transpiler-ast-types.md`) containing:
- Tree structure showing type hierarchy
- May use BNF notation, tree diagrams, or any clear format
- Examples of each type where helpful
- Cross-references to source files

## Format Options

BNF form (https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) or any other convenient notation:
- Tree diagrams
- TypeScript-style type definitions
- Nested bullet lists
- Combination of above

## Success Criteria

- [ ] All major AST node types documented
- [ ] Operator categories identified
- [ ] Internal transpiler types documented
- [ ] Clear hierarchy/tree structure
- [ ] Useful as developer reference

## Directory

`inav-configurator/js/transpiler/`
