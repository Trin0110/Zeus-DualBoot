#!/usr/bin/env bash
# Freestanding ARM64 compilation only; no kernel linkage or boot image produced.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/aarch64
for source in drivers/display/display.c drivers/touch/touch.c drivers/storage/storage.c platform/sm8450/platform.c; do
  clang --target=aarch64-none-elf -std=c11 -ffreestanding -fno-builtin \
    -Wall -Wextra -Werror -O2 -c "$source" -o "build/aarch64/$(basename "$source" .c).o"
done
file build/aarch64/*.o
