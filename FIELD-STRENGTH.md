# External-opponent strength pass

Updated 2026-11-02 05:37 UTC.

Current recommended executable SHA256: `b3f8f697330f939fb121c8889d4786cde99df49bd8e9c62e20418ae13158b5e9`.

The recommended executable was selected using the predeclared external-field gate below. The same frozen C++ executable serves both competition controls.

## Original C++ changes

- Reuse per-ply move/scoring buffers and fixed pawn lists; avoid repeated board hashes and unnecessary exchange searches.
- Stop legal-existence tests after one legal move and return forced replies promptly.
- Reuse board transpositions with repetition, halfmove-clock and mate guards. This wider practical mode is a heuristic, not a general graph-history-interaction proof.
- Blend queen/king safety terms and add mobility. Material values, piece-square tables and evaluation coefficients are original project data.
- Preserve stable move-order ties with explicit ordinals; update piece hashes and king locations incrementally.
- Exit a quiet quiescence node before generating all captures when stand-pat already cuts off, while preserving legal-existence, draw and mate-bound handling.
- Test broader mobility, reduced quiescence pruning, quiet checks and blocked-passer scaling; retain failed variants without promoting them.

The king-cache/quiescence optimisation preserved moves, scores, depths and node counts over 204 positions including retained-table draw/mate cases, plus six depth-6 benchmarks. Its median elapsed-time speedup was about 1.23x over the preceding candidate in that six-position concurrent benchmark. Earlier allocation/hash changes measured about 1.27x against the old implementation. These are limited timing samples, not universal speed or strength claims.

## Preliminary screens

Screening selects candidates; it is not independent confirmation. Random eight-ply legal starts can have large colour advantages. Versions play both colours against the same opponent from the same starts. A draw contributes half a point. This is not move accuracy.

| Batch | Games | Candidate | Matched point-score difference | Approximate 95% interval |
|---|---:|---|---:|---|
| screen-a | 256 | balanced | -1.56 pp | [-15.29, +12.17] pp |
| screen-b | 384 | blend | +6.45 pp | [-0.35, +13.26] pp |
| screen-c | 256 | blendclock | +6.45 pp | [-2.34, +15.24] pp |
| forcing-screen | 96 | blendclock | +10.94 pp | [-2.46, +24.33] pp |
| passer-screen | 96 | passer | +5.00 pp | [-13.64, +23.64] pp |

The passed-pawn correction missed the predeclared selection criterion and was not selected. The final candidate keeps the blended evaluation with the search-preserving speed work. Stockfish Skill 3/5 are reduced UCI settings, not Lichess levels. Four opponent configurations use two separately installed engine implementations. Full-strength Stockfish and GNU Chess remain difficult opponents.

## Independent validation

The first batch compares the published engine and phase-one candidate: 48 new colour pairs per opponent at 0.15 seconds per move, four workers, 768 planned games. The final batch compares the published engine, phase-one control and frozen final candidate: 32 different colour pairs per opponent at 0.12 seconds per move, six workers, 768 planned games. The final selection was frozen before this batch. Books are disabled and opponent analysis is never requested. Both harnesses adjudicate a draw whenever the rules library says a legal draw claim is available; this includes claims by an intended repeating move. This policy is separate from the live BOT account preference.

### confirmation

| Version | Opponent | W–D–L | Completed | Points | Unfinished / failures |
|---|---|---|---:|---:|---|
| baseline | Stockfish19-Skill3 | 48–27–20 | 95 | 61.5 | 1 / 0 |
| baseline | Stockfish19-Skill5 | 24–24–47 | 95 | 36 | 1 / 0 |
| baseline | GNUChess6.3 | 3–6–87 | 96 | 6 | 0 / 0 |
| baseline | Stockfish19-full | 3–2–91 | 96 | 4 | 0 / 0 |
| candidate | Stockfish19-Skill3 | 65–19–12 | 96 | 74.5 | 0 / 0 |
| candidate | Stockfish19-Skill5 | 31–23–41 | 95 | 42.5 | 1 / 0 |
| candidate | GNUChess6.3 | 2–5–89 | 96 | 4.5 | 0 / 0 |
| candidate | Stockfish19-full | 3–1–92 | 96 | 3.5 | 0 / 0 |

| Version vs published baseline | Matched units | Point-score difference | Approximate 95% interval |
|---|---:|---:|---|
| candidate | 189 | +4.76 pp | [+1.00, +8.52] pp |

### final-confirmation

