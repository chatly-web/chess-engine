"""Match-based evaluation of original engines only; no external analysis."""
import chess,chess.pgn,json,random,time,pathlib,argparse
from search import Search
from baseline_v02 import Search as Baseline
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Material(Baseline):
 def evaluate(self,b):
  values=[0,100,315,335,510,950,0]
  v=sum((1 if p.color==b.turn else -1)*values[p.piece_type] for p in b.piece_map().values())
  return v
class Greedy:
 def __init__(self,positional=False):self.evaluator=Baseline() if positional else Material()
 def choose(self,b,seconds):
  best=-1e9;move=None
  for m in b.legal_moves:
   b.push(m)
   v=30000 if b.is_checkmate() else 0 if b.is_stalemate() else -self.evaluator.evaluate(b)
   b.pop()
   if v>best:best,move=v,m
  return move
FACTORIES={'candidate':Search,'baseline':Baseline,'material-search':Material,'positional-greedy':lambda:Greedy(True),'material-greedy':Greedy}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=float,default=.02);parser.add_argument('--pairs',type=int,default=2);args=parser.parse_args()
 rows=[];start=time.monotonic();pgn=open(ROOT/'arena-games.pgn','w')
 for competitor in ('baseline','candidate'):
  for opponent in ('baseline','material-search','positional-greedy','material-greedy'):
   for seed in range(args.pairs):
    initial=chess.Board();rng=random.Random(1100+seed)
    # Random legal starts are only in this offline harness, never an opening book.
    for _ in range(4):initial.push(rng.choice(list(initial.legal_moves)))
    for colour in (True,False):
     b=initial.copy();engines={colour:FACTORIES[competitor](),not colour:FACTORIES[opponent]()};elapsed={True:0.,False:0.};plies=0
     while not b.is_game_over(claim_draw=True) and plies<240:
      side=b.turn;t=time.monotonic();m=engines[side].choose(b,args.seconds);elapsed[side]+=time.monotonic()-t
      if m not in b.legal_moves:raise RuntimeError('illegal move')
      b.push(m);plies+=1
     finished=b.is_game_over(claim_draw=True);result=b.result(claim_draw=True) if finished else '*'
     score=(.5 if result=='1/2-1/2' else float((result=='1-0')==colour)) if finished else None
     row=dict(competitor=competitor,opponent=opponent,seed=seed,colour='white' if colour else 'black',result=result,finished=finished,score=score,plies=plies,seconds_per_search=args.seconds)
     rows.append(row);print(json.dumps(row),flush=True)
     game=chess.pgn.Game.from_board(b);game.headers.update(White=competitor if colour else opponent,Black=opponent if colour else competitor,Result=result,Termination='normal' if finished else '240-ply harness cap');print(game,file=pgn,end='\n\n');pgn.flush()
 pgn.close();summary={}
 for name in ('baseline','candidate'):
  games=[r for r in rows if r['competitor']==name];done=[r for r in games if r['finished']]
  summary[name]=dict(games=len(games),completed=len(done),unfinished=len(games)-len(done),wins=sum(r['score']==1 for r in done),draws=sum(r['score']==.5 for r in done),losses=sum(r['score']==0 for r in done),points=sum(r['score'] for r in done))
 (ROOT/'arena-results.json').write_text(json.dumps(dict(summary=summary,games=rows,duration=time.monotonic()-start,note='Small original-opponent league at short search budgets; not Elo or official TC validation. Unfinished games excluded from points.'),indent=2));print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
