# Zeus DualBoot engineering rules

Use the existing checkout; cloud tasks are isolated. Do not create worktrees unless requested.
Read README.md and docs/progress.md before continuing. Communicate with the user in Thai.

Research and inspect source before implementing a kernel or bootloader. Keep upstream licenses,
immutable revisions and attribution. Never infer hardware addresses from another board.
No Apple proprietary binaries, keys, firmware or SDK redistribution.

Until separately and explicitly authorized, do not unlock, flash, erase, repartition, change
vbmeta, reboot, temporary-boot or run experimental code on a phone. Read-only ADB metadata is
allowed. Android remains the default; userdata and recovery must be preserved. Do not run
upstream phone/install scripts: some overwrite userdata. Use only our allowlisted collector.

Unknown hardware values must remain null/UNKNOWN. Host tests and emulation do not prove hardware
support. Missing driver backends return unsupported, never success. Mock backends belong in tests.
Run `make check` after relevant changes. Record exact commands and results; never call a build
an XNU boot, a kernel boot an iOS boot, or either one persistent dual boot.
