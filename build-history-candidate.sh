#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build/history
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_EVAL_FAST=1 -DCLASH_ACTIVITY=1 \
  -DCLASH_HISTORY=1 -DCLASH_CAPTURE_LAST=0 \
  source/cpp/experimental/history_order/build-history/engine.cpp \
  -o build/history/clash-native
mv build/history/clash-native engine/clash-history
