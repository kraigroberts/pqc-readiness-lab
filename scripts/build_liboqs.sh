#!/usr/bin/env bash
set -euo pipefail

# Minimal, reliable build of liboqs with defaults
if ! command -v cmake >/dev/null 2>&1; then
  echo "cmake is required" >&2
  exit 1
fi

if command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  SUDO=""
fi

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

echo "[liboqs] cloning..."
git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git "$WORK_DIR/liboqs"

echo "[liboqs] building..."
cd "$WORK_DIR/liboqs"
mkdir build && cd build
cmake ..
CORES=$( (command -v nproc >/dev/null 2>&1 && nproc) || sysctl -n hw.ncpu || echo 2 )
make -j"${CORES}"
${SUDO} make install
echo "[liboqs] installed."

