# AT32F435/437 MUX Distribution Reference

Source: AT32F435/437 Reference Manual, chapter 6.2.9 (Tables 6-1..6-8), read directly per pin —
see `refman-iomux.json` and `parse_refman_iomux.py`.

**The MUX number for a peripheral is not fixed — it varies by pin.**
An earlier version of this file listed one MUX number per peripheral
(e.g. "I2C is always MUX4"); checking that assumption against the
Reference Manual's real per-pin tables found it wrong for about 1 in 5
signals. For example `I2C1_SCL` is MUX4 on most pins but MUX8 on PA9,
and `I2C3_SCL` is MUX7 on PB13 but MUX4 on PA8. **Always look up the
specific pin** in `alternate-functions.tsv` / `af-by-function.txt` —
never assume a peripheral's MUX number from its name alone.

## MUX numbers observed per peripheral prefix

| Prefix | MUX numbers used (occurrence count) |
|--------|---------------------------------------|
| CAN1 | MUX9 (8) |
| CAN2 | MUX9 (6) |
| CKE1 | MUX12 (1) |
| CLKOUT1 | MUX0 (1) |
| CLKOUT2 | MUX0 (1) |
| CS1 | MUX12 (1) |
| C_SDDQMH | MUX12 (1) |
| C_SDDQML | MUX12 (1) |
| D0 | MUX11 (1) |
| D1 | MUX11 (1) |
| DVP | MUX13 (37) |
| EMAC | MUX11 (41) |
| ERTC | MUX0 (1) |
| EVENTOUT | MUX15 (116) |
| H1 | MUX3 (1) |
| I2C1 | MUX4 (10), MUX8 (2) |
| I2C2 | MUX4 (17), MUX7 (1) |
| I2C3 | MUX4 (15), MUX7 (1) |
| I2S1 | MUX4 (3), MUX5 (10) |
| I2S2 | MUX5 (13), MUX6 (6), MUX7 (3) |
| I2S3 | MUX5 (3), MUX6 (10), MUX7 (4) |
| I2S4 | MUX5 (8), MUX6 (9) |
| IR | MUX0 (1), MUX1 (1) |
| JTCK | MUX0 (1) |
| JTDI | MUX0 (1) |
| JTDO | MUX0 (1) |
| JTMS | MUX0 (1) |
| OTG1 | MUX10 (6) |
| OTG2 | MUX11 (1), MUX12 (5) |
| QSPI1 | MUX9 (18), MUX10 (16) |
| QSPI2 | MUX5 (6), MUX9 (6), MUX10 (6) |
| SDIO1 | MUX12 (18), MUX13 (2), MUX14 (3) |
| SDIO2 | MUX10 (8), MUX11 (3), MUX13 (3), MUX14 (2) |
| SPI1 | MUX4 (4), MUX5 (10) |
| SPI2 | MUX5 (14), MUX6 (4), MUX7 (3) |
| SPI3 | MUX5 (2), MUX6 (11), MUX7 (3) |
| SPI4 | MUX5 (10), MUX6 (11) |
| SWCLK | MUX0 (1) |
| SWDIO | MUX0 (1) |
| SWO | MUX0 (1) |
| TMR1 | MUX1 (33) |
| TMR10 | MUX3 (2) |
| TMR11 | MUX3 (3) |
| TMR12 | MUX9 (2) |
| TMR13 | MUX9 (2) |
| TMR14 | MUX9 (2) |
| TMR2 | MUX1 (16) |
| TMR20 | MUX2 (24), MUX6 (11) |
| TMR3 | MUX2 (16) |
| TMR4 | MUX2 (9) |
| TMR5 | MUX2 (11) |
| TMR8 | MUX3 (21) |
| TMR9 | MUX3 (6) |
| UART4 | MUX7 (2), MUX8 (6) |
| UART5 | MUX8 (8) |
| UART7 | MUX8 (8) |
| UART8 | MUX7 (2), MUX8 (6) |
| USART1 | MUX7 (10) |
| USART2 | MUX6 (1), MUX7 (10), MUX8 (3) |
| USART3 | MUX7 (15), MUX8 (4) |
| USART6 | MUX8 (14) |
| XMC | MUX10 (19), MUX12 (79), MUX14 (16) |

## Timer DEF_TIM() Notes

In `target.c`, `DEF_TIM(TMR3, CH3, PB0, ...)` automatically resolves
the correct MUX number from the `DEF_TIM_AF__PB0__TCH_TMR3_CH3` macro
defined in `timer_def_at32f43x.h`. The `af` (flags) parameter in
`DEF_TIM` is unused for AT32 (pass 0). `parse_af_table.py` cross-checks
this file's MUX numbers against the Reference Manual on every run and
prints a warning for any disagreement.
