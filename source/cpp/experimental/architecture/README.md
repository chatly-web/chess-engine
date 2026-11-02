# Original search architecture experiments

These candidates implement two original changes to the v0.8 search. The competition executable remains unchanged until the recorded release gate passes. No GNU/Fruit source, evaluation weights or analysis labels are imported.

## Changes

1. **Four-slot transposition buckets:** same 262,144 entries and 12,582,912-byte entry storage as the baseline. The implementation can keep different reversible-history contexts for the same board. It prioritises usable deep entries when probing, retains recent deep exact results against shallow overwrites, and replaces entries using depth, exact-bound status and capped age. Full board keys, rule clocks, mate-score handling and the existing history guards remain. Age uses a 16-bit search generation. Four-way probing is a general design described in the [GNU Chess manual](https://www.gnu.org/software/chess/manual/gnuchess.html); the code and replacement policy here are original.
2. **Verified low-material null pruning:** require an own static fail-high before trying a null move. A null fail-high is verified when material phase is at most 8 or the side has at most one non-pawn piece. Verification searches the real position one ply shallower with null moves, reverse-futility pruning, late-move reductions, quiescence delta pruning and transposition-score cutoffs disabled. The verified bound is returned only when it confirms the cutoff. Rejected verification continues the normal search. Scoped state and history restoration handle interruption. This is a bounded heuristic safety improvement, not a proof that all zugzwangs are solved.

Evaluation weights, board representation, legal move generation and clock policy remain those of the checkpoint. All candidates use one search worker. Table memory and thread count are controlled between versions; this pass does not rely on giving a candidate four times the CPU allocation.

## Builds

`baseline.cpp` and `baseline` preserve the prior source/tested macOS ARM executable. `engine.cpp`, `tt_methods.inc`, `safe_null.inc` and `build_candidates.py` are the original experiment source/generator. The frozen directories contain the actual source/header/executable combinations:

| Directory | Cluster table | Verified null pruning |
|---|---:|---:|
| build-control | 0 | 0 |
| build-cluster | 1 | 0 |
| build-safe-null | 0 | 1 |
| build-combined | 1 | 1 |

From the repository root, compile one frozen directory without replacing production:

```sh
exp=source/cpp/experimental/architecture
variant=build-combined
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_CLUSTER_TT=1 -DCLASH_SAFE_NULL=1 \
  "$exp/$variant/engine.cpp" -o "$exp/$variant/clash-native"
```

Set the final two macros according to the table for another variant. `build_candidates.py` regenerates/compiles all four directories from the preserved baseline, never from a subsequently promoted engine. The native search/inference is C++; Python orchestrates offline checks and matches.

## Validation

The control is compared with the checkpoint at fixed depth. Table unit checks cover byte budget, bucket collisions, distinct histories, deeper-result retention, stale replacement and generation wrap. Focused null-mechanism tests exercise acceptance/rejection and restoration after node-budget interruption; they are not an independent endgame oracle. Rules-only tests cover bounded mates, legal moves, capture generation, draw/mate precedence, repeated histories and insufficient material. Sanitized builds check memory/undefined behaviour and incremental hash/king consistency.

`starts.json` records 160 human opening prefixes. They come from different games than all previous opening sets and human-model fitting/validation. The absolute starting score filter uses only our own baseline (at most150cp), and does not prove objective equality. Prefixes are harness inputs, not a book inside the engine. The public human-game corpus/provenance already resides in the neighbouring `human_learning` experiment directory. No foreign engine scores or PVs are collected. Both colours are tested, and capped games remain unfinished.

Plans, hashes, complete game records and final decisions are in the root `architecture-pass/` and `ARCHITECTURE.md`. Small samples, selective depth and node counts do not establish universal strength or near100% accuracy. Exact competition clocks must be checked on the same frozen binary before any promotion.


Compile the focused mechanism checks without `-DNDEBUG` so assertions remain active:

```sh
exp=source/cpp/experimental/architecture
c++ -std=c++17 -O1 -g -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_CLUSTER_TT=1 -DCLASH_SAFE_NULL=1 \
  -DCLASH_VERIFY_TT=1 -DCLASH_VERIFY_HASH=1 \
  "$exp/test_table.cpp" -o /tmp/clash-table-check
/tmp/clash-table-check
```

Use `test_null.cpp` for the verification/unwind check. Address/undefined-behaviour sanitizer flags can be added to these test builds. On the tested macOS runtime, run AddressSanitizer with `ASAN_OPTIONS=detect_leaks=0` because leak detection is unsupported. That setting does not disable address or undefined-behaviour checks.
