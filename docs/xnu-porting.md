# XNU integration boundary

XNU is an open-source kernel, not a complete open-source iOS distribution. A kernel
entry does not provide launchd, dyld/shared cache, frameworks, GPU userspace,
entitlements, Apple services or a working filesystem. No proprietary Apple binaries,
keys or signing materials are included or fetched for this project.

Initial source direction is XNU 8796/iOS 16-era research used by the inspected
ports, subject to ABI/toolchain evidence. DarwinBoot's parser accepts arm64/arm64e
metadata in host tests; that does not establish SM8450 PAC semantics or successful
execution of either kernel configuration. Board modifications should remain in a
device/platform layer and explicit patch series with their original licenses.

HakiOS `xnu-deps/setup.sh` requires a Theos/cctools setup and iPhoneOS16.5 SDK,
plus DriverKit headers from a macOS13.3 Kernel.framework archive. Those dependencies
are not installed in this cloud. The script references third-party SDK mirrors;
they were not downloaded. A complete kernel build and QEMU open-kernel boot remain
BLOCKED pending a verified, appropriately licensed toolchain/header path. This is
not evidence that an SDK-free approach is impossible, only a limitation of the
audited build route. ios-sweet's kernel CI uses macOS/Xcode, which this Linux
environment does not provide. No full XNU build command is described as passed.

The next independent integration work is to audit UniXNU's ArmCpu/ArmDTPlatform and
SM8450 common sources, resolve per-file licensing, and establish a reproducible
open-source kernel dependency set. Then implement a minimal platform-expert path
with validated interrupt/timer/memory inputs. Avoid storage-write, synthetic-success
and security-bypass patches merely to advance a boot log.