| Version | Opponent | W–D–L | Completed | Points | Unfinished / failures |
|---|---|---|---:|---:|---|
| baseline | Stockfish19-Skill3 | 26–19–19 | 64 | 35.5 | 0 / 0 |
| baseline | Stockfish19-Skill5 | 14–20–30 | 64 | 24 | 0 / 0 |
| baseline | GNUChess6.3 | 0–3–61 | 64 | 1.5 | 0 / 0 |
| baseline | Stockfish19-full | 2–1–61 | 64 | 2.5 | 0 / 0 |
| control | Stockfish19-Skill3 | 34–15–14 | 63 | 41.5 | 1 / 0 |
| control | Stockfish19-Skill5 | 21–20–23 | 64 | 31 | 0 / 0 |
| control | GNUChess6.3 | 0–7–57 | 64 | 3.5 | 0 / 0 |
| control | Stockfish19-full | 3–2–59 | 64 | 4 | 0 / 0 |
| candidate | Stockfish19-Skill3 | 35–12–17 | 64 | 41 | 0 / 0 |
| candidate | Stockfish19-Skill5 | 21–16–26 | 63 | 29 | 1 / 0 |
| candidate | GNUChess6.3 | 4–2–58 | 64 | 5 | 0 / 0 |
| candidate | Stockfish19-full | 3–3–58 | 64 | 4.5 | 0 / 0 |

| Version vs published baseline | Matched units | Point-score difference | Approximate 95% interval |
|---|---:|---:|---|
| control | 127 | +6.69 pp | [+1.78, +11.61] pp |
| candidate | 127 | +6.50 pp | [+1.32, +11.67] pp |

### Release gate

The gate requires a positive approximate 95% lower bound for candidate-minus-published point score, positive Skill-5 and nonnegative GNU differences, no recorded candidate technical failures, finite rules/protocol/history/mate/sanitizer checks, and exact-binary simulations at both 180+2 and 600+5. The phase-one comparison in the final batch is secondary descriptive evidence. If the final candidate scores lower than an already-qualified phase-one control, prefer that control.

Selection, planned gate, executable/source hashes and exact-source reproduction receipts are in `field-strength/selection.json`, `final-pass-plan.json`, `final-selection.json`, `reproducibility.json` and `v08-reproducibility.json`. The executable name and source basename matter for macOS linker metadata.

```json
{
  "phase1": {
    "state": "not_qualified",
    "checks": {
      "frozen_hash": true,
      "positive_matched_lower_bound": true,
      "skill5_positive": true,
      "gnu_nonnegative": false,
      "no_recorded_game_failures": true,
      "rules_and_symmetry": true,
      "protocol": true,
      "mate_subset": true,
      "history_subset": true,
      "exact_clock_hashes": true,
      "completed_clock_evidence": true,
      "no_own_clock_or_protocol_failure": true,
      "both_competition_controls": true,
      "sanitizer_checks": true
    },
    "comparison": {
      "matched_units": 189,
      "mean_point_score_difference": 0.047619047619047616,
      "approximate_95_interval": [
        0.010025979498906379,
        0.08521211573918885
      ],
      "per_opponent_difference": {
        "Stockfish19-Skill5": 0.08152173913043478,
        "GNUChess6.3": -0.015625,
        "Stockfish19-full": -0.005208333333333333,
        "Stockfish19-Skill3": 0.13297872340425532
      }
    },
    "candidate_completed_games": 383,
    "candidate_unfinished_games": 1,
    "candidate_field_failures": 0,
    "clock_games": 6,
    "unfinished_clock_games_excluded": 1
  },
  "final": {
    "state": "qualified",
    "checks": {
      "frozen_hash": true,
      "positive_matched_lower_bound": true,
      "skill5_positive": true,
      "gnu_nonnegative": true,
      "no_recorded_game_failures": true,
      "rules_and_symmetry": true,
      "protocol": true,
      "mate_subset": true,
      "history_subset": true,
      "exact_clock_hashes": true,
      "completed_clock_evidence": true,
      "no_own_clock_or_protocol_failure": true,
      "both_competition_controls": true,
      "sanitizer_checks": true
    },
    "comparison": {
      "matched_units": 127,
      "mean_point_score_difference": 0.06496062992125984,
      "approximate_95_interval": [
        0.013219365292068158,
        0.11670189455045152
      ],
      "per_opponent_difference": {
        "GNUChess6.3": 0.0546875,
        "Stockfish19-Skill3": 0.0859375,
        "Stockfish19-Skill5": 0.08870967741935484,
        "Stockfish19-full": 0.03125
      }
    },
    "candidate_completed_games": 255,
    "candidate_unfinished_games": 1,
    "candidate_field_failures": 0,
    "clock_games": 4,
    "unfinished_clock_games_excluded": 0
  },
  "final_minus_phase1_matched_point_score": -0.007936507936507936,
  "recommended": "v08",
  "note": "Predeclared finite field gate; unfinished clock games are excluded, and both controls require completed exact-binary evidence. Approximate descriptive intervals apply to sampled-opening short games, not Elo, accuracy or a first-prize guarantee. The phase1-control comparison is secondary descriptive evidence."
}
```

