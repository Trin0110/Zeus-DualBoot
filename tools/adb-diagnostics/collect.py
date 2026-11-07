#!/usr/bin/env python3
"""Read-only metadata collection. Raw device output is never written to disk."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import selectors
import subprocess
import time

LIMIT = 512 * 1024
PROPERTIES = (
    "ro.product.device", "ro.product.model", "ro.soc.model", "ro.board.platform",
    "ro.build.version.release", "ro.build.version.sdk", "ro.build.version.security_patch",
    "ro.build.display.id", "ro.boot.flash.locked", "ro.boot.verifiedbootstate",
    "ro.boot.slot_suffix",
)
# Every shell string is a literal. No serial, property or path from device output
# is interpolated into a shell command. getevent -lp enumerates capabilities only.
PROBES = {
    "kernel": "uname -r",
    "screen_size": "wm size",
    "display_modes": "dumpsys display",
    "framebuffer_modes": "cat /sys/class/graphics/fb0/modes /sys/class/graphics/fb0/virtual_size /sys/class/graphics/fb0/bits_per_pixel",
    "drm_modes": "cat /sys/class/drm/card*-*/modes",
    "input": "getevent -lp",
    "backlight": "for p in /sys/class/backlight/*; do echo ${p##*/}; cat \"$p/max_brightness\" \"$p/brightness\"; done",
    "panel_nodes": "find /sys/firmware/devicetree/base -maxdepth 8 -type d",
    "panel_compatible": "find /sys/firmware/devicetree/base -maxdepth 8 -type f -name compatible -path '*panel*' -exec cat {} \\;",
    "display_bindings": "ls -l /sys/class/graphics/fb0/device/driver /sys/class/drm/card0/device/driver",
    "kernel_display_summary": "dmesg",
}


class _PipeReader:
    """Wait for an anonymous pipe without blocking past the command deadline.

    Windows selectors accept sockets, not subprocess pipes. PeekNamedPipe also
    supports anonymous pipes and lets us read only bytes already available. The
    stream must be unbuffered and have exactly one reader. No reader threads or
    raw-output temporary files are needed, even if a child inherits the pipe.
    """
    def __init__(self, stream):
        self.stream = stream
        self.selector = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            import msvcrt
            self.ctypes = ctypes
            self.available = wintypes.DWORD()
            self.handle = wintypes.HANDLE(msvcrt.get_osfhandle(stream.fileno()))
            self.peek = ctypes.WinDLL("kernel32", use_last_error=True).PeekNamedPipe
            self.peek.argtypes = (wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
                                  wintypes.LPVOID, ctypes.POINTER(wintypes.DWORD),
                                  wintypes.LPVOID)
            self.peek.restype = wintypes.BOOL
        else:
            self.selector = selectors.DefaultSelector()
            try:
                self.selector.register(stream, selectors.EVENT_READ)
            except BaseException:
                self.selector.close()
                raise

    def read(self, maximum, deadline):
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            if self.selector is not None:
                if self.selector.select(remaining):
                    return os.read(self.stream.fileno(), maximum)
            else:
                if not self.peek(self.handle, None, 0, None,
                                 self.ctypes.byref(self.available), None):
                    error = self.ctypes.get_last_error()
                    if error == 109:  # ERROR_BROKEN_PIPE: all writers closed.
                        return b""
                    raise self.ctypes.WinError(error)
                if self.available.value:
                    return os.read(self.stream.fileno(), min(maximum, self.available.value))
                time.sleep(min(.01, remaining))

    def close(self):
        if self.selector is not None:
            self.selector.close()


def run_bounded(argv, timeout=8, limit=LIMIT):
    """Bound memory and runtime, combining stderr only in ephemeral memory."""
    if not math.isfinite(timeout) or timeout <= 0 or type(limit) is not int or limit < 0:
        raise ValueError("timeout must be finite and positive; limit must be a nonnegative integer")
    try:
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, bufsize=0, shell=False)
    except OSError:
        return "unavailable", ""
    data = bytearray()
    status = "ok"
    deadline = time.monotonic() + timeout
    reader = None
    try:
        reader = _PipeReader(proc.stdout)
        while True:
            chunk = reader.read(min(65536, limit + 1 - len(data)), deadline)
            if chunk is None:
                status = "timeout"
                break
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > limit:
                status = "output_limit"
                break
        if status == "ok":
            code = proc.wait(timeout=max(0, deadline - time.monotonic()))
            if code:
                status = "inaccessible"
    except subprocess.TimeoutExpired:
        status = "timeout"
    except OSError:
        status = "inaccessible"
    finally:
        # Reap our local command on every exit, including interrupted reads.
        # Closing the unbuffered pipe cannot wait on a blocked reader thread.
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        if reader is not None:
            reader.close()
        proc.stdout.close()
    text = bytes(data[:limit]).decode("utf-8", "replace")
    if status == "ok" and re.search(r"permission denied|not permitted|not found|no such file", text, re.I):
        status = "inaccessible"
    return status, text


def redact(text, identifiers=()):
    for value in sorted(set(identifiers), key=len, reverse=True):
        if value:
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    text = re.sub(r"(?i)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", "[MAC]", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP]", text)
    text = re.sub(r"(?i)\b[0-9a-f]{0,4}:(?:[0-9a-f:]{2,})\b", "[IP]", text)
    text = re.sub(r"(?i)\b(?:serial(?:no)?|imei|imsi|android_id)\s*[:=]\s*\S+", "[IDENTIFIER]", text)
    return text


def extract(name, text, identifiers=()):
    """Only persist known structural fields; never forward arbitrary log lines."""
    text = redact(text, identifiers)
    if name.startswith("property:"):
        # Properties themselves are allowlisted, and length/control characters bounded.
        value = text.strip()
        return value[:160] if re.fullmatch(r"[\w .+:/()\[\],-]{1,160}", value) else None
    if name == "kernel":
        match = re.fullmatch(r"[\w.+-]{1,160}", text.strip())
        return match.group(0) if match else None
    if name in ("screen_size", "framebuffer_modes", "drm_modes"):
        return sorted(set(re.findall(r"\b\d{2,5}[x,]\d{2,5}(?:p?-\d{2,3})?\b", text)))[:64]
    if name == "display_modes":
        # Display dumps may include app/window names; retain numerical mode fields only.
        modes = re.findall(r"width[= ]+(\d{2,5})[, ]+height[= ]+(\d{2,5})[, ]+(?:fps|refreshRate)[= ]+([0-9.]+)", text)
        return [{"width": int(w), "height": int(h), "refresh_hz": float(f)}
                for w, h, f in modes[:128] if re.fullmatch(r"\d+(?:\.\d+)?", f)]
    if name == "input":
        # Do not save arbitrary device names (Bluetooth names can identify people).
        controllers = sorted(set(re.findall(r"(?i)\b(?:goodix|focaltech|synaptics|novatek|fts|sec_touch|atmel|himax)[\w.-]*", text)))
        axes = []
        for line in text.splitlines():
            m = re.search(r"\b(ABS_[A-Z0-9_]+)\s*:\s*value\s+(-?\d+),\s*min\s+(-?\d+),\s*max\s+(-?\d+)", line)
            if m:
                axes.append({"axis": m[1], "min": int(m[3]), "max": int(m[4])})
        return {"controller_candidates": controllers, "axes": axes[:256],
                "note": "enumerated capabilities, not live input; candidates are not confirmed controller identities"}
    if name == "kernel_display_summary":
        keywords = ("dsi", "dsc", "panel", "drm", "backlight", "touch", "smmu")
        return {word: sum(bool(re.search(r"\b" + word + r"\b", line, re.I))
                          for line in text.splitlines()) for word in keywords}
    if name == "backlight":
        return {"numeric_values": [int(s) for s in text.splitlines() if re.fullmatch(r"\d{1,9}", s)][:32],
                "note": "max/current pairs in sysfs order when available; power sequencing remains unknown"}
    if name == "panel_compatible":
        return sorted(set(re.findall(r"(?:qcom|samsung|boe|tianma|novatek|himax|jdi),[a-zA-Z0-9._-]+", text)))[:64]
    if name == "panel_nodes":
        # Retain only node basenames; parent paths and unrelated nodes are discarded.
        return sorted(set(node.rsplit("/", 1)[-1] for node in text.splitlines()
                          if re.fullmatch(r"[a-zA-Z0-9_./@,-]+", node) and
                          re.search(r"(?i)(panel|display|dsi|dsc|touch|backlight)", node.rsplit("/", 1)[-1])))[:128]
    if name == "display_bindings":
        return sorted(set(re.findall(r"/drivers/([a-zA-Z0-9_.-]+)", text)))[:32]
    raise ValueError("unknown probe")


def collect(adb="adb", serial=None, runner=run_bounded):
    status, listing = runner([adb, "devices"])
    if status != "ok":
        raise ValueError("ADB unavailable; install platform-tools and check the local ADB server")
    devices = []
    identifiers = []
    for line in listing.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[1] in ("device", "unauthorized", "offline", "recovery", "sideload"):
            identifiers.append(fields[0])
            if fields[1] == "device":
                devices.append(fields[0])
    if serial is None:
        if len(devices) != 1:
            raise ValueError("Exactly one authorized Android device required; use --serial when multiple are connected")
        serial = devices[0]
    if serial not in devices:
        raise ValueError("Selected device is not an authorized Android device")
    identifiers.append(serial)
    result = {"schema_version": 1, "collected_at": datetime.now(timezone.utc).isoformat(),
              "status": "READ_ONLY_METADATA", "device_serial": "[REDACTED]", "probes": {},
              "limitations": ["No raw logs retained; display log counts only", "DSI timings, DSC PPS, power/reset sequences and framebuffer ownership require separate source/DT analysis",
                              "Reported metadata cannot verify replacement LCD hardware or XNU compatibility"]}
    commands = {**{"property:" + p: "getprop " + p for p in PROPERTIES}, **PROBES}
    for name, command in commands.items():
        status, output = runner([adb, "-s", serial, "shell", command])
        result["probes"][name] = {"status": status,
            "data": extract(name, output, identifiers) if status == "ok" else None}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", default="adb", help="path to trusted adb executable")
    parser.add_argument("--serial", help="local selector; never persisted")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = collect(args.adb, args.serial)
        # Exclusive creation protects previous reports. Only sanitized structure is serialized.
        # POSIX gets owner-only permissions at creation. Windows uses inherited
        # directory ACLs; chmod(0600) does not establish a private Windows ACL.
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    except (ValueError, OSError) as exc:
        # Avoid echoing filenames/device output (they may contain personal data).
        print(json.dumps({"status": "FAILED", "reason": str(exc) if isinstance(exc, ValueError) else "Cannot create report; output must be a new file in an existing directory"}))
        return 1
    print("Sanitized read-only metadata report created. Review it locally before sharing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
