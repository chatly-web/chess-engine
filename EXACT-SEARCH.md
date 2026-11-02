# Work-preserving cache prototype

This prototype was **not promoted**. Its median fixed-depth speed ratio was 1.0225× and total-time ratio 1.0221×, below the predeclared 1.10× threshold. No opponent matches were started for this prototype.

It keeps the narrow draw fix, skips an unused quiescence history-context hash, and tries the existing history-safe transposition return before generating legal moves. Draw and mate exceptions retain the original path. Evaluation, cutoff conditions, storage and clocks are unchanged.

The actual C++ search matched the narrow-fixed reference in 81 fixed-depth cases (move, score, nodes, depth), including sparse material, fifty-move boundaries and repetition histories with retained cache. Thirty-two further sparse positions matched at fixed depth6, and64 paired depth8 timing runs also matched. Rules, protocol,84 mate cases, address/undefined-behaviour sanitizer checks and564 draw-score comparisons passed. These finite checks are not a formal all-position proof or a strength improvement.

Source is in `source/cpp/experimental/exact_search/`; plans, raw timing rows and validation are in `exact-search-pass/`. The executable remains a local prototype and is not enabled in the BOT or included as a recommended engine.

Reproduce in a Python environment with python-chess and matching Clang/llvm-profdata:

```sh
python source/cpp/experimental/pgo/build.py --plan exact-search-pass/build-plan.json --source source/cpp/experimental/exact_search/engine.cpp --define CLASH_ENDGAME_Q=1 --define CLASH_TT_EARLY=1 --define CLASH_QCTX_FAST=1 --work-dir build/exact-reproduce --output engine/clash-exact-reproduce
```

The supplied helper checks source/header/macros and refuses existing work/output paths. This is original code and own-search profiling; no foreign engine intelligence, weights, runtime book or tablebase is used.
