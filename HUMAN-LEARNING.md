# Human-result learning and multicore search

This second strength pass starts from the recommended `a67bfda` checkpoint. It contains original C++ evaluation/search experiments and independent match evidence. The recommended competition executable remains the checkpoint until a candidate meets its recorded gate. No new Lichess move-accuracy percentage has been measured.

## Learned evaluation

The rules permit human game databases and original fitted weights. We collected 5,304 public rated human games with both players rated at least 2200 and initial clocks of at least three minutes. API exports disabled evaluations, accuracy, opening annotations and comments. After quiet-position filtering, 23,803 positions from 3,087 games supplied human final-result labels. A whole-game split separates training and validation. No foreign-engine evaluation, move-ranking label, pretrained network, opening book or tablebase was used.

Forty-two original middlegame/endgame feature contributions were fitted with regularisation, holding material and tempo fixed. Expected-outcome validation squared error fell from 0.1288653888 to 0.1272463325, a 1.26% relative error reduction. This is prediction error, not move accuracy or a win-rate gain. Runtime inference remains C++; Python performs offline fitting and match orchestration.

A 128-game selection screen compared full corrections, half corrections and the original evaluator. The half correction advanced to a fresh 384-game confirmation, together with a quiet-check/history variant. Balanced human opening prefixes came from games excluded from all fitting and validation. Prefix sets were also separate between selection and confirmation. These positions are supplied to the test harness only; the engine contains no opening lookup. The starting filter used an absolute score of at most 150 centipawns from our own baseline; this does not prove objective equality.

| Version | GNU Chess 6.3 W–D–L | Stockfish 19 Skill 5 W–D–L | Unfinished | Own technical failures |
|---|---|---|---:|---:|
| Recommended checkpoint | 1–2–61 | 21–19–24 | 0 | 0 |
| Half fitted correction | 1–3–60 | 19–26–19 | 0 | 0 |
| Half correction + quiet checks/history | 1–2–61 | 23–14–26 | 1 | 0 |

The half-correction candidate improved matched point score by 1.56 percentage points, with an approximate descriptive 95% interval of −5.58 to +8.71 points. The interval includes a regression. It failed the positive-lower-bound gate and was **not promoted**. Skill 5 is a reduced UCI setting, not a Lichess level or full-strength Stockfish. Strong opponents still win most GNU games. A draw is half a point; unfinished games receive no win/draw credit.

## Parallel search and clock allocation

The experiments add private search tables per C++ worker, atomic shared root bounds and cancellation, configurable UCI Threads, and soft/hard thinking budgets based only on the engine's own iteration changes. Explicit short move-time limits remain bounded. One variant searches the previous best root move before scheduling remaining moves; another restores late quiet-root reductions with a full-depth re-search whenever the reduced result improves the bound. The original-evaluation variants isolate search changes from fitted weights.

The host has 10 CPU cores. The parallel engine uses up to four root workers by default, while external opponents use one thread. Tests run concurrently on the local machine. These conditions are not an equal-CPU Elo comparison. Small depth samples did not show a higher median completed depth, so a universal parallel speedup is not claimed.

The first fitted parallel executable completed a standard-start **180+2 draw against GNU Chess 6.3** as White, 225 plies, with no recorded illegal move, crash or time forfeit. The rules-only harness stopped when a legal fifty-move claim became available by an intended move. This is an offline simulation, not a completed live Lichess game. One draw is not proof of superiority. The same frozen executable lost its 600+5 game as Black after 209 plies, with no recorded technical failure. Further exact-version games are listed below.

## Reliability and reproducibility

Feature accounting and colour symmetry passed 2,000 positions; two fitted models matched their own native inference formula over another 2,000 positions. Rules/perft, capture generation, UCI clocks/stops and bounded synthetic mate tests passed for the recorded builds. Additional concurrency tests exercise actual worker searches and thread resizing. Address/undefined-behaviour and thread-sanitized test builds completed their finite checks; these are not an all-position proof. Leak detection was disabled for AddressSanitizer because this macOS runtime explicitly does not support it.

A separate signed-byte board-storage experiment preserved the fixed-depth tree on 304 fresh positions, but its limited timing sample measured only 1.002x median speed, below the 1.05x release threshold. It is not a demonstrated speed improvement and is not promoted on that result.

Source, frozen binaries, clean human corpus, matrix, fitted weights and provenance are in `source/cpp/experimental/human_learning/`. Per-game PGNs, executable hashes, plans and result summaries are in `learning-pass/`. Every saved completed match can be replayed with a rules-only checker. Capped games remain unfinished. Other engines are isolated offline opponents, and their evaluations are never requested for learning.

The original guide supports result-based fitting: https://docs.google.com/document/d/1FfH7e7Njdvlk9aBPa-Cj13Jg0Igffu6rI1QIfsw7eag/edit . Competition restrictions: https://docs.google.com/document/d/1AUgyug3T_akye_rt3oEtTY7yXywO1AVG7TO77v9Py-g/edit . Public human-game licensing: https://database.lichess.org/ . Clock-allocation research consulted at the abstract level: https://doi.org/10.3233/ICG-2009-32403 . No existing engine search/evaluation code was copied.

