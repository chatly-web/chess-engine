# Original tactical-strength candidates

The goal of this pass is better game outcomes, with 3+2 knockout performance primary. Node rate, memory reduction and reported depth are not acceptance objectives. The recommended executable stays unchanged until the recorded strength gate passes.

## Changes

- Safe non-capturing checking moves are included during the first 3 quiescence plies. Static exchange testing rejects checks that simply lose the checking piece when a legal capture resolves the check. Main-search check evasions and mate/draw handling remain intact.
- A second variant orders quiet pawn threats ahead of ordinary history moves and exempts them from late-move reduction: pawn advances to the 6th/7th rank or attacks on opposing non-pawn pieces. These rules are general; no game position or opening sequence is embedded in the engine.
- A guarded alternative also restricts transposition-score cutoffs to matching reversible history and disables static reverse-futility pruning.

| Frozen directory | Quiet checks | Pawn threats | History-score reuse | Static reverse futility |
|---|---:|---:|---|---|
| build-control | Off | Off | v0.8 heuristic | On |
| build-checks | On | Off | v0.8 heuristic | On |
| build-threats | On | On | v0.8 heuristic | On |
| build-guarded | On | On | Exact context | Off |

All evaluation weights, board rules and clock allocation remain those of the existing original engine. `conservative.cpp` is an own-engine diagnostic ablation, with several pruning mechanisms disabled; it is not a recommended competition executable.

## King survival and evidence

Checkmate already has terminal priority near 30000, above material (queen 950 MG). A bigger static king penalty is not the mechanism here. The search must see a threat soon enough to avoid it.

The independent king-defence generator builds valid positions where some legal moves allow an opponent mate-in-one and another move avoids it. Exhaustive legal replies classify those moves. At requested main depth 1, across 12 positions and colour mirrors, the checkpoint avoided immediate mate in 16/24 cases; all three tactical candidates passed 24/24. Added quiescence checks search beyond nominal main depth. These cases were constructed to test this horizon behaviour; they are not overall accuracy or match-strength measurements.

The own loss replay also exposed an apparent queen sacrifice for which four specific queen-retreat alternatives allow a forced mate-in-two. The rules-only audit verifies the checking move and all legal defending replies. Own-engine scores are diagnostic only; no GNU/Stockfish evaluations, PVs, tuned parameters or weights were used as training targets. The code derives general search rules from the investigation rather than storing the observed moves.

## Reproduce

From the repository root, compile a frozen candidate without replacing production:

```sh
exp=source/cpp/experimental/strength_first
c++ -std=c++17 -O3 -DNDEBUG -pthread \
  -DCLASH_SEARCH_V2=2 -DCLASH_TACTICAL_GEN=1 -DCLASH_EVAL_STYLE=3 \
  -DCLASH_SEARCH_V3=3 -DCLASH_TT_REUSE=2 \
  -DCLASH_QCHECKS=1 -DCLASH_PAWN_THREATS=1 \
  "$exp/build-threats/engine.cpp" -o "$exp/build-threats/clash-native"
```

For checks-only set pawn threats 0; for guarded set history reuse 0 and search V3 to 2. The control sets checks/threats 0, history reuse 2 and search V3 to 3. `build_candidates.py` preserves the baseline and generates the four source/configuration combinations. Binaries provided here target the tested Apple Silicon machine. All runtime search/evaluation remains C++; Python runs offline orchestration and rules-only checks.

Use the project's Python environment for `king_defence.py` and `rules_mate_audit.py`. The latter reads the packaged own-game diagnostic JSON. Replay labels beginning `reproduced-` preserve original evidence. The arena takes a JSON spec and a fresh result label; run it from the repository root. Complete plans, hashes, PGNs and decisions live in `strength-first-pass/` and the root `STRENGTH-FIRST.md`.

Sources are original project code. Checking quiescence extends this project's earlier experimental forcing-search idea with legal/static-exchange filtering and a bounded three-ply window. No existing engine source was imported. Rules explicitly permit independent search methods; see the organiser guidelines: https://docs.google.com/document/d/1AUgyug3T_akye_rt3oEtTY7yXywO1AVG7TO77v9Py-g/edit .

## Offline reproduction environment

The recorded interpreter was Python 3.12, with `chess==1.11.2` and `numpy==2.5.4`. NumPy is needed only to audit/recreate the human-prefix split. C++ inference does not import either package. GNU Chess 6.3.0 and Stockfish 19 are separate installed opponents and are not bundled in the submitted engine.

After compiling the desired candidate, from the repository root:

```sh
exp=source/cpp/experimental/strength_first
CLASH_NATIVE_BINARY="$exp/build-threats/clash-native" \
  CLASH_TACTICAL_CHECK=1 CLASH_VERIFY_REPORT=reproduced-tactical-rules.json \
  python3 source/cpp/verify.py
CLASH_NATIVE_BINARY="$exp/build-threats/clash-native" \
  CLASH_PROTOCOL_REPORT=reproduced-tactical-protocol.json \
  python3 source/cpp/protocol_test.py
python3 "$exp/audit_starts.py"
python3 "$exp/king_defence.py"
python3 "$exp/rules_mate_audit.py"
python3 "$exp/audit_results.py"
python3 "$exp/qualify_results.py"
```

For fresh matches, use a new label to preserve recorded evidence:

```sh
python3 source/cpp/experimental/strength_first/arena.py \
  --spec source/cpp/experimental/strength_first/confirmation-spec.json \
  --pairs-per-opponent 24 --seconds 0.25 --workers 3 \
  --seed-base 42100000 --label strength-first-pass/reproduced-confirmation
python3 source/cpp/experimental/strength_first/clock_arena.py \
  --our-binary source/cpp/experimental/strength_first/build-threats/clash-native \
  --our-revision tactical-threats --opponent /opt/homebrew/bin/gnuchess \
  --opponent-arg=--uci --base 180 --increment 2 --colour white \
  --label strength-first-pass/reproduced-gnu-blitz-white
```

Change the second command to each colour and each control (180+2 and 600+5) to cover the four cases. The packaged clock harness only changes repository-root discovery from the original workspace harness; saved games were generated by the latter. These commands reproduce the procedure, not necessarily exact wall-clock outcomes. The qualification script evaluates the original recorded labels and never installs a candidate.
