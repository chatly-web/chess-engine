#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build/native
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 source/cpp/engine.cpp -o build/native/clash-native
mv build/native/clash-native engine/clash-native
