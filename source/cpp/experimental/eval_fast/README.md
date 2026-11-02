# Original C++ evaluation-efficiency experiments

This pass preserves the v0.8 chess evaluation, search heuristics, move ordering and clock allocation. It removes repeated calculations so the engine can search more under the same clock. No neural model was trained, no evaluation weights changed, and no other engine code, weights or analysis were imported.

## Implementations

- `incremental`: material, piece-square scores, raw game phase, bishop counts and occupied/pawn bitmaps update when a real search move is made. Temporary boards used only for legality or static exchange do not need these evaluation fields. Such temporary states never enter evaluation or the main search.
- `cached`: additionally caches file counts and passed-pawn status in 2,048 thread-local entries. Every hit compares both full pawn bitboards; collisions recompute. King distance and other non-pawn terms remain dynamic.
- `activity`: traces each knight/bishop/rook/queen once to calculate both mobility and pressure on the enemy king ring. Attacks include friendly occupied endpoints, while mobility excludes them, exactly matching the original functions.
- `combined`: incremental evaluation plus the shared activity scan, without the pawn cache. This was selected by benchmark speed before any strength games started.

The compiler switches are `CLASH_EVAL_FAST=0/1/2` and `CLASH_ACTIVITY=0/1`. Frozen directories contain the tested source, headers and Apple Silicon binaries. The control disables both. `prototype/` and `prototype-second/` preserve the earlier 4% and 7% speed prototypes; they did not proceed to strength games. No implementation changes were made after the selected candidate was frozen.

## Evidence and limits

The selected build matched the old C++ engine's evaluations on 5,000 legal random-walk positions and their colour mirrors, and matched moves, scores, depths and nodes on 204 fixed-depth searches. Legal/capture sets, perft, colour symmetry, UCI clocks/stops and address/undefined-behaviour sanitizer checks passed. Diagnostic builds independently reconstruct the incremental fields, piece hash and king locations after moves. These are finite checks, not a proof over all chess positions.

The benchmark uses 32 human prefixes and two passes at depth 6, with engine order shuffled per sample. All engines must return identical search outputs and node counts. The selected paired median wall-time ratio was about 1.20, equivalent to about 17% less time for this fixed work. This is a limited benchmark, not an Elo or accuracy measurement.

Strength testing uses another 96 human games for 192 paired-colour games against v0.8, then 24 further human games for 96 matched external-opponent games. Four standard-start GNU games cover both colours at 180+2 and 600+5. At most nine game-search workers run concurrently on the ten-core host. Prefix games exclude fitting and every prior pass's starting games. Different human games can still share common opening patterns. The baseline ±150 cp prefix filter does not establish objective equality.

The actual promotion gate and complete outcomes are in `eval-fast-pass/plan.json`, `qualification.json` and the root `EVAL-FAST.md`. Draws count as half a point and the offline rules harness can claim a draw by an intended move. Fixed-move tests do not replace full-clock tests or live Lichess validation.

## Rebuild

From the repository root, with the tested Clang/GCC C++17 toolchain:

```sh
exp=source/cpp/experimental/eval_fast
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_EVAL_FAST=1 -DCLASH_ACTIVITY=1 \
  "$exp/build-combined/engine.cpp" -o "$exp/build-combined/clash-native"
```

`build.py` rebuilds all variants from the preserved original baseline. Build flags and binary hashes are recorded in `eval-fast-pass/build-receipts.json`. Byte-exact rebuild checks refer to the recorded Apple Clang version and native platform. Other toolchains can produce different executable bytes.

## Reproduce checks

Offline scripts used Python 3.12, `chess==1.11.2` and `numpy==2.5.4`. Python is test orchestration; all competition move selection and evaluation remains C++. NumPy is used only for auditing the existing human-data split.

```sh
exp=source/cpp/experimental/eval_fast
CLASH_NATIVE_BINARY="$exp/build-combined/clash-native" \
  CLASH_TACTICAL_CHECK=1 CLASH_VERIFY_REPORT=reproduced-fast-rules.json \
  python3 source/cpp/verify.py
CLASH_NATIVE_BINARY="$exp/build-combined/clash-native" \
  CLASH_PROTOCOL_REPORT=reproduced-fast-protocol.json \
  python3 source/cpp/protocol_test.py
python3 "$exp/eval_equivalence.py"
python3 "$exp/audit_starts.py"
python3 "$exp/benchmark.py"
python3 "$exp/audit_results.py"
python3 "$exp/qualify_results.py"
```

Reproduction outputs use separate labels where new evidence is collected. The result audit and qualification scripts inspect the original saved evidence and never install a binary. The pawn cache persists across evaluation queries; the equality test exercises that reuse.

## Reproduce games

Use fresh labels to preserve original evidence. GNU and Stockfish are separately installed offline opponents, never part of the submitted engine. Adjust their paths in a copy of the external spec if necessary.

```sh
exp=source/cpp/experimental/eval_fast
python3 "$exp/selfplay.py" --label eval-fast-pass/reproduced-direct
python3 "$exp/arena.py" --spec "$exp/external-spec.json" \
  --label eval-fast-pass/reproduced-external --pairs-per-opponent 12 \
  --seconds 0.15 --workers 2 --seed-base 62100000
python3 "$exp/clock_arena.py" \
  --our-binary "$exp/build-combined/clash-native" --our-revision fast-combined \
  --opponent /opt/homebrew/bin/gnuchess --opponent-arg=--uci \
  --base 180 --increment 2 --colour white \
  --label eval-fast-pass/reproduced-gnu-blitz-white
```

Repeat the clock command for both colours and for 600+5. Wall-clock results can vary. External scores and PVs are not requested or used as labels. This pass learns no weights from external games; match outcomes assess the frozen implementation.

Implementation is original project code. Incremental accounting, memoizing pawn-only properties and sharing geometric calculations are general programming methods; no existing engine source was adapted. The original pawn-cache idea had been noted while studying engine design documentation; the selected combined build does not use that cache.

## Artificial move-cap completion

One original external game reached the 328-ply harness cap. `external-completion-plan.json` records the subsequent policy: replay the entire affected four-game paired unit once from its original prefix, using the unchanged engines/options/time and a 600-ply cap. Original capped records remain published as unfinished. All four original unit records are replaced together in `external-resolved.json`; this is not an extra independent 96-game sample. A repeat cap or any own technical failure still fails the completion gate.

`completion_arena.py` changes only the artificial limit from 328 to 600 plies. `complete_caps.py` can reproduce the procedure from the published original evidence with separate output labels. The independent audit checks original, replay and resolved PGNs. This procedure modifies no chess code or weights and makes no changes to the 192-game direct result.

The ready-to-run `engine/clash-fast` is byte-identical to the selected combined executable. `build-fast-candidate.sh` rebuilds that alternative while preserving the recommended engine. Its release status follows the full recorded gate, including the GNU comparison.
