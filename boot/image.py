"""Inspect Android boot v3/v4 files offline; never load or write device images.

Layout reference: AOSP system/tools/mkbootimg/include/bootimg/bootimg.h.
Legacy v0-v2 and vendor_boot are explicitly unsupported, not guessed.
"""
import argparse
import json
from pathlib import Path
import struct


def inspect_header(header, file_size):
    if len(header) < 44 or header[:8] != b"ANDROID!":
        raise ValueError("not a complete Android boot header")
    kernel, ramdisk, os_version, header_size = struct.unpack_from("<4I", header, 8)
    version = struct.unpack_from("<I", header, 40)[0]
    if version not in (3, 4):
        raise ValueError(f"unsupported boot header version {version}; only v3/v4 are implemented")
    expected = 1580 if version == 3 else 1584
    if header_size != expected or len(header) < expected:
        raise ValueError("invalid or truncated header size")
    if any(header[24:40]):
        raise ValueError("reserved header fields must be zero")
    if not kernel:
        raise ValueError("kernel payload is empty")
    page = 4096
    align = lambda n: (n + page - 1) // page * page
    sections = {"kernel": {"offset": page, "size": kernel},
                "ramdisk": {"offset": page + align(kernel), "size": ramdisk}}
    end = page + align(kernel) + align(ramdisk)
    if version == 4:
        signature = struct.unpack_from("<I", header, 1580)[0]
        sections["signature"] = {"offset": end, "size": signature}
        end += align(signature)
    if file_size < end:
        raise ValueError("truncated image or missing page padding")
    return {"header_version": version, "page_size": page, "sections": sections,
            "minimum_file_size": end, "trailing_bytes": file_size - end,
            "os_version_encoded": os_version, "status": "STRUCTURE_ONLY",
            "signature_verified": False, "zeus_compatibility": "UNKNOWN"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args(argv)
    try:
        with args.image.open("rb") as stream:
            header = stream.read(4096)
            stream.seek(0, 2)
            result = inspect_header(header, stream.tell())
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
