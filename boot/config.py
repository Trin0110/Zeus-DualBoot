"""Validate research manifests; acceptance never authorizes a hardware operation."""
import argparse
import json
from pathlib import Path

OBSERVATIONS = frozenset((
    "device_identity android_version firmware_build bootloader_unlocked boot_image_version "
    "temporary_boot_supported partition_layout memory_map reserved_memory gic timer_frequency "
    "uefi_handoff panel_controller touch_controller framebuffer ufs recovery_method"
).split())


def validate(document):
    errors, blockers = [], []
    if not isinstance(document, dict):
        return ["manifest must be an object"], ["hardware execution unavailable"]
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        errors.append("schema_version must be 1")
    target = document.get("target")
    if not isinstance(target, dict):
        errors.append("target must be an object")
    else:
        for key, value in {"codename": "zeus", "soc": "SM8450", "architecture": "aarch64"}.items():
            if target.get(key) != value:
                errors.append(f"target.{key} must be {value}")
    policy = document.get("policy")
    expected = {"default_os": "android", "allow_device_writes": False,
                "allow_reboot": False, "preserve_userdata": True}
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
    else:
        for key, value in expected.items():
            if type(policy.get(key)) is not type(value) or policy.get(key) != value:
                errors.append(f"policy.{key} must remain {value!r}")
    evidence = document.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        evidence = []
    observed = document.get("observed")
    if not isinstance(observed, dict):
        errors.append("observed must be an object")
        observed = {}
    for key in sorted(OBSERVATIONS):
        if key not in observed:
            errors.append(f"missing observed.{key}; use null when unknown")
        value = observed.get(key)
        if value is None:
            blockers.append(f"UNKNOWN: {key}")
        elif not any(isinstance(e, dict) and e.get("field") == key and
                     isinstance(e.get("artifact"), str) and e["artifact"].strip() and
                     e.get("status") == "VERIFIED_ON_HARDWARE" for e in evidence):
            errors.append(f"observed.{key} needs hardware evidence metadata")
    # This project intentionally has no hardware execution backend. Even a filled
    # manifest is not sufficient proof: evidence needs independent review.
    blockers.append("No validated zeus boot backend; evidence review and explicit device-test approval required")
    return errors, blockers


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.manifest.read_text())
        errors, blockers = validate(document)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}))
        return 1
    print(json.dumps({"status": "INVALID" if errors else "VALID_RESEARCH_CONFIG",
                      "errors": errors, "hardware_status": "BLOCKED", "blockers": blockers}, indent=2))
    return 1 if errors else 2 if args.require_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
