# Original adaptive search ordering

The ready-to-run experimental candidate is `./engine/clash-history`; rebuild it with `./build-history-candidate.sh`. Existing default and faster executables remain unchanged.

This pass tests search quality on top of the faster original C++ build. It preserves the evaluation coefficients and clock allocation while changing how the engine learns move-order preferences from its own search. The general history-heuristic idea is described in [Schaeffer's research](https://webdocs.cs.ualberta.ca/~jonathan/publications/ai_publications/pami.pdf); this project's implementation and parameters are independently written.

The selected variant bounds quiet-move history, rewards quiet cutoffs, penalizes earlier unsuccessful quiet moves, ages history before each root search, and avoids learning new history/killers in quiescence. A separate losing-capture ordering change was rejected by the screen. These heuristics guide search; no neural weights were trained and no other engine code, parameters or analysis were imported.

An own-engine diagnostic replay of a saved GNU loss observed no saturated history entries at the replay's limited depth/time. The code's lack of aging was therefore a hypothesis to test, not a confirmed explanation of that loss. The screen chose history-only at 53.125% game points; the combined and captures-only alternatives scored below 50% and were not carried forward.

Confirmation initially recorded 128 games against the faster build and 64 against v0.8, plus 128 matched external games and four full competition-clock GNU games. The initial faster-build interval crossed 50%, so one fixed independent replication of 128 games was added with an unchanged binary. The final pooled interval uses a 97.5% two-sided normal bound to account for two looks. Original results are preserved separately; the screen is excluded from the pooled estimate. This is a fixed replication, not repeated tuning until a favourable result.

All starting-game IDs exclude earlier fitting and test sets, with separate screen/direct/external/replication subsets. Common opening patterns, concurrent load and short fixed-move clocks still limit inference. Full-clock games use the same frozen engine for 3+2 and 10+5. Finite rules, protocol, mate, history, sanitizer, source and independent PGN/clock audits accompany the results.

<!-- RESULTS_START -->
## Completed results

| Direct opponent / batch | W–D–L | Game-point score | Interval |
|---|---|---:|---|
| Faster build, initial128 | 48–44–36 | 54.69% | 95% [48.24, 61.13]% |
| Faster build, independent128 | 43–55–30 | 55.08% | 95% [48.61, 61.55]% |
| v0.8,64games | 31–19–14 | 63.28% | 95% [53.45, 73.12]% |

The pooled comparison against the faster build is **91 wins, 99 draws and 66 losses**, **54.88% game points**, with corrected approximate **97.5% interval [49.68, 60.09]%**, over 128 complete colour pairs. The original screen is excluded. A draw counts as half a point; these are not Lichess accuracy or Elo measurements.

| External opponent | Candidate W–D–L | Candidate points / completed | Fast reference W–D–L | Fast points / completed |
|---|---|---|---|---|
| GNUChess6.3 | 2–1–29 | 2.5/32 | 0–2–30 | 1/32 |
| Stockfish19-Skill5 | 10–8–14 | 14/32 | 7–13–12 | 13.5/32 |

| Full-clock GNU game | Our colour | Result | Plies | Game technical failure |
|---|---|---|---:|---|
| 180+2 | white | loss | 128 | none |
| 180+2 | black | loss | 103 | none |
| 600+5 | white | loss | 198 | none |
| 600+5 | black | loss | 89 | none |

The pass recorded 544 short games, 0 unfinished/capped records and 0 recorded short-game technical failures, plus four full-clock games. Original losses and caps are retained. GNU needed post-game forced cleanup in 4 full-clock games after not answering quit within two seconds; that is separate from a move or clock failure.

**Promotion rejected.** The corrected pooled lower bound is below 50%, so superiority over the faster build was not established. Existing recommended and faster builds remain unchanged.

All reported matches are offline simulations. The result does not establish near-100% accuracy, GNU dominance, universal reliability or a guaranteed prize. Live Lichess play still needs verification.

Selected native SHA256: `bb117a724f65b35ab376f14afee837870176b95962363d7afc170aa60b663444`. Complete plans, controls, prototype outcomes, disjoint split audits, source, diagnostic limits, corrected intervals, PGNs, clock records and qualification are in `history-pass/` and `source/cpp/experimental/history_order/`.
<!-- RESULTS_END -->
