# Original history-ordering search experiments

This pass starts from the project's faster original C++ build, keeping its board rules, evaluation coefficients, shared activity calculations and clock allocation. It independently implements search-order changes motivated by the general [history-heuristic research](https://webdocs.cs.ualberta.ca/~jonathan/publications/ai_publications/pami.pdf). No existing engine source, tuned parameters, weights or analysis were imported.

## Variants

- `history`: update quiet-move history with a bounded gravity rule, reward a quiet cutoff, and penalize earlier quiet moves that failed to produce that cutoff. Halve history before each root search. Restrict the new history/killer learning to main-search cutoffs, avoiding quiescence pollution.
- `captures`: order losing static-exchange captures below ordinary quiet moves.
- `combined`: both changes.
- `control`: both disabled. Its executable is byte-identical to the faster baseline.

The original parameters chosen for this implementation are a history bound of 10,000, reward `min(1000,16*depth*depth)`, unsuccessful-quiet penalty of half that reward, root aging by division by two, and a losing-capture score shift of 1,200,000. These are heuristic search-order choices, not evaluation weights or values learned from another engine. They can change search outcomes because the existing search uses selective reductions and pruning.

The screen selected **history only** at 53.125% game points across 32 games against the faster baseline. Capture-only and combined scored 43.75% and 48.4375%. The selected binary was frozen before confirmation. Full plans, hashes and game records are in `history-pass/`.

## Investigation and checks

The original history only accumulated positive rewards up to a cap and never aged per root search. A diagnostic replay of a saved GNU loss used only our own engine at bounded depth/time and recorded history values. It observed a maximum of 3,591 and no saturated entries. Thus saturation was a possible long-search risk, not a demonstrated cause of that loss. The diagnostic does not recreate the original clock/search state and is not a unique explanation of losses.

Normal rules/perft, capture/mirror, UCI clocks/stops, bounded mate, history-boundary and address/undefined-behaviour sanitizer checks accompany the candidate. The selected build passed 84/84 shortest synthetic mates. The C++ evaluation fragment and coefficient header are unchanged, and the control's byte identity provides an exact baseline check on the new feature switches. Finite checks do not prove universal correctness or timing reliability.

## Fixed tests and replication

The 96-game screen uses 16 human-game prefixes with both colours for each candidate. Fresh confirmation uses 64 different prefixes for 128 games against the faster build, 32 other prefixes for 64 games against v0.8, and 32 more for 128 matched external games against GNU and Stockfish Skill 5. The short-game requested limits are 0.06 seconds in the screen, 0.08 in direct confirmation and 0.15 in the external batch. Artificial caps are 600 plies; caps remain unfinished, never credited draws.

The initial direct-fast result was 54.6875% with a 95% interval crossing 50%. One fixed replication of 64 new prefix pairs was added without changing the candidate. The final paired comparison pools those two batches with a 97.5% two-sided normal interval; the initial corrected interval is also reported, providing a Bonferroni adjustment for two looks. No further replication or parameter tuning is allowed in this pass. Approximate normal intervals, common opening patterns and concurrent local timing limit inference.

Four standard-start GNU games cover both colours at 180+2 and 600+5 using the exact frozen executable. At most nine game-search workers run on the ten-core test host. All prefixes exclude fitting and every prior pass's starting-game IDs; separate games may still share common opening patterns. No prefix database is read by the competition executable.

## Rebuild selected candidate

From the repository root on the recorded Clang/GCC C++17 platform:

```sh
exp=source/cpp/experimental/history_order
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_EVAL_FAST=1 -DCLASH_ACTIVITY=1 \
  -DCLASH_HISTORY=1 -DCLASH_CAPTURE_LAST=0 \
  "$exp/build-history/engine.cpp" -o "$exp/build-history/clash-native"
```

`build.py` rebuilds all variants from the frozen fast source. `baseline` is the faster build; `old-baseline` is v0.8. Their corresponding sources and the common coefficient header are supplied. Provided binaries target Apple Silicon macOS. Byte-exact checks refer to the recorded Apple Clang version; other platforms require rebuilding and can produce different bytes. Runtime chess reasoning remains C++; Python only orchestrates offline tests.

## Reproduce

Offline scripts used Python 3.12, `chess==1.11.2` and `numpy==2.5.4` (NumPy only for split auditing). Use fresh output labels to preserve original evidence.

```sh
exp=source/cpp/experimental/history_order
CLASH_NATIVE_BINARY="$exp/build-history/clash-native" \
  CLASH_TACTICAL_CHECK=1 CLASH_VERIFY_REPORT=reproduced-history-rules.json \
  python3 source/cpp/verify.py
CLASH_NATIVE_BINARY="$exp/build-history/clash-native" \
  CLASH_PROTOCOL_REPORT=reproduced-history-protocol.json \
  python3 source/cpp/protocol_test.py
python3 "$exp/audit_starts.py"
python3 "$exp/history_checks.py"
python3 "$exp/diagnose.py"
python3 "$exp/selfplay.py" --candidate "$exp/build-history/clash-native" \
  --reference "$exp/baseline" --label history-pass/reproduced-direct-fast \
  --start 16 --pairs 64 --seconds 0.08 --workers 2 --seed 63100000
python3 "$exp/replication.py" --candidate "$exp/build-history/clash-native" \
  --reference "$exp/baseline" --label history-pass/reproduced-replication \
  --pairs 64 --seconds 0.08 --workers 2 --seed 63400000
python3 "$exp/arena.py" --spec "$exp/external-spec.json" \
  --label history-pass/reproduced-external --pairs-per-opponent 16 \
  --seconds 0.15 --workers 2 --seed-base 63300000
python3 "$exp/audit_results.py"
python3 "$exp/qualify_results.py"
```

The last two scripts audit and qualify the original recorded evidence and never install an engine. The clock harness can reproduce each colour at 180+2 and 600+5 with `--our-binary`, a separately installed GNU opponent and a fresh label, as documented in the preceding evaluation-efficiency pass. No opponent evaluation scores or PVs are requested. Own diagnostic scores and match outcomes are not foreign training labels.

The packaged `engine/clash-history` is byte-identical to the selected history candidate. Build it with `build-history-candidate.sh`. It is a separate experimental alternative; the release decision and existing default are preserved in the root report. Choose one fixed submitted version for both competition stages.
