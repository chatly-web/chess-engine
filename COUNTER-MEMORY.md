# Timed memory and countermove validation

**Promotion rejected. The candidate remains experimental; the current checkpoint and live BOT are unchanged.**

The selected original C++ candidate recorded **138 wins, 140 draws and 106 losses** against `clash-pgo` in 384 fresh short games: **54.17% game points**, with conservative approximate paired **97.5% interval [49.68, 58.65]%**. A draw is half a point. This is not Lichess move accuracy. The interval includes 50%; a reliable strength increase was not established. Matched external performance also fell below the reference, so the larger-memory change is not recommended as a proven winning upgrade.

## What was tested

Both variants keep the minimal insufficient-material draw protection from [AGGRESSIVE-TESTS.md](AGGRESSIVE-TESTS.md). They do not use the rejected broad endgame pruning change. The original table grows from 262,144 to 1,048,576 entries, approximately 12 to 48 MiB for the table on this ABI. A second variant adds an independently written version of the general [countermove heuristic](https://journals.sagepub.com/doi/10.3233/ICG-1992-15103): remember the own quiet beta-cutoff response keyed by side and the previous move; rank it below killers and avoid reducing these promising quiet moves. Null moves carry no counter context.

The screen selected **memory**. In this tested executable, `CLASH_COUNTER=0`; the new countermove heuristic is **not enabled**. Original history ordering remains. Evaluation function text/header and the clock/parser suffix are byte-identical to the parent. No foreign engine code, evaluation/PV labels, weights, runtime books or tablebases are imported. Own-search compiler profiling uses permitted human prefixes and affects machine-code layout, not evaluation weights.

| 32-game screen | W–D–L | Game points |
|---|---|---:|
| memory | 11–13–8 | 54.69% |
| counter | 7–15–10 | 45.31% |

The selected binary was frozen before confirmation. The 384 games use 192 new colour pairs at 0.14 seconds requested per move, three workers. Screening games are excluded from confirmation. A pre-screen protocol amendment increased the initial planned sample to 384 before candidate build/results; both plans are retained. The conservative interval and the earlier rejected confirmation are preserved in `two-look-context.json`; there is no repeated confirmation until a favourable outcome.

## Strong external opponents

| Opponent | Candidate W–D–L | Candidate points | Reference W–D–L | Reference points |
|---|---|---:|---|---:|
| GNUChess6.3 | 0–2–14 | 1/16 | 0–2–14 | 1/16 |
| Stockfish19-Skill5 | 3–6–7 | 6/16 | 10–5–1 | 12.5/16 |
| Stockfish19-full | 0–1–15 | 0.5/16 | 0–2–14 | 1/16 |

These 96 games use eight further human prefixes per opponent, both colours, the frozen candidate and reference, and equal requested 0.14-second budgets. Opponent evaluations/PVs are not requested or fitted. GNU has its book disabled; Stockfish uses one thread, 64 MB hash, and separately recorded Skill 5/full-strength configurations. Weakened Stockfish randomness is not seeded. Raw PGNs, settings, hashes and comparisons are retained; results are not universal Elo or accuracy estimates.

## Full competition-clock games

| Opponent | Control | Our colour | Result | Plies | Technical game failure |
|---|---|---|---|---:|---|
| GNU Chess 6.3.0 | 3+2 | white | loss | 102 | none |
| Stockfish 19 | 3+2 | black | loss | 111 | none |
| GNU Chess 6.3.0 | 10+5 | black | loss | 105 | none |
| Stockfish 19 | 10+5 | white | loss | 102 | none |

These four games start from the standard position with genuine remaining clocks and increments, no movetime override or accelerated clock. They overlap with the short tests as a local load/stability test; two clock games and up to three short-game workers run concurrently. This is not every colour/opponent/control combination or an unbiased tournament win-rate estimate. Each stored elapsed-time/remaining-clock update was independently recomputed, and every PGN legally replayed. Two additional full-clock GNU games of the minimal draw fix completed; their raw results and independent clock audit are retained separately. They are technical validation, not a strength confirmation.

## Coverage and decision

Finite checks passed for both candidates: three reference perfts, 2,000 legal/capture/promotion/symmetry positions, 84 shortest-mate puzzles, 564 immediate-draw lower-bound cases, UCI special moves, node caps, malformed-input recovery, terminal roots, 30 low-clock samples and 20 interrupted searches. Both candidates and the reference also passed 64 independently labelled avoidable-mate defence puzzles at 0.2 seconds per puzzle.

The selected optimized binary stayed within its clock in all 30 measured low-clock samples. The diagnostic sanitizer binary exceeded its 5/10 ms clocks in 11 samples; address and undefined-behaviour checks passed, including the protocol's hard timing assertions at 50 ms and above. That slower diagnostic executable is not the competition binary. Leak detection is unsupported on this macOS build and is not claimed. These finite results do not establish correctness or winning play in every possible position or network/hardware condition.

| Predeclared condition | Outcome |
|---|---|
| finite rules protocol mates draws king defence sanitizer | pass |
| all short games complete no technical failure | pass |
| corrected direct lower bound above half | FAIL |
| external points not below reference | FAIL |
| four selected actual clock games complete no own failure | pass |
| public rebuild semantics match | pass |

The 232 starting human-game IDs exclude fitting and earlier prefix sets. Screen/direct/external splits are disjoint within this pass, although common opening structures and shared concurrent hardware still limit inference. Independent audits check legal PGNs, terminal results, the interval, frozen hashes and actual clocks. No fallback search errors or sanitizer memory errors were found in the collected logs.

## Source and alternative executable

The tested experimental executable is `./engine/clash-memory`, SHA256 `d74294ceefaf202a76edac0f9a80b057eb99e461de75b4f0f4be7d590fc5cab1`. The exact source/header and rejected optional countermove implementation are in `source/cpp/experimental/counter_memory/`. It is **not enabled in the live BOT**. The previous executables and ZIP are unchanged; the requested delivery is GitHub only. No learned neural weights were trained in this pass. The strongest-engine games remain losses; a prize or near-100% accuracy is not established.

From the repository root with Clang/llvm-profdata and a Python environment containing python-chess:

```sh
python source/cpp/experimental/pgo/build.py --plan counter-memory-pass/build-plan.json --source source/cpp/experimental/counter_memory/engine.cpp --define CLASH_ENDGAME_Q=1 --define CLASH_HASH_BITS=20 --define CLASH_COUNTER=0 --work-dir build/memory-reproduce --output engine/clash-memory-reproduce
python source/cpp/experimental/counter_memory/test_draws.py
python source/cpp/experimental/counter_memory/test_king_defence.py --binary engine/clash-memory
```

The helper verifies the declared source, header and macros before compiling and refuses to overwrite an existing output/work directory. A separately regenerated profile rebuilt the same fixed-depth behavior in 32 tested positions, while producing a different binary hash; byte-identical reproduction is not claimed. Chess search is entirely C++; Python runs offline profiling/testing and the separate hosting bridge. Use one exact chosen executable for both event stages, following the supplied freeze rule.
