# Implementation status against the supplied plan

This is a historical implementation log. Current C++ source, validated release, BOT connection and public GitHub publication supersede the earlier pending statuses below. See [STRONG-SEARCH.md](STRONG-SEARCH.md), [NATIVE.md](NATIVE.md) and [BOT-SETUP.md](BOT-SETUP.md) for current status.

The current v0.4.1 work was preserved. This pass adds configuration, permitted-data tuning, experimental self-play validation, and correctness fixes. It does not establish tournament-winning strength.

## Implemented

- Existing alpha-beta/PVS, iterative deepening, quiescence, transposition cache, move ordering and UCI clock handling retained.
- Material and piece-square tables, passed-pawn tables, tempo, mobility coefficients, and shared evaluation coefficient magnitudes exposed in `default-weights.json`. Mirrored scalar terms intentionally share parameters so tuning retains colour symmetry. Structural constants and search-pruning margins are not treated as evaluation weights.
- Set `CLASH_WEIGHTS=../experimental-weights.json` when launching the engine to load a configuration. Relative paths resolve against `engine/`; no environment setting means the original defaults. Unknown keys, wrong table lengths and invalid values are rejected. Mobility is implemented with default weights zero pending evidence.
- Texel-style tuning in `source/tune.py`: completed game outcomes, conservative quiet filtering, grouped train/validation split by game, fitted sigmoid scale, coordinate descent and held-out model selection. This implementation tunes shared scalar coefficients; the exposed tables can be edited but automatic per-cell table tuning is not implemented.
- `source/sprt.py`: fixed-draw-probability WDL SPRT with documented independent-observation assumptions. This is an exploratory tool, not a pentanomial paired-game SPRT; paired correlation invalidates nominal independent-game error guarantees. No automatic promotion.
- `source/weight_match.py`: independent starting seeds, colours reversed, experimental versus default weights through UCI. Capped games remain unfinished rather than being counted as draws.
- Fixed a Black pawn-shield penalty sign, included halfmove clock in the transposition key, corrected reduced-depth re-search, prevented consecutive null moves, and restored terminal/draw detection and underpromotions in quiescence. Checkmate takes precedence over the fifty-move condition.

## Measured experiment

75 quiet positions from original-agent games; 55 training and 20 validation positions from disjoint game groups. Validation squared error improved from 0.017605 to 0.017351. Experimental weights then scored 3/8 in held-out self-play and the SPRT decision remained `continue`. Experimental weights were NOT promoted. This dataset and match sample are too small for a strength claim. Full per-game results are in `weight-validation.json` and PGNs in `weight-validation.pgn`.

External benchmark reports predating the user's v0.4.1 changes record losses to Stockfish at 3+2, Fairy-Stockfish at 3+2, and GNU Chess at 10+5. Those are not performance results for this updated source. Source hashes in those reports identify their tested versions. No opponent analysis was used as training data.

## Still dependent on resources or user action

- Larger human/self-play dataset and substantially larger controlled match testing. No statistical evidence currently supports promoting the experimental weights.
- Optional C++ move generator / compiled core and optional neural evaluator were not implemented. They are alternatives in the plan, not prerequisites for the Python UCI entry.
- Live lichess-bot validation, BOT account and private tokens require account setup. Never publish bot:play credentials. Confirm organiser acceptance of AI-assisted code.
- GitHub publication needs valid authentication. The located github.com credential returned HTTP 401. A broad Keychain scan was rejected by automatic approval review; no bypass was attempted. Use `gh auth login --hostname github.com --git-protocol https --web`, then publish with `gh repo create chess-engine --public --source . --remote origin --push` after checking that repository name is available.


## Native implementation update

The subsequent C++ implementation is complete and now recommended; see NATIVE.md. The earlier optional-C++ status above is historical. It passed differential move/evaluation tests, perft, sanitizer checks and eight short self-play matches against Python. Native runtime scalar tuning is not implemented, and the neural network remains optional and unimplemented. A 0.25-second-per-move game against full-strength Stockfish 19 was a normal loss after 60 plies; no illegal move or time failure was recorded. It was not a 3+2 game.
