#!/usr/bin/env node
/**
 * Codebase Indexer for Claude
 * 
 * Generates a JSON index of symbols (functions, classes, exports) with their locations.
 * Claude can read this index to jump directly to definitions instead of searching.
 * 
 * Usage: node codebase-indexer.js <directory> [output.json]
 */

const fs = require('fs');
const path = require('path');
const acorn = require('acorn');

class CodebaseIndexer {
  constructor() {
    this.index = {
      generated: new Date().toISOString(),
      symbols: {},      // name -> [{ file, line, type, signature }]
      files: {},        // file -> { exports, imports, symbols }
      exports: {},      // exported name -> { file, localName }
    };
    this.errors = [];
  }

  /**
   * Index a directory recursively
   */
  indexDirectory(dir, baseDir = dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      // Skip node_modules, hidden files, etc.
      if (entry.name.startsWith('.') || 
          entry.name === 'node_modules' ||
          entry.name === 'dist' ||
          entry.name === 'build') {
        continue;
      }
      
      if (entry.isDirectory()) {
        this.indexDirectory(fullPath, baseDir);
      } else if (entry.isFile() && /\.(js|ts|mjs|cjs)$/.test(entry.name)) {
        // Skip .d.ts declaration files
        if (entry.name.endsWith('.d.ts')) continue;
        
        const relativePath = path.relative(baseDir, fullPath);
        this.indexFile(fullPath, relativePath);
      }
    }
  }

  /**
   * Index a single file
   */
  indexFile(filePath, relativePath) {
    let code;
    try {
      code = fs.readFileSync(filePath, 'utf-8');
    } catch (err) {
      this.errors.push({ file: relativePath, error: `Read error: ${err.message}` });
      return;
    }

    // Strip TypeScript-specific syntax for parsing
    const strippedCode = this.stripTypeScript(code);

    let ast;
    try {
      ast = acorn.parse(strippedCode, {
        ecmaVersion: 2022,
        sourceType: 'module',
        locations: true,
        allowHashBang: true,
        // Be lenient with parsing
        allowReserved: true,
      });
    } catch (err) {
      // Try as script instead of module
      try {
        ast = acorn.parse(strippedCode, {
          ecmaVersion: 2022,
          sourceType: 'script',
          locations: true,
          allowHashBang: true,
          allowReserved: true,
        });
      } catch (err2) {
        this.errors.push({ file: relativePath, error: `Parse error: ${err2.message}` });
        return;
      }
    }

    const fileInfo = {
      exports: [],
      imports: [],
      symbols: []
    };

    this.walkAST(ast, relativePath, fileInfo, code);
    this.index.files[relativePath] = fileInfo;
  }

  /**
   * Strip TypeScript syntax so Acorn can parse it
   */
  stripTypeScript(code) {
    // Remove type annotations (simplified - handles most cases)
    return code
      // Remove interface/type declarations
      .replace(/^(export\s+)?(interface|type)\s+\w+[\s\S]*?(?=\n(export|import|const|let|var|function|class|\/\*|\/\/|$))/gm, '')
      // Remove : Type annotations
      .replace(/:\s*[\w<>\[\]|&\s,]+(?=\s*[=;,)\]}])/g, '')
      // Remove <Type> generics
      .replace(/<[\w<>\[\]|&\s,]+>/g, '')
      // Remove 'as Type' assertions
      .replace(/\s+as\s+[\w<>\[\]|&]+/g, '')
      // Remove 'implements', 'extends' type parts
      .replace(/implements\s+[\w<>\[\]|&\s,]+/g, '')
      // Remove access modifiers
      .replace(/\b(public|private|protected|readonly)\s+/g, '')
      // Remove abstract keyword
      .replace(/\babstract\s+/g, '');
  }

  /**
   * Walk AST and extract symbols
   */
  walkAST(node, file, fileInfo, code) {
    if (!node || typeof node !== 'object') return;

    switch (node.type) {
      case 'FunctionDeclaration':
        if (node.id) {
          this.addSymbol(node.id.name, {
            file,
            line: node.loc.start.line,
            endLine: node.loc.end.line,
            type: 'function',
            signature: this.extractSignature(node, code),
            async: node.async || false,
            generator: node.generator || false
          });
          fileInfo.symbols.push(node.id.name);
        }
        break;

      case 'ClassDeclaration':
        if (node.id) {
          const classInfo = {
            file,
            line: node.loc.start.line,
            endLine: node.loc.end.line,
            type: 'class',
            methods: [],
            properties: []
          };
          
          // Extract methods and properties
          if (node.body && node.body.body) {
            for (const member of node.body.body) {
              if (member.type === 'MethodDefinition' && member.key) {
                const methodName = member.key.name || member.key.value;
                classInfo.methods.push({
                  name: methodName,
                  line: member.loc.start.line,
                  kind: member.kind, // 'constructor', 'method', 'get', 'set'
                  static: member.static
                });
                
                // Also index as ClassName.methodName
                this.addSymbol(`${node.id.name}.${methodName}`, {
                  file,
                  line: member.loc.start.line,
                  type: 'method',
                  className: node.id.name
                });
              } else if (member.type === 'PropertyDefinition' && member.key) {
                const propName = member.key.name || member.key.value;
                classInfo.properties.push({
                  name: propName,
                  line: member.loc.start.line,
                  static: member.static
                });
              }
            }
          }
          
          this.addSymbol(node.id.name, classInfo);
          fileInfo.symbols.push(node.id.name);
        }
        break;

      case 'VariableDeclaration':
        for (const decl of node.declarations) {
          if (decl.id && decl.id.type === 'Identifier') {
            const symbolInfo = {
              file,
              line: node.loc.start.line,
              type: 'variable',
              kind: node.kind // const, let, var
            };
            
            // Check if it's a function expression or arrow function
            if (decl.init) {
              if (decl.init.type === 'FunctionExpression' || 
                  decl.init.type === 'ArrowFunctionExpression') {
                symbolInfo.type = 'function';
                symbolInfo.signature = this.extractSignature(decl.init, code);
              } else if (decl.init.type === 'ClassExpression') {
                symbolInfo.type = 'class';
              }
            }
            
            this.addSymbol(decl.id.name, symbolInfo);
            fileInfo.symbols.push(decl.id.name);
          }
        }
        break;

      case 'ExportNamedDeclaration':
        if (node.declaration) {
          // export function foo() or export class Bar
          this.walkAST(node.declaration, file, fileInfo, code);
          
          // Mark as exported
          if (node.declaration.id) {
            const name = node.declaration.id.name;
            fileInfo.exports.push(name);
            this.index.exports[name] = { file, localName: name };
          } else if (node.declaration.declarations) {
            for (const decl of node.declaration.declarations) {
              if (decl.id && decl.id.name) {
                fileInfo.exports.push(decl.id.name);
                this.index.exports[decl.id.name] = { file, localName: decl.id.name };
              }
            }
          }
        }
        
        if (node.specifiers) {
          // export { foo, bar as baz }
          for (const spec of node.specifiers) {
            const exported = spec.exported.name;
            const local = spec.local.name;
            fileInfo.exports.push(exported);
            this.index.exports[exported] = { file, localName: local };
          }
        }
        break;

      case 'ExportDefaultDeclaration':
        fileInfo.exports.push('default');
        if (node.declaration) {
          if (node.declaration.id) {
            this.index.exports['default'] = { file, localName: node.declaration.id.name };
          }
          this.walkAST(node.declaration, file, fileInfo, code);
        }
        break;

      case 'ImportDeclaration':
        const importInfo = {
          source: node.source.value,
          specifiers: []
        };
        
        for (const spec of node.specifiers) {
          if (spec.type === 'ImportDefaultSpecifier') {
            importInfo.specifiers.push({ type: 'default', local: spec.local.name });
          } else if (spec.type === 'ImportNamespaceSpecifier') {
            importInfo.specifiers.push({ type: 'namespace', local: spec.local.name });
          } else if (spec.type === 'ImportSpecifier') {
            importInfo.specifiers.push({
              type: 'named',
              imported: spec.imported.name,
              local: spec.local.name
            });
          }
        }
        
        fileInfo.imports.push(importInfo);
        break;

      case 'AssignmentExpression':
        // Handle module.exports = ... and exports.foo = ...
        if (node.left && node.left.type === 'MemberExpression') {
          const obj = node.left.object;
          const prop = node.left.property;
          
          if (obj.name === 'module' && prop.name === 'exports') {
            // module.exports = something
            if (node.right.type === 'Identifier') {
              this.index.exports['default'] = { file, localName: node.right.name };
            } else if (node.right.type === 'ObjectExpression') {
              // module.exports = { foo, bar }
              for (const p of node.right.properties) {
                if (p.key) {
                  const name = p.key.name || p.key.value;
                  fileInfo.exports.push(name);
                  this.index.exports[name] = { file, localName: name };
                }
              }
            }
          } else if (obj.name === 'exports' && prop.name) {
            // exports.foo = ...
            fileInfo.exports.push(prop.name);
            this.index.exports[prop.name] = { file, localName: prop.name };
          }
        }
        break;
    }

    // Recurse into child nodes
    for (const key of Object.keys(node)) {
      if (key === 'loc' || key === 'range') continue;
      
      const child = node[key];
      if (Array.isArray(child)) {
        for (const item of child) {
          this.walkAST(item, file, fileInfo, code);
        }
      } else if (child && typeof child === 'object' && child.type) {
        this.walkAST(child, file, fileInfo, code);
      }
    }
  }

  /**
   * Extract function signature from source
   */
  extractSignature(node, code) {
    if (!node.loc) return null;
    
    const lines = code.split('\n');
    const startLine = lines[node.loc.start.line - 1];
    
    // Extract just the function signature (first line or up to {)
    const match = startLine.match(/^.*?\([^)]*\)/);
    if (match) {
      return match[0].trim();
    }
    
    return null;
  }

  /**
   * Add a symbol to the index
   */
  addSymbol(name, info) {
    if (!this.index.symbols[name]) {
      this.index.symbols[name] = [];
    }
    this.index.symbols[name].push(info);
  }

  /**
   * Generate the final index
   */
  generate() {
    // Add summary statistics
    this.index.stats = {
      totalFiles: Object.keys(this.index.files).length,
      totalSymbols: Object.keys(this.index.symbols).length,
      totalExports: Object.keys(this.index.exports).length,
      errors: this.errors.length
    };
    
    if (this.errors.length > 0) {
      this.index.errors = this.errors;
    }
    
    return this.index;
  }

  /**
   * Save index to file
   */
  save(outputPath) {
    const index = this.generate();
    fs.writeFileSync(outputPath, JSON.stringify(index, null, 2));
    return index;
  }
}

