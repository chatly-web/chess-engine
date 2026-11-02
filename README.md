# Clash Native C++ chess engine

An original AI-assisted C++17 UCI engine for the DAU Chess Engine Clash-Off. The same frozen executable is used for **3+2 (180+2)** and **10+5 (600+5)**.

## Run the recommended engine

```sh
./engine/clash-native
```

The included executable targets Apple Silicon macOS. Rebuild on another hosting platform with a C++17 compiler:

```sh
./build-native.sh
```

Use the build script's validated flags. C++ handles every chess move, including rules, evaluation and search. Python is used only for offline tests/training and the separate Lichess bridge.

## Latest measured improvement

The current release adds mate-distance bounds, guarded shallow reverse-futility pruning and selective quiescence pruning to our existing PVS, iterative deepening, transposition table, null-move pruning, late-move reductions and check extensions. Evaluation weights are unchanged.

- **256 fresh validation games against the previous release:** 124 wins, 71 draws, 61 losses; **159.5/256 points (62.30%)**. Approximate pair-aware 95% interval: **57.99%–66.62%**.
- **Actual event-clock head-to-head:** **4–0** against the previous release, both colours at both 3+2 and 10+5. Four games alone are not a universal win-rate estimate.
- **11 completed clock games**, including stronger opponents: no recorded illegal move, crash or time forfeit. Stronger-opponent losses and the draw are retained in the report.
- Selected binary SHA256: `2dd66add6e79fce8082283f0f70368a8a17db9f147933ac8b61dd9c457c0b045`.

See [STRONG-SEARCH.md](STRONG-SEARCH.md) for all algorithms tried, independent batches, clock results, hashes, failures and limitations. This point score is against our previous engine; it is not Lichess move accuracy. No near-100% accuracy, full-strength Stockfish dominance or first-prize guarantee is supported.

## Validate or reproduce

Install the rules-only Python test dependency in a separate environment:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python source/cpp/verify.py
.venv/bin/python source/cpp/protocol_test.py
.venv/bin/python source/cpp/mate_tactics.py --binary engine/clash-native --label my-mate-check
```

The release passed perft, 2,000-position rules/evaluation differential tests, protocol/clock/stop tests and an address/undefined-behaviour sanitizer build. All 576 screen/validation PGNs and 11 complete clock reports were independently replayed. Finite passing checks do not prove universal tactical or hard real-time reliability. Use unique labels for new validation batches; existing evidence is protected from accidental overwrites.

## Competition hosting and provenance

BOT account: [ayushgohil](https://lichess.org/@/ayushgohil). BOT conversion and an authenticated bridge connection are verified. Completed live Lichess games remain to be tested. See [BOT-SETUP.md](BOT-SETUP.md) for the private allowlist, live tests, draw-claim setting and final submission requirements.

Search and evaluation are original AI-assisted implementations. No existing engine source, pretrained networks, opening books, tablebases, online move sources or external-engine analysis labels are used. Other engines are separately installed offline opponents only. Organiser acceptance of AI-assisted code should be confirmed. Credentials and populated bridge configuration stay outside the public repository and ZIP.

Implementation: [NATIVE.md](NATIVE.md). Previous C++ release: [LONG-PASS.md](LONG-PASS.md). Earlier own-game weight-fitting experiment: [TRAINING-CYCLE.md](TRAINING-CYCLE.md); its fitted weights were not promoted. Historical Python implementation: [PYTHON-REFERENCE.md](PYTHON-REFERENCE.md). Earlier plan log: [PLAN-STATUS.md](PLAN-STATUS.md).
