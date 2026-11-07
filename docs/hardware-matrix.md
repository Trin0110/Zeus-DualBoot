# Device evidence matrix

| Property | Evidence | Status |
| --- | --- | --- |
| Xiaomi 12 Pro / zeus / SM8450 / Adreno 730 / 256 GB | User specification | User-reported, not hardware-verified here |
| Aftermarket LCD and touch work on Android | User specification | User-reported |
| Android version/build, running kernel | None from this phone | UNKNOWN |
| Bootloader lock, A/B slot/partition layout, AVB/rollback | None from this phone | UNKNOWN |
| Panel/controller/bridge, DSI lanes/timing/DSC, reset/regulators | None from this phone | UNKNOWN |
| Touch controller and firmware | None from this phone | UNKNOWN |
| Valid bootloader framebuffer, RAM/reservations/GIC/timer | None from this phone | UNKNOWN |
| Temporary boot, UEFI, persistent secondary storage, recovery | None from this phone | UNKNOWN |

`adb devices` executed in the cloud and returned an empty device list. No physical
diagnostics, boot, flash, partition write or reboot was performed. Reports from a
different zeus unit must retain their provenance and cannot fill this matrix as
VERIFIED_ON_HARDWARE. The manifest separately records user reports and observations.