## Completed competition-clock records

<!-- CLOCK_TABLE_START -->
| Exact experimental build | Clock | Our colour | Result | Plies | Technical failure | Evidence |
|---|---|---|---|---:|---|---|
| Compact board | 180+2 | white | Loss | 106 | None recorded | [JSON](learning-pass/compact-gnu-180-2-white.json) / [PGN](learning-pass/compact-gnu-180-2-white.pgn) |
| Compact board | 600+5 | black | Loss | 115 | None recorded | [JSON](learning-pass/compact-gnu-600-5-black.json) / [PGN](learning-pass/compact-gnu-600-5-black.pgn) |
| Original-evaluation parallel | 180+2 | white | Draw | 150 | None recorded | [JSON](learning-pass/original-parallel-gnu-180-2-white.json) / [PGN](learning-pass/original-parallel-gnu-180-2-white.pgn) |
| Original-evaluation parallel | 600+5 | black | Loss | 77 | None recorded | [JSON](learning-pass/original-parallel-gnu-600-5-black.json) / [PGN](learning-pass/original-parallel-gnu-600-5-black.pgn) |
| Fitted parallel | 180+2 | white | Draw | 225 | None recorded | [JSON](learning-pass/parallel-gnu-180-2-white.json) / [PGN](learning-pass/parallel-gnu-180-2-white.pgn) |
| Fitted parallel | 600+5 | black | Loss | 209 | None recorded | [JSON](learning-pass/parallel-gnu-600-5-black.json) / [PGN](learning-pass/parallel-gnu-600-5-black.pgn) |
| Reduced-root parallel | 180+2 | black | Loss | 125 | None recorded | [JSON](learning-pass/reduced-gnu-180-2-black.json) / [PGN](learning-pass/reduced-gnu-180-2-black.pgn) |
| Reduced-root parallel | 600+5 | white | Draw | 86 | None recorded | [JSON](learning-pass/reduced-gnu-600-5-white.json) / [PGN](learning-pass/reduced-gnu-600-5-white.pgn) |

All listed games start from the standard initial position against GNU Chess 6.3, with books disabled. Runs overlap on the same 10-core Mac with other local tests. This is offline clock/playing evidence under shared CPU load, not an isolated-host Elo estimate. A draw may be claimed by an intended move under the rules-library policy. One GNU process needed forced cleanup after the first draw; no game move/clock failure was recorded.
<!-- CLOCK_TABLE_END -->

## Original-evaluation parallel comparison

The fresh 96-game batch compared the recommended checkpoint, a serial control, and four-worker original-evaluation root search. Against Stockfish Skill 5, the four-worker variant scored 9 wins, 6 draws and 1 loss; the checkpoint completed 6 wins, 4 draws and 5 losses, with one unfinished game. Against GNU, the four-worker variant lost all 16 games; the checkpoint had 1 win, 1 draw and 14 losses. The paired overall difference was +5.00 percentage points, approximate 95% interval [−8.69, +18.69]. The GNU regression and uncertain overall gain failed the gate. This variant remains experimental despite its separate standard-start 3+2 draw. More workers are not a universally stronger engine.

## Exact fitted-parallel final comparison

A final 64-game batch directly compared the exact fitted four-worker executable (`020658f1…`) that completed both competition-clock games with the checkpoint. Its 16 new balanced human prefixes were excluded from every previous selection/confirmation batch and all training/validation. Move limits were 0.3 seconds, with two concurrent workers, four own search threads and one opponent thread.

| Version | GNU Chess 6.3 W–D–L | Stockfish 19 Skill 5 W–D–L | Overall points | Technical failures |
|---|---|---|---:|---:|
| Checkpoint | 0–0–16 | 6–5–5 | 8.5/32 | 0 |
| Fitted parallel | 1–0–15 | 9–3–4 | 11.5/32 | 0 |

All 64 games completed. The matched point-score difference was **+9.375 percentage points**, approximate descriptive 95% interval **[−10.06, +28.81] pp**, over 16 colour-paired units. GNU and Skill-5 differences were +6.25 and +12.5 points respectively. The positive estimate is promising, but the lower bound is negative and the release gate was not met. The fitted parallel engine remains an experimental alternative; the recommended competition executable remains `b3f8f697…`. Its one GNU win here used a balanced human opening prefix, not the standard-start clock games.

Across this pass, four arena batches recorded 672 games: 670 completed and two remained unfinished at their caps. No arena technical failure was recorded. These are limited local test conditions, not 100% reliability, Lichess move accuracy, universal win probability or a guarantee of first prize. Exact standard-start clock games are accounted for separately in the table above. Source reproduction is byte-exact for the fitted parallel executable (`learning-pass/source-reproduction.json`).

All **eight** standard-start competition-clock games in this pass completed: three draws and five losses against GNU Chess, with no recorded technical failures. Each of the four frozen experimental builds completed both 180+2 and 600+5. The previous recommended executable remains unchanged because none of the new candidates passed its strength/performance gate.
