# Real-card SD blackbox tests (PR #12150)

Rig: an INAV board with an SD slot, USB, no props/motors/ESC. Results from the HUMMINGBIRD_FC305_H7 run: split gap 64.5-69.6 ms over 3 splits; one power cut between delete and relocate left 0 FAT violations and logging recovered.

1. `hw_setup.py apply` - receiver_type=MSP, ARM on AUX1 (saved to EEPROM); `hw_setup.py restore` undoes it.
2. Make a split happen quickly: `cli_cmd.py msc`, then (board in mass-storage mode, a USB replug may be needed) `shrink_freefile.py /dev/sdX --superclusters 4`. Only the freefile directory-entry size is changed. Never `--restore` after the freefile has moved: it rewrites the whole directory sector.
3. Gap: `measure_split_gap.py --splits 3 --max-seconds 600` (exit 0 ok, 2 no split/stall). Then `cli_cmd.py msc`, `read_card_logs.py /dev/sdX --out DIR --min-number N`, `blackbox_split_gap.py DIR/LOG*.TXT` (exit 0 <250 ms, 3 warn, 4 fail >=1 s).
4. Power cut: needs a test firmware that holds ~40 s between the delete and the freefile relocation and lights LED0/LED1 (a local patch, not for the PR). `cut_trial.py` arms and logs; pull USB when both LEDs light. Check with `read_card_logs.py --list`, the FAT walker `../../sitl/sdcard/fat_inspect.py` and `fsck.vfat -n` (read-only; FAT copy 2 and chain-length complaints are advisory, afatfs does not write copy 2).
5. A failsafe lockout (ARMING_DISABLED_FAILSAFE_SYSTEM) after an abandoned armed run needs a USB power cycle.
Scripts that import `measure_split_gap` rely on its `__main__` guard.
