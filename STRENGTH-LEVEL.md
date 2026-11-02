# Stockfish skill calibration

The exact tested original C++ engine is `engine/clash-draw-safe`, SHA256 `6e2abb852a87fa8c466f1f13c238eaaeb819c80876caf3d817dd29e4263c9bdb`. This pass measures its opponent range without modifying its code, weights or parameters. The live BOT configuration is unchanged.

## Short-game screen

| Stockfish 19 Skill | Wins | Draws | Losses | Game points |
|---|---:|---:|---:|---:|
| 0 | 8 | 0 | 0 | 8/8 |
| 2 | 7 | 0 | 1 | 7/8 |
| 5 | 4 | 3 | 1 | 5.5/8 |
| 8 | 0 | 4 | 4 | 2/8 |
| 12 | 0 | 1 | 7 | 0.5/8 |
| 20 | 0 | 0 | 8 | 0/8 |

Each setting has eight games: four human-opening prefixes, both colours, 0.2 seconds requested per move. The same four prefixes are reused across settings for comparability; their game IDs exclude earlier fitting and prefix sets. They are test input, not a runtime book. The highest setting meeting the predeclared positive-score screen was Skill 5; screening does not establish guaranteed wins or a precise strength boundary between untested settings.

## Actual event-clock observations

| Skill | Control | Wins | Draws | Losses | Unfinished/failed | Games |
|---|---|---:|---:|---:|---:|---:|
| 2 | 3+2 | 1 | 0 | 0 | 0 | 1 |
| 2 | 10+5 | 1 | 0 | 0 | 0 | 1 |
| 5 | 3+2 | 1 | 0 | 1 | 0 | 2 |
| 5 | 10+5 | 1 | 1 | 0 | 0 | 2 |

These start from the standard position with real 180+2 or 600+5 clocks and no movetime override. Skill 5 plays both colours at each control. Skill 2 adds one White 3+2 game and one Black 10+5 game after both Skill 5 blitz games finish, retaining at most four concurrent full games. Games share the same Mac with up to four concurrent matches; this is not an isolated single-match hardware benchmark. Every PGN was legally replayed; each elapsed/remaining-clock update was independently recomputed. These are small preliminary observations, not proof of a stable win probability or single-game guarantee.

## GNU and scale limits

The same exact binary previously lost both full GNU Chess 6.3 games: White 3+2 and Black 10+5, with no recorded game failures. Those original results remain in `counter-memory-pass/narrow-clock-summary.json`. GNU is not assigned an invented Stockfish-equivalent level.

Stockfish 19 reports a Skill Level range 0–20; this is not a Lichess AI 1–8 setting or our engine's human Elo rating. The [official Stockfish FAQ](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html) explains that reduced skill intentionally selects weaker moves and that UCI_Elo takes precedence if strength limiting is enabled. The screen explicitly disables UCI_LimitStrength; fresh full-game engines use the verified default false. Stockfish uses one thread and 64 MB hash. Skill randomness is not seeded. Scores may differ with time, hardware, starting positions and randomness.

All six actual-clock games and 48 screen games are retained with identities, options, hashes and results. Opponent evaluations/PVs are not requested or fitted. No foreign chess intelligence, book or tablebase is incorporated into the original engine. No code change, live challenge, account modification or model deployment was performed in this calibration.
