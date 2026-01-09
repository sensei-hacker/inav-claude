/**
 * scope-analyzer.js - Variable Scope Analysis
 *
 * This module analyzes variable usage, definition, and modification in AST nodes.
 * It's the core of determining what becomes parameters and return values when
 * extracting code blocks.
 *
 * WHAT IT DOES:
 *   - Finds all variables used (referenced) in a block
 *   - Finds all variables defined (declared) in a block
 *   - Finds all variables modified (assigned) in a block
 *   - Distinguishes between different variable binding types
 *
 * KEY CONCEPTS:
 *   - "Used" = Variable is referenced (read)
 *   - "Defined" = Variable is declared (const, let, var, function, param)
 *   - "Modified" = Variable is assigned to (=, +=, ++, etc.)
 *
 * ALGORITHMS:
 *   Parameters = (used - defined) ∩ availableBefore
 *   Return values = modified ∩ usedAfter
 *
 * MAIN FUNCTIONS:
 *   findUsedVariables(nodes)
 *     Returns Set of variable names that are referenced
 *
 *   findDefinedVariables(nodes)
 *     Returns Set of variable names that are declared
 *
 *   findModifiedVariables(nodes)
 *     Returns Set of variable names that are assigned to
 *
 * USAGE:
 *   import { findUsedVariables, findDefinedVariables } from './scope-analyzer.js';
 *   import { getStatementsInLineRange } from './line-mapper.js';
 *
 *   const statements = getStatementsInLineRange(ast, 10, 20);
 *   const used = findUsedVariables(statements);
 *   const defined = findDefinedVariables(statements);
 *   const params = [...used].filter(v => !defined.has(v));
 *
 * @module utils/scope-analyzer
 * @version 0.1.0
 * @status Phase 2 - In Development
 */

import { walk } from './line-mapper.js';

/**
 * Find all variables used (referenced) in given AST nodes
 * @param {Array|object} nodes - AST node or array of nodes
 * @returns {Set<string>} Set of variable names that are used
 */
export function findUsedVariables(nodes) {
  const used = new Set();
  const nodesArray = Array.isArray(nodes) ? nodes : [nodes];

  nodesArray.forEach(node => {
    walk(node, (n) => {
      // Identifier in expression context (being read)
      if (n.type === 'Identifier') {
        // Don't count identifiers that are property names or declaration names
        // We'll handle those separately
        used.add(n.name);
      }

      // Member expressions (obj.prop) - only count the object part
      if (n.type === 'MemberExpression' && !n.computed) {
        // The property name (n.property) is not a variable reference
        // Only the object (n.object) is
        // walk() will handle n.object separately
      }

      // Call expressions - the callee is used
      if (n.type === 'CallExpression') {
        // walk() will handle the callee
      }
    });
  });

  return used;
}

/**
 * Find all variables defined (declared) in given AST nodes
 * @param {Array|object} nodes - AST node or array of nodes
 * @returns {Set<string>} Set of variable names that are declared
 */
export function findDefinedVariables(nodes) {
  const defined = new Set();
  const nodesArray = Array.isArray(nodes) ? nodes : [nodes];

  nodesArray.forEach(node => {
    walk(node, (n) => {
      // Variable declarations (const, let, var)
      if (n.type === 'VariableDeclaration') {
        n.declarations.forEach(declarator => {
          if (declarator.id.type === 'Identifier') {
            defined.add(declarator.id.name);
          } else if (declarator.id.type === 'ObjectPattern') {
            // Destructuring: const { a, b } = obj
            extractPatternNames(declarator.id, defined);
          } else if (declarator.id.type === 'ArrayPattern') {
            // Destructuring: const [a, b] = arr
            extractPatternNames(declarator.id, defined);
          }
        });
      }

      // Function declarations
      if (n.type === 'FunctionDeclaration' && n.id) {
        defined.add(n.id.name);
      }

      // Function parameters (for function expressions in the block)
      if ((n.type === 'FunctionDeclaration' || n.type === 'FunctionExpression' || n.type === 'ArrowFunctionExpression') && n.params) {
        n.params.forEach(param => {
          if (param.type === 'Identifier') {
            defined.add(param.name);
          } else if (param.type === 'ObjectPattern' || param.type === 'ArrayPattern') {
            extractPatternNames(param, defined);
          } else if (param.type === 'RestElement' && param.argument.type === 'Identifier') {
            defined.add(param.argument.name);
          }
        });
      }

      // Class declarations
      if (n.type === 'ClassDeclaration' && n.id) {
        defined.add(n.id.name);
      }

      // Catch clause parameters
      if (n.type === 'CatchClause' && n.param && n.param.type === 'Identifier') {
        defined.add(n.param.name);
      }
    });
  });

  return defined;
}

