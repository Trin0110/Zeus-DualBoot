# Device testing gate

No device-changing operation is authorized by the present work. Do not run upstream
phone/install/flash targets. The researched iOSPlus10 bootlog implementation writes
userdata without its normal root-write switch, and HakiOS's loader has block-write
paths. A temporary boot is not automatically non-destructive.

Before requesting one concrete future hardware action, establish the exact device
and firmware, actual lock/boot requirements, complete tested backups, matching stock
firmware and checksums, an evidence-backed stock recovery route, data-loss/rollback
risks and the full reviewed command/image. Obtain explicit approval for that action.
Unlocking may erase userdata. EDL availability or a successful recovery on another
Xiaomi model is not proof of recovery here.

The smallest currently useful device action is the supplied read-only metadata
collector. It neither needs nor attempts root. Unreadable information should stay
unknown until a separately scoped source/firmware investigation can resolve it.
