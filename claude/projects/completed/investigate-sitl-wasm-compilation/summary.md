# Project: Investigate SITL WebAssembly Compilation

**Status:** TODO
**Priority:** MEDIUM
**Type:** Research / Investigation
**Created:** 2025-12-01
**Assigned:** Developer

## Objective

Investigate the feasibility of compiling INAV's SITL (Software In The Loop) target for WebAssembly (wasm), enabling the simulator to run in web browsers.

## Background

**SITL (Software In The Loop):** INAV's SITL target allows running the flight controller firmware on a PC for simulation and testing without physical hardware. Currently, SITL is compiled as a native executable.

**WebAssembly (wasm):** A portable binary instruction format that runs in web browsers at near-native speed. Compiling SITL to wasm could enable:
- Browser-based flight simulation
- Integration with web-based configurator
- Easier testing and development (no local compilation needed)
- Educational tools and demos

## Research Questions

### 1. Technical Feasibility

**Core Questions:**
- Can the SITL target be compiled with Emscripten (LLVM-to-wasm compiler)?
- What dependencies does SITL have that may not be wasm-compatible?
- Are there platform-specific APIs or system calls that need wasm equivalents?
- What is the expected binary size of wasm output?

**Areas to Investigate:**
- SITL build system (CMake configuration)
- SITL dependencies (libraries, system APIs)
- Networking requirements (MSP, simulator connections)
- File I/O requirements (if any)
- Threading/concurrency usage
- Memory requirements

### 2. Architecture Analysis

**Investigate:**
- How does SITL differ from hardware targets?
- What abstraction layers exist between firmware and platform?
- Which SITL-specific files would need wasm adaptation?
- Are there hardware simulation dependencies (e.g., sensors, I/O)?

### 3. Emscripten Compatibility

**Research:**
- Which Emscripten APIs would replace SITL's platform layer?
- How would MSP communication work in browser context?
- How would simulator connections work (TCP sockets → WebSockets)?
- Can Emscripten's POSIX emulation support SITL's needs?

### 4. Prior Art

**Research Similar Projects:**
- Has Betaflight or other flight controllers done this?
- Are there similar embedded firmware → wasm ports?
- What challenges did they encounter?
- What tooling/frameworks exist for embedded → wasm?

### 5. Effort Estimation

**If feasible, estimate:**
- Changes required to build system
- Platform layer adaptations needed
- API porting effort (sockets, I/O, timing)
- Testing infrastructure requirements
- Documentation needs

## Investigation Approach

### Phase 1: SITL Architecture Review (2-3h)

1. **Examine SITL build configuration:**
   - `CMakeLists.txt` for SITL target
   - Compiler flags and dependencies
   - Build outputs and artifacts

2. **Map SITL code structure:**
   - SITL-specific source files
   - Platform abstraction layers
   - Hardware simulation interfaces
   - External dependencies

3. **Document key findings:**
   - What makes SITL different from hardware targets?
   - Which components are platform-dependent?
   - What APIs/libraries does SITL use?

### Phase 2: WebAssembly/Emscripten Research (2-3h)

1. **Study Emscripten capabilities:**
   - POSIX API support
   - Networking (WebSockets, fetch API)
   - File system emulation (MEMFS, IDBFS)
   - Threading (pthreads via SharedArrayBuffer)
   - Performance characteristics

2. **Research prior art:**
   - Search for similar firmware-to-wasm projects
   - Betaflight, ArduPilot, PX4 wasm efforts
   - Embedded systems in browser examples
   - WebAssembly flight simulators

3. **Identify compatibility gaps:**
   - Which SITL features map cleanly to wasm?
   - Which require significant adaptation?
   - Which may be impossible/impractical?

### Phase 3: Feasibility Assessment (2-3h)

1. **Analyze dependencies:**
   - List all SITL dependencies
   - Check Emscripten compatibility for each
   - Identify alternatives where needed

2. **Create compatibility matrix:**
   - Platform APIs: Native → Emscripten mapping
   - Networking: Sockets → WebSockets approach
   - Timing/scheduling: How to maintain real-time behavior
   - I/O: File system, serial ports, etc.

3. **Proof of concept (if time permits):**
   - Attempt minimal SITL build with Emscripten
   - Identify immediate blockers
   - Document compilation errors/issues

### Phase 4: Report and Recommendation (1-2h)

1. **Document findings:**
   - Technical feasibility assessment
   - Architecture compatibility analysis
   - Required changes and effort estimate
   - Challenges and risks

2. **Provide recommendation:**
   - GO: Feasible with reasonable effort
   - MAYBE: Feasible but significant challenges
   - NO-GO: Not practical/possible

3. **If GO/MAYBE, outline next steps:**
   - Phase 1: Minimal compilation
   - Phase 2: API porting
   - Phase 3: Integration testing
   - Estimated timeline

## Success Criteria

- [x] SITL architecture documented
- [x] WebAssembly/Emscripten capabilities understood
- [x] Prior art researched
- [x] Compatibility analysis complete
- [x] Feasibility assessment with clear recommendation
- [x] Report submitted to manager

## Potential Benefits (If Feasible)

**Browser-based SITL could enable:**
- Web configurator with integrated simulation
- No-install testing environment
- Educational demos and tutorials
- Community contributions without toolchain setup
- Cross-platform compatibility (Linux, Windows, macOS, mobile)
- Easier CI/CD testing in browser context

## Potential Challenges

**Known obstacles to consider:**
- Real-time performance requirements
- Binary size (wasm + firmware could be large)
- Networking API differences (sockets → WebSockets)
- Threading/concurrency limitations in browser
- Debugging and profiling differences
- Browser security restrictions
- Memory limitations in browser context

## Related Work

**Projects to research:**
- Betaflight web-based configurator (do they have wasm simulator?)
- QGroundControl (QT-based, any web efforts?)
- ArduPilot/PX4 web tools
- Flight simulator engines in WebAssembly
- Embedded RTOS in browser projects

## Estimated Time

**Total:** 7-10 hours

- Phase 1 (SITL architecture): 2-3h
- Phase 2 (wasm/Emscripten): 2-3h
- Phase 3 (feasibility): 2-3h
- Phase 4 (report): 1-2h

## Deliverables

**Submit to Manager:**

1. **SITL Architecture Summary**
   - Build system analysis
   - Code structure map
   - Platform dependencies

2. **Emscripten Compatibility Analysis**
   - Feature mapping (native → wasm)
   - Dependency compatibility
   - API translation requirements

3. **Prior Art Summary**
   - Similar projects reviewed
   - Lessons learned from others
   - Available tools/frameworks

4. **Feasibility Assessment**
   - GO / MAYBE / NO-GO recommendation
   - Justification with technical details
   - Effort estimate (if feasible)
   - Risk analysis

5. **Next Steps (if feasible)**
   - Implementation roadmap
   - Timeline estimate
   - Resource requirements

## Notes

**This is pure research** - no code changes expected at this stage.

**Key Question:** Would browser-based SITL provide enough value to justify the porting effort?

**Alternative Consideration:** Could a subset of SITL run in wasm (e.g., just PID tuning simulation) rather than full SITL?

## Location

`claude/projects/investigate-sitl-wasm-compilation/`
