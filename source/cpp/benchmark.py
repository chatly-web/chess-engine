import chess,chess.engine,chess.pgn,pathlib,sys,time,random,json
ROOT=pathlib.Path(__file__).resolve().parents[2]
cmds={'native':[str(ROOT/'engine/clash-native')],'python':[sys.executable,str(ROOT/'engine/main.py')]}
rows=[];rng=random.Random(223);b=chess.Board();positions=[b.copy()]
for i in range(30):
 b.push(rng.choice(list(b.legal_moves)))
 if i in (7,15,23):positions.append(b.copy())
for idx,b in enumerate(positions):
 for name,cmd in cmds.items():
  with chess.engine.SimpleEngine.popen_uci(cmd) as e:
   t=time.monotonic();r=e.play(b,chess.engine.Limit(time=.5),info=chess.engine.INFO_BASIC|chess.engine.INFO_SCORE);elapsed=time.monotonic()-t
   assert r.move in b.legal_moves;rows.append(dict(position=idx,engine=name,depth=r.info.get('depth'),nodes=r.info.get('nodes'),elapsed=elapsed,move=r.move.uci()))
print(json.dumps(rows,indent=2),flush=True)
(ROOT/'cpp-speed.json').write_text(json.dumps(rows,indent=2))
games=[];pgn=[]
for seed in range(4):
 b0=chess.Board();rng=random.Random(5200+seed)
 for i in range(4):b0.push(rng.choice(list(b0.legal_moves)))
 for nativewhite in (True,False):
  b=b0.copy()
  with chess.engine.SimpleEngine.popen_uci(cmds['native']) as n,chess.engine.SimpleEngine.popen_uci(cmds['python']) as py:
   while not b.is_game_over(claim_draw=True) and b.ply()<244:
    r=(n if b.turn==nativewhite else py).play(b,chess.engine.Limit(time=.05));assert r.move in b.legal_moves;b.push(r.move)
  result=b.result(claim_draw=True);score=None if result=='*' else .5 if result=='1/2-1/2' else float((result=='1-0')==nativewhite)
  row=dict(seed=seed,native_white=nativewhite,result=result,score=score,plies=b.ply());games.append(row);print(row,flush=True)
  game=chess.pgn.Game.from_board(b);game.headers.update(White='Native' if nativewhite else 'Python',Black='Python' if nativewhite else 'Native',Result=result);pgn.append(str(game))
(ROOT/'cpp-matches.json').write_text(json.dumps(games,indent=2));(ROOT/'cpp-matches.pgn').write_text('\n\n'.join(pgn)+'\n')
