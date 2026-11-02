# Original bit-mask attack prototype

This prototype changes only attack detection and the geometry needed to support it. Evaluation, move ordering, pruning and clock allocation stay those of the faster C++ baseline. See the root `BIT-ATTACKS.md` for measured results and the early stop: about 8.3% throughput gain did not reach the 15% threshold for launching matches. The candidate is not promoted or combined with the history experiment.

Generate ray, pawn-source, knight and king masks from square coordinates at startup. On each ray, the nearest occupied square is identified with a nonzero bit scan. Temporary legality and static-exchange boards always update occupied/pawn/knight geometry, even when they skip material/positional bookkeeping. FEN construction initializes geometry before checking validity. Diagnostic builds independently reconstruct that geometry after moves.

The control is byte-identical to the faster baseline. Finite validation covers 5,000 full attack maps (640,000 square/colour checks), perft, 2,000 legal/capture/mirror positions, UCI protocol/clocks/stops, 204 identical fixed-depth search outputs and address/undefined-behaviour sanitizers. Pawn-mask direction, blocker direction, promotions, castling and en-passant handling remain subject to these finite checks, not a universal proof.

From the repository root, compile with the recorded Clang/GCC C++17 toolchain:

```sh
exp=source/cpp/experimental/bit_attacks
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_EVAL_FAST=1 -DCLASH_ACTIVITY=1 -DCLASH_BIT_ATTACKS=1 \
  "$exp/build-candidate/engine.cpp" -o "$exp/build-candidate/clash-native"
```

`build.py` reconstructs both variants. Supplied executables target Apple Silicon macOS; other platforms require rebuilding. The attack-map helper includes the same frozen candidate source with its UCI entry renamed and exposes only rules geometry for comparison. Its source and executable are supplied; compile `attack_map.cpp` with the same flags when rebuilding elsewhere.

Offline scripts used Python 3.12, `chess==1.11.2` and `numpy==2.5.4` (NumPy for the split audit only). Reproduction outputs preserve the original reports:

```sh
exp=source/cpp/experimental/bit_attacks
python3 "$exp/attack_map_check.py"
python3 "$exp/benchmark.py"
python3 "$exp/audit_starts.py"
CLASH_NATIVE_BINARY="$exp/build-candidate/clash-native" \
  CLASH_TACTICAL_CHECK=1 CLASH_VERIFY_REPORT=reproduced-bit-rules.json \
  python3 source/cpp/verify.py
CLASH_NATIVE_BINARY="$exp/build-candidate/clash-native" \
  CLASH_PROTOCOL_REPORT=reproduced-bit-protocol.json \
  python3 source/cpp/protocol_test.py
```

The native executable reads no prefix database, external engine, opening book, tablebase or online service. Geometry masks implement the rules and do not contain chess evaluations or best moves. Implementation is original project code, not copied engine code.
