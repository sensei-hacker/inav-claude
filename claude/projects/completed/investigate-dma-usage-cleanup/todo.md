# TODO: Investigate DMA Usage and Cleanup Opportunities

**Created:** 2025-11-24
**Status:** Not yet assigned

---

## Phase 1: Research Betaflight's DMA Cleanup

- [ ] Search Betaflight repository for DMA-related commits/PRs
- [ ] Identify key cleanup changes (PRs, commit messages, issues)
- [ ] Document what problems they were solving
- [ ] Note techniques or patterns used
- [ ] Save findings to `research-notes.md`

**Deliverable:** Understanding of Betaflight's approach

---

## Phase 2: Understand INAV DMA Architecture

- [ ] Read and document DMA abstraction layer (`drivers/dma.h`)
- [ ] Review platform implementations:
  - [ ] `dma_stm32f4xx.c`
  - [ ] `dma_stm32f7xx.c`
  - [ ] `dma_stm32h7xx.c`
- [ ] Document DMA tag system and resource ownership
- [ ] Review DMA CLI interface (`dma_cli.h`, `dma_cli_stm32_impl.c`)

**Deliverable:** Architecture overview section

---

## Phase 3: Analyze Peripheral DMA Usage

### UART/Serial
- [ ] Review `serial_uart_hal.c` DMA usage
- [ ] Review `serial_uart_stm32f7xx.c` DMA usage
- [ ] Review `serial_uart_stm32h7xx.c` DMA usage
- [ ] Document TX vs RX DMA patterns
- [ ] Note which UARTs use DMA by default

### SPI
- [ ] Review `bus_spi_hal_ll.c` DMA usage
- [ ] Review gyro SPI DMA requirements
- [ ] Review MAX7456 OSD SPI usage (`max7456.c`)
- [ ] Document DMA vs polling strategies

### Timers
- [ ] Review `timer_impl_hal.c` DMA usage
- [ ] Review motor output DMA (`pwm_output.c`)
- [ ] Review LED strip DMA (`light_ws2811strip.c`)
- [ ] Document timer DMA channel requirements

### SD Card
- [ ] Review SDIO/SDMMC implementation (`sdmmc_sdio*.c`)
- [ ] Note H7 BDMA usage for SDIO
- [ ] Document resource requirements

### ADC
- [ ] Check if ADC uses DMA
- [ ] Document battery/current sensing DMA needs

**Deliverable:** Peripheral DMA mappings section

---

## Phase 4: Review Target Configurations

- [ ] Analyze DMA assignments in 10-15 representative targets:
  - [ ] MATEKF405 (popular F4)
  - [ ] MATEKF722 (popular F7)
  - [ ] DAKEFPVH743 (H7)
  - [ ] TBS_LUCID_H7 (H7)
  - [ ] SpeedyBee boards
  - [ ] Other popular boards
- [ ] Document common DMA assignment patterns
- [ ] Identify any conflicts in target.h files
- [ ] Note platform-specific differences

**Deliverable:** Target-specific configurations section

---

## Phase 5: Create DMA Channel Inventory

- [ ] Document F4 DMA resources (2 × 8 streams)
- [ ] Document F7 DMA resources (2 × 8 streams)
- [ ] Document H7 DMA resources (2 × 8 streams + BDMA)
- [ ] Create table of typical allocations by peripheral type
- [ ] Identify resource-constrained scenarios

**Deliverable:** DMA channel inventory section

---

## Phase 6: Identify Improvement Areas

- [ ] Look for unnecessary DMA allocations
- [ ] Identify potential conflicts
- [ ] Note areas where polling could replace DMA
- [ ] Compare with Betaflight's approach
- [ ] Document specific improvement opportunities

**Deliverable:** Areas for potential improvement section

---

## Phase 7: Documentation

- [ ] Create `inav/docs/development/DMA-USAGE.md`
- [ ] Write architecture overview
- [ ] Write DMA channel inventory
- [ ] Write peripheral DMA mappings
- [ ] Write target-specific configurations
- [ ] Write areas for potential improvement (if any)
- [ ] Add diagrams or tables as needed
- [ ] Proofread and polish

**Deliverable:** Complete DMA usage documentation

---

## Phase 8: Completion

- [ ] Review documentation for completeness
- [ ] Ensure F7/H7 focus is clear
- [ ] Verify all deliverables are complete
- [ ] Send completion report to manager inbox
- [ ] Include summary of findings
- [ ] List any follow-up projects needed

**Deliverable:** Completion report with findings

---

## Notes

- Focus Phase 1 analysis on F7 and H7 platforms
- Note F4 issues separately only if they don't apply to F7/H7
- If major issues are discovered, pause and consult manager before proceeding
- Keep research notes organized for future reference
- Documentation should be clear enough for new developers
