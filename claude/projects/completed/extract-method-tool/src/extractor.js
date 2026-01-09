/**
 * extractor.js - Code Extraction Engine
 *
 * This module generates extracted functions and replacement calls for the
 * Extract Method refactoring pattern. It takes analyzed code blocks and
 * produces syntactically correct JavaScript code.
 *
 * WHAT IT DOES (Phase 3):
 *   - Generates function with detected parameters
 *   - Copies statements from original block
 *   - Transforms control flow (break → return)
 *   - Adds return statement if needed
 *   - Generates replacement function call
 *   - Produces code preview for user review
 *
 * MAIN FUNCTIONS:
 *   extractMethod(analysis, functionName, options)
 *     Generates extracted function and replacement call
 *
 *   generateExtractedFunction(analysis, functionName, options)
 *     Creates the new function code
 *
 *   generateReplacementCall(analysis, functionName, options)
 *     Creates the function call that replaces the original block
 *
 * USAGE:
 *   import { extractMethod } from './extractor.js';
 *   const result = extractMethod(analysis, 'handleSave');
 *   console.log(result.extractedFunction); // "function handleSave() { ... }"
 *   console.log(result.replacementCall);   // "handleSave();"
 *
 * @module extractor
 * @version 0.3.0
 * @status Phase 3 - In Progress
 */

import * as recast from 'recast';

/**
 * Extract a code block into a function
 *
 * @param {Object} analysis - Analysis result from analyzer.js
 * @param {string} functionName - Name for the extracted function
 * @param {Object} options - Extraction options
 * @param {boolean} options.transformBreak - Transform break to return (default: auto-detect)
 * @param {string} options.placement - Where to place function: 'before' | 'after' | 'top'
 * @returns {Object} Extraction result
 */
export function extractMethod(analysis, functionName, options = {}) {
  if (!analysis.feasible) {
    throw new Error('Cannot extract: analysis indicates extraction is not feasible');
  }

  if (!functionName || typeof functionName !== 'string') {
    throw new Error('Function name is required');
  }

  // Validate function name (basic check)
  if (!/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(functionName)) {
    throw new Error(`Invalid function name: ${functionName}`);
  }

  const extractedFunction = generateExtractedFunction(analysis, functionName, options);
  const replacementCall = generateReplacementCall(analysis, functionName, options);

  return {
    functionName,
    extractedFunction,
    replacementCall,
    parameters: analysis.metrics.parameters,
    returnValue: analysis.metrics.returnValue,
    controlFlow: analysis.metrics.controlFlow
  };
}

/**
 * Generate the extracted function code
 *
 * @param {Object} analysis - Analysis result
 * @param {string} functionName - Name for the function
 * @param {Object} options - Generation options
 * @returns {string} Generated function code
 */
export function generateExtractedFunction(analysis, functionName, options = {}) {
  const { parameters, returnValue, controlFlow } = analysis.metrics;

  // Parse the original file to get the AST
  const { ast, sourceLines } = analysis._sourceInfo;
  const { statements } = analysis._extractedNodes;

  // Determine if we need to transform break statements
  const shouldTransformBreak = options.transformBreak !== undefined
    ? options.transformBreak
    : (analysis.parentType === 'SwitchCase' && controlFlow.breaks > 0);

  // Build function parameters
  const paramNames = parameters.map(p => p.name);

  // Clone the statements and transform them
  const transformedStatements = statements.map(stmt => {
    // Deep clone the statement
    const cloned = JSON.parse(JSON.stringify(stmt));

    // Transform break → return if in switch case
    if (shouldTransformBreak) {
      transformBreakToReturn(cloned);
    }

    return cloned;
  });

  // Add return statement if needed
  if (returnValue) {
    const returnStmt = {
      type: 'ReturnStatement',
      argument: {
        type: 'Identifier',
        name: returnValue
      }
    };
    transformedStatements.push(returnStmt);
  }

  // Build the function AST
  const functionAst = {
    type: 'FunctionDeclaration',
    id: {
      type: 'Identifier',
      name: functionName
    },
    params: paramNames.map(name => ({
      type: 'Identifier',
      name: name
    })),
    body: {
      type: 'BlockStatement',
      body: transformedStatements
    }
  };

  // Generate code from AST using recast
  const output = recast.print(functionAst, {
    tabWidth: 2,
    useTabs: false,
    quote: 'single'
  });

  return output.code;
}

