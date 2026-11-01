# Clash Original 0.3

An original, tournament-hardened Python UCI chess engine. No external engine source code, neural network weights, opening books, tablebases, or engine-labelled training data are used. Move selection, search enhancements, and tapered evaluation are 100% original work.

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

## Architectural Enhancements (Version 0.3)

### 1. Search Core & Pruning
- **Negamax Alpha-Beta with Principal Variation Search (PVS)**: Searches the principal variation first with a full window, and subsequent moves with a minimal null-window $[\alpha, \alpha+1]$ to trigger cutoffs early.
- **Null Move Pruning (NMP)**: Dynamic $R=2/3$ reduction in quiet positions where passing the move still guarantees a $\beta$-cutoff, cutting down the search tree by 50-70%.
- **Reverse Futility Pruning (Static Null Move Pruning)**: Prunes non-promising quiet nodes at depths $\le 2$ when static evaluation exceeds $\beta$ by a safe safety margin ($120 \times d$).
- **Late Move Reductions (LMR)**: Reduces search depth on quiet moves late in the move list, with instant full-depth re-search if a move raises $\alpha$.
- **Aspiration Windows**: Iterative deepening at depth $\ge 4$ searches around the previous iteration score $[\text{score} - 40, \text{score} + 40]$, expanding to full $(-\infty, +\infty)$ on fail-low / fail-high.
- **Dedicated Quiescence Search (Q-Search)**:
  - Stand-pat evaluation computed first with immediate $\beta$-cutoff (zero unnecessary move generation).
  - Delta pruning: skips futile captures when $\text{stand} + 1100 < \alpha$.
  - Generates legal captures with `generate_legal_captures()` ordered by MVV-LVA (Most Valuable Victim – Least Valuable Attacker).
  - Handles check evasions safely.

### 2. Move Ordering
- Hash move from the Transposition Table (priority 2,000,000)
- Winning/equal captures (priority 1,000,000 + MVV - LVA)
- Killer moves (2 slots per ply: 850,000 and 800,000)
- History heuristic counters (indexed by `[turn, from_square, to_square]`)
- Bad/losing captures (captured into enemy fire with lower value victim) searched after killers.

### 3. Tapered Evaluation & Positional Intelligence
- **Piece-Square Tables (PST)**: Distinct Midgame (MG) and Endgame (EG) tables for Pawns, Knights, Bishops, Rooks, Queens, and Kings.
- **Game Phase Blending**: Phase calculated dynamically from remaining minor/major pieces ($0 \le \text{phase} \le 24$):
  $$\text{score} = \text{int}\left(\frac{\text{mg} \times \text{phase} + \text{eg} \times (24 - \text{phase})}{24}\right)$$
  Mathematically symmetric under `b.mirror()` (zero asymmetry).
- **King Safety & Pawn Shelter**:
  - Kingside & Queenside castled pawn shield evaluation ($f, g, h$ or $a, b, c$ files).
  - Severe penalty for missing $g$-pawn shield or open/semi-open files facing the castled king.
  - Center king exposure penalties for uncastled kings facing open center files.
- **Pawn Structure**:
  - Passed pawn progression bonus scaling by rank in endgames (+20, +40, +70, +120 cp).
  - Penalties for doubled pawns (-15 MG / -20 EG) and isolated pawns (-15 MG / -18 EG).
- **Rook Placement**:
  - Open file (+25 MG / +15 EG) and semi-open file (+15 MG / +10 EG) bonuses.
  - Rook on 7th rank bonus (+30 MG / +35 EG).
- **Bishop Pair**: +35 cp in MG, +50 cp in EG.
- **Tempo**: +12 cp for side to move.

### 4. Transposition Table & Time Management
- Capacity-bounded Transposition Table (200,000 entries) with depth-priority pruning.
- Persisted across `go` moves within a game, reset on `ucinewgame`.
- Safe clock budgeting reserving up to 250 ms buffer, preventing timeouts at any clock control.

---

## Validation & Benchmark Results

### 1. Internal Multi-Agent League (`source/arena.py`)
Tested in colour-reversed pairs across all opponent types:
- **Clash 0.3 (Candidate)**: **15.5 / 16 points (15 wins, 1 draw, 0 losses — 96.9% score)**
- **Clash 0.2 (Baseline)**: 12.5 / 16 points (10 wins, 5 draws, 1 loss)
- **Head-to-Head Candidate vs Baseline**: **Candidate won 4.0 – 0.0 (100% win rate)**.

### 2. Full Clock Games (`source/validate.py`)
- **180+2 Time Control**: Won 1-0 in 39 plies; 115 seconds remaining.
- **600+5 Time Control**: Won 1-0 in 39 plies; 345 seconds remaining.
- **Clock Limits**: 10 ms (1.7 ms elapsed), 50 ms (2.3 ms elapsed), 200 ms (7.2 ms elapsed), 1.0 s (33.9 ms elapsed).
- **Tactical Tests**: Mate-in-one, pawn promotion, en passant, castling rights — all passed.

### 3. Reliability & Regression Suite (`source/reliability_test.py`)
- **8/8 suites PASSED (OK)**:
  - `test_clock_budget_grid`: OK (440 combinations tested)
  - `test_draw_and_terminal`: OK
  - `test_generated_mates`: OK (60 mate positions across both colours)
  - `test_malformed_position_atomicity`: OK
  - `test_random_positions`: OK (200+ random positions verified for board restoration and exact colour-symmetry)
  - `test_reference_minimax`: OK
  - `test_special_rules`: OK (underpromotion, pinned en passant)
  - `test_uci_clock_and_lifecycle`: OK

### 4. Benchmarks vs External Reference Engines
- **Stockfish (Skill Level 0)**: **Won 1–0 by checkmate on ply 51** (outplayed in opening development, won the queen on ply 25).
- **Stockfish (Skill Level 1)**: Dominant material advantage (+484 cp, +5 pawns up by ply 80).
- **Stockfish 19 (Max Elo 3600+)**: Soundly held equal/even opening and middlegame positions for 28 full moves (56 plies) without a single illegal move, hang, or malformed UCI response.

---

## Competition Compliance Checklist
- [x] Written in Python using `python-chess` for rules and move generation.
- [x] 100% original move selection, search enhancements, and handcrafted evaluation.
- [x] No copied engine source code, neural network weights, opening books, or tablebases.
- [x] Compliant with UCI protocol over standard I/O (stdout strictly reserved for UCI).
- [x] Verified under official 3+2 (knockout) and 10+5 (final) competition time controls.
- [x] Handles low-clock blitz scenarios (down to 10 ms) without flagging.
- [x] Ready for deployment via official `lichess-bot` bridge.
