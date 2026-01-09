#!/usr/bin/env node

/**
 * extract-method CLI Tool
 *
 * Command-line interface for the Extract Method refactoring tool.
 * Analyzes JavaScript code blocks and helps extract them into separate functions.
 *
 * USAGE:
 *   extract-method analyze <file> --lines <start>-<end>
 *     Analyze a code block for extraction feasibility
 *
 *   extract-method preview <file> --lines <start>-<end> --name <functionName>
 *     Preview what the extracted function would look like (Phase 3)
 *
 *   extract-method apply <file> --lines <start>-<end> --name <functionName>
 *     Apply the extraction and modify the file (Phase 4)
 *
 * OPTIONS:
 *   --json       Output results as JSON for programmatic use
 *   --verbose    Show detailed AST information
 *   --help       Display help information
 *   --version    Show version number
 *
 * EXAMPLES:
 *   # Analyze a code block
 *   extract-method analyze src/config.js --lines 145-195
 *
 *   # Get JSON output (useful for tools and scripts)
 *   extract-method analyze src/config.js --lines 145-195 --json
 *
 * EXIT CODES:
 *   0  Success
 *   2  File not found or parse error
 *   4  Extraction not feasible
 *
 * @version 0.1.0
 * @status Phase 1 Complete (analyze command only)
 */

import { Command } from 'commander';
import { analyzeExtraction, formatAnalysis, formatAnalysisJSON } from '../src/analyzer.js';
import { extractMethod, formatPreview, formatPreviewJSON } from '../src/extractor.js';
import chalk from 'chalk';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Read package.json for version
const packageJson = JSON.parse(
  readFileSync(join(__dirname, '../package.json'), 'utf-8')
);

const program = new Command();

program
  .name('extract-method')
  .description('Extract Method refactoring tool with AST verification')
  .version(packageJson.version);

/**
 * Parse line range string (e.g., "10-20") into start and end numbers
 */
function parseLineRange(rangeStr) {
  const match = rangeStr.match(/^(\d+)-(\d+)$/);
  if (!match) {
    throw new Error('Invalid line range format. Use: <start>-<end> (e.g., 10-20)');
  }

  const start = parseInt(match[1], 10);
  const end = parseInt(match[2], 10);

  if (start < 1 || end < 1) {
    throw new Error('Line numbers must be positive');
  }

  if (start > end) {
    throw new Error('Start line must be less than or equal to end line');
  }

  return { start, end };
}

// Analyze command
program
  .command('analyze')
  .description('Analyze a code block for extraction feasibility')
  .argument('<file>', 'JavaScript file to analyze')
  .requiredOption('--lines <range>', 'Line range to extract (e.g., 10-20)')
  .option('--json', 'Output results as JSON')
  .option('--verbose', 'Verbose output with AST details')
  .action((file, options) => {
    try {
      // Parse line range
      const { start, end } = parseLineRange(options.lines);

      // Analyze the extraction
      const analysis = analyzeExtraction(file, start, end);

      // Output results
      if (options.json) {
        console.log(formatAnalysisJSON(analysis));
      } else {
        console.log(formatAnalysis(analysis));
      }

      // Exit with appropriate code
      process.exit(analysis.feasible ? 0 : 4);

    } catch (error) {
      console.error(chalk.red('Error:'), error.message);
      if (options.verbose) {
        console.error(error.stack);
      }
      process.exit(2);
    }
  });

// Preview command
program
  .command('preview')
  .description('Preview the extracted function')
  .argument('<file>', 'JavaScript file')
  .requiredOption('--lines <range>', 'Line range to extract')
  .requiredOption('--name <name>', 'Name for extracted function')
  .option('--json', 'Output results as JSON')
  .option('--verbose', 'Verbose output')
  .action((file, options) => {
    try {
      // Parse line range
      const { start, end } = parseLineRange(options.lines);

      // First, analyze the extraction
      const analysis = analyzeExtraction(file, start, end);

      // Check if extraction is feasible
      if (!analysis.feasible) {
        console.error(chalk.red('Error: Extraction is not feasible'));
        console.log('\n' + formatAnalysis(analysis));
        process.exit(4);
      }

      // Generate the extraction
      const extraction = extractMethod(analysis, options.name);

      // Output results
      if (options.json) {
        console.log(JSON.stringify(formatPreviewJSON(extraction), null, 2));
      } else {
        console.log(formatPreview(extraction, analysis));
      }

      process.exit(0);

    } catch (error) {
      console.error(chalk.red('Error:'), error.message);
      if (options.verbose) {
        console.error(error.stack);
      }
      process.exit(2);
    }
  });

// Apply command (placeholder for Phase 4)
program
  .command('apply')
  .description('Apply the extraction (Coming in Phase 4)')
  .argument('<file>', 'JavaScript file')
  .requiredOption('--lines <range>', 'Line range to extract')
  .requiredOption('--name <name>', 'Name for extracted function')
  .option('--location <where>', 'Where to place function (before|after|top)', 'before')
  .action(() => {
    console.log(chalk.yellow('Apply command will be implemented in Phase 4'));
    console.log('For now, use the analyze command to check extraction feasibility');
    process.exit(0);
  });

// Parse arguments
program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
