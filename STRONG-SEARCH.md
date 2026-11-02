# Stronger original C++ search: research and validation

The selected candidate is now the recommended `engine/clash-native`, using the same frozen executable for 3+2 and 10+5. This pass tested independently written search changes against release `09f17cf`. The competition entry remains original: no existing engine code, neural-network weights, opening book, tablebase or external-engine evaluation labels are incorporated. Other engines run only as separate offline test opponents. Evaluation weights remain unchanged.

## What the research supports

[Lichess confirms that Stockfish powers its computer analysis](https://lichess.org/faq). Stockfish combines search with an [efficiently updatable neural evaluator, NNUE](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html). Its [original NNUE announcement](https://stockfishchess.org/blog/2020/introducing-nnue-evaluation/) describes training on millions of evaluated positions. A neural architecture alone does not supply strong weights. Borrowing Stockfish or its weights would violate the competition's originality requirement; no such substitution was made here.

The practical experiment is an original implementation of additional selective search on top of our existing PVS, iterative deepening, transposition table, null move, check extensions and move ordering:

- Mate-distance bounds exclude scores that cannot improve the known mate distance.
- Reverse futility pruning at shallow, non-check, non-PV nodes uses a conservative depth margin, excluding mate-score windows.
- Quiescence delta and exchange pruning skip selected non-checking losing captures, preserving promotions and captures that give check, and disabling these quiescence prunes near the fifty-move threshold.

Six fixed-depth comparisons reduced total searched nodes from **46,740 to 20,868 (55.35%)**, preserving all six selected moves while changing one search score; see [node-comparison.json](strong-search/node-comparison.json). This does not establish a wall-time speedup or Elo gain by itself.

These are heuristics, not mathematically complete pruning rules. They can miss ideas and must earn their place through independent games. No feature is credited with a win-rate guarantee merely because another strong engine uses a related concept.

## Exploratory screens

Each screen has 32 colour-reversed opening pairs, requested limits of 0.05/0.1 seconds per move, and seed base 2100000. These screens select a candidate and are not its held-out evidence.

| Experiment | Points / 64 | Wins | Draws | Losses | Decision |
|---|---:|---:|---:|---:|---|
| Shallow reverse futility + mate bounds | 33 | 24 | 18 | 22 | No clear gain |
| Above + quiescence delta/exchange pruning | 36.5 | 28 | 17 | 19 | Selected for fresh validation |
| Above + more aggressive late-move reductions | 32.5 | 24 | 17 | 23 | Rejected |
| Positional ordering + mate bounds | 30 | 22 | 16 | 26 | Rejected |
| Exact static-evaluation cache + mate bounds | 31 | 23 | 16 | 25 | Rejected |

Smaller board storage, whole-board hash memoization, a target-based king-pressure implementation and an overlay-based legality check did not show a useful fixed-search speed gain and were not adopted. The evaluation-cache timing gain was noisy and did not translate into a better game score. Reports and PGNs are in `strong-search/`.

## Frozen candidate and fresh validation

Candidate SHA256: `2dd66add6e79fce8082283f0f70368a8a17db9f147933ac8b61dd9c457c0b045`.

Baseline SHA256: `fd9318156a13b933a10301620943876782d3cd87eb53b87ce486c8839fa1ddd2`.

The first fresh 128-game batch, seed base 2600000, finished **60 wins, 36 draws and 32 losses**, **78/128 points (60.94%)**. Its approximate pair-aware 95% point-score interval is **54.68%–67.19%**. The separate conditional decisive-pair SPRT remained below its decision boundary at that point. See `strong-search/first-analysis.json`.

The corrected second fixed 128-game batch, seed base 2800000, scored **81.5/128 points** with the same unchanged binary. Combined, the two independent batches finished **124 wins, 71 draws and 61 losses**, scoring **159.5/256 (62.30%)**. The approximate pair-aware 95% interval is **57.99%–66.62%**. The conditional decisive-pair SPRT is reported separately in [final-analysis.json](strong-search/final-analysis.json). The gate passed: both independent batches completed, the combined pair-aware interval exceeded 50%, correctness checks passed and all planned event-clock games completed. The exact frozen candidate was promoted. Point score is not Lichess move accuracy, Elo or first-prize probability.

## Actual clock games

All runs use real decrementing clocks and increments. All **11 completed clock games** ended normally with **zero recorded technical failures**. The candidate beat the previous release **4–0**, winning with both colours at both **180+2** and **600+5**. These four games are a small sample, supported by the separate 256-game validation.

| Clock | Opponent | Candidate colour | Result | Plies | Record |
|---|---|---|---|---:|---|
| 180+2 | Previous native release (09f17cf) | White | Win | 103 | [JSON](strong-search/candidate-baseline-3plus2.json) / [PGN](strong-search/candidate-baseline-3plus2.pgn) |
| 180+2 | Previous native release (09f17cf) | Black | Win | 62 | [JSON](strong-search/candidate-baseline-3plus2.json) / [PGN](strong-search/candidate-baseline-3plus2.pgn) |
| 180+2 | Stockfish 19, Skill 5 (reduced) | White | Win | 83 | [JSON](strong-sf5-blitz-white.json) / [PGN](strong-sf5-blitz-white.pgn) |
| 180+2 | Stockfish 19, Skill 5 (reduced) | Black | Loss | 177 | [JSON](strong-sf5-blitz-black.json) / [PGN](strong-sf5-blitz-black.pgn) |
| 180+2 | Stockfish 19, full strength | White | Loss | 82 | [JSON](strong-r2-full-blitz-white.json) / [PGN](strong-r2-full-blitz-white.pgn) |
| 600+5 | GNU Chess 6.3.0 | White | Loss | 122 | [JSON](strong-r2-gnu-rapid-white.json) / [PGN](strong-r2-gnu-rapid-white.pgn) |
| 600+5 | GNU Chess 6.3.0 | Black | Loss | 101 | [JSON](strong-r2-gnu-rapid-black.json) / [PGN](strong-r2-gnu-rapid-black.pgn) |
| 600+5 | Previous native release (09f17cf) | White | Win | 111 | [JSON](strong-search/r2-candidate-baseline-10plus5.json) / [PGN](strong-search/r2-candidate-baseline-10plus5.pgn) |
| 600+5 | Previous native release (09f17cf) | Black | Win | 168 | [JSON](strong-search/r2-candidate-baseline-10plus5.json) / [PGN](strong-search/r2-candidate-baseline-10plus5.pgn) |
| 600+5 | Stockfish 19, Skill 5 (reduced) | White | Draw | 171 | [JSON](strong-r2-sf5-rapid-white.json) / [PGN](strong-r2-sf5-rapid-white.pgn) |
| 600+5 | Stockfish 19, Skill 5 (reduced) | Black | Loss | 107 | [JSON](strong-r2-sf5-rapid-black.json) / [PGN](strong-r2-sf5-rapid-black.pgn) |

Stockfish Skill Level 5 is a reduced-strength UCI setting, not Lichess computer level 5. At 10+5 the candidate drew one game and lost one against Skill 5; it lost both GNU Chess games and the full-strength Stockfish blitz game. No completed full-strength win has been demonstrated. The result supports a stronger original engine, not dominance over those opponents.

Games share the local machine and are not isolated Elo measurements. Opponent threads/hash are recorded per report. Opponent scores/PVs are not requested for learning (`INFO_NONE`).

## Correctness and experiment failures

The selected candidate passed all three perft totals, 2,000-position legal/tactical-move/evaluation differential checks, protocol/clock/interruption checks, and the address/undefined-behaviour sanitizer suite. In 84 rules-oracle mate cases it retained a forced mate within three moves in all 84; **82/84 chose a shortest mate**. These are finite checks, not universal tactical or hard real-time guarantees.

The first attempt at the second validation batch exposed a harness defect: seed 2800000 reaches checkmate at ply seven (`e2e3 h7h6 f1d3 f7f6 e1f1 h8h7 d3g6`), so choosing an eighth legal move raised `IndexError`. This was not an engine failure. The failed attempt produced no retained completed results and is excluded. The generator now deterministically rejects terminal starts; the reproducing seed needs two attempts. The fix passed 1,001 seeds with deterministic replay. A historical audit of **2,422 saved games found zero terminal random starts**, so the earlier recorded results are unaffected. New validation batches durably save each completed pair and refuse to overwrite an existing label.

Seven clock tests were interrupted when their execution sessions disappeared. Their partial moves and unfinished PGNs are preserved in `strong-search/interrupted-clock-tests.json` and accompanying `*-interrupted.pgn` files. None is credited as a win, loss or draw. Replacement tests start from the standard position under new `strong-r2-*` labels and prevent idle sleep. The exact cause of the execution-session interruption is not established. All seven replacement games completed; the interrupted games remain excluded. [Artifact audit](strong-search/artifact-audit.json) independently replayed all **576 exploratory/validation games** and all **11 clock games**, checking outcomes, legal moves and clock arithmetic.

## Rebuild the experiments

```sh
# C++17; separate executable, default recommended engine remains untouched.
./build-strong-experimental.sh 3
# Other experimental flag combinations: 1, 7, 8, 16.
```

`source/cpp/experimental/strong_search.cpp` reproduces the selected candidate's machine-code text with the recorded flags; whole-file hashes can differ because of Mach-O UUID/signature metadata. The alternate source preserves the rejected ordering/cache implementations. Both use only this project's own tables.

The exact tested executable is deployed as `engine/clash-native`; `build-native.sh` and `build-trained.sh` enable the validated flags. [Build manifest](strong-search/build-manifest.json) records the source/compiler and confirms matching rebuilt machine-code text. The deployed file repeated the rules/protocol suites (`strong-release-rules.json`, `strong-release-protocol.json`). Before the event, use the same frozen executable for both 3+2 and 10+5, complete live BOT tests, authorise organiser accounts in the private allowlist and submit the required credentials through the organiser's private channel. No engine can guarantee winning every round.
