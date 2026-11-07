#!/usr/bin/env bash
# Build/test only. Never execute upstream phone, firmware, image or flash targets.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v clang >/dev/null
command -v lld-link >/dev/null
mkdir -p build/upstream
fetch() {
  local name=$1 revision=$2 destination=$3
  if [ ! -d "$destination/.git" ]; then
    git init -q "$destination"
    git -C "$destination" remote add origin "https://github.com/$name.git"
    git -C "$destination" fetch --depth 1 origin "$revision"
    git -C "$destination" checkout -q --detach FETCH_HEAD
  fi
  test "$(git -C "$destination" rev-parse HEAD)" = "$revision"
  # Reject edits to source; ignored build products may be retained.
  git -C "$destination" diff --quiet
  git -C "$destination" diff --cached --quiet
}
fetch UniXNU/DarwinBoot 3c75734014cdab0acd9541e88057b7606ee7ae08 build/upstream/DarwinBoot
python3 build/upstream/DarwinBoot/Test/test-kernel-parser.py
python3 build/upstream/DarwinBoot/Test/test-packed-ramdisk.py
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror build/upstream/DarwinBoot/Test/window-size.c -o build/upstream/window-size
build/upstream/window-size
fetch oosexgang/hakios-xnu-kernel 63fc2b4633bac3af8e57dadab9f5a8d4cb940438 build/upstream/HakiOS
# Explicitly overwrites only generated placeholder identity, not upstream source.
make -C build/upstream/HakiOS loader-open
# Remove the PE timestamp to make repeat builds deterministic with the same toolchain.
lld-link /subsystem:efi_application /entry:efi_main /nodefaultlib /base:0xA1000000 /timestamp:0 \
  /out:build/upstream/HakiOS/xnuloader/loader.efi build/upstream/HakiOS/xnuloader/loader.obj
python3 - <<'PY'
from pathlib import Path
import struct, hashlib, json
p = Path('build/upstream/HakiOS/xnuloader/loader.efi')
b = p.read_bytes()
assert b[:2] == b'MZ'
pe = struct.unpack_from('<I', b, 0x3c)[0]
assert b[pe:pe+4] == b'PE\0\0'
assert struct.unpack_from('<H', b, pe+4)[0] == 0xaa64  # ARM64
assert struct.unpack_from('<H', b, pe+24+68)[0] == 10  # EFI application
result = {'artifact': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
          'status': 'BUILD_VERIFIED', 'executed': False, 'zeus_compatible': 'UNKNOWN',
          'warning': 'Research loader contains board-specific addresses and storage writes. Not a zeus boot image.'}
Path('build/upstream/result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
PY
