/**
 * extractor.test.js - Extractor Module Tests
 *
 * Tests for code extraction functionality including:
 * - Function generation with parameters
 * - Return statement generation
 * - Control flow transformations (break → return)
 * - Replacement call generation
 * - Edge cases and error handling
 */

import { describe, it, expect } from 'vitest';
import { extractMethod, generateExtractedFunction, generateReplacementCall, formatPreview, formatPreviewJSON } from '../src/extractor.js';
import { analyzeExtraction } from '../src/analyzer.js';

describe('Extractor - extractMethod()', () => {
  it('should extract a simple block with no parameters or return value', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);
    const result = extractMethod(analysis, 'doWork');

    expect(result.functionName).toBe('doWork');
    expect(result.extractedFunction).toContain('function doWork()');
    expect(result.extractedFunction).toContain('console.log');
    expect(result.replacementCall).toContain('doWork()');
    expect(result.parameters).toEqual([]);
    expect(result.returnValue).toBeNull();
  });

  it('should extract a block with parameters', () => {
    const analysis = analyzeExtraction('test/fixtures/parameters-needed.js', 16, 18);
    const result = extractMethod(analysis, 'validateAndProcess');

    expect(result.functionName).toBe('validateAndProcess');
    expect(result.extractedFunction).toContain('function validateAndProcess(userData, config)');
    expect(result.replacementCall).toContain('validateAndProcess(userData, config)');
    expect(result.parameters).toHaveLength(2);
    expect(result.parameters[0].name).toBe('userData');
    expect(result.parameters[1].name).toBe('config');
  });

  it('should extract a block with a return value', () => {
    const analysis = analyzeExtraction('test/fixtures/return-value.js', 15, 16);
    const result = extractMethod(analysis, 'performSave');

    expect(result.functionName).toBe('performSave');
    expect(result.extractedFunction).toContain('return saveResult');
    expect(result.replacementCall).toContain('saveResult = performSave(data)');
    expect(result.returnValue).toBe('saveResult');
  });

  it('should transform break to return in switch case', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-switch.js', 14, 17);
    const result = extractMethod(analysis, 'handleSave');

    expect(result.functionName).toBe('handleSave');
    expect(result.extractedFunction).toContain('return');
    expect(result.extractedFunction).not.toContain('break');
    expect(result.controlFlow.breaks).toBe(1);
  });

  it('should throw error if extraction is not feasible', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 100, 200);

    expect(() => extractMethod(analysis, 'testFunc')).toThrow('not feasible');
  });

  it('should throw error if function name is missing', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);

    expect(() => extractMethod(analysis, '')).toThrow('Function name is required');
  });

  it('should throw error if function name is invalid', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);

    expect(() => extractMethod(analysis, '123invalid')).toThrow('Invalid function name');
    expect(() => extractMethod(analysis, 'has-dashes')).toThrow('Invalid function name');
  });

  it('should accept valid function names', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);

    expect(() => extractMethod(analysis, 'validName')).not.toThrow();
    expect(() => extractMethod(analysis, 'valid_name')).not.toThrow();
    expect(() => extractMethod(analysis, '$validName')).not.toThrow();
    expect(() => extractMethod(analysis, '_validName')).not.toThrow();
  });
});

describe('Extractor - generateExtractedFunction()', () => {
  it('should generate function with correct parameters', () => {
    const analysis = analyzeExtraction('test/fixtures/parameters-needed.js', 16, 18);
    const code = generateExtractedFunction(analysis, 'testFunc');

    expect(code).toContain('function testFunc(userData, config)');
  });

  it('should generate function with no parameters', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);
    const code = generateExtractedFunction(analysis, 'testFunc');

    expect(code).toContain('function testFunc()');
  });

  it('should include return statement if returnValue is present', () => {
    const analysis = analyzeExtraction('test/fixtures/return-value.js', 15, 16);
    const code = generateExtractedFunction(analysis, 'testFunc');

    expect(code).toContain('return saveResult');
  });

  it('should not include return statement if returnValue is null', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);
    const code = generateExtractedFunction(analysis, 'testFunc');

    expect(code).not.toContain('return');
  });

  it('should transform break statements to return', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-switch.js', 14, 17);
    const code = generateExtractedFunction(analysis, 'testFunc');

    expect(code).toContain('return');
    expect(code).not.toContain('break');
  });
});

