# Read-only collector contract

Run `python3 tools/adb-diagnostics/collect.py --output NEW_REPORT.json` on the host
that can see an already-authorized Android device. Python 3 and ADB are sufficient;
there are no Python dependencies. `--adb` chooses a trusted local executable;
`--serial` selects among devices and is passed as a separate process argument.
No automatic network connection, pairing, USB authorization or root is attempted.

Probes are literal allowlisted shell commands: selected `getprop`, `uname -r`,
`wm size`, `dumpsys display`, graphics/DRM modes, sysfs backlight, DT panel names
and compatible strings, driver symlink names, `getevent -lp`, and `dmesg`.
`getevent -lp` reports capabilities and exits; no key/touch event stream is recorded.
No `su`, full getprop, logcat, file pull, block reads/writes, reboot or fastboot command
is used. Rootless vendor restrictions are normal and appear as `inaccessible`.

Each process has an 8-second limit and a 512 KiB output cap. Timeout/truncated/failed
probes discard their data. The JSON stores only extracted fields; raw stdout/stderr
is transient memory. Device selectors, labeled identifiers, email/MAC/IP patterns
are redacted. Arbitrary input device names and raw display/log lines are omitted.
All probe statuses are retained, and missing fields must remain UNKNOWN.

Selected firmware/model properties and vendor node names still describe the device;
review the report before sharing. Pattern redaction cannot promise to recognize
every custom identifier a vendor puts inside otherwise normal hardware metadata.
The output is exclusively created with mode 0600 and existing reports are not overwritten.

Host tests use fake ADB responses, including multi-device/unauthorized states,
private log strings, malformed data, nonzero exit, subprocess timeout and oversized
output. They validate collector behavior, not Android shell compatibility. No real
device report has been collected yet.
