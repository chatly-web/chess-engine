# Native C++ engine

The recommended UCI launch is `./engine/clash-native` on the tested Apple Silicon macOS machine. The previous Python engine remains available as `python engine/main.py`. Both are original AI-assisted implementations; organiser acceptance of AI assistance still needs confirmation.

Build on the hosting machine with `./build-native.sh` (C++17 compiler and threads required). A ready-to-run Apple Silicon executable and the complete source are included. A macOS executable does not run on Linux or Windows: rebuild there before the event. No chess engine library or external engine source is linked. Runtime Python is not required by the native executable.

## What changed

C++ now handles board state, legal move generation, checks, castling, en passant, all promotions, draw state, evaluation and search. Search uses iterative deepening, alpha-beta/PVS, capture/killer/history ordering, transposition storage, guarded null-move pruning, late-move reductions and quiescence. The search is independently implemented and is not a node-for-node replica of the Python search. Increasing search depth remains subject to the supplied clock; it never forces a fixed depth at the expense of the clock.

The native evaluation reproduces the Python default evaluation on 2,000 deterministic positions. `source/cpp/tables.h` contains this project's own material and piece-square tables. Regenerate it using `python source/cpp/generate_tables.py`, then rebuild. An optional `--weights PATH` supports validated table overrides at build time. Custom scalar overrides are deliberately rejected, rather than silently ignored. Runtime `CLASH_WEIGHTS` and the experimental scalar tuning file currently apply to Python only. Do not assume the native engine consumes that environment variable.

## Measured validation

- Starting-position perft depth 4: 197281 legal leaf positions.
- Kiwipete perft depth 3: 97862.
- Rook/pawn endgame perft depth 4: 43238.
- 2,000 positions: exact legal-move-set agreement with python-chess and zero default-evaluation differences versus Python.
- The same perft/differential suite passed an AddressSanitizer/UndefinedBehaviorSanitizer build without reported errors.
- At a 0.5-second requested move limit (about 0.45 seconds used), native completed depths 7/6/6/6 versus Python 5/4/4/3 across four positions. Different search heuristics and node-count conventions mean depth and node counts are not an Elo estimate.
- Eight colour-reversed games at a 0.05-second requested move limit: native won all eight against the current Python version. This is a small short-control sample, not proof of dominance at tournament controls.
- Protocol checks: mate, rook underpromotion, en passant, terminal positions, 30 low-clock samples over both colours, 20 interrupted searches with readiness checks, node caps, malformed-position recovery and a repetition root after an earlier search. Sub-50ms timings are observations, not hard real-time guarantees.

Results: `cpp-verification.json`, `cpp-speed.json`, `cpp-matches.json`, `cpp-matches.pgn`, `cpp-protocol.json`. Earlier tournament-clock reports concern the earlier Python sources identified by their hashes. They must not be attributed to C++.

Run validation with the project's Python test environment:

```sh
python source/cpp/verify.py
python source/cpp/protocol_test.py
python source/cpp/benchmark.py
```

The benchmark does not load an opening book into the engine. It uses deterministic random test starts only in the offline match harness. External opponents are optional, separate installations and never bundled in this repository. `source/external_arena.py --native` selects C++; no opponent scores, PVs, weights or analysis are imported for training.

## Event setup

Configure lichess-bot for UCI and the executable `clash-native` in `engine/`; no Python interpreter is needed for this launch. Disable online moves, books and tablebases. Keep the bot:play token private. Live Lichess testing is still required, as are the BOT account, organiser access to the repository, and submission of the separately scoped challenge token. Freeze the same executable for both tournament stages.

A separate full-strength Stockfish 19 game at a 0.25-second requested move limit ended in a normal loss after 60 plies. No technical failure was recorded. This remains a large strength gap; the native engine is not claimed to beat Stockfish.


## Native v0.6 performance candidate

The current build adds target-based attack detection, pawn-square lists/cached king positions within evaluation, direct king-ring enumeration, and precomputed move ordering scores. Evaluation weights and search decisions at a fixed completed depth were preserved. Across six depth-4 comparisons against commit `26817ac`, chosen moves, scores and searched node counts matched exactly; median elapsed-time speedup was 1.62x (range 1.53x–1.67x).

Twelve new colour-reversed matches against the previous C++ binary at a 0.1-second requested move limit yielded 5 wins, 3 draws and 4 losses (6.5/12). This is insufficient to establish a statistically reliable strength gain. Baseline binary hashes and a baseline rebuild script are provided; rebuilding the baseline requires a Git clone with the historical commit, not only the ZIP.

Two actual 180+2 games against Stockfish 19 configured with `Skill Level=3` were wins: White in 53 plies and Black in 44 plies. Both ended normally without recorded technical failures. Opponent threads were set to one and hash to 64 MB. These were concurrent local test games; they are not live Lichess tests, full-strength Stockfish wins, a reliable win-rate estimate, or a guarantee about the competition field.

The candidate repeated the 2,000-position differential tests, perft checks, UCI/clock/interruption checks and address/undefined-behaviour sanitizer run. See `native-improvement-summary.json`, `native-improvement-fixed.json`, `native-improvement-matches.json`, and the `native-v06-level3-*` reports/PGNs.

The BOT account has not been created. See `BOT-SETUP.md` for the remaining live-hosting and submission steps.
