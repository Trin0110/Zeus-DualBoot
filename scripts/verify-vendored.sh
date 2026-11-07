#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('third_party/DarwinBoot')
manifest = json.loads((root / 'UPSTREAM.json').read_text())
for name, expected in manifest['files'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
print('PASS: pinned DarwinBoot source integrity')
PY
python3 third_party/DarwinBoot/Test/test-kernel-parser.py
python3 third_party/DarwinBoot/Test/test-packed-ramdisk.py
mkdir -p build
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror third_party/DarwinBoot/Test/window-size.c -o build/window-size
./build/window-size
echo 'PASS: DarwinBoot window size boundaries'
