# Original human-result learning and parallel-search experiments

These are experimental C++ builds. The recommended competition executable remains `engine/clash-native` until a candidate meets the recorded match gate. No experiment is described as a guaranteed winner or as having a newly measured Lichess accuracy.

## What was learned

The collector exported public rated standard human games through the official Lichess API with `evals=false`, `accuracy=false`, `literate=false`, and rejected BOT titles. Both players were rated at least 2200, with an initial clock of at least 180 seconds. The clean snapshot contains 5,304 games. Of those, 3,087 games provided 23,803 quiet positions. Human final game results are the only training targets; feature values and base scores come from this project's original C++ evaluator. No opponent score/PV, existing engine weights, opening book, tablebase or puzzle solution is a training input.

A deterministic game-level split separates 19,143 training positions in 2,453 games from 4,660 validation positions in 634 games. Forty-two features represent middlegame/endgame contributions of 21 semantic groups. Material and tempo corrections are fixed at zero. Regularised squared expected-score fitting selects coefficients on the training/validation split. Validation expected-outcome squared error falls from 0.1288653888 to 0.1272463325, about 1.26% relative error reduction. This is not move accuracy, Elo or proof of stronger play. A costly added mobility feature was pruned before matches under a stated validation-error threshold; a half-sized correction was also tested.

Human training/validation games are excluded from all independent match starting prefixes. These prefixes are harness inputs only, never an engine opening book. Preliminary screening and fresh confirmation use different games. The 384-game learned-weight confirmation did not meet the predeclared positive lower-bound criterion, so fitted weights were not promoted.

## Search experiments

- Cache pure static evaluations by board hash; repetition and clock adjudication remain in search.
- Extend a bounded soft time budget when the engine's own completed iterations change substantially or its previous root evaluation falls. Explicit `movetime` budgets are unchanged.
- Test quiet-check ordering and an original bounded moving-average history heuristic.
- Split root moves across private worker search tables, sharing atomic bounds and cancellation only. The `parallel-original` version searches the preceding best root move before scheduling the others and retains the original evaluation. UCI `Threads` is configurable from 1 to the detected limit (capped at 8), with default 4 or available cores if fewer. Node-limited and very short searches use the serial path.

More cores consume more hardware. Parallel/serial match scores are not equal-CPU Elo measurements. Selective root search, private tables and scheduling can change moves; parallelism is not asserted to preserve the serial tree. Finite correctness checks do not establish all-position correctness.

## Frozen builds

`build-trained`, `build-half`, `build-candidate` (adaptive clock), `build-tactical` (quiet checks/history), `build-parallel` (fitted residual and parallel search), `build-parallel-pv` (first root move first), `build-parallel-reduced` (guarded late-root reductions) and `build-parallel-original` contain original source, headers and the tested macOS ARM executables. `feature-source` is the zero-residual extractor snapshot. `snapshot-sha256.json` records original bytes before this README was added. Source/binary basenames may affect local macOS linker metadata. Match records identify the actual executable hashes.

Compile a frozen directory, without modifying the recommended engine:

```sh
exp=source/cpp/experimental/human_learning
variant=build-parallel-original
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_MOVE_ORDER_STYLE=0 \
  "$exp/$variant/engine.cpp" -o "$exp/$variant/clash-native"
```

Use `CLASH_MOVE_ORDER_STYLE=1` for tactical and fitted parallel variants; use 0 for the original-evaluation variant. All inference and move search run in C++; Python is offline collection, fitting and match orchestration.

## Reproduce the fit

From the repository root, use Python 3.12 in a separate virtual environment with `python-chess==1.999`, `numpy==2.5.4`, `scipy==1.18.1`. The included clean human PGN and matrix make another network download unnecessary. Decompress `data/human-clean.pgn.gz` to `data/human-clean.pgn` to rerun preparation. The `features-zero` executable is platform-specific; on another platform compile `feature-source/engine.cpp` with the same search/evaluation macros into `features-zero` first.

```sh
python source/cpp/experimental/human_learning/prepare_data.py
python source/cpp/experimental/human_learning/fit_weights.py
```

`data/manifest.json` records source URLs, export/clean hashes and accepted game IDs. `data/preparation.json`, `model.json`, `candidate-selection.json` and inference/feature checks document the dataset and fit. Game exports are public data; no account token is needed. Lichess publishes its game database under CC0: https://database.lichess.org/ . The separately provided Stockfish evaluation database and puzzle solution labels were not used.

The supplied arena scripts take explicit frozen binary paths and a JSON spec; run them from the repository root. Reproduction labels must be fresh to avoid overwriting evidence. The supplied specs record the original opening sets and model mapping. Opponents run as separate executables with analysis collection disabled. Do not feed opponent evaluations into fitting. Actual-clock records have a 600-ply cap; capped games remain unfinished. See the root `HUMAN-LEARNING.md` and `learning-pass/` for results, gates and limitations.

## Research and provenance

The competition's own building guide describes result-based evaluation fitting and permits human game databases: https://docs.google.com/document/d/1FfH7e7Njdvlk9aBPa-Cj13Jg0Igffu6rI1QIfsw7eag/edit . Its competition rules prohibit foreign engine analysis and pretrained weights: https://docs.google.com/document/d/1AUgyug3T_akye_rt3oEtTY7yXywO1AVG7TO77v9Py-g/edit . Research on time management supports investigating clock allocation, not any claimed measured gain for this implementation: Solak and Vuckovic, *Time Management During a Chess Game*, https://doi.org/10.3233/ICG-2009-32403 (abstract consulted). All search, fitting, feature and threading implementation here is original AI-assisted project code; no existing engine source was copied.

The separate `build-compact` signed-byte board experiment and `build-context` quiescence-context experiment preserve the fixed-depth search in their differential samples, but neither limited timing sample established the required 1.05x median speedup. They are not recommended replacements. `verify_experiment.py` checks an explicit binary; `audit_results.py` replays saved match artifacts using rules only.

Verify the supplied source/data independently from the repository root:

```sh
python source/cpp/experimental/human_learning/audit_data_split.py
python source/cpp/experimental/human_learning/check_features.py
python source/cpp/experimental/human_learning/check_inference.py
python source/cpp/experimental/human_learning/audit_results.py
```
