# Todo List: Analyze Pitot Blockage APA Issue

## Phase 1: Research & Understanding

- [ ] Read GitHub issue #11208
  - [ ] Read issue description thoroughly
  - [ ] Review user's reported behavior
  - [ ] Note all suggested solutions
  - [ ] Study attached graphs/images
  - [ ] Read all comments and discussion

- [ ] Read PDF document
  - [ ] Open `/home/raymorris/Downloads/pitot blockage sanity check.pdf`
  - [ ] Extract all technical details
  - [ ] Note additional suggestions
  - [ ] Document proposed solutions
  - [ ] Extract any diagrams or data

- [ ] Read wiki documentation
  - [ ] https://github.com/iNavFlight/inav/wiki/PID-Attenuation-and-scaling#Fixedwing-APA
  - [ ] Understand intended behavior
  - [ ] Note configuration parameters
  - [ ] Document expected use cases

## Phase 2: Code Analysis

- [ ] Locate APA implementation code
  - [ ] Search for `apa_pow` in codebase
  - [ ] Find PIFF gain scaling code
  - [ ] Identify cruise speed reference
  - [ ] Find airspeed reading location

- [ ] Analyze gain scaling logic
  - [ ] Document the scaling formula
  - [ ] Understand above-cruise behavior (reduction)
  - [ ] Understand below-cruise behavior (increase)
  - [ ] Identify where `apa_pow` is used
  - [ ] Calculate actual percentage ranges

- [ ] Check for existing safety features
  - [ ] Look for airspeed sanity checks
  - [ ] Check for minimum airspeed thresholds
  - [ ] Look for pitot blockage detection
  - [ ] Check for rate-of-change validation
  - [ ] Review sensor validation code

- [ ] Trace failure scenarios
  - [ ] What happens when pitot reads 0?
  - [ ] What happens when pitot reads very low (<25 km/h)?
  - [ ] What happens on sudden airspeed drop?
  - [ ] Are there any fail-safes?

## Phase 3: Solution Evaluation

- [ ] Evaluate Solution 1: No gain increase below cruise
  - [ ] Pros: Simple, safe, prevents issue
  - [ ] Cons: May affect slow-speed performance
  - [ ] Code complexity: Low
  - [ ] Backward compatibility impact
  - [ ] User impact assessment

- [ ] Evaluate Solution 2: Separate increase/decrease parameters
  - [ ] Pros: Maximum flexibility for users
  - [ ] Cons: More settings, more complexity
  - [ ] Code changes required
  - [ ] UI/configurator changes needed
  - [ ] Default value recommendations
  - [ ] User education requirements

- [ ] Evaluate Solution 3: Airspeed sanity checks
  - [ ] Define useful sanity checks
  - [ ] Minimum airspeed threshold
  - [ ] Maximum rate of change
  - [ ] Cross-check with other sensors (GPS?)
  - [ ] Implementation complexity
  - [ ] False positive risk

- [ ] Consider hybrid approaches
  - [ ] Combine no-increase with sanity checks
  - [ ] Combine separate parameters with limits
  - [ ] Layered safety (multiple checks)

- [ ] Choose recommended solution
  - [ ] Weigh pros and cons
  - [ ] Consider safety first
  - [ ] Consider user experience
  - [ ] Consider implementation complexity
  - [ ] Document rationale

## Phase 4: Detailed Proposal

- [ ] Document current behavior
  - [ ] Code flow diagram
  - [ ] Formula documentation
  - [ ] Behavior graphs (above/below cruise)
  - [ ] Failure mode analysis

- [ ] Propose specific code changes
  - [ ] Identify files to modify
  - [ ] Write pseudo-code or actual code snippets
  - [ ] Show before/after comparison
  - [ ] Include new settings if needed
  - [ ] Document default values

- [ ] Define testing approach
  - [ ] SITL test scenarios
  - [ ] Simulated pitot failure
  - [ ] Normal operation verification
  - [ ] Edge case testing
  - [ ] Hardware test recommendations

- [ ] Address backward compatibility
  - [ ] Migration path for existing users
  - [ ] Settings conversion if needed
  - [ ] Deprecation warnings
  - [ ] Documentation updates required

## Phase 5: Report Creation

- [ ] Create analysis report
  - [ ] Executive summary
  - [ ] Problem statement
  - [ ] Current code analysis
  - [ ] Solution evaluation
  - [ ] Recommended solution
  - [ ] Proposed code changes
  - [ ] Testing recommendations
  - [ ] Backward compatibility plan

- [ ] Save report to `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

## Completion

- [ ] All research complete
- [ ] All code analyzed
- [ ] All solutions evaluated
- [ ] Recommendation made
- [ ] Report complete and detailed
- [ ] Send completion report to manager
