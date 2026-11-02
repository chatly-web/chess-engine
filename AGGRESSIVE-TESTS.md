# Aggressive endgame-search validation

**Promotion rejected: the declared strength gate was not met. The new build remains experimental; the existing checkpoint and live BOT are unchanged.**

This pass built two original C++ variants, ran 256 short games and eight full competition-clock games, and kept the selected executable frozen before confirmation. The known search defect is fixed in the alternative source. A verified correctness improvement is separate from a demonstrated increase in match strength.

## Reproduced defect and original change

For `6k1/8/7b/8/5p2/8/8/2B3K1 w - - 0 1`, `Bxf4` is a legal capture that immediately leaves only kings and bishops on the same colour: insufficient material. The old direct quiescence probe returns −197 centipawns after discarding it with a −230 static-exchange estimate. A legal immediate draw is available, so a full-window quiescence score below zero loses that known lower bound.

Mode 1 protects captures whose resulting position has insufficient material from delta/SEE pruning. Mode 2 additionally disables those pruning tests when the original raw material phase is at most six. The evaluation coefficients, history heuristic, time allocator and all other chess code are unchanged. Both variants use their own search-execution compiler profiles; no opponent evaluation, move target, source or weights are imported. There is no runtime opening book, tablebase or online move source.

The screen selected **endgame-safe**. All 64 targeted draw regressions passed after the fix. In a separate 500-position rules-generated sparse set, the original preserved the available draw lower bound in 491 cases, and both variants in 500. This is a finite property check, not Lichess accuracy, a solved endgame set or a tablebase. The public test compiles a probe of the actual shared C++ search, while python-chess independently verifies the immediate material draw.

## Own-engine matches

| Batch | W–D–L | Game points | Approximate paired 95% interval |
|---|---|---:|---|
| Screen: draw-safe | 10–15–7 | 54.69% | excluded from confirmation |
| Screen: endgame-safe | 17–4–11 | 59.38% | excluded from confirmation |
| Frozen selected, fresh confirmation | 29–37–30 | 49.48% | [41.97, 56.99]% |

The screen uses 0.12 seconds per move. Confirmation uses 0.16 seconds per move and 48 new colour pairs. Draws count as half a point. Its 96 results are analysed once; screening games are excluded. The interval crosses 50%, so these results do not establish superiority over `clash-pgo`.

## Matched external confirmation

| Opponent | Candidate W–D–L | Candidate points | Reference W–D–L | Reference points |
|---|---|---:|---|---:|
| GNUChess6.3 | 0–2–14 | 1/16 | 0–3–13 | 1.5/16 |
| Stockfish19-Skill5 | 7–4–5 | 9/16 | 5–5–6 | 7.5/16 |
| Stockfish19-full | 0–3–13 | 1.5/16 | 0–1–15 | 0.5/16 |

Each engine plays both colours on eight separate prefixes per opponent, with 0.16 seconds per move. Foreign engines are benchmarks only; their evaluations/PVs are not requested or fitted. Stockfish uses one thread, 64 MB hash and the explicitly reported skill setting; GNU's book is disabled. The full-strength configuration is separate from Skill 5. Raw outcomes, opponent identities, options, hashes and paired comparisons are retained in `aggressive-pass/external.json`.

## Full competition-clock games

| Build | Opponent | Control | Our colour | Result | Plies | Game failure |
|---|---|---|---|---|---:|---|
| reference | GNU Chess 6.3.0 | 3+2 | white | loss | 136 | none |
| reference | Stockfish 19 | 3+2 | black | loss | 65 | none |
| reference | GNU Chess 6.3.0 | 10+5 | black | loss | 121 | none |
| reference | Stockfish 19 | 10+5 | white | loss | 112 | none |
| selected | GNU Chess 6.3.0 | 3+2 | white | loss | 140 | none |
| selected | Stockfish 19 | 3+2 | black | loss | 65 | none |
| selected | GNU Chess 6.3.0 | 10+5 | black | loss | 143 | none |
| selected | Stockfish 19 | 10+5 | white | loss | 62 | none |

These are complete games starting from the standard position, with actual remaining clocks and increments, **no movetime override or clock scaling**. They are separate from the short matches and earlier initial-move probes. The clock record was independently replayed, legal moves and result checked, and every stored `remaining + increment − elapsed` update recomputed.

Clock suites run two games each. Reference and selected suites overlap with short confirmation (up to four clock games plus two short-game workers), so these are local load/stability tests and small field samples, not controlled Elo estimates. Both colours are represented across controls; this is not every colour/opponent/control combination. Normal post-game GNU quit timeouts, if observed in logs, are distinct from illegal moves or clock forfeits. Losses and all records are retained.

## Decision and finite checks

| Predeclared condition | Outcome |
|---|---|
| finite rules protocol mates draw oracles sanitizers | pass |
| all short games finished without technical failure | pass |
| direct lower95 above half | FAIL |
| external points at least reference | pass |
| selected full games finished without own failure | pass |

Both normal variants passed three reference perfts, 2,000 legal/capture/promotion/colour-symmetry positions, 84 shortest-mate cases, UCI edge cases, 30 low-clock samples and 20 interrupted searches. The selected source passed address and undefined-behaviour sanitizer rules/protocol checks. An initial leak-detector request was unsupported on this macOS platform and stopped before testing; rerunning with leak detection disabled retained the address/undefined checks, without changing engine source. Leak detection is not claimed.

The published helper rebuilt the variant without missing-profile warnings. Thirty-two fixed-depth searches matched the frozen tested executable in move, score, nodes and depth; independently regenerated compiler profiles did not produce a byte-identical binary. Tests and decision details are in `aggressive-pass/`. The 96 human-prefix game IDs exclude earlier fitting and prefix sets; screen, direct and external subsets are disjoint within this pass. Shared opening structures and concurrent load still limit inference.

## Alternative executable and reproduction

The tested alternative is `./engine/clash-endgame`, SHA256 `f9a1c66a423e2296bfff8fb28982fcdb243e50aa2ee122146e61e6de8b6a35a9`. It is **not enabled in the live BOT**. Core search remains C++; Python is used for offline tests, compiler profiling and the separate hosting bridge. The same chosen executable handles both clock settings; do not switch engines between event stages. The existing release ZIP remains unchanged; publication here is GitHub only as requested.

From the repository root, with Clang, matching llvm-profdata and a Python environment containing python-chess:

```sh
python source/cpp/experimental/pgo/build.py --plan aggressive-pass/build-plan.json --source source/cpp/experimental/endgame_safe/engine.cpp --define CLASH_ENDGAME_Q=2 --work-dir build/endgame-reproduce --output engine/clash-endgame-reproduce
python source/cpp/experimental/endgame_safe/test_draws.py
```

The build refuses to overwrite an existing output/work directory. Exact source, header, macro flags, compiler-profile provenance and binary hashes are recorded. No credentials or populated bridge configuration are included. The pass does not establish near-100% accuracy, universal reliability or a guaranteed prize.