/**
 * Generate the replacement function call
 *
 * @param {Object} analysis - Analysis result
 * @param {string} functionName - Name of the extracted function
 * @param {Object} options - Generation options
 * @returns {string} Generated function call code
 */
export function generateReplacementCall(analysis, functionName, options = {}) {
  const { parameters, returnValue } = analysis.metrics;

  // Build argument list
  const args = parameters.map(p => p.name);

  // Build call expression
  const callExpr = {
    type: 'CallExpression',
    callee: {
      type: 'Identifier',
      name: functionName
    },
    arguments: args.map(name => ({
      type: 'Identifier',
      name: name
    }))
  };

  // Wrap in assignment if there's a return value
  let statement;
  if (returnValue) {
    statement = {
      type: 'ExpressionStatement',
      expression: {
        type: 'AssignmentExpression',
        operator: '=',
        left: {
          type: 'Identifier',
          name: returnValue
        },
        right: callExpr
      }
    };
  } else {
    statement = {
      type: 'ExpressionStatement',
      expression: callExpr
    };
  }

  // Generate code
  const output = recast.print(statement, {
    tabWidth: 2,
    useTabs: false,
    quote: 'single'
  });

  return output.code;
}

/**
 * Transform break statements to return statements
 *
 * This is needed when extracting switch case blocks, where break
 * exits the switch but return exits the function.
 *
 * @param {Object} node - AST node to transform (mutates in place)
 */
function transformBreakToReturn(node) {
  if (!node || typeof node !== 'object') {
    return;
  }

  // If this is a break statement (unlabeled), convert to return
  if (node.type === 'BreakStatement' && !node.label) {
    node.type = 'ReturnStatement';
    node.argument = null;
    delete node.label;
  }

  // Recursively transform child nodes
  for (const key in node) {
    if (key === 'type' || key === 'loc' || key === 'range') {
      continue;
    }

    const value = node[key];

    if (Array.isArray(value)) {
      value.forEach(transformBreakToReturn);
    } else if (value && typeof value === 'object') {
      transformBreakToReturn(value);
    }
  }
}

/**
 * Format extraction result for preview display
 *
 * @param {Object} extraction - Extraction result from extractMethod()
 * @param {Object} analysis - Original analysis result
 * @returns {string} Formatted preview text
 */
export function formatPreview(extraction, analysis) {
  const lines = [];

  lines.push('=== EXTRACTED FUNCTION ===\n');
  lines.push(extraction.extractedFunction);
  lines.push('\n');

  lines.push('=== REPLACEMENT CODE ===\n');
  lines.push(extraction.replacementCall);
  lines.push('\n');

  lines.push('=== SUMMARY ===');
  lines.push(`Function name: ${extraction.functionName}`);
  lines.push(`Parameters: ${extraction.parameters.length}`);

  if (extraction.parameters.length > 0) {
    extraction.parameters.forEach(p => {
      lines.push(`  - ${p.name} (${p.reason})`);
    });
  }

  if (extraction.returnValue) {
    lines.push(`Return value: ${extraction.returnValue}`);
  } else {
    lines.push('Return value: none');
  }

  const { breaks, earlyReturns, continues } = extraction.controlFlow;
  if (breaks > 0 || earlyReturns > 0 || continues > 0) {
    lines.push('\nControl flow transformations:');
    if (breaks > 0) {
      lines.push(`  - ${breaks} break statement(s) → return`);
    }
    if (earlyReturns > 0) {
      lines.push(`  - ${earlyReturns} early return statement(s) (kept as-is)`);
    }
    if (continues > 0) {
      lines.push(`  - ${continues} continue statement(s) (kept as-is)`);
    }
  }

  return lines.join('\n');
}

/**
 * Format extraction result as JSON
 *
 * @param {Object} extraction - Extraction result from extractMethod()
 * @returns {Object} JSON-serializable object
 */
export function formatPreviewJSON(extraction) {
  return {
    functionName: extraction.functionName,
    extractedFunction: extraction.extractedFunction,
    replacementCall: extraction.replacementCall,
    parameters: extraction.parameters,
    returnValue: extraction.returnValue,
    controlFlow: extraction.controlFlow
  };
}
