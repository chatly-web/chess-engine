#!/bin/sh
# Reproduce the comparison baseline from its committed source.
set -eu
cd "$(dirname "$0")/../.."
OUT_DIR="${1:?Pass a scratch output directory}"
mkdir -p "$OUT_DIR"
git show 26817ac:source/cpp/engine.cpp > "$OUT_DIR/engine.cpp"
git show 26817ac:source/cpp/tables.h > "$OUT_DIR/tables.h"
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread "$OUT_DIR/engine.cpp" -o "$OUT_DIR/native-v05"
