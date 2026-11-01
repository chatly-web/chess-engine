"""Held-out colour-reversed UCI selfplay for experimental weights."""
import sys,os,json,time,random,pathlib
import chess,chess.engine,chess.pgn
from sprt import test
ROOT=pathlib.Path(__file__).resolve().parents[1]
cmd=[sys.executable,str(ROOT/'engine/main.py')];env=dict(os.environ);env['CLASH_WEIGHTS']='../experimental-weights.json';clean=dict(os.environ);clean.pop('CLASH_WEIGHTS',None)
(ROOT/'weight-validation.pgn').write_text('')
scores=[];games=[]
for seed in (781,782,783,784):
 b0=chess.Board();rng=random.Random(seed)
 for _ in range(4):b0.push(rng.choice(list(b0.legal_moves)))
 for colour in (True,False):
  b=b0.copy()
  with chess.engine.SimpleEngine.popen_uci(cmd,env=env) as candidate,chess.engine.SimpleEngine.popen_uci(cmd,env=clean) as baseline:
   while not b.is_game_over(claim_draw=True) and b.ply()<244:
    e=candidate if b.turn==colour else baseline;r=e.play(b,chess.engine.Limit(time=.02));assert r.move in b.legal_moves;b.push(r.move)
  result=b.result(claim_draw=True);score=None if result=='*' else .5 if result=='1/2-1/2' else float((result=='1-0')==colour)
  if score is not None:scores.append(score)
  row=dict(seed=seed,candidate_white=colour,result=result,score=score);games.append(row);print(row,flush=True)
  g=chess.pgn.Game.from_board(b);g.headers.update(White='Experimental' if colour else 'Default',Black='Default' if colour else 'Experimental',Result=result)
  with open(ROOT/'weight-validation.pgn','a') as f:f.write(str(g)+'\n\n')
(ROOT/'weight-validation.json').write_text(json.dumps(dict(games=games,sprt=test(scores),promoted=False,note='Exploratory small paired sample; fixed-draw independent-game SPRT assumptions do not cover paired correlation. No automatic promotion.'),indent=2))
