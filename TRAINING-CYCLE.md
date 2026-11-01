# Full-game self-play training cycle

This cycle learns original evaluation weights from complete engine-versus-engine games. It does not learn Stockfish moves, import an engine's evaluation labels, call an online service during play, or claim neural-network training. The recommended executable remains on the previous weights because the trained candidate did not establish an improvement.

## Completed dataset and fit

400 full short-control games were generated between copies of the original native engine: 153 White wins, 141 Black wins and 106 draws, with no unfinished games. They used 0.03-second requested move limits for data throughput. They are not 3+2 tournament results. Each run records its engine binary SHA256. Mirrored starting positions share a group identifier.

The conservative quiet-position extractor retained 1,295 labelled positions. Training and validation are separated by game group; canonical/mirrored positions shared with validation are removed from training. The fit used 1,011 training and 284 validation positions, from 140 and 46 groups with retained samples. Groups are not individual games. The sigmoid calibration is fitted on training only. Two passes of coordinate descent tune the shared scalar coefficients; this cycle does not optimise individual PST cells or train a neural network.

Held-out expected-outcome squared error changed from 0.0591216670 to 0.0588303533. That is prediction error, not Lichess accuracy and not evidence of better play.

## First independent match gate

The experimental candidate played 32 new games (16 colour-reversed starting-position pairs) against the previous default weights, at requested move limits of 0.05 and 0.1 seconds. Results: 9 wins, 11 draws, 12 losses, no unfinished games, 14.5/32 points. The paired decisive-pair SPRT remained `continue`. The candidate was NOT promoted. Sixteen pairs are a screening run and cannot cross the selected upper likelihood boundary even with all pair wins; larger independently sampled runs are required for an acceptance decision.

The SPRT compares conditional decisive-pair win probability H0=0.5 to H1=0.6, not Elo. Drawn pairs supply no evidence. Its nominal error bounds assume independent sampled pairs and stationary probabilities; they do not prove universal performance. Merely lowering fitting loss never triggers promotion.

## Executables and weight configuration

- `engine/clash-native`: recommended default, retaining the prior weights.
- `engine/clash-trained-experimental`: the tested experimental candidate, not recommended for submission based on this result.
- `trained-cycle-weights.json`: learned scalar values, fitting metadata and promotion status.
- `default-weights.json`: defaults for the recommended build.

Native scalar, tempo and mobility overrides are now supported at build time. Both competing engines always run as native C++ processes; Python is offline training and match orchestration only. Material and PST overrides remain supported. Native binaries embed a weight fingerprint in the UCI name. Runtime `CLASH_WEIGHTS` remains a Python-only setting. To rebuild an experimental executable without changing the default tables:

```sh
./build-trained.sh trained-cycle-weights.json engine/clash-trained-experimental
```

Both default and trained mappings matched the Python evaluation on 2,000 deterministic positions. A separate perturbed-parameter test also matched. The trained candidate passed move-generation counts and address/undefined-behaviour sanitizer checks. These are recorded tests, not a guarantee for all positions or hardware.

## Reproduce the cycle

Use the project's Python environment with `requirements.txt` installed:

```sh
python source/cpp/selfplay_cycle.py --games 400 --seconds .03 --workers 4
python source/tune.py extract training-selfplay.pgn training-cycle-data.jsonl --source selfplay
python source/tune.py train training-cycle-data.jsonl trained-cycle-weights.json
./build-trained.sh trained-cycle-weights.json engine/clash-trained-experimental
python source/cpp/validate_training.py --candidate engine/clash-trained-experimental --baseline engine/clash-native --pairs 16
```

For subsequent serious acceptance testing, use more pairs with fresh starting seeds and a preregistered gate, rather than repeatedly testing the same sample until a favourable result appears. Fixed short-control tests can screen candidates; they do not replace official-clock games on the hosting machine or live lichess-bot validation.

`source/cpp/clock_selfplay.py` runs two original builds against each other at 180+2 by default, one game per colour. It records every move and its clock, detects illegal moves and time forfeits, and leaves capped games unfinished. The completed exact-clock run is recorded in `clock-training.json` and `clock-training.pgn`: the newer default drew as White and lost as Black to the older original build, with no recorded technical failures. These games use the default and earlier original builds, not the experimental trained candidate. They were excluded from the first 400-game fit and included in the final 402-game fit below.

The final 40-game pilot files are retained with a `pilot-` prefix for provenance. The pilot did not support a weight change. No 100% accuracy or tournament-winning claim is made by this experiment.


## Final fit including the real-clock games

The combined corpus `match-training.pgn` contains 402 completed games: 400 short-control games and two complete 180+2 games. No opening book or opponent-engine evaluations were used. The strict quiet filter retained 1,296 positions: 1,017 training and 279 validation positions, separated into 141 and 46 game groups. Only one additional position passed the filter from the exact-clock games; adding a group also changed the deterministic group split. Therefore do not compare the two experiments' raw validation losses as though they used the same validation set.

`match-trained-weights.json` records the final fit. Within that split, validation squared error fell from 0.0584615802 to 0.0578184370. This is not a Lichess accuracy measurement. The original native implementation of the learned mobility term was slow; that candidate scored 24/64 in fresh matches and was not promoted (`slow-trained-validation.json`).

A C++ optimization computes the same mobility counts directly from piece directions, without testing all 64 target squares. It preserves moves, scores and node counts on six fixed-depth comparisons (`trained-inference-fixed.json`) and matches the Python evaluation on 2,000 positions with the final learned weights. The optimized experimental executable is `engine/clash-match-trained-efficient-experimental`. Rebuild it with `./build-trained.sh match-trained-weights.json engine/clash-match-trained-efficient-experimental`.

The efficient candidate then played 64 further games on new starting-position pairs, with both colours and two short move budgets: 24 wins, 18 draws and 22 losses, 33/64 points. The paired SPRT remained `continue`; this is not statistically established strength improvement. The slow and efficient match runs used different seeds, so their score difference cannot be attributed solely to the optimization. The exact fixed-depth timing comparison is the evidence for inference speed.

The recommended executable `engine/clash-native` retains default weights. The trained experimental builds are supplied for reproduction, not as proven event winners. The default and final trained candidate passed UCI/clock checks; the learned evaluator also passed an address/undefined-behaviour sanitizer build. The final fit, matches and complete per-game PGNs are supplied. No candidate was promoted on fitting loss alone.

There are 160 held-out validation games across the three candidate screens (32 + 64 + 64), in addition to the 402 training games and the 40-game pilot. This is a finite completed training cycle, not an indefinitely running promise to reach 100% accuracy. Update: BOT account `ayushgohil` and its authenticated bridge connection are now verified; completed live games and final submission still require verification. See LONG-PASS.md.
