# Assignment: Investigate SITL WebAssembly Compilation

**Date:** 2025-12-01 17:35
**To:** Developer
**From:** Manager
**Subject:** New Assignment - Research SITL Compilation for WebAssembly
**Priority:** MEDIUM
**Project:** investigate-sitl-wasm-compilation

---

## Assignment Overview

You are assigned to investigate the feasibility of compiling INAV's SITL (Software In The Loop) target for WebAssembly (wasm), which would enable running the simulator in web browsers.

**Project Location:** `claude/projects/investigate-sitl-wasm-compilation/`

---

## Background

**What is SITL?**

INAV's SITL target allows running the flight controller firmware on a PC for simulation and testing without physical hardware. It's currently compiled as a native executable that runs on Linux/macOS/Windows.

**What is WebAssembly?**

WebAssembly (wasm) is a portable binary instruction format that runs in web browsers at near-native speed. It's designed to be a compilation target for languages like C/C++.

**Why is this interesting?**

Compiling SITL to wasm could enable:
- **Browser-based flight simulation** - No local installation required
- **Web configurator integration** - Test firmware changes directly in the configurator
- **Educational tools** - Interactive demos and tutorials
- **Easier development** - Lower barrier to entry for contributors
- **Cross-platform compatibility** - Works anywhere with a modern browser

---

## Research Question

**"Can we compile INAV's SITL target for WebAssembly?"**

This is a pure feasibility investigation. We need to understand:
1. Is it technically possible?
2. What would it take to do it?
3. Is the effort justified by the benefits?

---

## Investigation Tasks

### Phase 1: SITL Architecture Review (2-3h)

**Understand how SITL works:**

1. **Examine build configuration:**
   - Find SITL-related CMakeLists.txt files
   - Identify compiler flags and dependencies
   - Understand how SITL target differs from hardware targets

2. **Map code structure:**
   - Which source files are SITL-specific?
   - What platform abstraction layers exist?
   - How does SITL simulate hardware (sensors, I/O)?
   - What external libraries does SITL use?

3. **Document dependencies:**
   - System APIs (sockets, threading, file I/O)
   - External libraries (if any)
   - Platform-specific code

**Deliverable:** SITL architecture summary document

### Phase 2: WebAssembly/Emscripten Research (2-3h)

**Understand the wasm compilation toolchain:**

1. **Study Emscripten:**
   - Emscripten is the LLVM-based C/C++ to wasm compiler
   - Research what POSIX APIs it supports
   - Understand networking in wasm (WebSockets instead of sockets)
   - Learn about file system emulation (MEMFS, IDBFS)
   - Check threading support (pthreads via SharedArrayBuffer)

2. **Research prior art:**
   - Has Betaflight compiled to wasm?
   - Any ArduPilot or PX4 web efforts?
   - Other embedded firmware → wasm projects?
   - Flight simulator engines in WebAssembly?

3. **Identify gaps:**
   - Which SITL features map cleanly to wasm APIs?
   - Which require significant changes?
   - Which might be impossible in browser context?

**Deliverable:** Emscripten compatibility analysis

### Phase 3: Feasibility Assessment (2-3h)

**Determine if this is doable:**

1. **Create compatibility matrix:**
   - For each SITL dependency, find wasm equivalent
   - Socket communication → WebSockets?
   - File I/O → Browser APIs?
   - Threading → Web Workers?
   - Timing/scheduling → requestAnimationFrame?

2. **Identify blockers:**
   - Are there hard requirements that wasm can't meet?
   - Performance concerns?
   - Binary size concerns?
   - Security restrictions?

3. **Estimate effort (if feasible):**
   - What code changes would be needed?
   - Build system modifications?
   - API porting work?
   - Testing infrastructure?

**Optional (if time permits):**
- Try a minimal SITL compilation with Emscripten
- See what errors come up
- Document immediate issues

**Deliverable:** Feasibility assessment with effort estimate

### Phase 4: Report and Recommendation (1-2h)

**Synthesize findings into clear recommendation:**

**Recommendation format:**
- ✅ **GO:** Feasible with reasonable effort → Provide implementation roadmap
- ⚠️ **MAYBE:** Feasible but significant challenges → Detail challenges and mitigations
- ❌ **NO-GO:** Not practical or possible → Explain why

**Report contents:**
- Executive summary (2-3 paragraphs)
- Technical findings (architecture, compatibility, blockers)
- Effort estimate (if GO/MAYBE)
- Risk analysis
- Recommendation with justification
- Next steps (if GO/MAYBE)

**Deliverable:** Completion report to manager

---

## Success Criteria

- Understanding of SITL architecture documented
- WebAssembly/Emscripten capabilities researched
- Prior art reviewed (other projects doing similar things)
- Compatibility analysis complete
- Clear GO/MAYBE/NO-GO recommendation with justification
- If feasible, rough effort estimate provided

---

## Key Questions to Answer

**Technical:**
1. Can Emscripten compile the SITL target?
2. How would networking work? (MSP over WebSockets?)
3. How would simulator connections work?
4. What's the expected wasm binary size?
5. Can real-time performance be maintained?

**Practical:**
1. Has anyone done this before? (Prior art)
2. What would be required to make it work?
3. How much effort would it take?
4. What are the main risks/challenges?

**Value:**
1. What use cases would browser-based SITL enable?
2. Is the juice worth the squeeze?

---

## Investigation Tips

**SITL Build Files:**
- Look in `cmake/` directory for SITL-related configuration
- Search for "SITL" in CMakeLists.txt files
- Check `src/main/target/SITL/` directory

**Emscripten Resources:**
- Official docs: https://emscripten.org/docs/
- Porting guide: https://emscripten.org/docs/porting/
- API reference: https://emscripten.org/docs/api_reference/

**Search Terms:**
- "flight controller webassembly"
- "betaflight wasm"
- "embedded firmware browser"
- "flight simulator webassembly"

**Prior Art to Check:**
- Betaflight Configurator (any wasm components?)
- ArduPilot web tools
- PX4 browser integration
- WebAssembly RTOS projects

---

## Estimated Time

**Total:** 7-10 hours

- Phase 1 (SITL architecture): 2-3h
- Phase 2 (wasm/Emscripten research): 2-3h
- Phase 3 (feasibility assessment): 2-3h
- Phase 4 (report): 1-2h

---

## Notes

**This is research, not implementation.** Don't spend time actually porting code - we just need to know if it's feasible and what it would take.

**Think about value.** Even if it's technically feasible, is it worth doing? What would browser-based SITL enable that we can't do now?

**Consider alternatives.** Maybe a subset of SITL (e.g., just PID simulation) is more practical than full SITL?

**Document as you go.** Save your findings in the project directory so the analysis is preserved for future reference.

---

## Deliverables

**Submit to Manager:**

1. SITL architecture summary
2. Emscripten compatibility analysis
3. Prior art research findings
4. Feasibility assessment with recommendation
5. Effort estimate (if feasible)
6. Completion report with next steps

---

## Context: Why This Matters

This investigation is related to the web/PWA configurator migration work. If we can run SITL in a browser, it could enable:

- **Integrated testing** - Test firmware changes without leaving the configurator
- **Tutorials** - Interactive flight controller lessons
- **PID tuning** - Live simulation feedback
- **Community** - Lower barrier for contributors to test changes

But only if it's technically feasible and not too much work.

**Your job:** Tell us if this is a good idea or not.

---

**Good luck with the research!**

---

**Development Manager**
2025-12-01 17:35
