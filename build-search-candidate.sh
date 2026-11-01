#!/bin/sh
set -eu
cd "$(dirname "$0")"
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 source/cpp/engine.cpp -o engine/clash-search-v08-candidate
