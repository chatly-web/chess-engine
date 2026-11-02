# Evaluation efficiency under equal clocks

The ready-to-run faster alternative is `./engine/clash-fast`; rebuild it with `./build-fast-candidate.sh`. The recommended `./engine/clash-native` remains unchanged.

This original C++ pass preserves the recommended v0.8 evaluation coefficients, search, move ordering and time management. Its purpose is to get more search from each second by removing repeated work. No neural model was trained in this pass, and no existing engine's code, parameters, weights or analysis were imported.

The selected combined build updates material and positional bookkeeping when real search moves occur, and shares piece geometry between mobility and king-ring pressure. Temporary legality/SEE boards skip evaluation bookkeeping. Pawn-cache variants were investigated but not selected. Initial prototypes saved only about 4% and 7% in throughput and are preserved as such; strength tests started only after the final implementation was frozen.

The final fixed-depth benchmark measured a paired median baseline/candidate time ratio of **1.2023**, approximately **16.8% less wall time** for the same work. All 64 samples required identical moves, scores, depths and node counts. This is a limited performance measurement, not a win-rate or accuracy claim.

Finite checks passed: 10,000 own-engine score comparisons including colour mirrors; 204 fixed-depth search comparisons; perft, 2,000 legal/capture/mirror cases, UCI clock/stop tests and address/undefined-behaviour sanitizers. Diagnostic builds reconstruct incremental fields and hashes after moves. The packaged selected source reproduces the tested native executable byte for byte on the recorded compiler/platform.

The fixed strength collection is 192 paired-colour games against v0.8 at a requested 0.08 seconds per move, 96 matched games against GNU Chess and Stockfish Skill 5 at 0.15 seconds per move, and four standard-start GNU games covering both colours at 3+2 and 10+5. Starting human games exclude model fitting and all earlier pass prefixes, with separate benchmark/direct/external subsets. Concurrent local load, limited samples and fixed-move clocks constrain the interpretation. Full protocol and independent legal/result/clock audits accompany the saved PGNs and JSON.

Promotion requires the predeclared speed and correctness checks, a positive fresh paired direct-game lower 95% bound, nonnegative aggregate external point difference with no fewer GNU wins, and all four full-clock games finished without own technical failures. It does not imply GNU dominance, near-100% Lichess accuracy or a guaranteed prize.

<!-- RESULTS_START -->
## Completed results

The selected frozen build scored **74 wins, 73 draws and 45 losses** against v0.8: **57.55% game points**, approximate paired 95% interval **[52.26, 62.84]%**, across 96 colour pairs. A draw counts as half a point. This is not Lichess move accuracy or an external Elo estimate.

### Original external batch

| Opponent | Candidate W–D–L | Candidate points / finished | Baseline W–D–L | Baseline points / finished |
|---|---|---|---|---|
| GNUChess6.3 | 0–0–24 | 0/24 | 1–0–23 | 1/24 |
| Stockfish19-Skill5 | 9–5–9 | 11.5/23 | 8–5–11 | 10.5/24 |

The original external batch contains 1 unfinished game(s) at the artificial 328-ply cap. They are retained as unfinished, not draws. The recorded completion policy replays all four games in every affected paired unit once at a 600-ply cap, with unchanged engines, prefixes, options and move budgets. This is an offline harness completion, not a candidate modification or a restart inside a competition game. Original results remain separately published; no technical failure is repaired.

### External comparison after complete-unit replay

| Opponent | Candidate W–D–L | Candidate points / finished | Baseline W–D–L | Baseline points / finished |
|---|---|---|---|---|
| GNUChess6.3 | 0–0–24 | 0/24 | 1–0–23 | 1/24 |
| Stockfish19-Skill5 | 11–4–9 | 13/24 | 7–6–11 | 10/24 |

Additional games played for this completion: 4. The resolved comparison comprises 96 matched records, replacing each affected original four-game unit in full; it is not an additional independent 96-game sample.

### Exact competition clocks against GNU

| Control | Our colour | Result | Plies | Game technical failure |
|---|---|---|---:|---|
| 180+2 | white | loss | 90 | none |
| 180+2 | black | loss | 131 | none |
| 600+5 | white | loss | 166 | none |
| 600+5 | black | loss | 123 | none |

4 GNU process(es) needed closing after not answering the post-game quit command within two seconds. These cleanup events occurred after game results and are distinct from move/clock failures. Logs are included.

The pass played 292 short games in total plus four full-clock games. Original caps, completion replays and all losses are retained. The independent audit replays every saved PGN, checks results and clocks, and recomputes summaries and paired intervals.

**Promotion rejected.** The candidate had zero short-game GNU wins versus one for the checkpoint, failing the predeclared GNU condition. The default v0.8 executable is retained; the faster candidate and its positive direct-game result remain available as experimental evidence.

All games here are offline simulations. Live Lichess end-to-end play still needs verification. No new Lichess accuracy, first-prize guarantee or universal reliability claim is made.

Selected binary SHA256: `06ae951b3d75731b2c0ace364ba2c581f78b6ea195b1b1ddae3994376cb3bed7`. Rebuild provenance, original prototype measurements, split audits, source, correctness results, PGNs and the qualification decision are packaged under `source/cpp/experimental/eval_fast/` and `eval-fast-pass/`.
<!-- RESULTS_END -->