## Finite reliability checks

- Exact final candidate: three perft totals of 197,281; 97,862; 43,238, 2,000 legal/capture move-set comparisons, and 2,000 colour-mirror evaluation comparisons.
- UCI recovery, 30 clock samples, 20 stopped searches, terminal roots and node limits.
- Address/undefined-behaviour sanitizer build, with incremental piece-hash and king-location assertions after every move.
- 84/84 synthetic forced-mate checks; shortest mates reported separately. The exact count is in `v08-mate-tactics.json`.
- Retained-table repetition, 50-move and mate-priority regressions.
- The old Python evaluator comparison is explicitly disabled for the changed C++ evaluation. Rules, perft and symmetry checks still run.

These passing subsets do not prove universal tactics, accuracy, history safety or hard real-time behaviour.

## Standard-start competition-clock simulations

| Revision | Opponent | Control | Colour | Result | Technical failure |
|---|---|---|---|---|---|
| field-blendclock | GNU Chess 6.3.0 | 180+2 | black | loss (1-0) | none |
| field-blendclock | GNU Chess 6.3.0 | 180+2 | white | loss (0-1) | none |
| field-blendclock | GNU Chess 6.3.0 | 600+5 | black | loss (1-0) | none |
| field-blendclock | GNU Chess 6.3.0 | 600+5 | white | loss (0-1) | none |
| field-final-671eb096 | GNU Chess 6.3.0 | 180+2 | black | loss (1-0) | none |
| field-final-671eb096 | GNU Chess 6.3.0 | 180+2 | white | loss (0-1) | none |
| field-final-671eb096 | GNU Chess 6.3.0 | 600+5 | black | loss (1-0) | none |
| field-final-671eb096 | GNU Chess 6.3.0 | 600+5 | white | loss (0-1) | none |
| field-final-671eb096 | Stockfish 19 (Skill 5) | 180+2 | white | win (1-0) | none |
| field-final-671eb096 | Stockfish 19 (Skill 5) | 600+5 | black | unfinished (*) | none |
| field-final-671eb096 | Stockfish 19 (Skill 5) | 600+5 | white | win (1-0) | none |
| field-v08-b3f8f697 | GNU Chess 6.3.0 | 180+2 | white | loss (0-1) | none |
| field-v08-b3f8f697 | GNU Chess 6.3.0 | 600+5 | black | loss (1-0) | none |
| field-v08-b3f8f697 | Stockfish 19 (Skill 5) | 180+2 | black | loss (1-0) | none |
| field-v08-b3f8f697 | Stockfish 19 (Skill 5) | 600+5 | white | draw (1/2-1/2) | none |

Unfinished games are excluded from strength scores. Technical opponent forfeits, if any, are labelled separately. Clock results apply only to their recorded binary hash. Earlier candidate games do not substitute for exact-final-binary tests. These are local simulations; completed live Lichess games still require verification.

## Provenance and limits

All chess decisions use the original C++17 engine. Python schedules offline games, verifies rules and runs the separate Lichess bridge. Games do not automatically train a neural model; search/evaluation changes are selected by outcomes and checked on fresh games. No foreign engine source, pretrained networks, opening books, tablebases or opponent analysis labels enter the engine. The optional loss review contains only our own engine scores.

No near-100% accuracy, wins against every engine or first-prize guarantee is supported. Local scheduling, short move budgets, unseeded opponent skill randomness and sampled openings limit inference. Approximate paired-unit intervals describe these tests, not Elo or tournament win probability. Historical 62.8% accuracy and own-engine point scores are different measurements and cannot be used as this pass's baseline.

Completed PGNs, outcome records, hash associations and per-move clock arithmetic are audited with `source/verify_field_results.py`. Credentials and populated bridge configuration stay outside the public repository and ZIP.
