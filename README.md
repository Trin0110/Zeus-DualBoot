# Zeus DualBoot

Experimental engineering toward an XNU port for Xiaomi 12 Pro (`zeus`, SM8450),
preserving Android. **There is no working zeus XNU/iOS boot image or dual boot yet.**
This first implementation provides real host-tested support code, a read-only ADB
metadata collector, offline boot checks and pinned upstream build experiments.

## Run the verified development workflow

The prepared cloud environment uses Debian 13, GCC 14.2, Clang/LLD 19.1.7 and
Python 3.12. No Python packages or Apple binaries are required for these checks.

```sh
cd /workspace/Zeus-DualBoot
export PATH=/workspace/.zeus-tools/bin:$PATH
make check                 # native library, ASan/UBSan, Python and actual upstream parser tests
make cross-check           # freestanding AArch64 object compilation
make upstream-check        # pinned HakiOS EFI build + upstream host tests; network on first run
```

`bash scripts/setup-cloud.sh` reproduces the selected Debian cloud tool setup and
executes all three checks. Its package revisions are pinned; it fails if unavailable.
On other Linux systems install C compiler, make, Python 3, clang and lld normally.
`make check` is offline once tools are installed. GitHub CI is configured, but no
GitHub Actions run has been observed or claimed in this session.

## Read-only phone diagnostics

On a computer that already has authorized ADB access to the phone:

```sh
python3 tools/adb-diagnostics/collect.py --output zeus-diagnostics.json
# If multiple authorized devices are present, add --serial YOUR_LOCAL_SELECTOR.
```

The collector reads only fixed metadata probes, requires no root, bounds output
and time, and stores sanitized structured fields instead of raw logs. It never
collects live touch events, unlocks, flashes or reboots. See [diagnostics](docs/diagnostics.md).
No device was connected in the cloud session; its behavior on the real phone is unverified.

## Implemented components

| Component | Evidence and scope |
| --- | --- |
| `devices/zeus/device.json` | User-reported target; observed hardware fields remain null |
| `boot/config.py` | Host-tested policy validation; always blocks physical execution |
| `boot/image.py` | Offline Android boot v3/v4 header/section validation; no signature or compatibility claim |
| `drivers/display` | Bounded RGBX/BGRX framebuffer writes to caller-owned mapped memory; hardware callbacks absent |
| `drivers/touch` | Contact range/state validation; hardware polling callback absent |
| `drivers/storage` | Checked read-only block view and output bounds; no UFS backend |
| `platform/sm8450` | RAM/reservation validation; no invented register map |
| `third_party/DarwinBoot` | Unmodified BSD-2-Clause-Patent parser sources and original tests with hashes |
| `scripts/verify-upstreams.sh` | ARM64 EFI loader cross-build; research output must not be booted on zeus |

Start with [progress and evidence](docs/progress.md), [upstream audit](docs/upstream-audit.md)
and [boot architecture](docs/boot-architecture.md). The new project's code is MIT;
vendored code retains its original license. See [third-party notices](LICENSES/README.md).

The next device-dependent input is the sanitized diagnostic report. Firmware build,
panel, touch, reserved memory, partitions and boot mechanisms must be established
before implementing board initialization. Device-changing tests require separate
explicit authorization and a verified recovery plan.
