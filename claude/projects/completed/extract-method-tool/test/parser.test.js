/**
 * parser.test.js - Tests for JavaScript Parser Utility
 *
 * Test suite for the parser module (src/utils/parser.js).
 * Verifies that JavaScript source code is correctly parsed to AST,
 * location/range information is included, and errors are handled.
 *
 * TEST COVERAGE:
 *   - parseSource() - Parsing source strings
 *   - parseFile() - Parsing files
 *   - getNodeSource() - Extracting node source code
 *   - Error handling for invalid syntax
 *   - Modern JavaScript feature support
 *
 * RUN TESTS:
 *   npm test                    # All tests
 *   npm test -- parser.test.js  # This file only
 *
 * @module test/parser
 * @requires vitest
 */

import { describe, it, expect } from 'vitest';
import { parseFile, parseSource, getNodeSource } from '../src/utils/parser.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

describe('Parser', () => {
  describe('parseSource', () => {
    it('should parse valid JavaScript code', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);

      expect(ast).toBeDefined();
      expect(ast.type).toBe('Program');
      expect(ast.body).toHaveLength(1);
      expect(ast.body[0].type).toBe('VariableDeclaration');
    });

    it('should include location information', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);

      expect(ast.loc).toBeDefined();
      expect(ast.loc.start).toBeDefined();
      expect(ast.loc.end).toBeDefined();
      expect(ast.body[0].loc.start.line).toBe(1);
    });

    it('should include range information', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);

      expect(ast.range).toBeDefined();
      expect(ast.body[0].range).toBeDefined();
      expect(ast.body[0].range).toHaveLength(2);
    });

    it('should throw error for invalid syntax', () => {
      const source = 'const x = ;'; // Invalid syntax

      expect(() => parseSource(source)).toThrow(/Parse error/);
    });

    it('should parse modern JavaScript features', () => {
      const source = 'const fn = async (x) => { await x(); };';
      const ast = parseSource(source);

      expect(ast).toBeDefined();
      expect(ast.type).toBe('Program');
    });

    it('should parse multiple statements', () => {
      const source = `
        const x = 1;
        const y = 2;
        console.log(x + y);
      `;
      const ast = parseSource(source);

      expect(ast.body).toHaveLength(3);
    });
  });

  describe('parseFile', () => {
    it('should parse a JavaScript file', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const ast = parseFile(filePath);

      expect(ast).toBeDefined();
      expect(ast.type).toBe('Program');
      expect(ast.body.length).toBeGreaterThan(0);
    });

    it('should include location info from file', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const ast = parseFile(filePath);

      expect(ast.body[0].loc).toBeDefined();
    });
  });

  describe('getNodeSource', () => {
    it('should extract source code for a node', () => {
      const source = 'const x = 1;';
      const ast = parseSource(source);
      const varDecl = ast.body[0];

      const nodeSource = getNodeSource(source, varDecl);

      expect(nodeSource).toBe('const x = 1;');
    });

    it('should handle multi-line nodes', () => {
      const source = `function test() {
  return 1;
}`;
      const ast = parseSource(source);
      const funcDecl = ast.body[0];

      const nodeSource = getNodeSource(source, funcDecl);

      expect(nodeSource).toContain('function test()');
      expect(nodeSource).toContain('return 1;');
    });

    it('should throw error if node has no range', () => {
      const source = 'const x = 1;';
      const fakeNode = { type: 'Identifier' }; // No range property

      expect(() => getNodeSource(source, fakeNode)).toThrow(/range information/);
    });
  });
});
