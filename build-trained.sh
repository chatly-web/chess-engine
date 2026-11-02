#!/bin/sh
set -eu
cd "$(dirname "$0")"
WEIGHTS_FILE="${1:?Pass a weights JSON file}"
OUTPUT_FILE="${2:-engine/clash-trained-experimental}"
mkdir -p build/trained
cp source/cpp/engine.cpp build/trained/engine.cpp
"${PYTHON:-python3}" source/cpp/generate_tables.py --weights "$WEIGHTS_FILE" --output build/trained/tables.h
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 -DCLASH_SEARCH_V3=3 build/trained/engine.cpp -o "$OUTPUT_FILE"
