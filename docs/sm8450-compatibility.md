# SM8450 compatibility

The user reports Xiaomi 12 Pro, SM8450, Adreno 730, 256 GB UFS. These are target
requirements, not observations from a connected phone. The Android build and board
revision remain unknown.

Source anchors:

* Linux `v6.12/arch/arm64/boot/dts/qcom/sm8450.dtsi` was downloaded from
  [torvalds/linux](https://github.com/torvalds/linux/blob/v6.12/arch/arm64/boot/dts/qcom/sm8450.dtsi).
  It describes the SoC interrupt, timer, clock, SMMU, display and UFS topology;
  it does not identify this phone's panel or current reserved-memory ownership.
* Official [MiCode zeus-s-oss](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/tree/zeus-s-oss)
  resolves to `7d10d738b2c4299f3b8549c61a01ece39f19c788`. Its Makefile says Linux 5.10.43.
  This verifies a source branch, **not** the running kernel version. An initially
  guessed `cupid-s-oss` branch returned no ref; branch discovery found `zeus-s-oss`.
* Blaze414's zeus DTS `7acfc074` derives from cupid and explicitly identifies
  unverified regulator values. Its own stock dump must not override this device's
  evidence. The v6.12 mainline cupid DTS URL returned 404; no file was assumed.
* iOSPlus10/negroni use the same SoC but a different board, firmware, panel and
  storage layout. fuxi/sheng SM8550, raphael SM8150, beryllium SDM845 and GS101 are
  not interchangeable register/firmware configurations.

| Subsystem | Reusable contract | Still required for zeus |
| --- | --- | --- |
| CPU/MMU | AArch64 objects compile; DarwinBoot parser handles arm64/arm64e metadata | Actual EL, granule, PAC implications, cache state and kernel configuration |
| GIC/timer | Linux DTS provides research topology | Live DT correspondence, redistributor range, interrupt routing, counter rate |
| RAM | Checked range/exclusion API | Actual RAM and reserved ranges, secure/DMA/framebuffer ownership |
| Clocks/power | Linux/Xiaomi references | Firmware calls, regulators, reset order, rollback behavior |
| Display | Bounded framebuffer writes and explicit callbacks | Validated handoff mapping, format, stride, coherency and LCD identity |
| Touch | Bounded contact event state machine | Actual controller/bus/IRQ/power/firmware and XNU IOKit integration |
| GPU | Adreno 730 target only | Firmware provenance, SMMU, allocator, command ABI and userland stack |
| UFS | No block device backend provided | Controller state, DMA/SMMU/cache ownership, read-only root path first |

`platform/sm8450/reference.json` records GIC/UFS/GCC windows and timer facts checked
against the retrieved Linux v6.12 DTS, with its hash. It is an inert source-reference
table, never consumed by runtime code. No observed hardware address or panel command
has been added to the zeus manifest. Actual ownership and firmware mappings are unknown.
