# External-field experiments (2 November 2026)

These original implementations are experiments. The recommended executable remains `engine/clash-native` until the independent validation gate recorded in `field-strength/selection.json` passes.

No foreign engine implementation or evaluation labels were used. Separately installed Stockfish and GNU Chess supply opponent moves and final results only. The test harness requests `INFO_NONE`; books are disabled.

All builds use C++17, `-O3 -DNDEBUG -pthread -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 -DCLASH_SEARCH_V3=3`. Add the evaluation macro listed below. Includes resolve to this project's unchanged `source/cpp/tables.h`.

| Screen name | Source in this directory | Extra flags | Change |
|---|---|---|---|
| fast | fast.cpp | none | Reusable search buffers, fixed pawn storage, fewer repeated hashes/exchange calls |
| fast2 | fast2.cpp | none | Earlier legal-existence exit, forced-reply time savings |
| balanced | eval.cpp | `-DCLASH_EVAL_STYLE=1` | Smaller queen/king safety terms |
| mobile | eval.cpp | `-DCLASH_EVAL_STYLE=2` | Balanced evaluation plus mobility |
| guarded | v10.cpp | none | Practical guarded board-transposition reuse, exact halfmove count |
| blend | v10.cpp | `-DCLASH_EVAL_STYLE=3` | Blended queen/king safety and mobility |
| mobility | v10.cpp | `-DCLASH_EVAL_STYLE=4` | Original safety terms plus mobility |
| cautious | v10.cpp | `-DCLASH_EVAL_STYLE=3 -DCLASH_SEARCH_V3=1` | Blended evaluation without quiescence delta/SEE pruning |
| ruleclock | v11.cpp | none | Clock-compatible transposition reuse |
| blendclock | v11.cpp | `-DCLASH_EVAL_STYLE=3` | Clock reuse plus blended evaluation |
| forcing | forcing.cpp | `-DCLASH_EVAL_STYLE=3` | Quiet checking moves in first quiescence ply |
| blendclock-sort | sort.cpp | `-DCLASH_EVAL_STYLE=3` | Preserve move-order ties explicitly without allocating stable sort |
| phase-one candidate | hash.cpp | `-DCLASH_EVAL_STYLE=3` | Incremental piece hashing on top of sorted variant |
| forcing-fast | forcing-hash.cpp | `-DCLASH_EVAL_STYLE=3` | Forcing-check variant with the same allocation/hash work |
| passer | passer.cpp | `-DCLASH_EVAL_STYLE=3` | Scale passed-pawn bonuses when the forward path is blocked |
| king | king.cpp | `-DCLASH_EVAL_STYLE=3` | Cached king locations, verified after moves in diagnostic builds |
| qking | qking.cpp | `-DCLASH_EVAL_STYLE=3` | King cache plus early quiescence stand-pat exit with legal-existence/draw checks |
| passer-king / passer-qking | corresponding .cpp file | `-DCLASH_EVAL_STYLE=3` | Combine the pawn variant with those optimisations |

Reproduce the frozen selected candidate from repository root:

```sh
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  source/cpp/experimental/field/hash.cpp -o blendclock-fast
cp blendclock-fast engine/field-candidate
```

The tested Apple Silicon build SHA256 is recorded in `field-strength/selection.json`. The output basename `blendclock-fast` preserves the tested macOS ad-hoc signing identifier; a different output name also changes the binary hash. Different compilers/platforms can produce different bytes. Add `-DCLASH_VERIFY_HASH=1` to a diagnostic build to recompute and check the incremental piece hash after every move. Sanitizer checks use this flag and address/undefined-behaviour sanitizers.

`CLASH_TT_REUSE=0` restricts score cutoffs to matching history context, `1` adds the bounded short-span experiment, and `2` selects the practical wider heuristic. Mode 2 checks repetition state, halfmove compatibility and mate range; it is not a general graph-history-interaction proof. The selected release mode and its limitations are recorded in FIELD-STRENGTH.md.

A declared evaluation change intentionally differs from the historical Python evaluator. Run `verify.py` with `CLASH_COMPARE_EVAL=0` only for those variants; legal/capture move sets, perft and 2,000 colour-mirror comparisons still run. The selected changed-evaluation release disables the historical Python comparison by default; set CLASH_COMPARE_EVAL=1 for original-evaluation variants. Legal, capture, perft and colour-symmetry checks always run.

## Final frozen candidate

`release/engine.cpp` adds cached king locations and an early quiescence stand-pat exit to the phase-one blended-evaluation candidate. It preserves the rules/draw/terminal handling in the tested search comparisons. No passed-pawn correction or quiet-check experiment was selected.

Build it with the same common flags and `-DCLASH_EVAL_STYLE=3`, using output basename `clash-native` to preserve macOS signing metadata:

```sh
mkdir -p build/final
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 \
  -DCLASH_SEARCH_V3=3 -DCLASH_EVAL_STYLE=3 \
  source/cpp/experimental/field/release/engine.cpp -o build/final/clash-native
```

The public-source rebuild matches frozen SHA256 `b3f8f697330f939fb121c8889d4786cde99df49bd8e9c62e20418ae13158b5e9` on the tested compiler/platform. `field-strength/qualification.json` records whether this candidate qualifies for the recommended release. Until qualified, `engine/field-final-candidate` is experimental. `baseline.cpp` archives our own previous published source, not third-party engine code.
