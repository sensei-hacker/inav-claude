# Todo List: Debug ESP32 ChaCha Crash

## Phase 1: Basic ESP32 Verification

- [ ] Create minimal test firmware
  - [ ] Basic ESP32 initialization only
  - [ ] Serial communication over USB
  - [ ] Simple "hello world" loop
- [ ] Build and flash to ESP32 TX
- [ ] Verify stable operation (1+ minutes)

## Phase 2: Incremental ChaCha Testing

- [ ] Step 2a: Add ChaCha library include
  - [ ] Build, flash, test
  - [ ] Document result
- [ ] Step 2b: Create ChaCha object
  - [ ] `ChaCha cipher(12);`
  - [ ] Build, flash, test
  - [ ] Document result
- [ ] Step 2c: Initialize ChaCha
  - [ ] Set key and nonce
  - [ ] Build, flash, test
  - [ ] Document result
- [ ] Step 2d: Single encrypt operation
  - [ ] Encrypt small buffer
  - [ ] Build, flash, test
  - [ ] Document result
- [ ] Step 2e: Test ChaCha20
  - [ ] Change to 20 rounds
  - [ ] Build, flash, test
  - [ ] Document result
- [ ] Step 2f: Benchmark loop
  - [ ] Add 1000 iteration loop
  - [ ] Build, flash, test
  - [ ] Document result

## Phase 3: Production Verification

- [ ] Flash normal production firmware
- [ ] Test TX boot and initialization
- [ ] Test encryption handshake with RX
- [ ] Verify encrypted link operation
- [ ] Document production status

## Analysis and Reporting

- [ ] Identify exact crash point
- [ ] Document root cause hypothesis
- [ ] Provide fix or investigation path
- [ ] Send completion report to manager

## Completion

- [ ] All tests passing or crash identified
- [ ] Production safety verified
- [ ] Completion report sent
