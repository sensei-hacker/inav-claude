/**
 * analyzer.test.js - Tests for Code Block Analyzer
 *
 * Test suite for the analyzer module (src/analyzer.js).
 * Verifies that code blocks are correctly analyzed for extraction
 * feasibility and output is properly formatted.
 *
 * TEST COVERAGE:
 *   - analyzeExtraction() - Block analysis
 *   - formatAnalysis() - Human-readable output
 *   - formatAnalysisJSON() - JSON output
 *   - Feasibility detection
 *   - Issue detection (no statements, etc.)
 *   - Metrics reporting
 *
 * RUN TESTS:
 *   npm test                      # All tests
 *   npm test -- analyzer.test.js  # This file only
 *
 * @module test/analyzer
 * @requires vitest
 */

import { describe, it, expect } from 'vitest';
import { analyzeExtraction, formatAnalysis, formatAnalysisJSON } from '../src/analyzer.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

describe('Analyzer', () => {
  describe('analyzeExtraction', () => {
    it('should analyze a simple extractable block', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 14, 16);

      expect(analysis.feasible).toBe(true);
      expect(analysis.startLine).toBe(14);
      expect(analysis.endLine).toBe(16);
      expect(analysis.lineCount).toBe(3);
      expect(analysis.statementCount).toBeGreaterThan(0);
      expect(analysis.issues.length).toBe(0);
    });

    it('should detect when no statements are in range', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 1, 2); // Comment lines

      expect(analysis.feasible).toBe(false);
      expect(analysis.statementCount).toBe(0);
      expect(analysis.issues.some(i => i.type === 'error')).toBe(true);
    });

    it('should analyze switch case block', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-switch.js');
      const analysis = analyzeExtraction(filePath, 14, 16);

      expect(analysis.feasible).toBe(true);
      expect(analysis.statementCount).toBeGreaterThan(0);
      expect(analysis.parentType).toBeDefined();
    });

    it('should handle invalid line range gracefully', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 100, 200);

      expect(analysis.feasible).toBe(false);
      expect(analysis.statementCount).toBe(0);
    });

    it('should include metrics placeholder', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 14, 16);

      expect(analysis.metrics).toBeDefined();
      expect(analysis.metrics.parameters).toBeDefined();
      expect(analysis.metrics.returnValue).toBeDefined();
      expect(analysis.metrics.controlFlow).toBeDefined();
    });

    it('should include suggestion', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 14, 16);

      expect(analysis.suggestion).toBeDefined();
      expect(analysis.suggestion.recommended).toBe(true);
      expect(analysis.suggestion.reason).toBeDefined();
    });
  });

  describe('formatAnalysis', () => {
    it('should format analysis as human-readable text', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 14, 16);
      const output = formatAnalysis(analysis);

      expect(output).toContain('Analysis of');
      expect(output).toContain('lines 14-16');
      expect(output).toContain('FEASIBLE');
      expect(output).toContain('Metrics:');
      expect(output).toContain('Recommendation:');
    });

    it('should include issues in output when present', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 100, 200);
      const output = formatAnalysis(analysis);

      expect(output).toContain('NOT FEASIBLE');
      expect(output).toContain('Issues:');
    });

    it('should show success indicator for feasible extraction', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 14, 16);
      const output = formatAnalysis(analysis);

      expect(output).toContain('✓');
    });
  });

  describe('formatAnalysisJSON', () => {
    it('should format analysis as valid JSON', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 14, 16);
      const output = formatAnalysisJSON(analysis);

      expect(() => JSON.parse(output)).not.toThrow();
    });

    it('should include all analysis fields in JSON', () => {
      const filePath = join(__dirname, 'fixtures', 'simple-block.js');
      const analysis = analyzeExtraction(filePath, 14, 16);
      const output = formatAnalysisJSON(analysis);
      const parsed = JSON.parse(output);

      expect(parsed.feasible).toBeDefined();
      expect(parsed.filePath).toBeDefined();
      expect(parsed.startLine).toBeDefined();
      expect(parsed.endLine).toBeDefined();
      expect(parsed.metrics).toBeDefined();
      expect(parsed.suggestion).toBeDefined();
    });
  });
});
