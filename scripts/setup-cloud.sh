#!/usr/bin/env bash
# Rootless setup for the selected Debian 13 cloud image. APT verifies Debian
# signed indexes and package hashes; no trust checks are disabled.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 --version
cc --version | head -n 1
make --version | head -n 1
test "$(dpkg --print-architecture)" = amd64
test -r /usr/share/keyrings/debian-archive-keyring.gpg
tool_root=${ZEUS_TOOL_ROOT:-/workspace/.zeus-tools}
mkdir -p "$tool_root/apt/lists/partial" "$tool_root/apt/cache/archives/partial" "$tool_root/debs" "$tool_root/bin"
cat > "$tool_root/apt/sources.list" <<'EOF'
deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] https://deb.debian.org/debian trixie main
EOF
apt_options=(-o "Dir::Etc::sourcelist=$tool_root/apt/sources.list" -o Dir::Etc::sourceparts=-
  -o "Dir::State::lists=$tool_root/apt/lists" -o "Dir::Cache=$tool_root/apt/cache")
/usr/bin/apt-get "${apt_options[@]}" update
(
  cd "$tool_root/debs"
  /usr/bin/apt-get "${apt_options[@]}" download \
    clang-19=1:19.1.7-3+b1 libclang-cpp19=1:19.1.7-3+b1 \
    libclang-common-19-dev=1:19.1.7-3+b1 lld-19=1:19.1.7-3+b1 \
    adb=1:34.0.5-12 android-libbase=1:34.0.5-12 android-libboringssl=14.0.0+r45-2 \
    android-libcutils=1:34.0.5-12 android-liblog=1:34.0.5-12 android-libziparchive=1:34.0.5-12
  for package in ./*.deb; do dpkg-deb -x "$package" "$tool_root/root"; done
)
ln -sf ../root/usr/bin/clang-19 "$tool_root/bin/clang"
ln -sf ../root/usr/bin/lld-link-19 "$tool_root/bin/lld-link"
cat > "$tool_root/bin/adb" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
tool_root=$(cd "$(dirname "$0")/.." && pwd)
export LD_LIBRARY_PATH="$tool_root/root/usr/lib/x86_64-linux-gnu/android${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$tool_root/root/usr/bin/adb" "$@"
EOF
chmod +x "$tool_root/bin/adb"
export PATH="$tool_root/bin:$PATH"
clang --version
lld-link --version
adb version
make check cross-check upstream-check
