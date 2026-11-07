# Read-only collector contract

Run `python3 tools/adb-diagnostics/collect.py --output NEW_REPORT.json` on the host
that can see an already-authorized Android device. Python 3.10+ and ADB are sufficient;
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
Reports are exclusively created and existing reports are not overwritten. POSIX
uses mode 0600 at creation. Windows inherits the destination directory's ACLs:
use your own user-profile directory, not a shared/public folder. `chmod(0600)`
would not enforce an owner-only Windows ACL and is no longer used for that purpose.

## Windows 10/11 (PowerShell)

Install Python 3.10+ (3.14 recommended) from [python.org](https://www.python.org/downloads/windows/)
with the `py` launcher, and [Git for Windows](https://git-scm.com/download/win).
Use Google's [official Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools)
Windows distribution. No WSL, C compiler, Python packages, root or administrator
PowerShell is needed for the collector. The shell commands in `PROBES` run on
Android through `adb.exe shell`, not in PowerShell or `cmd.exe`.

Run this once to obtain/update the existing project and download official tools:

```powershell
$ErrorActionPreference = 'Stop'
py -3 --version
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.10+ with the py launcher first.' }
$ZeusRoot = Join-Path $env:LOCALAPPDATA 'Zeus-DualBoot'
$ZeusRepo = Join-Path $ZeusRoot 'source'
$ZeusTools = Join-Path $ZeusRoot 'android-tools'
New-Item -ItemType Directory -Force -Path $ZeusRoot | Out-Null
if (Test-Path (Join-Path $ZeusRepo '.git')) {
    git -C $ZeusRepo pull --ff-only origin main
} else {
    git clone --branch main https://github.com/Trin0110/Zeus-DualBoot.git $ZeusRepo
}
if ($LASTEXITCODE -ne 0) { throw 'Git update failed; resolve local changes before continuing.' }
$ZeusZip = Join-Path $ZeusRoot 'platform-tools.zip'
# PowerShell 5.1: use TLS 1.2 while keeping normal certificate verification.
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile $ZeusZip
Expand-Archive -LiteralPath $ZeusZip -DestinationPath $ZeusTools -Force
$ZeusAdb = Join-Path $ZeusTools 'platform-tools\adb.exe'
& $ZeusAdb version
if ($LASTEXITCODE -ne 0) { throw 'Official adb.exe could not start.' }
Set-Location $ZeusRepo
py -3 -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Host tests failed; do not collect yet.' }
```

Connect the Xiaomi 12 Pro by USB with USB debugging already enabled, unlock its
screen and accept its USB debugging RSA prompt for your own computer. Then run:

```powershell
$ZeusRoot = Join-Path $env:LOCALAPPDATA 'Zeus-DualBoot'
$ZeusRepo = Join-Path $ZeusRoot 'source'
$ZeusAdb = Join-Path $ZeusRoot 'android-tools\platform-tools\adb.exe'
& $ZeusAdb devices
# Continue when exactly one intended phone is listed with status "device".
$ZeusReports = Join-Path $ZeusRoot 'reports'
New-Item -ItemType Directory -Force -Path $ZeusReports | Out-Null
$ZeusReport = Join-Path $ZeusReports ("zeus-diagnostics-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
py -3 (Join-Path $ZeusRepo 'tools\adb-diagnostics\collect.py') --adb $ZeusAdb --output $ZeusReport
if ($LASTEXITCODE -ne 0) { throw 'Collection failed. No successful report should be assumed.' }
Get-Content -LiteralPath $ZeusReport -Raw -Encoding UTF8
```

For multiple authorized devices, add `--serial 'THE_LOCAL_ADB_SELECTOR'` to the
collector command after checking `adb devices` locally. Do not share that listing;
the collector removes selectors from its JSON. `unauthorized` means the phone has
not accepted the RSA prompt; `offline` means ADB has no usable connection. If no
device appears, check the USB data cable and the appropriate manufacturer's Windows
ADB driver. These conditions do not require bootloader unlocking or firmware changes.

Restricted Android interfaces may report `inaccessible`; this is a successful
partial metadata report, not a reason to enable root. Review the JSON before sharing.

## Windows implementation and verification

Windows uses `PeekNamedPipe` on the subprocess's unbuffered anonymous pipe to read
only available bytes; POSIX uses selectors. Windows selectors support sockets but
not these pipes. Both implementations share the same deadline, byte budget, process
cleanup and redaction. No worker threads or raw-output temporary files are used.

GitHub Actions runs native subprocess tests on `windows-2022` and `windows-2025`,
each with Python 3.10 and 3.14. CI downloads Google's official Windows Platform Tools
into a path containing spaces and calls `adb.exe version` through `run_bounded`.
These runners use Windows Server, not consumer Windows 10/11, and do not have a
phone attached. This validates the Windows APIs/process path and metadata handling,
not actual Xiaomi USB connectivity or panel compatibility. The Windows-only test
fails if the collector attempts to construct a selector for a subprocess pipe.

Host tests use fake ADB responses, including multi-device/unauthorized states,
private log strings, malformed data, nonzero exit, silent/closed-pipe timeouts,
exact/oversized byte limits, stderr floods, Unicode paths, UTF-8 decoding, cleanup
and exclusive report creation. They validate collector behavior, not Android shell compatibility. No real
device report has been collected yet.
