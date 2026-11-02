# Original search-memory and endgame-pruning architecture

This pass implements two original changes in C++ and evaluates them separately and together. The recommended competition executable remains the v0.8 checkpoint until independent evidence meets the gate. Evaluation weights and clock allocation are unchanged; every competing own build uses one search worker and a 12MiB transposition-entry allocation.

## Implemented changes

- Four adjacent slots per table bucket, retaining full board and reversible-history keys. The table can retain separate contexts for one board, protects recent deep exact results against shallow overwrites, and chooses replacement victims by depth, bound quality and age. Capacity remains262,144 entries, each48bytes, as checked in each executable. Rule clocks and mate normalisation retain the existing guards.
- Static-evaluation gating before null search. In low-material positions or when the side has at most one non-pawn piece, a null fail-high must be confirmed by searching the real position one ply shallower. Verification disables null moves, reverse-futility and late-move reductions, quiescence delta pruning and transposition-score cutoffs. A rejected result resumes normal search. Scoped state/history restoration protects interrupted searches.

These are independently implemented general concepts. The [GNU manual](https://www.gnu.org/software/chess/manual/gnuchess.html) documents multi-probe replacement and endgame null verification. No GNU/Fruit source, evaluation values, weights or analysis labels were copied. The source and reproducible build flags are preserved in `source/cpp/experimental/architecture/`.

Verification is bounded, not an endgame-solving proof. The checkpoint's practical transposition-history reuse heuristic is retained; this pass does not provide a general graph-history-interaction proof.

## Checks before matches

- Control build: identical moves, scores, completed depths and node counts on104 own-engine differential positions, including retained-table draw/mate cases.
- Each variant: perft197281/97862/43238;2,000 legal/capture/evaluation-mirror positions; UCI special moves,30 short-clock samples and20 stop requests.
- Each candidate:84/84 bounded synthetic mate tests;82 shortest mates. These finite KQ tests do not establish general tactical accuracy.
- Table mechanism: same byte budget, colliding keys, distinct contexts, retained deep exact results, stale replacement and16-bit generation wrap.
- Null mechanism:18 focused runs,116 verification calls,6 rejected shortcuts and9 node-budget interruptions. Verification nesting and board-history stack were restored. These counts exercise the mechanism; they are not independent proof of each position's value.
- Address/undefined-behaviour sanitizers, rule checks and incremental hash/king consistency checks passed for the combined implementation. Leak detection is disabled because this macOS runtime does not support it.
- Retained-table history tests preserve mate priority at halfmove98/99, repetition draws and insufficient material.

## Speed and depth

A12-position timing sample at0.6 seconds requested per move completed median depth8 for the checkpoint and all three candidates. That sample does not demonstrate a depth gain. Node counts differ because search trees and retained entries differ; they are not equivalent-work speed measurements. Match results, clock safety and correctness determine any replacement.

## Independent match design

The first screen compares the checkpoint with cluster-only, safe-null-only and combined variants:8 colour pairs per opponent against GNU Chess6.3 and Stockfish19 Skill5,128 games,0.15-second requested move limits, two concurrent games. GNU score is the primary exploratory selection criterion, with Skill5 as the tie breaker.

A frozen selected candidate then faces a fresh confirmation:24 colour pairs each against GNU, Skill5 and full-strength Stockfish,288 games,0.2-second requested move limits, three concurrent games. The screen and confirmation use different human games, all excluded from previous prefix sets and human-model fitting/validation. Starting positions are filtered using only our own score (absolute150cp maximum); this does not establish objective equality. They are offline harness inputs, never an agent opening book.

Opponents are separate installed executables; no scores or PVs are requested. Books are disabled. Both colours are tested. A draw is half a point; capped games remain unfinished. Skill5 is a reduced UCI strength setting, not a Lichess level. All candidates and opponents use one search worker. Local concurrency and small paired samples limit conclusions.

Promotion requires a positive fresh approximate95% lower bound in matched point score, nonnegative GNU difference, no own technical failures, passed finite checks, and completion of both180+2 and600+5 by the exact frozen binary with at least one standard-start GNU non-loss. No setting is changed to fit the confirmation games. Exact clocks are offline simulations, not completed live Lichess games.

<!-- RESULTS_START -->
### Exploratory screen

All128 games were recorded;127 finished and one combined-variant game reached its cap. No technical failure was recorded.

| Version | GNU W–D–L | Stockfish Skill5 W–D–L | Matched point-score difference |
|---|---|---|---:|
| v0.8 | 1–0–15 | 6–7–3 | Reference |
| Cluster table | 1–0–15 | 6–6–4 | −1.56pp |
| Safer null | 1–0–15 | 7–4–5 | −1.56pp |
| Combined | 1–0–15 | 2–7–6,1 unfinished | −11.67pp |

The individual variants tied under the stated GNU-first/Skill5 tie-break. The recorded exact-tie preference chose the table-only build. Its screen difference was −1.56pp, approximate95% interval[−12.94,+9.81]pp; the small screen did not establish improvement. The table-only executable advanced to the separate confirmation and both exact competition clocks below.

### Fresh confirmation and decision

All288 confirmation games completed without recorded technical failures.

| Version | GNU W–D–L | Stockfish Skill5 W–D–L | Full Stockfish W–D–L | Points |
|---|---|---|---|---:|
| v0.8 | 0–2–46 | 21–5–22 | 0–1–47 | 25/144 |
| Cluster table | 0–0–48 | 20–11–17 | 0–3–45 | 27/144 |

The matched point-score estimate was **+1.39 percentage points**, approximate95% interval **[−3.15,+5.92]pp**, over72 colour-paired units. GNU score regressed by2.08pp; Skill5 and full-Stockfish scores rose by4.17 and2.08pp. Full Stockfish wins were zero for both versions. The evidence does not establish a strength improvement.

The exact selected executable completed standard-start GNU tests at both competition controls:

| Clock | Our colour | Result | Plies | Recorded technical failure |
|---|---|---|---:|---|
| 180+2 | White | Loss | 106 | None |
| 600+5 | Black | Loss | 85 | None |

The planned release gate failed: the interval lower bound was negative, GNU score regressed, and neither standard-start GNU game was a non-loss. **The recommended competition executable remains v0.8.** The table and verified-null implementations are supplied as experimental original source, not proven stronger replacements. No new Lichess accuracy percentage or universal speed/depth gain is claimed.

This pass recorded416 short matches (415 completed,one capped) and two completed full-clock games, with no recorded technical failure. Rules-only replay verified the saved moves, results and clock accounting. The selected binary rebuilds byte-exactly from the packaged source. Reports, PGNs, checksums and decisions are in `architecture-pass/`.

<!-- RESULTS_END -->
