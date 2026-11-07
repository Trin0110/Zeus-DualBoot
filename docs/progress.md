# Session evidence — 2026-11-07

## Windows collector follow-up

The collector now uses Windows `PeekNamedPipe` for subprocess pipes and retains
POSIX selectors, the byte/time budget, fixed read-only probes and privacy filtering.
`make check` passed locally: 23 Python tests passed, the native Windows selector
regression was skipped on Linux, and the C and DarwinBoot host checks passed.
Windows CI now covers Server 2022/2025 with Python 3.10/3.14 and official `adb.exe`;
check the [workflow runs](https://github.com/Trin0110/Zeus-DualBoot/actions/workflows/check.yml)
for the current commit's result. This is host validation, not phone execution.
Exact Windows 10/11 setup/collection commands and ACL semantics are documented in
[diagnostics.md](diagnostics.md#windows-1011-powershell).

## Original foundation session

The initial empty repository now contains functional development infrastructure.
No code was committed or pushed, and no physical device operation was performed.
Prepared files are in the current cloud checkout; future-task restoration has not
been independently tested. Read README.md for commands and scope.

## Verified results

| Component | Status | Evidence |
| --- | --- | --- |
| Python boot manifest/header checks and ADB collector behavior | HOST_TESTED | 14 unittest methods passed; `evidence/validation/setup-cloud.log` |
| Display/touch/memory/read-only storage C contracts | HOST_TESTED | Native test executable passed under AddressSanitizer and UBSan |
| C library | BUILD_VERIFIED | `build/libzeus-host.a`, GCC 14.2.0, C11, warnings as errors |
| Same four C modules for ARM64 | BUILD_VERIFIED | `build/aarch64/*.o`, Clang 19.1.7 `--target=aarch64-none-elf -ffreestanding` |
| DarwinBoot production Mach-O parser | HOST_TESTED | Original host script checks CPU subtypes, malformed ranges, file-set membership and entry |
| DarwinBoot production packed ramdisk parser/copy | HOST_TESTED | Actual C/Python round-trip, 1 TiB limit, 13 refusal cases |
| DarwinBoot memory-window rules | HOST_TESTED | Original C boundary test |
| HakiOS loader-open | BUILD_VERIFIED | ARM64 PE32+ EFI application, 66,048 bytes; never executed |
| ADB installation/server | BUILD_VERIFIED | ADB 1.0.41/34.0.5; `adb devices` returned no devices |
| Full XNU, QEMU kernel boot, iOS, physical drivers and persistent dual boot | BLOCKED | Missing validated kernel dependency/toolchain route and device evidence; none run |
| GitHub Actions | IMPLEMENTED_UNTESTED on GitHub | Workflow added; equivalent commands passed locally |

Commands actually executed:

```sh
bash scripts/setup-cloud.sh
make check
make cross-check
make upstream-check
```

The final complete setup script was exercised twice during development (and again
after source changes), including package extraction and repeated upstream builds.
The final setup log is retained. APT emitted permission warnings for a system cache
cleanup hook and one system config file; signed-index/package retrieval and all
requested tools completed successfully without changing system permissions.

HakiOS build initially failed because clang was absent. Rootless Debian APT packages
resolved that prerequisite. Original `make loader-open` embeds a changing PE timestamp;
our build wrapper relinks the unchanged object with `/timestamp:0`. Two builds with
Clang/LLD 19.1.7 produced SHA256:

`75fe9d47c56f88d0af91ebd780c08d85dcd785bd3cee7e6c2fc6956d6c1b1846`

This establishes repeatability with this toolchain, not universal cross-toolchain
bit identity. `evidence/validation/upstream-build.json` records artifact scope.
No Apple binary, SDK or proprietary identity was required for this loader-only test.

## Research and remaining work

All eleven requested GitHub candidates, DarwinBoot and three additional discovered
SM8450/cupid repositories were source-inspected (15 total).
UniXNU/DarwinBoot is the selected architecture; HakiOS provides the verified Linux
EFI build reference. Detailed revisions, license caveats and inherited code/fork
relationships are in `docs/upstream-audit.md` and `evidence/research/upstreams.json`.
The actual parser source subset is retained unchanged with per-file SHA256 hashes.

The official Xiaomi `zeus-s-oss` branch and Linux v6.12 SM8450 DTS were found.
They do not prove the user's running firmware/panel. All device-observed manifest
fields remain null. Six Chinese/community/registry destinations were blocked by
proxy CONNECT 403; proposed domain additions were saved to the environment draft.
Their runtime access has not been changed or revalidated.

The environment draft now saves `install_script`, `start_skill` and six custom
research domains. Review and save in environment settings, then Publish to make the
prepared snapshot/configuration available for future tasks. Draft persistence is
confirmed; runtime network application, publication and new-task restoration are
not claimed. Existing repository membership was preserved.

Next priorities:

1. Collect the smallest read-only report using `tools/adb-diagnostics/collect.py`
   from a host with authorized ADB access; map exact firmware, LCD and touch evidence.
2. Extend the initial SM8450 common audit into UniXNU ArmCpu/ArmDTPlatform build
   dependencies; resolve licensing and trace every board value to source plus device.
3. Establish a licensed/reproducible XNU kernel build path. The audited HakiOS path
   depends on SDK/header distributions not installed here; see `docs/xnu-porting.md`.
4. Implement verified ADT/boot-argument and kernel platform integration, then obtain
   separate authorization for one recoverable device test. No current result warrants
   claiming shim execution, kernel entry, root mount, iOS startup or dual boot on zeus.
