# Todo List: 3D Hardware Acceleration Auto-Fallback

## Phase 1: Investigation

- [ ] Find existing "disable 3D hardware acceleration" setting
- [ ] Identify all code locations using WebGL/3D rendering
- [ ] Document affected features
- [ ] Check magnetometer calibration 3D view
- [ ] Check model viewers

## Phase 2: Capability Detection

- [ ] Implement WebGL context creation test
- [ ] Detect full failure vs partial/degraded support
- [ ] Add detection before 3D feature usage

## Phase 3: Automatic Fallback

- [ ] Implement 2D alternatives where possible
- [ ] Add user-friendly fallback messages
- [ ] Add logging for debugging
- [ ] Ensure no crashes on 3D failure

## Phase 4: Testing

- [ ] Test on system without GPU support
- [ ] Test in VM
- [ ] Test with remote desktop
- [ ] Verify graceful degradation in all scenarios

## Completion

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Pull request created
- [ ] Send completion report to manager
