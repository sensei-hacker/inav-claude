/**
 * analyzer.js - Code Block Analysis for Extract Method Refactoring
 *
 * This module analyzes JavaScript code blocks to determine if they can be
 * safely extracted into separate functions. It examines the AST structure,
 * identifies statements, and checks for basic feasibility.
 *
 * WHAT IT DOES (Phase 1):
 *   - Parses JavaScript files to AST
 *   - Identifies statements within specified line ranges
 *   - Determines containing scope (parent node)
 *   - Checks basic extraction feasibility
 *   - Formats output for human reading or JSON
 *
 * WHAT IT WILL DO (Phase 2+):
 *   - Detect which variables need to be passed as parameters
 *   - Detect which variables need to be returned
 *   - Analyze control flow (break, return, continue)
 *   - Calculate code complexity
 *
 * MAIN FUNCTIONS:
 *   analyzeExtraction(filePath, startLine, endLine)
 *     Analyzes a code block and returns feasibility report
 *
 *   formatAnalysis(analysis)
 *     Formats analysis as human-readable text
 *
 *   formatAnalysisJSON(analysis)
 *     Formats analysis as JSON
 *
 * USAGE:
 *   import { analyzeExtraction } from './analyzer.js';
 *   const result = analyzeExtraction('file.js', 10, 20);
 *   console.log(result.feasible); // true or false
 *
 * @module analyzer
 * @version 0.2.0
 * @status Phase 2 - In Progress
 */

import { parseFile } from './utils/parser.js';
import {
  getStatementsInLineRange,
  getLineRangeInfo,
  findContainingParent,
  walk
} from './utils/line-mapper.js';
import {
  findUsedVariables,
  findDefinedVariables,
  findModifiedVariables,
  cleanUsedVariables
} from './utils/scope-analyzer.js';

/**
 * Analyze a code block for extraction
 * @param {string} filePath - Path to JavaScript file
 * @param {number} startLine - Start line number (1-based)
 * @param {number} endLine - End line number (1-based)
 * @returns {object} Analysis results
 */
export function analyzeExtraction(filePath, startLine, endLine) {
  // Parse the file
  const ast = parseFile(filePath);

  // Get basic info about the line range
  const lineInfo = getLineRangeInfo(ast, startLine, endLine);

  // Get statements in the range
  const statements = getStatementsInLineRange(ast, startLine, endLine);

  // Find the containing parent
  const parent = findContainingParent(ast, startLine, endLine);

  // Basic feasibility checks
  const issues = [];

  if (statements.length === 0) {
    issues.push({
      type: 'error',
      message: 'No statements found in the specified line range'
    });
  }

  if (!parent) {
    issues.push({
      type: 'warning',
      message: 'Could not determine containing scope'
    });
  }

  // Determine initial feasibility
  let feasible = issues.filter(i => i.type === 'error').length === 0;

  // Phase 2: Variable scope analysis
  let parameters = [];
  let returnValue = null;
  let controlFlow = { earlyReturns: 0, breaks: 0, continues: 0 };

  if (feasible && statements.length > 0) {
    // Get statements before and after the block for context
    const beforeStatements = getStatementsInLineRange(ast, 1, startLine - 1);
    const afterStatements = getStatementsInLineRange(ast, endLine + 1, 9999);

    // Analyze variables in the block
    const usedInBlock = findUsedVariables(statements);
    const definedInBlock = findDefinedVariables(statements);
    const modifiedInBlock = findModifiedVariables(statements);

    // Analyze variables available before the block
    const definedBefore = findDefinedVariables(beforeStatements);

    // Analyze variables used after the block
    const usedAfter = findUsedVariables(afterStatements);

    // Detect parameters: variables used but not defined in block, and available before
    const freeVars = cleanUsedVariables(usedInBlock, definedInBlock);
    parameters = [...freeVars]
      .filter(v => definedBefore.has(v))
      .map(name => ({ name, reason: 'used-not-defined' }));

    // Detect return value: variables modified in block and used after
    const returnCandidates = [...modifiedInBlock].filter(v => usedAfter.has(v));
    if (returnCandidates.length === 1) {
      returnValue = returnCandidates[0]; // Simple string for single return value
    } else if (returnCandidates.length > 1) {
      returnValue = `{ ${returnCandidates.join(', ')} }`; // Object destructuring for multiple
    }

    // Analyze control flow
    controlFlow = analyzeControlFlow(statements);

    // Check for issues
    if (parameters.length > 5) {
      issues.push({
        type: 'warning',
        message: `Too many parameters required (${parameters.length}). Consider extracting a smaller block.`
      });
    }

    if (returnValue && returnCandidates.length > 1) {
      issues.push({
        type: 'warning',
        message: `Multiple return values needed (${returnCandidates.length}). Will return an object.`
      });
    }
  }

  // Re-determine feasibility after Phase 2 analysis
  feasible = issues.filter(i => i.type === 'error').length === 0;

  return {
    feasible,
    filePath,
    startLine,
    endLine,
    lineCount: lineInfo.lineCount,
    statementCount: statements.length,
    parentType: lineInfo.parentType,
    issues,
    metrics: {
      parameters,
      returnValue,
      controlFlow,
      complexity: 0 // TODO: Calculate cyclomatic complexity
    },
    suggestion: {
      recommended: feasible && issues.filter(i => i.type === 'warning').length === 0,
      reason: feasible ? (issues.length > 0 ? 'Feasible with warnings' : 'Block appears extractable') : 'Issues detected'
    },
    // Phase 3: Include source information for extractor
    _sourceInfo: {
      ast,
      filePath
    },
    _extractedNodes: {
      statements,
      parent
    }
  };
}

