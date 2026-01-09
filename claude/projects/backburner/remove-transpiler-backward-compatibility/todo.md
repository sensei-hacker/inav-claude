# Todo List: Remove Transpiler Backward Compatibility

## Phase 1: Preparation (February 2026)

- [ ] Review current backward compatibility implementation
  - [ ] Check parser.js for old syntax support
  - [ ] Check codegen.js for old syntax support
  - [ ] Check analyzer.js for old syntax support
  - [ ] Check action_generator.js for old syntax support
  - [ ] Review transpiler-namespace-refactoring.md documentation

- [ ] Create feature branch
  - [ ] Determine appropriate base branch (maintenance-9.x or maintenance-10.x)
  - [ ] Create branch: `transpiler-remove-backward-compat`

## Phase 2: Code Removal

- [ ] Remove backward compatibility from parser.js
  - [ ] Remove old edge() function recognition
  - [ ] Remove old gvar[]/rc[] array recognition
  - [ ] Update parser to require inav.* prefix

- [ ] Remove backward compatibility from codegen.js
  - [ ] Remove old gvar[]/rc[] code generation
  - [ ] Remove old function call generation
  - [ ] Ensure only inav.* syntax is generated

- [ ] Remove backward compatibility from analyzer.js
  - [ ] Remove old syntax validation paths
  - [ ] Update to validate only inav.* syntax

- [ ] Remove backward compatibility from action_generator.js
  - [ ] Remove old action generation paths
  - [ ] Update to generate only for inav.* syntax

## Phase 3: Testing

- [ ] Run all transpiler tests
  - [ ] Verify all existing tests still pass
  - [ ] Check no tests rely on old syntax
  - [ ] Update any tests using old syntax to new syntax

- [ ] Test edge cases
  - [ ] Verify error messages for old syntax are clear
  - [ ] Test that new syntax still works correctly
  - [ ] Verify decompiler output still works

## Phase 4: Documentation & Examples

- [ ] Update examples
  - [ ] Find any examples using old syntax
  - [ ] Update to use new syntax
  - [ ] Verify examples compile and work

- [ ] Update documentation
  - [ ] Remove references to backward compatibility
  - [ ] Update to show new syntax only
  - [ ] Add migration note if needed

## Phase 5: Pull Request

- [ ] Create PR
  - [ ] Write clear PR description
  - [ ] Explain breaking change and migration period
  - [ ] Include test results
  - [ ] Reference original refactoring work

- [ ] Address review feedback
  - [ ] Make any requested changes
  - [ ] Re-run tests after changes

## Completion

- [ ] PR merged
- [ ] Project archived to archived_projects/
- [ ] INDEX.md updated
- [ ] Send completion report to manager
