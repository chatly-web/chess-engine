"""Generate permitted original-engine outcome data with auditable provenance."""
import concurrent.futures,pathlib,sys,random,json,time,hashlib,argparse
import chess,chess.engine,chess.pgn
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--games',type=int,default=40);p.add_argument('--seed-base',type=int,default=30000);p.add_argument('--seconds',type=float,default=.05);p.add_argument('--workers',type=int,default=4);a=p.parse_args();binary=ROOT/'engine/clash-native';sha=hashlib.sha256(binary.read_bytes()).hexdigest()
def play(index):
 rng=random.Random(a.seed_base+index//2);b=chess.Board()
 for _ in range(8):b.push(rng.choice(list(b.legal_moves)))
 # Mirror every second position so the training set includes colour-reversed starts.
 if index%2:b=b.mirror()
 with chess.engine.SimpleEngine.popen_uci(str(binary)) as w,chess.engine.SimpleEngine.popen_uci(str(binary)) as black:
  while not b.is_game_over(claim_draw=True) and b.ply()<320:
   r=(w if b.turn else black).play(b,chess.engine.Limit(time=a.seconds),info=chess.engine.INFO_NONE)
   if r.move not in b.legal_moves:raise RuntimeError('Illegal move in selfplay')
   b.push(r.move)
 result=b.result(claim_draw=True);g=chess.pgn.Game.from_board(b);g.headers.update(White='Clash',Black='Clash',Result=result,Event='Original selfplay training',EngineSHA256=sha,TrainingGroup=str(index//2))
 return dict(index=index,result=result,plies=b.ply()),str(g)
rows=[];games=[];start=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
 for row,pgn in pool.map(play,range(a.games)):
  rows.append(row);games.append(pgn);print(row,flush=True)
(ROOT/'training-selfplay.pgn').write_text('\n\n'.join(games)+'\n');(ROOT/'training-selfplay.json').write_text(json.dumps(dict(source='selfplay',engine_sha256=sha,games=rows,seconds_per_move=a.seconds,workers=a.workers,duration=time.monotonic()-start,note='Only own-engine moves and final results. Fixed short controls generate data; these are not official-clock tournament tests. Unfinished games excluded by extractor.'),indent=2))
