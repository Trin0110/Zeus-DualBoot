import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("collector", Path(__file__).resolve().parents[1] / "tools/adb-diagnostics/collect.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class DiagnosticsTests(unittest.TestCase):
    def python(self, source, **kwargs):
        return collector.run_bounded([sys.executable, "-c", source], **kwargs)

    def test_exact_limit_empty_and_one_byte_over(self):
        for size, limit, expected in ((0, 0, "ok"), (1, 0, "output_limit"),
                                       (4096, 4096, "ok"), (4097, 4096, "output_limit")):
            with self.subTest(size=size, limit=limit):
                status, output = self.python(f"import os; os.write(1, b'x' * {size})", limit=limit)
                self.assertEqual(status, expected)
                self.assertEqual(len(output), min(size, limit))

    def test_stderr_flood_is_bounded_and_reaped(self):
        start = time.monotonic()
        children = []
        real_popen = subprocess.Popen
        def spawn(*args, **kwargs):
            self.assertFalse(kwargs["shell"])
            child = real_popen(*args, **kwargs)
            children.append(child)
            return child
        with mock.patch.object(collector.subprocess, "Popen", side_effect=spawn):
            status, output = self.python("import os\nwhile True: os.write(2, b'x' * 8192)", limit=1234)
        self.assertEqual(status, "output_limit")
        self.assertEqual(len(output), 1234)
        self.assertLess(time.monotonic() - start, 5)
        # Assert the local process has actually exited, not just that the read returned.
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)

    def test_silent_process_timeout_and_closed_pipe_timeout(self):
        for prefix in ("", "os.close(1); os.close(2); "):
            with self.subTest(prefix=prefix):
                start = time.monotonic()
                self.assertEqual(self.python("import os,time; " + prefix + "time.sleep(10)", timeout=.2)[0], "timeout")
                self.assertLess(time.monotonic() - start, 3)

    def test_short_writes_and_invalid_utf8(self):
        status, output = self.python("import os,time; os.write(1,b'hello'); time.sleep(.05); os.write(2,b'\\xff world')")
        self.assertEqual((status, output), ("ok", "hello\ufffd world"))

    def test_pipe_error_is_graceful_and_child_reaped(self):
        children = []
        real_popen = subprocess.Popen
        def spawn(*args, **kwargs):
            child = real_popen(*args, **kwargs)
            children.append(child)
            return child
        with mock.patch.object(collector.subprocess, "Popen", side_effect=spawn), \
             mock.patch.object(collector._PipeReader, "read", side_effect=OSError("private device output")):
            status, output = self.python("import time; time.sleep(10)")
        self.assertEqual((status, output), ("inaccessible", ""))
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)

    def test_invalid_limits_do_not_spawn(self):
        with mock.patch.object(collector.subprocess, "Popen") as spawn:
            for kwargs in ({"timeout": 0}, {"timeout": float('inf')}, {"timeout": float('nan')},
                           {"limit": -1}, {"limit": 1.5}, {"limit": True}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    collector.run_bounded([sys.executable], **kwargs)
            spawn.assert_not_called()

    @unittest.skipUnless(os.name == "nt", "native Windows pipe regression")
    def test_windows_does_not_select_pipes(self):
        with mock.patch.object(collector.selectors, "DefaultSelector", side_effect=AssertionError("Windows pipe selector used")):
            self.assertEqual(self.python("print('native Windows pipe')"), ("ok", "native Windows pipe\r\n"))

    @unittest.skipUnless(os.environ.get("ZEUS_TEST_ADB"), "official platform-tools smoke test enabled by CI")
    def test_official_platform_tools_executable(self):
        status, text = collector.run_bounded([os.environ["ZEUS_TEST_ADB"], "version"])
        self.assertEqual(status, "ok")
        self.assertIn("Android Debug Bridge version", text)

    def test_unicode_spaced_paths_and_literal_arguments(self):
        with tempfile.TemporaryDirectory(prefix="zeus pipe ") as tmp:
            script = Path(tmp) / "ทดสอบ pipe.py"
            script.write_text("import json,sys; print(json.dumps(sys.argv[1:]))", encoding="utf-8")
            literal = 'device; echo forbidden & "quote"'
            status, output = collector.run_bounded([sys.executable, str(script), literal])
            self.assertEqual(status, "ok")
            self.assertEqual(json.loads(output), [literal])

    def test_report_unicode_path_privacy_and_no_overwrite(self):
        def fake(cmd):
            if cmd[-1] == "devices":
                return "ok", "TEST_SERIAL_ONLY device\r\n"
            if cmd[-1] == "dmesg":
                return "ok", "panel TEST_SERIAL_ONLY alice@example.org 10.2.3.4"
            return "inaccessible", "private failure TEST_SERIAL_ONLY"
        report = collector.collect(runner=fake)
        with tempfile.TemporaryDirectory(prefix="zeus report ") as tmp:
            output = Path(tmp) / "ข้อมูล จอ.json"
            with mock.patch.object(collector, "collect", return_value=report), mock.patch("builtins.print"):
                self.assertEqual(collector.main(["--output", str(output)]), 0)
                original = output.read_bytes()
                self.assertEqual(collector.main(["--output", str(output)]), 1)
                self.assertEqual(output.read_bytes(), original)
            text = original.decode('utf-8')
            self.assertNotIn("TEST_SERIAL_ONLY", text)
            self.assertNotIn("alice@example.org", text)
            self.assertNotIn("10.2.3.4", text)
            self.assertEqual(json.loads(text)["status"], "READ_ONLY_METADATA")
            if os.name != "nt":
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)

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
