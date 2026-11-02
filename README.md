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

BOT account: [ayushgohil](https://lichess.org/@/ayushgohil). See [BOT-SETUP.md](BOT-SETUP.md) for the private bridge, approved incoming challenges, live tests and submission requirements. Keep the Mac powered, awake and online while hosting.

Search and evaluation are original AI-assisted implementations. No existing engine source, pretrained evaluation networks, opening books, tablebases, online moves or opponent analysis labels are used. Other engines are separate offline opponents. Organiser acceptance of AI-assisted code still needs confirmation. Credentials stay outside the public repository and ZIP.

Near-100% accuracy, full-strength Stockfish dominance and first prize are not supported claims. Historical accuracy percentages and earlier own-engine point scores use different metrics and opponents.

Earlier release reports: [STRONG-SEARCH.md](STRONG-SEARCH.md), [LONG-PASS.md](LONG-PASS.md). Port details: [NATIVE.md](NATIVE.md). Historical Python implementation: [PYTHON-REFERENCE.md](PYTHON-REFERENCE.md).
