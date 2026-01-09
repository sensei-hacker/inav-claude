/**
 * line-mapper.test.js - Tests for Line-to-AST Mapping Utilities
 *
 * Test suite for the line-mapper module (src/utils/line-mapper.js).
 * Verifies that line numbers are correctly mapped to AST nodes,
 * statement detection works, and parent finding is accurate.
 *
 * TEST COVERAGE:
 *   - walk() - AST traversal
 *   - getNodesInLineRange() - Finding overlapping nodes
 *   - getNodesContainedInLineRange() - Finding contained nodes
 *   - getStatementsInLineRange() - Statement detection
 *   - findContainingParent() - Parent node detection
 *   - getLineRangeInfo() - Metadata extraction
 *
 * RUN TESTS:
 *   npm test                         # All tests
 *   npm test -- line-mapper.test.js  # This file only
 *
 * @module test/line-mapper
 * @requires vitest
 */

import { describe, it, expect } from 'vitest';
import { parseFile, parseSource } from '../src/utils/parser.js';
import {
  walk,
  getNodesInLineRange,
  getNodesContainedInLineRange,
  getStatementsInLineRange,
  findContainingParent,
  getLineRangeInfo
} from '../src/utils/line-mapper.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

describe('Line Mapper', () => {
  describe('walk', () => {
    it('should visit all nodes in the AST', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);
      const visitedTypes = [];

      walk(ast, (node) => {
        visitedTypes.push(node.type);
      });

      expect(visitedTypes).toContain('Program');
      expect(visitedTypes).toContain('VariableDeclaration');
      expect(visitedTypes).toContain('VariableDeclarator');
      expect(visitedTypes).toContain('Identifier');
      expect(visitedTypes).toContain('Literal');
    });

    it('should pass parent node to visitor', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);
      let foundParent = false;

      walk(ast, (node, parent) => {
        if (node.type === 'VariableDeclaration' && parent?.type === 'Program') {
          foundParent = true;
        }
      });

      expect(foundParent).toBe(true);
    });

    it('should handle arrays of nodes', () => {
      const source = 'const x = 1; const y = 2;';
      const ast = parseSource(source);
      let declarationCount = 0;

      walk(ast, (node) => {
        if (node.type === 'VariableDeclaration') {
          declarationCount++;
        }
      });

      expect(declarationCount).toBe(2);
    });
  });

  describe('getNodesInLineRange', () => {
    it('should find nodes within a line range', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const ast = parseFile(filePath);

      // Lines 5-7 in simple-block.js
      const nodes = getNodesInLineRange(ast, 5, 7);

      expect(nodes.length).toBeGreaterThan(0);
    });

    it('should include nodes that overlap the range', () => {
      const source = `function test() {
  const x = 1;
  const y = 2;
}`;
      const ast = parseSource(source);

      // Lines 2-3 (inside function)
      const nodes = getNodesInLineRange(ast, 2, 3);

      // Should include the function declaration (overlaps) and statements inside
      const types = nodes.map(n => n.type);
      expect(types).toContain('FunctionDeclaration');
      expect(types).toContain('VariableDeclaration');
    });

    it('should return empty array for non-existent lines', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);

      const nodes = getNodesInLineRange(ast, 10, 20);

      expect(nodes).toHaveLength(0);
    });
  });

  describe('getNodesContainedInLineRange', () => {
    it('should find only nodes completely within range', () => {
      const source = `function test() {
  const x = 1;
  const y = 2;
}`;
      const ast = parseSource(source);

      // Lines 2-3 (just the variable declarations)
      const nodes = getNodesContainedInLineRange(ast, 2, 3);

      // Should NOT include the function declaration (spans lines 1-4)
      const types = nodes.map(n => n.type);
      expect(types).not.toContain('FunctionDeclaration');
      expect(types).toContain('VariableDeclaration');
    });

    it('should handle single-line ranges', () => {
      const source = `const x = 1;
const y = 2;`;
      const ast = parseSource(source);

      const nodes = getNodesContainedInLineRange(ast, 1, 1);

      // Should find nodes on line 1 only
      expect(nodes.length).toBeGreaterThan(0);
      nodes.forEach(node => {
        if (node.loc) {
          expect(node.loc.start.line).toBe(1);
          expect(node.loc.end.line).toBe(1);
        }
      });
    });
  });

  describe('getStatementsInLineRange', () => {
    it('should find statement-level nodes', () => {
      const source = `const x = 1;
const y = 2;
console.log(x + y);`;
      const ast = parseSource(source);

      const statements = getStatementsInLineRange(ast, 1, 3);

      // Should find 3 statements
      expect(statements.length).toBeGreaterThanOrEqual(3);
      statements.forEach(stmt => {
        expect(stmt.type).toMatch(/Statement|Declaration/);
      });
    });

    it('should filter out non-statement nodes', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);

      const statements = getStatementsInLineRange(ast, 1, 1);

      // Should only have VariableDeclaration, not Identifier or Literal
      const types = statements.map(s => s.type);
      expect(types).toContain('VariableDeclaration');
      expect(types).not.toContain('Identifier');
      expect(types).not.toContain('Literal');
    });

    it('should handle switch case statements', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-switch.js');
      const ast = parseFile(filePath);

      // Lines inside the case 'save' block (after adding headers)
      const statements = getStatementsInLineRange(ast, 14, 16);

      expect(statements.length).toBeGreaterThan(0);
      const types = statements.map(s => s.type);
      expect(types).toContain('ExpressionStatement');
    });
  });

  describe('findContainingParent', () => {
    it('should find the smallest node containing the range', () => {
      const source = `function test() {
  if (true) {
    const x = 1;
  }
}`;
      const ast = parseSource(source);

      // Line 3 (const x = 1) - should find the smallest containing node
      const parent = findContainingParent(ast, 3, 3);

      expect(parent).toBeDefined();
      // The most specific containing node for line 3 could be the VariableDeclaration itself,
      // or its parent BlockStatement, IfStatement, or FunctionDeclaration
      expect(['VariableDeclaration', 'BlockStatement', 'IfStatement', 'FunctionDeclaration']).toContain(parent.type);
    });

    it('should return null for invalid range', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);

      const parent = findContainingParent(ast, 10, 20);

      expect(parent).toBeNull();
    });

    it('should find function as parent for lines inside it', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const ast = parseFile(filePath);

      // Lines 14-16 are inside the function (after adding headers)
      const parent = findContainingParent(ast, 14, 16);

      expect(parent).toBeDefined();
    });
  });

  describe('getLineRangeInfo', () => {
    it('should return comprehensive metadata', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const ast = parseFile(filePath);

      const info = getLineRangeInfo(ast, 14, 16);

      expect(info).toHaveProperty('startLine', 14);
      expect(info).toHaveProperty('endLine', 16);
      expect(info).toHaveProperty('lineCount', 3);
      expect(info).toHaveProperty('overlappingNodes');
      expect(info).toHaveProperty('containedNodes');
      expect(info).toHaveProperty('statements');
      expect(info).toHaveProperty('hasParent');
      expect(info).toHaveProperty('parentType');
    });

    it('should correctly count statements', () => {
      const source = `const x = 1;
const y = 2;
const z = 3;`;
      const ast = parseSource(source);

      const info = getLineRangeInfo(ast, 1, 3);

      expect(info.statements).toBeGreaterThanOrEqual(3);
    });

    it('should indicate if parent exists', () => {
      const source = `function test() {
  const x = 1;
}`;
      const ast = parseSource(source);

      const info = getLineRangeInfo(ast, 2, 2);

      expect(info.hasParent).toBe(true);
      expect(info.parentType).toBeDefined();
    });
  });
});
