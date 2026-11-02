#!/bin/sh
set -eu
cd "$(dirname "$0")"
FLAGS="${1:-3}"
case "$FLAGS" in
  1|3|7) SOURCE=source/cpp/experimental/strong_search.cpp ;;
  8|16) SOURCE=source/cpp/experimental/alternative_search.cpp ;;
  *) echo 'Choose experiment flags 1, 3, 7, 8 or 16.' >&2; exit 2 ;;
esac
"${CXX:-c++}" -std=c++17 -O3 -DNDEBUG -pthread -I source/cpp -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 -DCLASH_SEARCH_V3="$FLAGS" "$SOURCE" -o "${2:-engine/clash-strong-experimental}"