/**
 * Find all variables modified (assigned to) in given AST nodes
 * @param {Array|object} nodes - AST node or array of nodes
 * @returns {Set<string>} Set of variable names that are modified
 */
export function findModifiedVariables(nodes) {
  const modified = new Set();
  const nodesArray = Array.isArray(nodes) ? nodes : [nodes];

  nodesArray.forEach(node => {
    walk(node, (n) => {
      // Assignment expressions (=, +=, -=, etc.)
      if (n.type === 'AssignmentExpression') {
        if (n.left.type === 'Identifier') {
          modified.add(n.left.name);
        } else if (n.left.type === 'MemberExpression' && n.left.object.type === 'Identifier') {
          // obj.prop = value modifies obj
          modified.add(n.left.object.name);
        }
      }

      // Update expressions (++, --)
      if (n.type === 'UpdateExpression' && n.argument.type === 'Identifier') {
        modified.add(n.argument.name);
      }

      // Variable declarations with initializers
      if (n.type === 'VariableDeclaration') {
        n.declarations.forEach(declarator => {
          // A declaration with an initializer is both a definition and a modification
          if (declarator.init) {
            if (declarator.id.type === 'Identifier') {
              modified.add(declarator.id.name);
            } else if (declarator.id.type === 'ObjectPattern' || declarator.id.type === 'ArrayPattern') {
              extractPatternNames(declarator.id, modified);
            }
          }
        });
      }
    });
  });

  return modified;
}

/**
 * Extract variable names from destructuring patterns
 * @param {object} pattern - ObjectPattern or ArrayPattern node
 * @param {Set<string>} nameSet - Set to add names to
 */
function extractPatternNames(pattern, nameSet) {
  if (pattern.type === 'ObjectPattern') {
    pattern.properties.forEach(prop => {
      if (prop.type === 'Property' && prop.value.type === 'Identifier') {
        nameSet.add(prop.value.name);
      } else if (prop.type === 'Property' && (prop.value.type === 'ObjectPattern' || prop.value.type === 'ArrayPattern')) {
        // Nested destructuring
        extractPatternNames(prop.value, nameSet);
      } else if (prop.type === 'RestElement' && prop.argument.type === 'Identifier') {
        nameSet.add(prop.argument.name);
      }
    });
  } else if (pattern.type === 'ArrayPattern') {
    pattern.elements.forEach(element => {
      if (element && element.type === 'Identifier') {
        nameSet.add(element.name);
      } else if (element && (element.type === 'ObjectPattern' || element.type === 'ArrayPattern')) {
        // Nested destructuring
        extractPatternNames(element, nameSet);
      } else if (element && element.type === 'RestElement' && element.argument.type === 'Identifier') {
        nameSet.add(element.argument.name);
      }
    });
  }
}

/**
 * Remove variables that are not actually free (defined by parent scope constructs)
 * This handles edge cases where identifiers appear in non-reference positions
 * @param {Set<string>} used - Set of used variable names
 * @param {Set<string>} defined - Set of defined variable names
 * @returns {Set<string>} Cleaned set of truly used variables
 */
export function cleanUsedVariables(used, defined) {
  const cleaned = new Set();

  for (const varName of used) {
    // If it's defined in the block, it's not a free variable
    if (!defined.has(varName)) {
      cleaned.add(varName);
    }
  }

  return cleaned;
}