describe('Extractor - generateReplacementCall()', () => {
  it('should generate simple call with no parameters', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);
    const code = generateReplacementCall(analysis, 'testFunc');

    expect(code).toBe('testFunc();');
  });

  it('should generate call with parameters', () => {
    const analysis = analyzeExtraction('test/fixtures/parameters-needed.js', 16, 18);
    const code = generateReplacementCall(analysis, 'testFunc');

    expect(code).toContain('testFunc(userData, config)');
  });

  it('should generate call with assignment if return value exists', () => {
    const analysis = analyzeExtraction('test/fixtures/return-value.js', 15, 16);
    const code = generateReplacementCall(analysis, 'testFunc');

    expect(code).toContain('saveResult = testFunc(data)');
  });

  it('should generate call without assignment if no return value', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);
    const code = generateReplacementCall(analysis, 'testFunc');

    expect(code).toBe('testFunc();');
    expect(code).not.toContain('=');
  });
});

describe('Extractor - formatPreview()', () => {
  it('should format preview with all sections', () => {
    const analysis = analyzeExtraction('test/fixtures/parameters-needed.js', 16, 18);
    const extraction = extractMethod(analysis, 'testFunc');
    const preview = formatPreview(extraction, analysis);

    expect(preview).toContain('=== EXTRACTED FUNCTION ===');
    expect(preview).toContain('=== REPLACEMENT CODE ===');
    expect(preview).toContain('=== SUMMARY ===');
    expect(preview).toContain('Function name: testFunc');
  });

  it('should show parameter count and names', () => {
    const analysis = analyzeExtraction('test/fixtures/parameters-needed.js', 16, 18);
    const extraction = extractMethod(analysis, 'testFunc');
    const preview = formatPreview(extraction, analysis);

    expect(preview).toContain('Parameters: 2');
    expect(preview).toContain('userData');
    expect(preview).toContain('config');
  });

  it('should show return value if present', () => {
    const analysis = analyzeExtraction('test/fixtures/return-value.js', 15, 16);
    const extraction = extractMethod(analysis, 'testFunc');
    const preview = formatPreview(extraction, analysis);

    expect(preview).toContain('Return value: saveResult');
  });

  it('should show "none" if no return value', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);
    const extraction = extractMethod(analysis, 'testFunc');
    const preview = formatPreview(extraction, analysis);

    expect(preview).toContain('Return value: none');
  });

  it('should show control flow transformations', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-switch.js', 14, 17);
    const extraction = extractMethod(analysis, 'testFunc');
    const preview = formatPreview(extraction, analysis);

    expect(preview).toContain('Control flow transformations:');
    expect(preview).toContain('break statement(s) → return');
  });
});

describe('Extractor - formatPreviewJSON()', () => {
  it('should return JSON-serializable object', () => {
    const analysis = analyzeExtraction('test/fixtures/parameters-needed.js', 16, 18);
    const extraction = extractMethod(analysis, 'testFunc');
    const json = formatPreviewJSON(extraction);

    expect(json).toHaveProperty('functionName');
    expect(json).toHaveProperty('extractedFunction');
    expect(json).toHaveProperty('replacementCall');
    expect(json).toHaveProperty('parameters');
    expect(json).toHaveProperty('returnValue');
    expect(json).toHaveProperty('controlFlow');
  });

  it('should include all extraction details', () => {
    const analysis = analyzeExtraction('test/fixtures/return-value.js', 15, 16);
    const extraction = extractMethod(analysis, 'testFunc');
    const json = formatPreviewJSON(extraction);

    expect(json.functionName).toBe('testFunc');
    expect(json.parameters).toHaveLength(1);
    expect(json.returnValue).toBe('saveResult');
    expect(json.extractedFunction).toContain('function testFunc');
  });
});

describe('Extractor - Edge Cases', () => {
  it('should handle blocks with no statements gracefully', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 100, 200);

    expect(() => extractMethod(analysis, 'testFunc')).toThrow();
  });

  it('should handle function names with underscores and dollar signs', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);

    const result1 = extractMethod(analysis, '_privateFunc');
    expect(result1.functionName).toBe('_privateFunc');

    const result2 = extractMethod(analysis, '$jQueryStyle');
    expect(result2.functionName).toBe('$jQueryStyle');
  });

  it('should preserve statement structure in extracted function', () => {
    const analysis = analyzeExtraction('test/fixtures/simple-block.js', 14, 16);
    const result = extractMethod(analysis, 'testFunc');

    // Extracted function should have all original statements
    expect(result.extractedFunction).toContain('const x = 1');
    expect(result.extractedFunction).toContain('const y = 2');
    expect(result.extractedFunction).toContain('console.log(x + y)');
  });
});
