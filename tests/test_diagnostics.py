import importlib.util
import json
from pathlib import Path
import sys
import unittest

spec = importlib.util.spec_from_file_location("collector", Path(__file__).resolve().parents[1] / "tools/adb-diagnostics/collect.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class DiagnosticsTests(unittest.TestCase):
    def test_selection(self):
        for listing in ("", "secret unauthorized", "a device\nb device", "secret offline"):
            with self.subTest(listing=listing), self.assertRaises(ValueError):
                collector.collect(runner=lambda cmd: ("ok", listing))

    def test_safe_commands_and_private_output(self):
        calls = []
        def fake(cmd):
            calls.append(cmd)
            if cmd[-1] == "devices":
                return "ok", "List of devices attached\nSECRET123 device\n"
            if cmd[-1] == "getevent -lp":
                return "ok", 'name: "Alice Bluetooth SECRET123"\nABS_MT_POSITION_X : value 0, min 0, max 1440, fuzz 0\n'
            if cmd[-1] == "dmesg":
                return "ok", "panel secret mail@example.com 10.2.3.4 aa:bb:cc:dd:ee:ff\n"
            return "inaccessible", "SECRET123 permission denied"
        result = collector.collect(runner=fake)
        report = json.dumps(result)
        for value in ("SECRET123", "Alice", "mail@example.com", "10.2.3.4", "aa:bb:cc:dd:ee:ff"):
            self.assertNotIn(value, report)
        self.assertEqual(result["probes"]["input"]["data"]["axes"][0]["max"], 1440)
        self.assertEqual(result["probes"]["kernel"]["status"], "inaccessible")
        allowed = set(collector.PROBES.values()) | {"getprop " + p for p in collector.PROPERTIES}
        self.assertTrue(all(c[-1] in allowed for c in calls[1:]))
        self.assertTrue(all(c[1:4] == ["-s", "SECRET123", "shell"] for c in calls[1:]))

    def test_serial_is_never_shell_interpolated(self):
        commands = []
        serial = "bad;reboot"
        def fake(cmd):
            commands.append(cmd)
            return ("ok", serial + " device") if cmd[-1] == "devices" else ("ok", "")
        collector.collect(serial=serial, runner=fake)
        self.assertTrue(all(serial not in c[-1] for c in commands[1:]))

    def test_redaction(self):
        text = collector.redact("SERIAL imei=1234 bob@example.org 192.168.1.1 aa:bb:cc:dd:ee:ff 2001:db8::1", ["SERIAL"])
        for secret in ("SERIAL", "1234", "bob@example.org", "192.168.1.1", "aa:bb", "2001:db8"):
            self.assertNotIn(secret, text)

    def test_output_limit_timeout_and_exit_status(self):
        status, text = collector.run_bounded([sys.executable, "-c", "print('x'*200000)"], limit=100)
        self.assertEqual(status, "output_limit")
        self.assertLessEqual(len(text), 100)
        self.assertEqual(collector.run_bounded([sys.executable, "-c", "import time; time.sleep(10)"], timeout=.05)[0], "timeout")
        self.assertEqual(collector.run_bounded([sys.executable, "-c", "raise SystemExit(3)"])[0], "inaccessible")
        self.assertEqual(collector.run_bounded(["/no/such/adb"])[0], "unavailable")

    def test_empty_and_malformed_metadata(self):
        self.assertIsNone(collector.extract("property:ro.product.device", "secret\nsecond line"))
        self.assertEqual(collector.extract("drm_modes", "1440x3200\n1440x3200\n"), ["1440x3200"])
        self.assertEqual(collector.extract("panel_compatible", "qcom,mdss-dsi-panel\x00private"), ["qcom,mdss-dsi-panel"])
        self.assertEqual(collector.extract("display_modes", "private name width=1440, height=3200, fps=60.0"),
                         [{"width": 1440, "height": 3200, "refresh_hz": 60.0}])


if __name__ == "__main__":
    unittest.main()