/**
 * Query helper - find symbol locations
 */
function findSymbol(index, name) {
  // Direct match
  if (index.symbols[name]) {
    return index.symbols[name];
  }
  
  // Case-insensitive search
  const lowerName = name.toLowerCase();
  const matches = [];
  
  for (const [symbolName, locations] of Object.entries(index.symbols)) {
    if (symbolName.toLowerCase().includes(lowerName)) {
      matches.push({ name: symbolName, locations });
    }
  }
  
  return matches;
}

/**
 * Query helper - find where a symbol is exported from
 */
function findExport(index, name) {
  return index.exports[name] || null;
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.log('Usage: node codebase-indexer.js <directory> [output.json]');
    console.log('');
    console.log('Generates a symbol index for Claude to use when navigating code.');
    process.exit(1);
  }
  
  const directory = args[0];
  const output = args[1] || 'codebase-index.json';
  
  if (!fs.existsSync(directory)) {
    console.error(`Error: Directory '${directory}' does not exist`);
    process.exit(1);
  }
  
  console.log(`Indexing ${directory}...`);
  
  const indexer = new CodebaseIndexer();
  indexer.indexDirectory(directory);
  const index = indexer.save(output);
  
  console.log(`\nIndex saved to ${output}`);
  console.log(`  Files indexed: ${index.stats.totalFiles}`);
  console.log(`  Symbols found: ${index.stats.totalSymbols}`);
  console.log(`  Exports found: ${index.stats.totalExports}`);
  
  if (index.stats.errors > 0) {
    console.log(`  Errors: ${index.stats.errors}`);
  }
}

module.exports = { CodebaseIndexer, findSymbol, findExport };
