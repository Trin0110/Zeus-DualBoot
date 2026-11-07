# Boot architecture and implemented boundaries

Proposed future chain: device's supported temporary mechanism -> verified SM8450
UEFI -> DarwinBoot -> XNU platform expert -> read-only root. Each arrow remains a
separate hardware milestone. Neither temporary loading nor UEFI support is assumed
for the current phone/firmware.

Implemented today:

* Research manifest validation preserves Android default and disallows device writes
  and reboots. `python3 -m boot.config devices/zeus/device.json` succeeds for a valid
  **research** configuration. Add `--require-ready`: exit 2 is the expected BLOCKED
  outcome. Even a filled manifest cannot enable hardware execution.
* `python3 -m boot.image PATH` validates Android boot v3/v4 header sizes, magic,
  reserved fields, alignment, payload bounds and signature-section layout offline.
  It does not authenticate AVB/signatures, validate kernel machine code, handle
  vendor_boot or v0-v2, or establish target compatibility. The actual phone's boot
  header version is unknown.
* Production Mach-O and packed ramdisk parsing are reused from pinned DarwinBoot,
  with unchanged original tests. ELF AArch64 objects of our C interfaces compile
  freestanding. No new kernel or bootloader is synthesized to bypass missing data.

Before handoff implementation: establish current EL/cache/MMU state, RAM/reserved
ownership, page-size alignment, kernel segment bounds, valid entry ABI and ADT
schema. UEFI memory-map keys can change before ExitBootServices; use the upstream
retry/ownership logic and test failure paths. Kernel panic/early-console output
must be captured through a validated channel without writing phone storage.

The HakiOS EFI artifact is an upstream research build. It contains fixed payload
addresses and block-write functions. No script here packages or executes it on zeus.
Its successful compilation proves the ARM64 PE toolchain only. The placeholder
identity is intentionally not real iOS identity and cannot launch iOS userland.
