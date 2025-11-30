#!/usr/bin/env node
/**
 * Index Query Tool
 * 
 * Quick lookup of symbols from the codebase index.
 * Designed to be fast and token-efficient for Claude to use.
 * 
 * Usage:
 *   node index-query.js <index.json> find <symbol>     - Find symbol definition
 *   node index-query.js <index.json> export <name>     - Find where name is exported
 *   node index-query.js <index.json> file <path>       - Show file summary
 *   node index-query.js <index.json> stats             - Show index statistics
 *   node index-query.js <index.json> methods <class>   - List class methods
 */

const fs = require('fs');

function loadIndex(indexPath) {
  if (!fs.existsSync(indexPath)) {
    console.error(`Index file not found: ${indexPath}`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
}

function findSymbol(index, name) {
  // Exact match first
  if (index.symbols[name]) {
    return { exact: true, results: { [name]: index.symbols[name] } };
  }
  
  // Partial/case-insensitive match
  const lowerName = name.toLowerCase();
  const results = {};
  
  for (const [symbolName, locations] of Object.entries(index.symbols)) {
    if (symbolName.toLowerCase().includes(lowerName)) {
      results[symbolName] = locations;
    }
  }
  
  return { exact: false, results };
}

function formatLocation(loc) {
  let str = `${loc.file}:${loc.line}`;
  if (loc.endLine && loc.endLine !== loc.line) {
    str += `-${loc.endLine}`;
  }
  str += ` [${loc.type}]`;
  if (loc.signature) {
    str += ` ${loc.signature}`;
  }
  if (loc.kind) {
    str += ` (${loc.kind})`;
  }
  return str;
}

function cmdFind(index, name) {
  const { exact, results } = findSymbol(index, name);
  
  if (Object.keys(results).length === 0) {
    console.log(`No symbols found matching "${name}"`);
    return;
  }
  
  if (exact) {
    console.log(`Found "${name}":`);
  } else {
    console.log(`Partial matches for "${name}":`);
  }
  
  for (const [symbolName, locations] of Object.entries(results)) {
    if (!exact) console.log(`\n  ${symbolName}:`);
    for (const loc of locations) {
      console.log(`    ${formatLocation(loc)}`);
    }
  }
}

function cmdExport(index, name) {
  const exp = index.exports[name];
  
  if (!exp) {
    // Try partial match
    const matches = Object.entries(index.exports)
      .filter(([n]) => n.toLowerCase().includes(name.toLowerCase()));
    
    if (matches.length === 0) {
      console.log(`No export found matching "${name}"`);
      return;
    }
    
    console.log(`Partial matches for "${name}":`);
    for (const [expName, info] of matches) {
      console.log(`  ${expName} -> ${info.file} (local: ${info.localName})`);
    }
    return;
  }
  
  console.log(`Export "${name}":`);
  console.log(`  File: ${exp.file}`);
  console.log(`  Local name: ${exp.localName}`);
  
  // Also show the symbol definition if available
  if (index.symbols[exp.localName]) {
    console.log(`  Definition:`);
    for (const loc of index.symbols[exp.localName]) {
      if (loc.file === exp.file) {
        console.log(`    ${formatLocation(loc)}`);
      }
    }
  }
}

function cmdFile(index, filePath) {
  // Normalize path for matching
  const normalizedPath = filePath.replace(/\\/g, '/');
  
  // Find matching file (exact or partial)
  let fileInfo = index.files[normalizedPath];
  let matchedPath = normalizedPath;
  
  if (!fileInfo) {
    // Try partial match
    const matches = Object.entries(index.files)
      .filter(([p]) => p.includes(normalizedPath) || normalizedPath.includes(p));
    
    if (matches.length === 0) {
      console.log(`No file found matching "${filePath}"`);
      return;
    }
    
    if (matches.length > 1) {
      console.log(`Multiple matches for "${filePath}":`);
      for (const [p] of matches) {
        console.log(`  ${p}`);
      }
      return;
    }
    
    [matchedPath, fileInfo] = matches[0];
  }
  
  console.log(`File: ${matchedPath}`);
  
  if (fileInfo.exports.length > 0) {
    console.log(`\nExports (${fileInfo.exports.length}):`);
    for (const exp of fileInfo.exports) {
      console.log(`  ${exp}`);
    }
  }
  
  if (fileInfo.imports.length > 0) {
    console.log(`\nImports (${fileInfo.imports.length}):`);
    for (const imp of fileInfo.imports) {
      const specs = imp.specifiers.map(s => 
        s.type === 'default' ? s.local :
        s.type === 'namespace' ? `* as ${s.local}` :
        s.imported === s.local ? s.local : `${s.imported} as ${s.local}`
      ).join(', ');
      console.log(`  ${imp.source}: { ${specs} }`);
    }
  }
  
  if (fileInfo.symbols.length > 0) {
    console.log(`\nSymbols (${fileInfo.symbols.length}):`);
    for (const sym of fileInfo.symbols) {
      const symInfo = index.symbols[sym];
      if (symInfo) {
        for (const loc of symInfo) {
          if (loc.file === matchedPath) {
            console.log(`  L${loc.line}: ${sym} [${loc.type}]`);
          }
        }
      }
    }
  }
}

function cmdStats(index) {
  console.log('Index Statistics:');
  console.log(`  Generated: ${index.generated}`);
  console.log(`  Files: ${index.stats.totalFiles}`);
  console.log(`  Symbols: ${index.stats.totalSymbols}`);
  console.log(`  Exports: ${index.stats.totalExports}`);
  
  if (index.stats.errors > 0) {
    console.log(`  Errors: ${index.stats.errors}`);
  }
  
  // Type breakdown
  const typeCount = {};
  for (const locations of Object.values(index.symbols)) {
    for (const loc of locations) {
      typeCount[loc.type] = (typeCount[loc.type] || 0) + 1;
    }
  }
  
  console.log('\nSymbol types:');
  for (const [type, count] of Object.entries(typeCount).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${type}: ${count}`);
  }
}

function cmdMethods(index, className) {
  const classInfo = index.symbols[className];
  
  if (!classInfo) {
    // Try partial match
    const matches = Object.entries(index.symbols)
      .filter(([name, locs]) => 
        name.toLowerCase().includes(className.toLowerCase()) &&
        locs.some(l => l.type === 'class')
      );
    
    if (matches.length === 0) {
      console.log(`No class found matching "${className}"`);
      return;
    }
    
    console.log(`Partial matches for "${className}":`);
    for (const [name] of matches) {
      console.log(`  ${name}`);
    }
    return;
  }
  
  for (const loc of classInfo) {
    if (loc.type === 'class') {
      console.log(`Class: ${className}`);
      console.log(`  File: ${loc.file}:${loc.line}`);
      
      if (loc.methods && loc.methods.length > 0) {
        console.log(`\nMethods (${loc.methods.length}):`);
        for (const method of loc.methods) {
          const prefix = method.static ? 'static ' : '';
          const kind = method.kind === 'constructor' ? '[constructor]' :
                       method.kind === 'get' ? '[getter]' :
                       method.kind === 'set' ? '[setter]' : '';
          console.log(`  L${method.line}: ${prefix}${method.name} ${kind}`);
        }
      }
      
      if (loc.properties && loc.properties.length > 0) {
        console.log(`\nProperties (${loc.properties.length}):`);
        for (const prop of loc.properties) {
          const prefix = prop.static ? 'static ' : '';
          console.log(`  L${prop.line}: ${prefix}${prop.name}`);
        }
      }
    }
  }
}

// Main
const args = process.argv.slice(2);

if (args.length < 2) {
  console.log('Usage:');
  console.log('  node index-query.js <index.json> find <symbol>');
  console.log('  node index-query.js <index.json> export <name>');
  console.log('  node index-query.js <index.json> file <path>');
  console.log('  node index-query.js <index.json> stats');
  console.log('  node index-query.js <index.json> methods <class>');
  process.exit(1);
}

const indexPath = args[0];
const command = args[1];
const arg = args[2];

const index = loadIndex(indexPath);

switch (command) {
  case 'find':
    if (!arg) {
      console.error('Usage: find <symbol>');
      process.exit(1);
    }
    cmdFind(index, arg);
    break;
    
  case 'export':
    if (!arg) {
      console.error('Usage: export <name>');
      process.exit(1);
    }
    cmdExport(index, arg);
    break;
    
  case 'file':
    if (!arg) {
      console.error('Usage: file <path>');
      process.exit(1);
    }
    cmdFile(index, arg);
    break;
    
  case 'stats':
    cmdStats(index);
    break;
    
  case 'methods':
    if (!arg) {
      console.error('Usage: methods <class>');
      process.exit(1);
    }
    cmdMethods(index, arg);
    break;
    
  default:
    console.error(`Unknown command: ${command}`);
    process.exit(1);
}
