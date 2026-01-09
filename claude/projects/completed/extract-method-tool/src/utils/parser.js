/**
 * parser.js - JavaScript Parser Utility
 *
 * This module provides a wrapper around the Acorn parser for parsing
 * JavaScript source code into Abstract Syntax Trees (AST). It handles
 * both file and string input and ensures proper location/range information
 * is included for all nodes.
 *
 * WHAT IT DOES:
 *   - Parses JavaScript files to AST using Acorn
 *   - Parses JavaScript source strings to AST
 *   - Extracts source code text for specific AST nodes
 *   - Configures Acorn for modern JavaScript (ES2023+)
 *   - Includes location (line/column) and range (character offset) info
 *
 * MAIN FUNCTIONS:
 *   parseFile(filePath, options)
 *     Reads and parses a JavaScript file
 *
 *   parseSource(source, options)
 *     Parses a JavaScript source string
 *
 *   getNodeSource(source, node)
 *     Extracts the original source code for a given AST node
 *
 * USAGE:
 *   import { parseFile } from './parser.js';
 *   const ast = parseFile('myfile.js');
 *   console.log(ast.body); // Array of top-level statements
 *
 * AST FORMAT:
 *   Uses ESTree format (standard JavaScript AST format)
 *   See: https://github.com/estree/estree
 *
 * @module utils/parser
 * @requires acorn
 * @version 0.1.0
 */

import * as acorn from 'acorn';
import { readFileSync } from 'fs';

/**
 * Parse a JavaScript file to AST
 * @param {string} filePath - Path to JavaScript file
 * @param {object} options - Acorn parser options
 * @returns {object} AST with source location information
 */
export function parseFile(filePath, options = {}) {
  const source = readFileSync(filePath, 'utf-8');
  return parseSource(source, options);
}

/**
 * Parse JavaScript source code to AST
 * @param {string} source - JavaScript source code
 * @param {object} options - Acorn parser options
 * @returns {object} AST with source location information
 */
export function parseSource(source, options = {}) {
  const defaultOptions = {
    ecmaVersion: 'latest',
    sourceType: 'module',
    locations: true,  // Include line/column info
    ranges: true,     // Include character offset ranges
    allowReturnOutsideFunction: true,
    allowImportExportEverywhere: true,
    allowAwaitOutsideFunction: true,
  };

  try {
    const ast = acorn.parse(source, { ...defaultOptions, ...options });
    return ast;
  } catch (error) {
    throw new Error(`Parse error: ${error.message}`);
  }
}

/**
 * Get the source code for a specific node
 * @param {string} source - Full source code
 * @param {object} node - AST node with range info
 * @returns {string} Source code for the node
 */
export function getNodeSource(source, node) {
  if (!node.range) {
    throw new Error('Node does not have range information');
  }
  return source.slice(node.range[0], node.range[1]);
}
