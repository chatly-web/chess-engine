"""Tournament grinder: continuous match simulation against a battery of opponents."""
import json, pathlib, sys, time, chess, chess.engine, chess.pgn

ROOT = pathlib.Path(__file__).resolve().parents[1]

OPPONENTS = [
    {"name": "Stockfish Level 0", "cmd": ["/opt/homebrew/bin/stockfish"], "level": 0, "protocol": "uci"},
    {"name": "Stockfish Level 1", "cmd": ["/opt/homebrew/bin/stockfish"], "level": 1, "protocol": "uci"},
    {"name": "Stockfish Level 2", "cmd": ["/opt/homebrew/bin/stockfish"], "level": 2, "protocol": "uci"},
    {"name": "Stockfish Level 3", "cmd": ["/opt/homebrew/bin/stockfish"], "level": 3, "protocol": "uci"},
]

def run_game(opp_spec, our_colour, movetime=0.2):
    ours = chess.engine.SimpleEngine.popen_uci([sys.executable, str(ROOT / 'engine/main.py')], timeout=30)
    other = chess.engine.SimpleEngine.popen_uci(opp_spec["cmd"], timeout=30)
    opts = {'Threads': 1, 'Hash': 32, 'Ponder': False}
    if opp_spec.get("level") is not None and 'Skill Level' in other.options:
        opts['Skill Level'] = opp_spec["level"]
    other.configure({k: v for k, v in opts.items() if k in other.options and not other.options[k].is_managed()})

    white = (our_colour == 'white')
    b = chess.Board()
    failure = None
    moves_log = []
    start = time.monotonic()
    
    try:
        while not b.is_game_over(claim_draw=True) and b.ply() < 240:
            side = b.turn
            engine = ours if side == white else other
            limit = chess.engine.Limit(time=movetime)
            t = time.monotonic()
            r = engine.play(b, limit, info=chess.engine.INFO_NONE)
            elapsed = time.monotonic() - t
            if r.move not in b.legal_moves:
                failure = f"illegal move by {'ours' if side == white else 'opp'}"
                break
            moves_log.append(r.move.uci())
            b.push(r.move)
        result = b.result(claim_draw=True) if failure is None else ('0-1' if side else '1-0')
    finally:
        for e in (ours, other):
            try:
                e.quit()
            except Exception:
                pass
            finally:
                e.close()

    duration = time.monotonic() - start
    g = chess.pgn.Game.from_board(b)
    g.headers.update(
        White='Clash' if white else opp_spec['name'],
        Black=opp_spec['name'] if white else 'Clash',
        Result=result,
        TimeControl=f"{movetime}s/move"
    )
    return {
        "opponent": opp_spec["name"],
        "our_colour": our_colour,
        "result": result,
        "plies": b.ply(),
        "duration": duration,
        "failure": failure,
        "pgn": str(g)
    }

def main():
    rounds = 2
    results = []
    all_pgns = []
    our_score = 0.0
    total_games = 0
    completed_games = 0
    wins = draws = losses = 0

    print("Starting tournament grind session...", flush=True)
    for r in range(rounds):
        for opp in OPPONENTS:
            for colour in ["white", "black"]:
                total_games += 1
                print(f"Round {r+1} | Clash ({colour}) vs {opp['name']}...", end=" ", flush=True)
                res = run_game(opp, colour, movetime=0.25)
                results.append(res)
                all_pgns.append(res["pgn"])
                
                # Calculate score
                res_str = res["result"]
                pts = 0.0
                if res_str == "1-0":
                    pts = 1.0 if colour == "white" else 0.0
                elif res_str == "0-1":
                    pts = 0.0 if colour == "white" else 1.0
                elif res_str == "1/2-1/2":
                    pts = 0.5
                if res_str != '*':
                    completed_games += 1
                    wins += int(pts == 1.0)
                    draws += int(pts == 0.5)
                    losses += int(pts == 0.0)
                our_score += pts
                print(f"Result: {res_str} ({pts} pts in {res['plies']} plies, {res['duration']:.1f}s)", flush=True)

    summary = {
        "total_games": total_games,
        "our_score": our_score,
        "completed_games": completed_games,
        "unfinished_games": total_games - completed_games,
        "wins": wins, "draws": draws, "losses": losses,
        "win_rate": wins / completed_games if completed_games else None,
        "score_rate": our_score / completed_games if completed_games else None,
        "games": [{k: v for k, v in g.items() if k != "pgn"} for g in results]
    }
    (ROOT / "grind-results.json").write_text(json.dumps(summary, indent=2))
    (ROOT / "grind-games.pgn").write_text("\n\n".join(all_pgns) + "\n")
    print(f"\nGrind complete! Final Score: {our_score}/{total_games} ({summary['win_rate']*100:.1f}%)", flush=True)

if __name__ == '__main__':
    main()