/**
 * Analyze control flow statements in a block
 * @param {Array} statements - AST statement nodes
 * @returns {object} Control flow metrics
 */
function analyzeControlFlow(statements) {
  let earlyReturns = 0;
  let breaks = 0;
  let continues = 0;

  statements.forEach(stmt => {
    walk(stmt, (node) => {
      if (node.type === 'ReturnStatement') {
        earlyReturns++;
      }
      if (node.type === 'BreakStatement') {
        breaks++;
      }
      if (node.type === 'ContinueStatement') {
        continues++;
      }
    });
  });

  return { earlyReturns, breaks, continues };
}

/**
 * Format analysis results for human-readable output
 * @param {object} analysis - Analysis results
 * @returns {string} Formatted output
 */
export function formatAnalysis(analysis) {
  const lines = [];

  lines.push(`Analysis of ${analysis.filePath} lines ${analysis.startLine}-${analysis.endLine}:`);
  lines.push('');

  if (analysis.feasible) {
    lines.push('✓ Extraction is FEASIBLE');
  } else {
    lines.push('❌ Extraction is NOT FEASIBLE');
  }

  lines.push('');
  lines.push('Metrics:');
  lines.push(`  Lines of code: ${analysis.lineCount}`);
  lines.push(`  Statements: ${analysis.statementCount}`);
  lines.push(`  Parent scope: ${analysis.parentType || 'unknown'}`);

  // Phase 2: Display parameters
  if (analysis.metrics.parameters.length === 0) {
    lines.push(`  Parameters needed: 0`);
  } else {
    lines.push(`  Parameters needed: ${analysis.metrics.parameters.length}`);
    analysis.metrics.parameters.forEach(param => {
      lines.push(`    - ${param.name} (${param.reason})`);
    });
  }

  // Phase 2: Display return value
  if (analysis.metrics.returnValue) {
    lines.push(`  Return value: ${analysis.metrics.returnValue}`);
  } else {
    lines.push(`  Return value: none`);
  }

  // Phase 2: Display control flow
  const cf = analysis.metrics.controlFlow;
  if (cf.earlyReturns > 0 || cf.breaks > 0 || cf.continues > 0) {
    lines.push(`  Control flow:`);
    if (cf.earlyReturns > 0) lines.push(`    - ${cf.earlyReturns} return statement(s)`);
    if (cf.breaks > 0) lines.push(`    - ${cf.breaks} break statement(s)`);
    if (cf.continues > 0) lines.push(`    - ${cf.continues} continue statement(s)`);
  }

  if (analysis.issues.length > 0) {
    lines.push('');
    lines.push('Issues:');
    analysis.issues.forEach(issue => {
      const icon = issue.type === 'error' ? '❌' : '⚠️';
      lines.push(`  ${icon} ${issue.message}`);
    });
  }

  lines.push('');
  if (analysis.suggestion.recommended) {
    lines.push('Recommendation: ✓ ' + analysis.suggestion.reason);
  } else {
    lines.push('Recommendation: ❌ ' + analysis.suggestion.reason);
  }

  return lines.join('\n');
}

/**
 * Format analysis results as JSON
 * @param {object} analysis - Analysis results
 * @returns {string} JSON output
 */
export function formatAnalysisJSON(analysis) {
  return JSON.stringify(analysis, null, 2);
}
