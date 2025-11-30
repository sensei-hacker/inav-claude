# Project: Investigate Automated Testing with MCP Servers

**Type:** Research / Infrastructure
**Status:** Backburner
**Target Version:** TBD
**Pull Request:** N/A
**Priority:** Low

## Overview

Research and evaluate Model Context Protocol (MCP) servers for automated testing of the INAV Configurator Electron application. Specifically investigate tools that could enable Claude Code to interact with and test the Electron GUI programmatically.

## Motivation

Currently, testing the INAV Configurator requires manual interaction or traditional test frameworks. MCP servers could potentially enable:

- **Automated GUI testing** through Claude Code
- **Interactive debugging** of Electron applications
- **Screenshot-based verification** of UI states
- **Automated regression testing** for configurator changes
- **Integration testing** of transpiler features in the actual UI

This would be especially valuable for:
- Testing the transpiler JavaScript programming UI
- Verifying settings tabs work correctly
- Automated testing of firmware flashing workflows
- Regression testing across configurator versions

## Candidate MCP Servers

### 1. Electron MCP Server
**URL:** https://mcpmarket.com/server/electron-1

**Potential Capabilities:**
- Direct Electron application control
- Window management
- DevTools integration
- IPC communication testing

**Status:** Need to investigate

### 2. Circuit MCP
**URL:** https://github.com/snowfort-ai/circuit-mcp

**Potential Capabilities:**
- Test automation framework
- UI interaction capabilities
- Verification and assertion tools

**Status:** Need to investigate

## Technical Approach

### Phase 1: Research & Evaluation

1. **Understand MCP architecture**
   - How MCP servers work
   - Integration with Claude Code
   - Security considerations

2. **Evaluate Electron MCP Server**
   - Installation and setup
   - Capabilities and limitations
   - Compatibility with INAV Configurator
   - Documentation quality

3. **Evaluate Circuit MCP**
   - Installation and setup
   - Testing framework capabilities
   - Integration approach
   - Documentation quality

4. **Compare alternatives**
   - Traditional test frameworks (Playwright, Puppeteer)
   - Benefits/drawbacks of MCP approach
   - Cost/complexity tradeoffs

### Phase 2: Proof of Concept (if promising)

1. Set up simple test case
2. Automate basic configurator interaction
3. Verify screenshot/state capture
4. Test transpiler UI interaction

### Phase 3: Production Implementation (if successful)

1. Design test suite architecture
2. Implement core test scenarios
3. Integrate with CI/CD
4. Document usage

## Use Cases to Test

### High Priority
- Transpiler JavaScript programming tab
  - Load example code
  - Transpile to logic conditions
  - Verify output
  - Decompile and verify round-trip

### Medium Priority
- Firmware flashing workflow
- Settings import/export
- Tab navigation
- Connection to flight controller

### Low Priority
- Full UI regression testing
- Visual regression testing
- Performance testing

## Files to Investigate

### INAV Configurator Structure
- `inav-configurator/js/main.js` - Main Electron entry point
- `inav-configurator/tabs/javascript_programming.js` - Transpiler UI
- `inav-configurator/index.html` - Main UI
- Test framework integration points

## Risks & Considerations

### Potential Issues

- **MCP server maturity** - These tools may be new/unstable
- **Electron version compatibility** - INAV Configurator on older Electron?
- **Security concerns** - Running automated tools on flight controller software
- **Maintenance burden** - Is MCP approach worth the complexity?
- **Learning curve** - Team needs to understand MCP architecture

### Questions to Answer

- Can MCP servers interact with existing Electron apps?
- Performance impact on test execution?
- Does it work with Electron Forge (configurator build system)?
- Can it capture/verify visual state?
- Integration with GitHub Actions CI/CD?

## Success Criteria

### Research Phase Success
- [ ] Both MCP servers evaluated and documented
- [ ] Clear understanding of capabilities/limitations
- [ ] Comparison with traditional testing approaches
- [ ] Go/no-go recommendation with rationale

### POC Phase Success (if pursuing)
- [ ] Basic configurator interaction working
- [ ] Screenshot verification functional
- [ ] Transpiler UI test case automated
- [ ] Performance acceptable

### Production Success (if implementing)
- [ ] Test suite covers critical paths
- [ ] CI/CD integration functional
- [ ] Documentation complete
- [ ] Team trained on usage

## Alternative Approaches

If MCP servers don't work out:

1. **Playwright** - Standard Electron testing
2. **Spectron** - Electron-specific test framework (deprecated but still works)
3. **Puppeteer** - Chrome DevTools Protocol
4. **Manual testing scripts** - Simple automation via Node.js

## Resources

**MCP Servers:**
- Electron MCP: https://mcpmarket.com/server/electron-1
- Circuit MCP: https://github.com/snowfort-ai/circuit-mcp

**INAV Configurator:**
- Repository: https://github.com/iNavFlight/inav-configurator
- Current location: `inav-configurator/` and `bak_inav-configurator/`

**Related Documentation:**
- MCP Protocol: https://modelcontextprotocol.io/
- Electron Testing: https://www.electronjs.org/docs/latest/tutorial/automated-testing

## Timeline

**No timeline set - backburner project**

This is exploratory research to be picked up when:
- Transpiler work is complete and stable
- Need for automated testing becomes pressing
- Time available for infrastructure improvement

## Notes

- This could significantly improve development velocity if successful
- Particularly valuable for preventing regressions in transpiler UI
- May also benefit firmware testing workflows
- Consider reaching out to MCP server maintainers for Electron-specific guidance
- Document findings even if we decide not to pursue - valuable for future
