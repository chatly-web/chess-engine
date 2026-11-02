# Clash Native C++ chess engine

An original AI-assisted C++17 UCI engine for the DAU Chess Engine Clash-Off. The same frozen executable is used for **3+2 (180+2)** and **10+5 (600+5)**.

## Run

```sh
./engine/clash-native
```

The executable targets Apple Silicon macOS. Rebuild on another hosting platform with a C++17 compiler:

```sh
./build-native.sh
```

C++ handles every chess move, including rules, evaluation and search. Python runs offline tests and the separate Lichess bridge. Use the validated build flags; the public source archive also preserves exact build provenance.

## Measured opponent level

See [STRENGTH-LEVEL.md](STRENGTH-LEVEL.md) for the frozen `clash-draw-safe` build’s Stockfish 19 Skill 0–20 screen and genuine 3+2 / 10+5 results. These are game scores, not Lichess move accuracy, a human Elo estimate or guaranteed wins. The live BOT configuration is unchanged.

## Completed aggressive validation

The timed pass completed **550 games**, including six full games at **3+2 and 10+5**, plus rules, mate, king-defence, draw, protocol and sanitizer checks. The larger-memory candidate scored **138 wins, 140 draws and 106 losses** against `clash-pgo` in 384 fresh short games (54.17% game points; conservative 97.5% interval 49.68–58.65%), but lost ground in the external comparison. It was not promoted. The running BOT and previous ZIP remain unchanged. See [COUNTER-MEMORY.md](COUNTER-MEMORY.md) for complete outcomes and limits.

The independently verified immediate-draw correction is available separately as `./engine/clash-draw-safe`; its source, tests, two genuine-clock GNU games and rebuild instructions are described in [DRAW-SAFETY.md](DRAW-SAFETY.md). This corrects a search blind spot; an overall strength gain or guaranteed prize is not established. Earlier broad endgame and work-preserving cache trials are retained in [AGGRESSIVE-TESTS.md](AGGRESSIVE-TESTS.md) and [EXACT-SEARCH.md](EXACT-SEARCH.md).

## Profiled C++ candidate

The separate `./engine/clash-pgo` candidate compiles the original history-search source using its own search execution profile. A 64-pair depth-8 confirmation measured a **1.087× median speed ratio** with identical moves, scores, nodes and completed depth. A separate 32-game comparison against `clash-history` recorded **12 wins, 12 draws and 8 losses** (56.25% game points; the approximate paired 95% interval crosses 50%). This establishes a measured execution-speed improvement on this Mac, not a reliable win-rate gain or Lichess accuracy. Finite rules, mate, protocol and both competition-control clock probes passed; the four full-clock move probes are not full games. The active BOT, existing builds and release ZIP are unchanged. See [PGO-BUILD.md](PGO-BUILD.md) for source, rebuild instructions, full results and the event version-freeze constraint.

## Latest search-order candidate

The original history-ordering candidate scored **91 wins, 99 draws and 66 losses** against the faster build across 256 short games: **54.88% game points**, with a corrected approximate 97.5% interval **[49.68%, 60.09%]** after one fixed independent replication. Against v0.8 it scored **31 wins, 19 draws and 14 losses** in another 64 games (63.28% game points). These are game scores under short fixed-move budgets, not Lichess move accuracy.

Run the ready-to-use original C++ alternative with `./engine/clash-history`; rebuild it with `./build-history-candidate.sh`. It learns bounded quiet-move priorities from its own search and ages them between moves. The evaluation coefficients and clock allocation are unchanged. In fresh 0.15-second external games, it recorded two GNU wins versus none for the faster reference, but lost all four full-clock GNU games. Its corrected comparison with the faster build remains inconclusive, so it stays experimental and the existing default is preserved. See [HISTORY-SEARCH.md](HISTORY-SEARCH.md) for full results, limits, original research sources, source and audits. These are candidates to choose before submission; the competition requires one submitted version for both stages.

A separate bit-mask attack prototype passed 640,000 attacked-square checks and preserved fixed-depth search results, but its 8.3% speed gain fell below its predeclared threshold for match collection. It remains a documented prototype: [BIT-ATTACKS.md](BIT-ATTACKS.md).

## Faster C++ alternative

A new original evaluation implementation completes the same fixed-depth work in about **17% less time** (paired median ratio 1.20). It scored **74 wins, 73 draws and 45 losses** against v0.8 in 192 fresh short games: **57.55% game points**, approximate paired 95% interval [52.26%, 62.84%]. This measures improvement against that checkpoint under the tested budget, not Lichess accuracy.

Run the ready-to-use faster alternative:

```sh
./engine/clash-fast
```

Rebuild it with `./build-fast-candidate.sh`. It uses original C++ incremental evaluation and shared mobility/king-pressure calculations. All coefficients, search heuristics and clock allocation are unchanged. The resolved external comparison gained points against Stockfish Skill 5 but lost the checkpoint's one GNU win, so it failed the GNU release condition and remains an **experimental alternative**. The recommended `./engine/clash-native` is unchanged. Both executables use their own single frozen implementation for 3+2 and 10+5. See [EVAL-FAST.md](EVAL-FAST.md) for complete results, caps/replays, checks and source.

## Tactical-strength experiment

Original C++ candidates add safe quiet checking moves and protect forcing pawn moves from search reductions. A focused king-defence check improved from 16/24 to 24/24 at requested main depth 1, but the selected candidate failed the fresh strength gate and lost all four standard-start GNU games at 3+2 and 10+5. It remains experimental; v0.8 stays recommended. The pass preserves 416 short games and four full-clock games. See [STRENGTH-FIRST.md](STRENGTH-FIRST.md) for complete results, finite-check limits, original sources and permitted competitive advantages.

