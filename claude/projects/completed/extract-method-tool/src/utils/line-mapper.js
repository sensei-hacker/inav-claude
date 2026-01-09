/**
 * line-mapper.js - Line Number to AST Node Mapping
 *
 * This module provides utilities for mapping line numbers in source code
 * to AST nodes. It's the core of how the tool identifies which code to
 * extract based on user-specified line ranges.
 *
 * WHAT IT DOES:
 *   - Maps line numbers to AST nodes
 *   - Walks/traverses the entire AST tree
 *   - Finds nodes that overlap with line ranges
 *   - Finds nodes completely contained in line ranges
 *   - Identifies statement-level nodes (vs expressions)
 *   - Finds the containing parent scope for a line range
 *   - Provides comprehensive metadata about line ranges
 *
 * KEY CONCEPTS:
 *   - "Overlapping" nodes: Any node that touches the line range
 *   - "Contained" nodes: Nodes completely within the line range
 *   - "Statements": Top-level executable units (not sub-expressions)
 *   - "Parent": The smallest node that contains the entire range
 *
 * MAIN FUNCTIONS:
 *   walk(node, visitor, parent)
 *     Recursively walks AST and calls visitor on each node
 *
 *   getNodesInLineRange(ast, startLine, endLine)
 *     Finds all nodes that overlap with the line range
 *
 *   getNodesContainedInLineRange(ast, startLine, endLine)
 *     Finds nodes completely within the line range
 *
 *   getStatementsInLineRange(ast, startLine, endLine)
 *     Finds statement-level nodes in the range (what we extract)
 *
 *   findContainingParent(ast, startLine, endLine)
 *     Finds the smallest node containing the entire range
 *
 *   getLineRangeInfo(ast, startLine, endLine)
 *     Returns comprehensive metadata about the line range
 *
 * USAGE:
 *   import { getStatementsInLineRange } from './line-mapper.js';
 *   import { parseFile } from './parser.js';
 *
 *   const ast = parseFile('myfile.js');
 *   const statements = getStatementsInLineRange(ast, 10, 20);
 *   console.log(`Found ${statements.length} statements to extract`);
 *
 * @module utils/line-mapper
 * @version 0.1.0
 */

/**
 * Walk the AST and call visitor function on each node
 * @param {object} node - AST node
 * @param {function} visitor - Visitor function (node, parent) => void
 * @param {object} parent - Parent node
 */
export function walk(node, visitor, parent = null) {
  if (!node || typeof node !== 'object') return;

  visitor(node, parent);

  for (const key in node) {
    if (key === 'loc' || key === 'range' || key === 'start' || key === 'end') {
      continue; // Skip metadata
    }

    const child = node[key];
    if (Array.isArray(child)) {
      child.forEach(item => walk(item, visitor, node));
    } else if (child && typeof child === 'object' && child.type) {
      walk(child, visitor, node);
    }
  }
}

/**
 * Find all nodes that overlap with the specified line range
 * @param {object} ast - Root AST node
 * @param {number} startLine - Start line number (1-based)
 * @param {number} endLine - End line number (1-based)
 * @returns {Array} Array of nodes that overlap the line range
 */
export function getNodesInLineRange(ast, startLine, endLine) {
  const nodes = [];

  walk(ast, (node) => {
    if (!node.loc) return;

    const nodeStart = node.loc.start.line;
    const nodeEnd = node.loc.end.line;

    // Check if node overlaps with the line range
    if (nodeStart <= endLine && nodeEnd >= startLine) {
      nodes.push(node);
    }
  });

  return nodes;
}

/**
 * Find nodes that are completely contained within the line range
 * (More precise than getNodesInLineRange)
 * @param {object} ast - Root AST node
 * @param {number} startLine - Start line number (1-based)
 * @param {number} endLine - End line number (1-based)
 * @returns {Array} Array of nodes completely within the line range
 */
export function getNodesContainedInLineRange(ast, startLine, endLine) {
  const nodes = [];

  walk(ast, (node) => {
    if (!node.loc) return;

    const nodeStart = node.loc.start.line;
    const nodeEnd = node.loc.end.line;

    // Check if node is completely within the line range
    if (nodeStart >= startLine && nodeEnd <= endLine) {
      nodes.push(node);
    }
  });

  return nodes;
}

/**
 * Find the statement-level nodes within a line range
 * These are the nodes we typically want to extract
 * @param {object} ast - Root AST node
 * @param {number} startLine - Start line number (1-based)
 * @param {number} endLine - End line number (1-based)
 * @returns {Array} Array of statement nodes
 */
export function getStatementsInLineRange(ast, startLine, endLine) {
  const statementTypes = new Set([
    'ExpressionStatement',
    'VariableDeclaration',
    'FunctionDeclaration',
    'ReturnStatement',
    'IfStatement',
    'ForStatement',
    'WhileStatement',
    'DoWhileStatement',
    'SwitchStatement',
    'BreakStatement',
    'ContinueStatement',
    'ThrowStatement',
    'TryStatement',
    'BlockStatement',
  ]);

  const allNodes = getNodesContainedInLineRange(ast, startLine, endLine);

  // Filter to only statement-level nodes
  return allNodes.filter(node => statementTypes.has(node.type));
}

/**
 * Find the common parent node that contains all nodes in the line range
 * @param {object} ast - Root AST node
 * @param {number} startLine - Start line number (1-based)
 * @param {number} endLine - End line number (1-based)
 * @returns {object|null} Parent node or null if not found
 */
export function findContainingParent(ast, startLine, endLine) {
  let containingParent = null;

  walk(ast, (node, parent) => {
    if (!node.loc) return;

    const nodeStart = node.loc.start.line;
    const nodeEnd = node.loc.end.line;

    // Check if this node contains the entire range
    if (nodeStart <= startLine && nodeEnd >= endLine) {
      // This is a potential parent - keep track of the most specific one
      if (!containingParent ||
          (containingParent.loc.start.line < nodeStart ||
           containingParent.loc.end.line > nodeEnd)) {
        containingParent = node;
      }
    }
  });

  return containingParent;
}

/**
 * Get metadata about a line range
 * @param {object} ast - Root AST node
 * @param {number} startLine - Start line number (1-based)
 * @param {number} endLine - End line number (1-based)
 * @returns {object} Metadata about the line range
 */
export function getLineRangeInfo(ast, startLine, endLine) {
  const overlappingNodes = getNodesInLineRange(ast, startLine, endLine);
  const containedNodes = getNodesContainedInLineRange(ast, startLine, endLine);
  const statements = getStatementsInLineRange(ast, startLine, endLine);
  const parent = findContainingParent(ast, startLine, endLine);

  return {
    startLine,
    endLine,
    lineCount: endLine - startLine + 1,
    overlappingNodes: overlappingNodes.length,
    containedNodes: containedNodes.length,
    statements: statements.length,
    hasParent: parent !== null,
    parentType: parent ? parent.type : null,
  };
}
