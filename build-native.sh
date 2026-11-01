#!/bin/sh
set -eu
cd "$(dirname "$0")"
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread source/cpp/engine.cpp -o engine/clash-native
