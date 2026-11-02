# C++ search improvement and tournament-clock validation

Historical release `09f17cf`: the current recommended engine and newer results are in [STRONG-SEARCH.md](STRONG-SEARCH.md).

The promoted native release uses the same executable for **3+2** and **10+5**. It improves on our previous C++ baseline in a large independent short-control comparison. It does not approach a demonstrated 100% win rate against strong engines.

This improvement and validation session ran from **2026-11-01T18:46:57+00:00** to **2026-11-01T20:29:40.731439+00:00**, approximately **102.7 minutes**. The sustained frozen-binary league ran for 81.7 minutes within this session; full-clock matches overlapped with it. Timing and release metadata are in [session.json](long-pass/session.json).

## Changes selected by games

- Bounded check extensions preserve tactical replies in the main search.
- Aspiration windows from depth four retry with a full window on failure.
- An original static-exchange calculation demotes losing captures in move ordering. It does not prune captures.
- Quiescence generates captures and every promotion directly; check evasions still generate all legal moves and stalemate detection remains explicit. Six fixed-search comparisons preserved moves, scores and node counts, with median elapsed-time speedup 1.52x (range 1.06x–1.68x) over the same search without this optimisation.

Default evaluation weights are unchanged. The earlier fitted-weight experiment was rejected because its held-out results did not establish an improvement. No external engine scores, principal variations, weights or labels were used for fitting or selecting evaluation parameters. External engines were offline opponents only; the harness requests INFO_NONE.

## Frozen comparison

Previous release: commit `cfb06e1`, binary SHA256 `11274859f0388942c5c20ff261dd98336720976db7b4bb09bace66a2e0f76a3f`.

Promoted binary SHA256: `fd9318156a13b933a10301620943876782d3cd87eb53b87ce486c8839fa1ddd2`. This exact executable is included as `engine/clash-native` and `engine/clash-search-v08-candidate`. Source/compiler details: [build-manifest.json](long-pass/build-manifest.json).

The sustained validation ran with frozen binaries, 787 independently sampled starting-position pairs, eight random legal initial plies, colours reversed, and randomly chosen requested limits of 0.1 or 0.2 seconds per move. Several local matches ran concurrently. All **1,574 games completed**, with **818 wins, 353 draws and 403 losses** for the candidate: **994.5/1,574 points (63.18%)**, and **51.97% wins**. The approximate pair-aware 95% interval for point score is **61.31%–65.06%**. No technical failure was recorded.

This is a point score against the previous release under this test distribution, not Lichess move accuracy, tournament-field win probability or Elo. The conditional decisive-pair SPRT crossed its improvement boundary, subject to the sampling/stationarity assumptions in [final-analysis.json](long-pass/final-analysis.json). It is distinct from the point-score interval. Raw games and metadata: [sustained.pgn](long-pass/sustained.pgn), [sustained.jsonl](long-pass/sustained.jsonl), [sustained-summary.json](long-pass/sustained-summary.json).

Earlier 64-game screens scored 37/64 for check extensions plus aspiration and 38/64 after adding exchange ordering. A separate 128-game ablation removing exchange ordering scored 66/128 (49 wins, 34 draws, 45 losses); its SPRT remained inconclusive. That does not establish an independent benefit for exchange ordering, so the extensively validated combined candidate is retained. A further king-cache experiment showed mixed timing results and was not adopted. These exploratory screens are separate from the sustained held-out comparison.

## Actual tournament-clock games

These used real decrementing clocks and increments, standard starting positions, legal-move validation and timeout checks. Each row has both colours. External opponents used one thread and 64 MB hash where supported. Skill levels are reduced-strength settings, not full Stockfish.

| Clock | Our executable | Opponent | White result | Black result |
|---|---|---|---|---|
| 180+2 | Candidate | Previous native baseline | Win | Loss |
| 180+2 | Candidate | Stockfish 19, Skill Level 5 | Loss | Win |
| 600+5 | Previous native baseline | Stockfish 19, Skill Level 3 | Win | Draw |
| 600+5 | Candidate | Stockfish 19, Skill Level 3 | Win | Win |
| 600+5 | Candidate | GNU Chess 6.3.0 | Loss | Loss |
| 600+5 | Candidate | Stockfish 19, Skill Level 5 | Loss | Loss |
| 600+5 | Candidate | Stockfish 19, full strength | Loss | Loss |

