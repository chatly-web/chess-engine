#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build/fast
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_EVAL_FAST=1 -DCLASH_ACTIVITY=1 \
  source/cpp/experimental/eval_fast/build-combined/engine.cpp \
  -o build/fast/clash-native
mv build/fast/clash-native engine/clash-fast
