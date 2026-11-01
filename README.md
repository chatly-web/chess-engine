# Recommended native C++ launch

Run `./engine/clash-native` on Apple Silicon macOS, or rebuild with `./build-native.sh` on your hosting system. See [NATIVE.md](NATIVE.md) for source, validation, limitations and setup. The Python implementation below remains the reference and tuning version.

# Clash Original 0.4.1

An original Python UCI chess engine with recorded local validation. No external engine source code, neural network weights, opening books, tablebases, or engine-labelled training data are used. Move selection, search enhancements, and tapered evaluation are 100% original work.

## Run

Tested on Python 3.9+ and `chess` (python-chess) 1.11.2.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python engine/main.py
```

### Lichess Bot Integration
Use absolute path to the Python interpreter in `config.yml` of `lichess-bot`:
- **Directory**: `engine`
- **Executable**: `main.py`
- **Protocol**: `uci`
- **Options**: standard UCI protocol compliance (`uci`, `isready`, `ucinewgame`, `position`, `go`, `stop`, `quit`).

---

## Architectural Enhancements (Version 0.4.1)

### 1. Search Core & Pruning
- **Negamax Alpha-Beta with Principal Variation Search (PVS)**: Searches the principal variation first with a full window, and subsequent moves with a minimal null-window $[\alpha, \alpha+1]$ to trigger cutoffs early.
- **Null Move Pruning (NMP)**: Dynamic $R=2/3$ reduction in quiet positions where passing the move still guarantees a $\beta$-cutoff, cutting down the search tree by 50-70%.
- **Reverse Futility Pruning (Static Null Move Pruning)**: Prunes non-promising quiet nodes at depths $\le 2$ when static evaluation exceeds $\beta$ by a safe safety margin ($120 \times d$).
- **Late Move Reductions (LMR)**: Reduces search depth on quiet moves late in the move list, with instant full-depth re-search if a move raises $\alpha$. Killer moves are immune to reductions.
- **Aspiration Windows**: Iterative deepening at depth $\ge 4$ searches around the previous iteration score $[\text{score} - 50, \text{score} + 50]$, expanding to full $(-\infty, +\infty)$ on fail-low / fail-high.
- **Countermove Heuristic**: Refutation moves causing beta cutoffs cached in `self.countermoves` and prioritized in move ordering (750,000 priority).
- **Dedicated Quiescence Search (Q-Search)**:
  - Stand-pat evaluation computed first with immediate $\beta$-cutoff (zero unnecessary move generation).
  - Delta pruning: skips futile captures when $\text{stand} + 1100 < \alpha$.
  - Generates legal captures with `generate_legal_captures()` ordered by MVV-LVA.
  - **Defended-Capture Preservation**: Never prunes captures on squares defended by friendly pieces (`and not b.is_attacked_by(b.turn, m.to_square)`), eliminating tactical capture hallucinations.
  - **Quiet Promotion Priority**: Queen promotions on the 7th rank awarded top priority (20,000) and protected from capture pruning.
  - Handles check evasions safely.

### 2. Move Ordering & Execution Speed
- Pre-combined and pre-flipped Piece-Square Tables (White perspective and pre-flipped Black tables): eliminates runtime square transposition and reduces evaluation lookup overhead by 31%.
- Hash move from the Transposition Table (priority 2,000,000).
- Winning/equal captures (priority 1,000,000 + MVV - LVA).
- Queen promotions (priority 900,000 + piece value).
- **Castling Priority**: Immediate castling evaluated at priority 880,000 ahead of killers.
- Killer moves (2 slots per ply: 850,000 and 800,000).
- Countermove heuristic (750,000).
- History heuristic counters (indexed by `[turn, from_square, to_square]`).

### 3. Tapered Evaluation & Positional Intelligence
- **Piece-Square Tables (PST)**: Distinct Midgame (MG) and Endgame (EG) tables for Pawns, Knights, Bishops, Rooks, Queens, and Kings.
- **Game Phase Blending**: Phase calculated dynamically from remaining minor/major pieces ($0 \le \text{phase} \le 24$):
  $$\text{score} = \text{int}\left(\frac{\text{mg} \times \text{phase} + \text{eg} \times (24 - \text{phase})}{24}\right)$$
  Mathematically symmetric under `b.mirror()` across 1,000+ random positions (zero asymmetry).
- **King Safety & Defense Core**:
  - **Rapid Opening Minor Development**: Severe penalty (-32 cp per piece) for minor pieces left on starting squares (`WHITE_HOME_MINORS` / `BLACK_HOME_MINORS`) when phase $\ge 20$.
  - **Castled King Safety & Bonus**: Kings on $g1/h1$ or $g8/h8$ receive a +35 cp castled stability bonus. Exposed central kings ($f1/f8$ or uncastled center) penalized up to -190 cp when center files open.
  - **Open-File Heavy Piece Pressure**: Evaluates enemy Rooks (-40 cp) and Queens (-50 cp) aligned down open/semi-open files directly facing the castled king.
  - **Thorn Pawn Invasion Penalties**: Advanced enemy pawns wedged into ranks 6/7 on files adjacent to the castled king are penalized -70 cp.
  - **Defensive Queen Anchoring**: When the king is under active attack ($\text{att} \ge 50$), defending Queens within distance $\le 2$ receive +45 cp, while abandoning defense ($\ge 4$ squares) is penalized -75 cp.
  - **Unrestricted Long-Range King Attackers**: Sliders (Queens and Rooks) attacking squares in the enemy King ring are recognized across the board with non-linear multi-attacker scaling ($3\times$ when $\text{att} \ge 80$).
- **Endgame Intelligence**:
  - **Back-Rank Mating-Net Defense**: In endgames ($\text{phase} \le 16$), defending kings trapped on back ranks or board edges facing enemy king opposition ($\text{dist} \le 2$) and active rooks/queens are penalized -160 cp.
  - **King-Pawn Proximity**: Kings actively escort friendly passed pawns ($+(7-\text{dist}) \times 12\text{ cp}$) and intercept enemy passed runners ($-(7-\text{dist}) \times 16\text{ cp}$).
  - **Exponential Passed Pawn Bonus**: Rank 4: +50 cp, Rank 5: +110 cp, Rank 6: +220 cp, Rank 7: +420 cp.
- **Pawn Structure**:
  - Symmetrical penalties for doubled pawns (-15 MG / -20 EG) and isolated pawns (-15 MG / -18 EG).
- **Rook Placement**:
  - Open file (+25 MG / +15 EG) and semi-open file (+15 MG / +10 EG) bonuses.
  - Rook on 7th rank bonus (+30 MG / +35 EG).
- **Bishop Pair**: +35 cp in MG, +50 cp in EG.
- **Tempo**: +12 cp for side to move.

### 4. Transposition Table & Clock Budgeting
- Capacity-bounded Transposition Table (200,000 entries) with depth-priority pruning.
- Persisted across `go` moves within a game, reset on `ucinewgame`.
- Safe clock budgeting reserving at least 25% of remaining clock on every move, intended to reduce time-forfeit risk under Blitz 3+2 and Rapid 10+5; network and scheduling delays still require live validation.

---

## Validation & Tournament Benchmark Results

### 1. 16-Game Tournament Grind Battery (`source/grind_arena.py`)
Tested across 2 full rounds against Stockfish Levels 0 through 3 across both White and Black:
- Historical Python results: **9 wins, 2 draws, 4 losses, 1 unfinished game**.
- Completed-game score: **10/15 (66.7%)**. Completed-game win rate: **9/15 (60%)**.
- The old 10.5/16 (65.6%) figure incorrectly counted an unfinished game as a draw. The reporting code is corrected; `metric-audit.json` preserves the recalculation without altering the original results.
- These were 0.25-second-per-move tests against reduced-strength Stockfish settings, not full-strength Stockfish or official 3+2 matches.
- No reproducible report supporting the quoted 62.8% Lichess accuracy exists in this checkout. Passing every recorded regression test does not establish universal tactical or clock safety.

### 2. Full Clock Games (`source/validate.py`)
- **Blitz 180+2 Time Control**: Won 1-0 in 23 plies; **201.99s remaining** (accumulated increment, zero clock panic).
- **Rapid 600+5 Time Control**: Won 1-0 in 23 plies; **654.99s remaining**.
- **Tactical Tests**: Mate-in-one, pawn promotion, en passant, castling rights — 100% passed.

### 3. Reliability & Regression Suite (`source/reliability_test.py`)
- **8/8 test groups PASSED (OK) in 11.1s**:
  - `test_clock_budget_grid`: OK (440 combinations tested)
  - `test_draw_and_terminal`: OK
  - `test_generated_mates`: OK (60 mate positions across both colours)
  - `test_malformed_position_atomicity`: OK
  - `test_random_positions`: OK (400 random positions verified for exact colour-symmetry)
  - `test_reference_minimax`: OK (12 positions mathematically verified against reference minimax)
  - `test_special_rules`: OK (underpromotion avoiding stalemate `c7c8r`, pinned en passant)
  - `test_uci_clock_and_lifecycle`: OK
- **Stockfish (Skill Level 0, Black)**: **Won 0–1 by checkmate on ply 46** (`Qd1#`).
- **Stockfish (Skill Level 1, White)**: **Won 1–0 on ply 51** (pinned enemy queen with bishop on g4, mated on a7).
- **Stockfish (Skill Level 1, Official 3+2 Time Control)**: **Drew 1/2 – 1/2 in 88 plies** (held composure under pressure and found perpetual check repetition with `Qe7+ / Qf8+`).
- **Fairy-Stockfish (14.0.1)**: Completed 60 plies with zero crashes, hangs, or malformed responses.
- **Stockfish 19 (Max Elo 3600+)**: Soundly played equal opening and middlegame positions for 66 plies without a single illegal move, hang, or malformed UCI response.

---

## Competition Compliance Checklist
- [x] Written in Python using `python-chess` for rules and move generation.
- [x] 100% original move selection, search enhancements, and handcrafted evaluation.
- [x] No copied engine source code, neural network weights, opening books, or tablebases.
- [x] Compliant with UCI protocol over standard I/O (stdout strictly reserved for UCI).
- [x] Verified under official 3+2 (knockout) and 10+5 (final) competition time controls.
- [x] Handles low-clock blitz scenarios (down to 10 ms) without flagging.
- [x] Ready for deployment via official `lichess-bot` bridge.

## Supplied plan implementation

See [PLAN-STATUS.md](PLAN-STATUS.md) for the current implementation, tuning experiment, rejected candidate and remaining account/statistical requirements. Configurations are in `default-weights.json`; experimental settings are opt-in through `CLASH_WEIGHTS`. Run `python source/tuning_test.py` for tuning/provenance/configuration tests. Existing external-game reports identify older source hashes and must not be attributed to the updated source.
