# Experimental profiling build

`engine/clash-pgo` is an alternative native Apple Silicon executable. It uses the exact original history-search C++ source and feature flags. Compiler instrumentation records branch/function execution frequencies from 24 human-game prefixes searched by our own engine at depth 5. A second compilation uses those frequencies to optimize machine code. No chess evaluation parameters, neural weights, third-party engine code or engine-scored training data are added. The training positions and compiler profiles are not used at runtime. This follows [Clang's instrumentation profiling workflow](https://clang.llvm.org/docs/UsersManual.html).

The 32 timing positions have game IDs disjoint from the training set. Serial tests alternate engine order with a fixed random seed. Across 64 paired depth-6 runs, the median speed ratio was **1.0891×** and total-time ratio **1.0828×**. A longer depth-8 confirmation recorded **1.0866×** median and **1.0852×** total-time ratio over another 64 pairs. Best move, score, nodes and completed depth matched the previous build in every paired run. These are finite timing results on this Mac, not universal throughput guarantees.

A separate, untuned 32-game comparison against `clash-history`, with both colours on 16 further prefixes disjoint from compiler training and timing, recorded **12 wins, 12 draws and 8 losses**, **56.25% game points**, approximate paired 95% interval **[40.44, 72.06]%**. Each engine had 0.12 seconds per move. A draw counts as half a point. There were no recorded technical failures or unfinished games; PGNs were independently replayed and results checked. This small sample does not establish an Elo gain, Lichess accuracy or dominance over stronger opponents. Timing improvements do not imply a proportional win-rate improvement.

Finite validation passed: three reference perft positions; 2,000 legal-position, capture/promotion and colour-symmetry checks; 84/84 synthetic shortest-mate cases; UCI special moves, node limits, malformed-input recovery, 30 low-clock samples and 20 interrupted searches. Four additional initial-clock move probes covered both colours at 3+2 and 10+5. Those four probes are **not full games**. Full-match results for the previous builds remain separate and unchanged.

The existing production executables, BOT configuration and release ZIP are unchanged. This is an experimental candidate, not an automatic event upgrade. Follow the event's requirement to use the same submitted version in both stages; any post-submission replacement needs organiser acceptance.

## Rebuild

Use matching Clang/llvm-profdata tools and a Python environment with python-chess. The build helper refuses to overwrite an existing output or reuse a work directory:

```sh
python source/cpp/experimental/pgo/build.py --plan pgo-pass/plan.json --work-dir build/pgo-new --output engine/clash-pgo-new
```

Build profiles are local development artifacts; compiler version and CPU can affect the produced binary and measured performance. The source is `source/cpp/experimental/history_order/build-history/engine.cpp`; its SHA and all training/test prefixes are recorded in `pgo-pass/plan.json`. The tested executable SHA256 is `d34dbc226ca49159fd632480a3bf94e89db2f4e17a12bd276d1ec65844861350`. Complete benchmark rows, match PGNs, validation reports and a summary are under `pgo-pass/`.