All 14 clock games (12 candidate games and two baseline-reference games) ended normally, with no recorded illegal move, crash or time forfeit. The samples per opponent/control are small. The losses show a substantial strength gap against stronger engines. These are offline local games, not live Lichess games or an estimate of first-prize odds. All 1,574 league PGNs were independently replayed and all 14 clock reports had their legal moves, final results and clock arithmetic checked; see [artifact-audit.json](long-pass/artifact-audit.json). Full per-move clocks and PGNs are in `long-*.json/.pgn`; the baseline pair is in `long-pass/candidate-baseline-3plus2.*`.

## Rules, tactics and reliability

The candidate passed perft totals 197281, 97862 and 43238; 2,000-position differential checks for legal moves, captures/promotions and default evaluation; the address/undefined-behaviour sanitizer suite; and UCI checks covering special moves, terminal roots, malformed input recovery, node limits, 30 low-clock observations and 20 stop/readiness cycles. The promoted file repeated rules and protocol checks: `long-release-rules.json` and `long-release-protocol.json`.

An additional independent rules-only oracle generated 84 mate-in-one/mate-in-two cases across both colours. **83/84 chose a shortest mate**. The remaining move, `c1a1` in `k7/8/2K5/8/8/8/8/2Q5 w - - 0 1`, was exhaustively verified to force mate in three. Thus all 84 retained a bounded forced mate, while shortest-mate coverage was 98.8%. The original strict failure report is preserved as `long-pass/mate-tactics-strict.json`; the supplementary bounded proof is in `long-pass/mate-tactics.json`. The engine was not altered to fit this test. Finite passing checks are not universal tactical or hard real-time guarantees.

A clean rebuild had identical machine-code text and matched moves, scores, depths and node counts across the six fixed-search cases; UUID/signature metadata changes the whole-file hash. The frozen tested executable is delivered, rather than substituting the rebuild silently.

## Reproduce the checks

From the repository root, use a Python environment with `requirements.txt` installed for the harness, and a separately installed UCI opponent. External opponents are never bundled with the competition engine.

```sh
./build-native.sh
python source/cpp/verify.py
python source/cpp/protocol_test.py
python source/cpp/mate_tactics.py --binary engine/clash-native
# Repeat each clock with --colour black under another unique label.
python source/external_arena.py --native --opponent /absolute/path/to/opponent --base 180 --increment 2 --colour white --label my-3plus2-white
python source/external_arena.py --native --opponent /absolute/path/to/opponent --base 600 --increment 5 --colour white --label my-10plus5-white
```

For a new sustained comparison, retain the old binary before rebuilding and select a new output label:

```sh
python source/cpp/sustained_match.py --candidate engine/clash-native --baseline /absolute/path/to/old-native --minutes 90 --workers 4 --label my-new-validation
python source/cpp/analyse_sustained.py my-new-validation.jsonl --output my-new-analysis.json
```

These commands run real local games. Rebuilding creates a new platform executable; its measured performance must be validated again. Do not rebuild or run CPU-heavy benchmarks on the hosting machine during the competition.

## Hosting and remaining steps

BOT account `ayushgohil` is converted and authenticated; the bridge has connected with the promoted C++ executable. The private setup accepts only the user-approved friend's incoming challenges and disables matchmaking, external move sources and automatic chat. It prevents duplicate bridge instances. No completed live game is recorded yet. The friend should challenge the BOT to casual standard games at both controls, with both colours. Before competition, authorise the organiser accounts in the private allowlist and supply the separate `challenge:write` token through the designated private channel. See [BOT-SETUP.md](BOT-SETUP.md).

An actual prize or near-100% accuracy cannot be promised from these results. The defensible outcome is an improved original native engine, recorded full-clock wins and losses at both required controls, and a tested local hosting connection.