## Search architecture validation

Original C++ variants add four-slot depth/age-based search-memory replacement and low-material null-move verification. The pass recorded416 short games and two full-clock GNU games. The selected table variant did not pass the independent strength gate, so v0.8 remains recommended. See [ARCHITECTURE.md](ARCHITECTURE.md) for source, results and limitations.

## Human learning and multicore experiments

A further pass fits original C++ evaluation weights from 23,803 quiet positions in permitted human games and tests four-worker root search at both competition controls. The fitted four-worker candidate had a +9.375 percentage-point estimate in matched game score in its final 64-game comparison, but its approximate interval [−10.06, +28.81] pp did not establish improvement, so it remains experimental. A fitted parallel prototype drew one standard-start 180+2 game against GNU Chess; this does not establish superiority. See [HUMAN-LEARNING.md](HUMAN-LEARNING.md) for complete results and limitations.

## Latest external-opponent validation

The selected build gained **+6.50 percentage points** in matched game-point score against the published baseline. Its approximate paired-unit 95% interval is **[+1.32, +11.67] pp**, over 127 completed matched colour pairs. The independent batch recorded 768 games across all tested versions.

These tests use matched random eight-ply starts and a 0.12-second requested move budget. They are separate from full competition-clock simulations. A draw is half a point; this is **not Lichess move accuracy or a universal win rate**.

| Opponent configuration | Selected W–D–L | Selected points / completed | Published baseline points / completed |
|---|---|---|---|
| Stockfish19-Skill3 | 35–12–17 | 41/64 | 35.5/64 |
| Stockfish19-Skill5 | 21–16–26 | 29/63 | 24/64 |
| GNUChess6.3 | 4–2–58 | 5/64 | 1.5/64 |
| Stockfish19-full | 3–3–58 | 4.5/64 | 2.5/64 |

## Competition-clock evidence

| Opponent | Control | Colour | Result | Technical failure |
|---|---|---|---|---|
| GNU Chess 6.3.0 | 180+2 | white | loss | none |
| GNU Chess 6.3.0 | 600+5 | black | loss | none |
| Stockfish 19 (Skill 5) | 180+2 | black | loss | none |
| Stockfish 19 (Skill 5) | 600+5 | white | draw | none |

Losses and draws are retained. These small concurrent local samples do not establish performance against every opponent. Live Lichess end-to-end games still need verification.

## Implementation and checks

The selected original search combines iterative deepening, PVS/alpha-beta, transpositions, capture/killer/history ordering, null-move pruning, late-move reductions, check extensions and selective quiescence. This pass adds reusable search storage, incremental hashing, guarded transposition reuse and blended king/queen safety with mobility.
Cached king locations and an earlier quiescence stand-pat exit reduce search overhead; a six-position fixed-depth comparison measured about 1.23x speed over the preceding candidate with identical moves, scores and nodes. This limited benchmark is not an Elo estimate.

- Three perft positions, 2,000 legal/capture move-set checks and 2,000 colour-mirror evaluation checks passed.
- UCI recovery, clock budgets, interrupted searches, terminal roots and node limits passed.
- Address/undefined-behaviour sanitizer checks passed; incremental hashes are verified in diagnostic builds.
- Synthetic mate and targeted repetition/50-move/mate-priority checks passed. Finite checks do not prove universal tactical or timing reliability.
- Selected binary SHA256: `b3f8f697330f939fb121c8889d4786cde99df49bd8e9c62e20418ae13158b5e9`.

Full variants, independent batches, clock records, rejected changes, hashes, limits and the release gate are in [FIELD-STRENGTH.md](FIELD-STRENGTH.md). Wider history-compatible transposition reuse remains a practical heuristic, not a general graph-history proof.

## Reproduce validation

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python source/cpp/verify.py
.venv/bin/python source/cpp/protocol_test.py
.venv/bin/python source/verify_field_results.py
.venv/bin/python source/qualify_field_candidate.py
```

The C++ evaluation intentionally changed from the historical Python reference. The default verifier always checks rules, perft and colour symmetry; `CLASH_COMPARE_EVAL=1` additionally compares the old Python evaluator and is suitable only for legacy evaluation variants. Rules and symmetry checks are not skipped.

## Hosting and provenance

BOT account: [ayushgohil](https://lichess.org/@/ayushgohil). The current private human trial uses the frozen `clash-history` candidate; human match results remain unverified. See [HUMAN-VALIDATION.md](HUMAN-VALIDATION.md). See [BOT-SETUP.md](BOT-SETUP.md) for the private bridge, approved incoming challenges, live tests and submission requirements. Keep the Mac powered, awake and online while hosting.

Search and evaluation are original AI-assisted implementations. No existing engine source, pretrained evaluation networks, opening books, tablebases, online moves or opponent analysis labels are used. Other engines are separate offline opponents. Organiser acceptance of AI-assisted code still needs confirmation. Credentials stay outside the public repository and ZIP.

Near-100% accuracy, full-strength Stockfish dominance and first prize are not supported claims. Historical accuracy percentages and earlier own-engine point scores use different metrics and opponents.

Earlier release reports: [STRONG-SEARCH.md](STRONG-SEARCH.md), [LONG-PASS.md](LONG-PASS.md). Port details: [NATIVE.md](NATIVE.md). Historical Python implementation: [PYTHON-REFERENCE.md](PYTHON-REFERENCE.md).
