# Minimal draw-search correction

`./engine/clash-draw-safe` keeps the profiled original history-search checkpoint's evaluation, clocks, table size and search policy, with one targeted correction: delta/SEE pruning cannot discard a legal capture whose child immediately has insufficient material. The broad endgame pruning change and larger-memory/countermove changes are disabled.

For `6k1/8/7b/8/5p2/8/8/2B3K1 w - - 0 1`, `Bxf4` immediately draws, yet the original direct quiescence probe returns −197 after discarding that capture. The correction preserves the available draw in 64 targeted cases and 500 further random sparse positions. Independent rules verify each terminal draw. These are finite search-property checks, not move accuracy or a solved endgame tablebase.

Normal validation passed three reference perfts, 2,000 legal/capture/promotion/symmetry positions, 84 shortest-mate puzzles, UCI/clock/stop checks and the draw cases. A 32-game screen against the previous checkpoint scored 10 wins, 15 draws and 7 losses; it is not an independent strength confirmation. The two additional genuine-clock GNU games—3+2 as White and 10+5 as Black—both ended in losses without recorded game failures. Their PGNs and independent clock arithmetic audit are in `counter-memory-pass/narrow-*` and `counter-memory-pass/independent-audit.json`.

The alternative is original C++ and has no runtime opening book, tablebase, foreign weights or engine calls. No neural model was trained. It is not enabled in the live BOT, and the existing default/ZIP remain unchanged. It does not establish dominance over GNU/Stockfish or a guaranteed prize.

Tested SHA256: `6e2abb852a87fa8c466f1f13c238eaaeb819c80876caf3d817dd29e4263c9bdb`.

Rebuild from the repository root with Clang/llvm-profdata and a Python environment containing python-chess, used only for offline profiling:

```sh
python source/cpp/experimental/pgo/build.py --plan counter-memory-pass/minimal-build-plan.json --source source/cpp/experimental/endgame_safe/engine.cpp --define CLASH_ENDGAME_Q=1 --work-dir build/draw-reproduce --output engine/clash-draw-safe-reproduce
python source/cpp/experimental/endgame_safe/test_draws.py --mode 1
```

Source/header/macros are checked before compilation. Rebuilding refuses existing work/output paths; an independently regenerated profile need not yield a byte-identical executable. All chess decisions remain in C++.
