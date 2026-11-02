# Win-focused tactical-strength pass

The objective is stronger game outcomes, with **3+2 primary**. Speed and reported depth are diagnostics. Sections 7–8 of the [competition guidelines](https://docs.google.com/document/d/1AUgyug3T_akye_rt3oEtTY7yXywO1AVG7TO77v9Py-g/edit), rechecked on 2 November 2026, select the three prize winners through the 3+2 knockout. The later 10+5 showcase does not change those winners. The same submitted version must play both stages.

## Original search changes

An own-game replay showed a bishop capture receiving an optimistic shallow score before a quiet pawn push created a queen threat and mating attack. A rules-only oracle verified that **four specific queen retreats** later permit mate-in-two. This does not establish that every alternative loses or that a queen sacrifice was the optimal defence. Our own conservative search recognised danger earlier in the diagnostic comparison; that is a diagnostic, not proof of a unique cause for every loss.

The candidates add safe checking moves at the quiescence horizon, protect forcing quiet pawn moves from reduction, and test a more conservative pruning/history alternative. All implementation is original project C++. No evaluation weights changed, no opening moves were hardcoded, and no foreign-engine analysis or weights were imported. Frozen sources and reproduction tools are in `source/cpp/experimental/strength_first/`.

## Focused checks

- The control preserved moves, scores, depths and node counts over 104 own-engine differential positions.
- Each candidate passed legal/perft, capture/mirror, UCI clock/stop and bounded mate checks. Each passed all 84 synthetic shortest mates.
- In 24 purpose-built king-defence positions at requested main depth 1, the baseline avoided opponent mate-in-one in 16 cases; each candidate passed 24. Added quiescence checks search beyond nominal main depth. The independent rules oracle and both colour mirrors are supplied. This is a finite horizon result, not Lichess accuracy or proof of overall strength.
- Address/undefined-behaviour sanitizer diagnostics also check incremental hash and king-location consistency. Leak detection is disabled because this macOS runtime does not support it. The selected public source rebuilds to the exact tested binary hash.

## Fixed match design

The 128-game screen compares the checkpoint and three variants against GNU Chess 6.3 and Stockfish 19 Skill 5: both colours, eight pairs per configuration, 0.2-second requested moves and two concurrent games. Selection ranks GNU wins first, GNU points second, and Skill 5 points third. Exact ties prefer checks, threats, then guarded.

The frozen selection then faces 288 fresh games: 24 colour pairs each against GNU, Skill 5 and full-strength Stockfish, at 0.25-second requested moves with three concurrent games. The prefixes come from different human games than all earlier test sets and human-model fitting/validation. Their starting-score filter uses our own baseline at ±150 cp; this does not prove objective equality. They are offline harness inputs, never a runtime opening book.

The exact selected binary also plays four standard-start GNU games: White and Black at 180+2 and 600+5. These single-thread games run concurrently with confirmation, with at most seven active game-search workers on a ten-core machine. Opponent scores/PVs are not requested. The harness may claim a legal draw by an intended move. These are offline simulations, not live Lichess games.

Promotion requires a positive fresh matched game-point lower 95% bound, nonnegative GNU point difference and no fewer GNU wins than baseline, at least one standard-start GNU win at 180+2, all four full-clock games finished without own technical failures, and finite correctness/sanitizer/source checks. No candidate changes are fitted to confirmation outcomes. The gate is a meaningful winning milestone, not a guarantee of GNU dominance or first prize.

## Permitted competitive advantages

The guidelines permit independent search methods, our own trained models, human games and own generated data, general ML tools, and libraries for board rules or bot plumbing. They prohibit using, calling, wrapping or copying an existing chess engine, foreign pretrained weights/analysis, opening books, tablebases and outside move advice during play. Studying general methods does not create an exception to those restrictions.

The supplied guidelines state no numeric CPU/RAM limit. This pass uses our available local hardware; absence of a numeric limit does not establish approval for every hosting arrangement. No organiser messages or other players' challenges were sent. We found no substantiated exception allowing GNU Chess inside the submitted engine.

<!-- RESULTS_START -->
## Completed results

The screen selected **threats** (safe quiet checks plus forcing pawn moves). Its exploratory matched estimate was +6.25 percentage points. Selection was frozen before confirmation.

The fresh confirmation result follows. W–D–L is from our engine’s perspective; draws count as half a game point. These are short fixed-move simulations, not accuracy measurements.

| Opponent | Candidate W–D–L | Candidate points / completed | Baseline W–D–L | Baseline points / completed |
|---|---|---|---|---|
| GNUChess6.3 | 0–3–45 | 1.5/48 | 0–1–47 | 0.5/48 |
| Stockfish19-Skill5 | 12–19–17 | 21.5/48 | 27–12–9 | 33/48 |
| Stockfish19-full | 0–2–46 | 1/48 | 0–2–46 | 1/48 |

Matched game-point difference: **-7.29 pp**, approximate 95% interval **[-13.53, -1.05] pp**, over 72 complete paired units. This is descriptive evidence under the stated opponents, starts, concurrency and move budgets; it is not an Elo estimate.

| Standard-start GNU control | Our colour | Result | Plies | Game technical failure |
|---|---|---|---:|---|
| 180+2 | white | loss | 64 | none |
| 180+2 | black | loss | 79 | none |
| 600+5 | white | loss | 116 | none |
| 600+5 | black | loss | 101 | none |

The pass recorded 416 short games (416 finished, 0 capped/failed) and four full-clock games. Recorded short-game technical failures: 0. In all four full-clock games, GNU did not answer the post-game quit command within two seconds and was closed by the harness; this did not alter the already-completed game result. Cleanup logs are included.

**Promotion rejected.** It failed both the independent improvement requirement and the standard-start GNU blitz-win requirement. The recommended executable remains v0.8 at `b3f8f697330f939fb121c8889d4786cde99df49bd8e9c62e20418ae13158b5e9`. The 24/24 focused king-defence result did not establish stronger overall play or the requested ability to beat GNU at competition clocks. No new Lichess accuracy was measured, no live Lichess game is claimed here, and no prize or universal win guarantee is supported.

Evidence: `strength-first-pass/` contains original PGNs/JSON, plans, selection, independent rules/result/clock audits, source/build hashes and the explicit qualification decision. All losses and caps are retained.
<!-- RESULTS_END -->
