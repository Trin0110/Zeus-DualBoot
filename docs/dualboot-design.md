# Android-preserving dual boot

Android remains the default. The project currently has no boot selector, secondary
installation or persistence backend. A/B slots are Android update/recovery resources,
not automatically spare space for another OS. Inactive slot validity, rollback
indices, AVB, dynamic partitions and firmware dependencies must be known first.

| Approach | Prerequisite and current conclusion |
| --- | --- |
| Temporary boot | Exact bootloader support and image ABI must be verified. Not executed; current support UNKNOWN. Temporary loading can still run code that writes storage. |
| UEFI handoff | SM8450 firmware plus zeus board initialization and shutdown/return behavior. Other OnePlus/SM8550 firmware is not sufficient. |
| Dedicated boot manager | Verified Android chain loading, default Android selection, failure counter, watchdog and recovery handling. Persistent counter writes need their own safe storage design. |
| Persistent secondary OS | Explicit independent writable backing store, encryption/ownership boundaries, firmware/rollback compatibility and recovery. No layout selected. |

Free space inside encrypted Android userdata is not an independent partition. A
file-backed secondary filesystem would still require a proven access path through
Android filesystem/encryption layers and safe concurrent ownership; reserving raw
sectors inside userdata risks corruption. No partition modification is proposed.

Required evidence progresses separately: shim execution -> XNU entry -> kernel
initialization -> root filesystem -> iOS userland -> display/touch -> persistence ->
reboot/recovery -> both OSes independently booted. All are currently BLOCKED or
UNKNOWN on physical zeus. No current upstream audit establishes Android-preserving
persistent dual boot for this device.
