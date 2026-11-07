import copy
import json
from pathlib import Path
import struct
import unittest
from boot.config import validate, main
from boot.image import inspect_header
from contextlib import redirect_stdout
import io

ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "devices/zeus/device.json").read_text())

    def test_research_config_is_valid_but_blocked(self):
        errors, blockers = validate(self.manifest)
        self.assertEqual(errors, [])
        self.assertGreater(len(blockers), 10)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(ROOT / "devices/zeus/device.json"), "--require-ready"]), 2)

    def test_policy_changes_rejected(self):
        for key, value in (("default_os", "ios"), ("allow_device_writes", True),
                           ("allow_reboot", True), ("preserve_userdata", False), ("allow_reboot", 0)):
            with self.subTest(key=key, value=value):
                doc = copy.deepcopy(self.manifest)
                doc["policy"][key] = value
                self.assertTrue(validate(doc)[0])

    def test_invented_hardware_and_wrong_board(self):
        self.manifest["observed"]["panel_controller"] = "guessed-controller"
        self.assertTrue(validate(self.manifest)[0])
        self.manifest["target"]["soc"] = "SM8550"
        self.assertTrue(validate(self.manifest)[0])

    def test_invalid_types(self):
        for value in ([], None, 3, {"target": None, "observed": False, "policy": []}):
            self.assertTrue(validate(value)[0])

    def test_evidence_cannot_enable_execution(self):
        for field in self.manifest["observed"]:
            self.manifest["observed"][field] = "test fixture"
            self.manifest["evidence"].append({"field": field, "artifact": "fixture", "status": "VERIFIED_ON_HARDWARE"})
        self.assertTrue(validate(self.manifest)[1])


class ImageTests(unittest.TestCase):
    def header(self, version=3):
        h = bytearray(4096)
        h[:8] = b"ANDROID!"
        struct.pack_into("<4I", h, 8, 8192, 256, 0, 1580 if version == 3 else 1584)
        struct.pack_into("<I", h, 40, version)
        return h

    def test_v3_sections(self):
        result = inspect_header(self.header(), 16384)
        self.assertEqual(result["sections"]["ramdisk"], {"offset": 12288, "size": 256})
        self.assertFalse(result["signature_verified"])

    def test_v4_signature(self):
        header = self.header(4)
        struct.pack_into("<I", header, 1580, 4096)
        self.assertEqual(inspect_header(header, 20480)["sections"]["signature"]["offset"], 16384)
        with self.assertRaises(ValueError):
            inspect_header(header, 16384)

    def test_truncated_or_invalid(self):
        h = self.header()
        for size in (0, 40, 1579):
            with self.assertRaises(ValueError):
                inspect_header(h[:size], 16384)
        with self.assertRaises(ValueError):
            inspect_header(h, 8192)
        for offset, value in ((40, 2), (20, 40), (24, 1), (8, 0), (8, 0xffffffff)):
            invalid = h.copy()
            struct.pack_into("<I", invalid, offset, value)
            with self.assertRaises(ValueError):
                inspect_header(invalid, 16384)


if __name__ == "__main__":
    unittest.main()
