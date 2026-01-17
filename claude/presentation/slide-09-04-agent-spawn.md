```
[Task Tool - Spawning Agent]
subagent_type: "test-engineer"
prompt: "Check why terrain chart isn't displaying"

[Agent context: 492 lines - separate window]
✓ Chrome DevTools knowledge
✗ Build system (not needed)

test-engineer> Taking snapshot of Mission Control...
test-engineer> Checking console logs...
test-engineer> Found: plotElevation() commented out
test-engineer> Location: mission_control.js:4228-4351
test-engineer> Reason: ESM compatibility (Dec 2024)
```
