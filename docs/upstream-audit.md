# Source audit — 2026-11-07

All named GitHub repositories below were fetched and their source, license files
and recent history inspected. Full SHAs, history availability and license paths
are in `evidence/research/upstreams.json`. Evidence labels apply only to the
component stated. None is classified HARDWARE_VERIFIED for the user's zeus.
README claims, author notes and embedded logs are not independent hardware proof.

| Canonical candidate | Inspected revision | Source inspected / conclusion | Classification |
| --- | --- | --- | --- |
| [UniXNU/UniXNU](https://github.com/UniXNU/UniXNU) | `b6de3eb11f0b0118dfc14fad6eefc884a3b69737` | `components.toml`, package/build layout: explicit pins for ArmCpu, ArmDTPlatform, DarwinBoot, GopFramebuffer and SoC components. Real modular architecture; current advertised Adreno740 support is SM8550, not A730. BSD-2-Clause-Patent core, component licenses separate. | SOURCE_IMPLEMENTED; complete build unrun |
| [UniXNU/DarwinBoot](https://github.com/UniXNU/DarwinBoot) | `3c75734014cdab0acd9541e88057b7606ee7ae08` | `DarwinBootPkg/Driver/DarwinBoot.c`: Mach-O/file-set parsing, UEFI allocation/map, ADT and boot_args construction, ExitBootServices; `PackedRamdisk.h`, `WindowSize.h`. Production parser tests actually run. Full EFI driver needs EDK2. BSD-2-Clause-Patent. | BUILD_VERIFIED for extracted host parsers only |
| [oosexgang/hakios-xnu-kernel](https://github.com/oosexgang/hakios-xnu-kernel) | `63fc2b4633bac3af8e57dadab9f5a8d4cb940438` | `xnuloader/loader.c`, `efi.h`, `build.sh`, `mkidentity.py`, `xnu-deps/setup.sh`, Makefile inspected. Self-contained AArch64 EFI build works on Linux. Fixed payload conventions, board assumptions and block-write paths mean it is not safe to deploy unchanged. MIT loader; APSL kernel derivatives. | BUILD_VERIFIED loader only; XNU/QEMU unrun |
| [dipa-studio/ios-sweet](https://github.com/dipa-studio/ios-sweet) | `45263bee51df4a0f55cdf9c649af886399488ddb` | `shim/console.c`, `console.h`, `host_test.c`, `xnu/patches/`: real freestanding shim/console and XNU patch series. Host console rendered a verified PPM under ASan/UBSan. Fixed sweet framebuffer constants are not zeus values. Project MIT; kernel patches retain APSL obligations. `font.h` is generated from cp850 console font; its upstream asset provenance needs separate review, so no console/font code is vendored here. | BUILD_VERIFIED console; zeus INCOMPATIBLE without adaptation |
| [akshaynexus/iOSPlus10](https://github.com/akshaynexus/iOSPlus10) | `146e889430bab755329dde7104cc0fa002f44bfb` | `patches/xnu/`, `tools/bootlog-core-test/`, `userland/camera/`, `config/`, submodule references. SM8450/OnePlus-specific substantial code. `patches/xnu/README-bootlog.md` says patch 0367 writes userdata on every boot even without `ufsrw=1`. Mixed MIT/BSD/APSL and GPL/LGPL notices: review each file before combining. | SOURCE_IMPLEMENTED; installation INCOMPATIBLE with preserve-userdata policy |
| [pawlickerr/UniXNU-negroni](https://github.com/pawlickerr/UniXNU-negroni) | `f812002ae3e6b861d23007efdfd9f1c394934ba9` | `board.toml`, XNU patches, scripts. Board references negroni Mu-Silicium, external kernel CI and hardcoded DRAM; root arguments enable UFS/root writes. Recent history explicitly introduces flashing root to userdata. No root license discovered; do not copy unresolved files. Same negroni lineage, not independent zeus proof. | EXPERIMENTAL; installation INCOMPATIBLE |
| [Blaze414/postmarketOS-zeus](https://github.com/Blaze414/postmarketOS-zeus) | `7acfc074ff59a9be4e08ac44a63d2aa11c9a3529` | `src/dts/sm8450-xiaomi-zeus.dts`, `src/panel/panel-l2-38-0c-0a-dsc.c`: concrete Linux DTS and panel commands, GPL-2.0-only. DTS explicitly leaves regulator rails/battery parameters unverified; generated panel copyright attribution has FIXME. Useful reference, not this replacement LCD's identification. | SOURCE_IMPLEMENTED; hardware claims UNVERIFIED here |
| [bangprovn/ios-fuxi](https://github.com/bangprovn/ios-fuxi) | `27f6a31c8b27c6f9127f9cf27092968422579ccf` | `shim/ufs.c`, `xnu/fuxi-unixnu/SweetFramebuffer.cpp`, `sweet_ufs.c`: inherited sweet code still visible; UFS root defaults to userdata, write option present. SM8550 board. Multiple per-component licenses, no blanket permission inferred. | SOURCE_IMPLEMENTED; SM8450 direct reuse INCOMPATIBLE |
| [HeliumStudio-Dev/ios-raphael](https://github.com/HeliumStudio-Dev/ios-raphael) | `7ea2431bcc0ae2a5d79a31e1c2fea7de9be52cea` | `shim/ufs.c`, patches 0003/0004 and later raphael patches. Real XNU changes for SM8150, inherited SWEET machine configuration. Commit subjects claim CI/temporary boots; not independently validated. No root license found. | SOURCE_IMPLEMENTED; direct target INCOMPATIBLE |
| [ry-diffusion/Bergamota](https://github.com/ry-diffusion/Bergamota) | `37a7a7a917fc09945ed2f7d1ae68b84d4525b4cb` | `enxerto/fastboot.c`, `fastboot_test.c`, `bootui.c`: real protocol/storage machinery and host fixtures; SDM845/beryllium lineage, not zeus. Licensing of those files needs clarification; no root grant assumed. No device scripts executed. | SOURCE_IMPLEMENTED; direct target INCOMPATIBLE |
| [PixOS-Project/pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel) | `04457e5ddae2164778bd5e75c352a34dac916de9` | `soc/google/gs101/shim/ufsdiag.c`, `ufsinit.c`, `shim/ufs.c`: actual GS101 MMIO/cold-init code plus sweet ancestry. Per-component LICENSES present. Test log filenames alone are not boot proof. | SOURCE_IMPLEMENTED; GS101 hardware INCOMPATIBLE |
| [everettjf/pixel6ios](https://github.com/everettjf/pixel6ios) | `a461b34d16f97e721a9685e62d6ade000198187b` | patches 0005/0008, `research/pixelios-kernel/shim/ufs.c`: real guarded inventory/reset research layered on PixOS. Not a separate independent port success. Nested upstream license exists; top-level additions need review. | EXPERIMENTAL; GS101 hardware INCOMPATIBLE |

## Foundation decision

Additional source audit after search discovery:

| Candidate | Revision and inspected source | Assessment |
| --- | --- | --- |
| [obaosp/UniXNU-sm8450-common](https://github.com/obaosp/UniXNU-sm8450-common) | `156e46092b0afa00f5d3d8e4ebdb0b6a5a09a796`; `soc.toml`, `dts/sm8450.dtsi`, `kits/Sm8450Platform/GccUfs.h`, native-SMP and platform-power patch series | SOURCE_IMPLEMENTED. Root BSD-2-Clause-Patent, DTS BSD-3-Clause; XNU patch obligations separate. Explicitly disables Adreno730 pending a driver. UFS header is documented register facts, not an operational controller driver. Promising common topology reference; build/hardware unverified. |
| [obaosp/UniXNU-cupid](https://github.com/obaosp/UniXNU-cupid) | `b83e634bd63489b7c7ff3f976ca732ea80c98c03`; `board.toml`, package/config/patch layout, `unixnu.lock` | EXPERIMENTAL. Real board integration, but targets Xiaomi 12, different panel/board and iOS profile. Hardcoded userdata ranges and persistent-data flags must not transfer to zeus. No root license discovered; no files copied. |
| [v1-727/UniXNU-sm8450-common](https://github.com/v1-727/UniXNU-sm8450-common) | `89f3a5df982e06305044613566423c3cfe615f1b`; `ShengGmu.c`, `ShengGpuSmmu.c`, `ShengGmuCommandDb.c`, DTS and metadata | SOURCE_IMPLEMENTED. Real A730 GMU/SMMU logic, BSD-2-Clause-Patent headers. Requires generated source headers, external firmware/SMMU components and validated board inputs; no build attempted without them. Shared lineage, not independent hardware proof. |

These were shallow discovery fetches; only the available commit history was
inspected, as recorded in the evidence JSON. No complete ancestry claim is made.

Use UniXNU/DarwinBoot's UEFI architecture as the integration direction. It separates
common kernel parsing/handoff from board/SoC support, has traceable licenses, and
exposes production parsing code to meaningful malformed-input host tests. The
exact tested sources are included unchanged under `third_party/DarwinBoot`, with
hashes, immutable upstream URL/SHA and recent history. This is a partial snapshot,
not a fabricated fork history or a complete deployable bootloader.

Use HakiOS to validate a Linux-hosted EFI toolchain now. `make loader-open` produced
an ARM64 EFI application; no phone execution or XNU entry was performed. Its storage
write code and fixed addresses are audit requirements, not reusable zeus settings.
Use iOSPlus10/negroni only as SM8450 reference until per-file license, register and
storage-write reviews are complete. Do not combine GPL-derived driver logic into
APSL code without resolving license compatibility.

## Hardware and log claims

No actual user's device logs were supplied. Upstream code and documentation contain
boot claims, patch notes and traces, but this session did not authenticate their
origin or reproduce them on those devices. Therefore no candidate is upgraded to
HARDWARE_VERIFIED, and no persistent Android+iOS dual boot is established.
GPU, UFS and input implementations for another SoC are evidence of source, not
compatibility. Inherited sweet files in fuxi/raphael/PixOS and negroni-related
repositories must not be counted as independent successes.
