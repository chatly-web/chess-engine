"""Texel-style tuning from human/own-game outcomes, never external scores."""
import argparse,json,pathlib,math,random,hashlib
import chess,chess.pgn
import search
ROOT=pathlib.Path(__file__).resolve().parents[1]
def probability(score,k):
 return 1/(1+10**max(-30,min(30,-k*score/400)))
def extract(path,output,source):
 rows=[];allowed={'candidate','baseline','material-search','positional-greedy','material-greedy','Clash'}
 with open(path) as f:
  while True:
   game=chess.pgn.read_game(f)
   if game is None:break
   if source=='selfplay' and any(game.headers.get(c) not in allowed for c in ('White','Black')):raise ValueError('Selfplay file contains an external opponent; rejected')
   if game.errors:raise ValueError('Invalid PGN')
   result={'1-0':1.,'0-1':0.,'1/2-1/2':.5}.get(game.headers.get('Result'))
   if result is None:continue
   gid=hashlib.sha256(str(game).encode()).hexdigest();b=game.board()
   for m in game.mainline_moves():
    b.push(m)
    if b.ply()<12 or b.ply()%4 or b.is_check() or b.is_game_over():continue
    # Conservative quiet filter: no legal capture or checking continuation.
    if any(b.is_capture(m) or b.gives_check(m) or m.promotion for m in b.legal_moves):continue
    rows.append(dict(fen=b.fen(),result=result,game=gid,source=source))
 pathlib.Path(output).write_text(''.join(json.dumps(r)+'\n' for r in rows));return len(rows)
def train(path,output):
 rows=[json.loads(l) for l in pathlib.Path(path).read_text().splitlines() if l.strip()]
 if any(r['source'] not in ('human','selfplay') for r in rows):raise ValueError('Disallowed data provenance')
 games=sorted({r['game'] for r in rows});random.Random(17).shuffle(games)
 if len(games)<4:raise ValueError('At least four independent completed games required')
 hold=set(games[:max(1,len(games)//4)]);train=[r for r in rows if r['game'] not in hold];valid=[r for r in rows if r['game'] in hold]
 if not train or not valid:raise ValueError('Empty train/validation partition')
 engine=search.Search();boards={r['fen']:chess.Board(r['fen']) for r in rows}
 def loss(data,k):
  return sum((probability(engine.evaluate(boards[r['fen']])*(1 if boards[r['fen']].turn else -1),k)-r['result'])**2 for r in data)/len(data)
 k=min([.25,.5,.75,1.,1.5,2.,3.],key=lambda k:loss(train,k));before=loss(valid,k)
 original=dict(search.EVAL_WEIGHTS);best=dict(original);bestvalid=before
 for _ in range(2):
  for key in sorted(original):
   old=search.EVAL_WEIGHTS[key];base=loss(train,k);chosen=old
   for v in (max(0,old-3),old+3):
    search.EVAL_WEIGHTS[key]=v;l=loss(train,k)
    if l<base:base,chosen=l,v
   search.EVAL_WEIGHTS[key]=chosen
  v=loss(valid,k)
  if v<bestvalid:bestvalid=v;best=dict(search.EVAL_WEIGHTS)
 search.EVAL_WEIGHTS.update(original)
 result=dict(weights=best,K=k,training_positions=len(train),validation_positions=len(valid),training_games=len(games)-len(hold),validation_games=len(hold),validation_before=before,validation_after=bestvalid,promoted=False,note='Experimental. Validation error is not playing strength; requires independent selfplay SPRT before promotion.')
 pathlib.Path(output).write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 e=sub.add_parser('extract');e.add_argument('pgn');e.add_argument('output');e.add_argument('--source',choices=['human','selfplay'],required=True)
 t=sub.add_parser('train');t.add_argument('data');t.add_argument('output');a=p.parse_args()
 print(extract(a.pgn,a.output,a.source) if a.command=='extract' else train(a.data,a.output))
