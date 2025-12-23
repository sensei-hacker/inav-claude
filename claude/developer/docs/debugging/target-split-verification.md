# Target Directory Split Verification

When splitting multi-target directories (e.g., OMNIBUSF4 with 9 variants), use multiple verification tools.

## Key Insight: Preprocessor vs Source Analysis

Preprocessor testing validates **what goes into builds**, not **what's in source files**.

```c
#if defined(TARGET_A)
  // This appears in output
#else
  // DEAD CODE - preprocessor ignores, but still in source!
#endif
```

## Multi-Tool Verification Strategy

No single tool catches everything:

| Tool | Catches | Misses |
|------|---------|--------|
| unifdef | Simple conditionals | Complex boolean expressions |
| gcc -E | Functional correctness | Dead code in source |
| Pattern matching | Known violations | Complex logic errors |
| Cross-validation | Edge cases | Nothing (slowest) |

**Use defense-in-depth:** multiple independent verification methods.

## Verification Scripts

Location: `claude/developer/scripts/analysis/`

```bash
# Comprehensive multi-tool verification
python3 comprehensive_verification.py

# Pattern matching for target conditionals
python3 verify_target_conditionals.py

# Functional verification (gcc -E comparison)
python3 split_omnibus_targets.py

# Dead code detection
python3 detect_dead_code_gcc_dD.py
```

## Automation Boundaries

**Safe to automate:**
- Detection/reporting of issues
- Preprocessor comparison
- Pattern matching

**Risky to automate:**
- Removing dead code (nesting complexity)
- Simplifying boolean expressions

## Workflow

```bash
# 1. Before split - capture baseline
for target in TARGET1 TARGET2; do
    gcc -E -D$target orig/target.h > /tmp/before_${target}.i
done

# 2. Perform split with unifdef
./split_with_unifdef.sh

# 3. Run comprehensive verification
python3 comprehensive_verification.py

# 4. Fix reported issues manually

# 5. Run functional verification
python3 split_omnibus_targets.py

# 6. Build all targets
make TARGET1 TARGET2 ...
```

## Related

- GCC preprocessing: `gcc-preprocessing-techniques.md`
- Full investigation: `../investigations/target-split/` (gitignored)
