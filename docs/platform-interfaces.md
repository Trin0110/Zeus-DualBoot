# Platform library contracts

`make` produces `build/libzeus-host.a`. `make cross-check` compiles the same four
translation units as freestanding AArch64 ELF objects. Neither output is linked
into XNU. No MMIO register values, physical mappings or firmware callbacks exist.

* Display requires a caller-owned accessible mapping, known pixel format, size and
  stride. Validation protects buffer arithmetic, coordinates and padding. It does
  not validate page tables, cache coherency or active scanout. Missing power/mode/
  brightness/suspend/resume callbacks return UNSUPPORTED; backend errors propagate.
* Touch converts complete backend events into checked contact state. Coordinates,
  pressure and slot range must be within discovered capabilities. A move/up requires
  a previous down, and repeated down is refused. Backends must return NO_EVENT for
  no complete event, not fabricate input. No backend is shipped.
* Memory validation rejects invalid/overflowing RAM ranges, overlapping RAM and
  allocations crossing RAM windows or any reservation. Overlapping exclusions are
  allowed. The caller must supply verified complete reservations; unknown is not an
  empty reservation set.
* Storage exposes a bounded read-only logical view with no write callback. Relative
  reads must fit the selected block interval and output buffer. Absent backends
  return UNSUPPORTED. No UFS/controller initialization or partition selection is
  provided. The caller must still audit a backend for actual read-only behavior.

All C tests use synthetic RAM, addresses, event structures and block callbacks.
They run with ASan/UBSan and compiler warnings as errors. They establish HOST_TESTED
contracts only; hardware integration remains BLOCKED.
