from pathlib import Path
import numpy as np,chess,chess.pgn,json,hashlib,subprocess
p=Path(__file__).resolve().parent;old=p.parent/'human_learning';used=set(np.load(old/'data/train-matrix.npz')['game_ids']);used.update(r['game_id'] for r in json.loads((old/'human-starts.json').read_text()));pool=[]
import gzip
with gzip.open(old/'data/human-clean.pgn.gz','rt') as f:
 while (g:=chess.pgn.read_game(f)) is not None:
  gid=g.headers['Site'].rstrip('/').split('/')[-1]
  if gid in used or g.errors:continue
  pool.append((hashlib.sha256(('architecture-v10:'+gid).encode()).hexdigest(),gid,list(g.mainline_moves())))
pool.sort();e=subprocess.Popen([str(p/'baseline')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1);starts=[];seen=set()
try:
 for _,gid,moves in pool:
  length=[8,12,16][len(starts)%3]
  if len(moves)<=length:continue
  b=chess.Board()
  for m in moves[:length]:b.push(m)
  if b.is_game_over(claim_draw=True) or b.epd() in seen:continue
  e.stdin.write('position fen '+b.fen()+'\neval\n');e.stdin.flush();cp=int(e.stdout.readline())
  if abs(cp)>150:continue
  starts.append({'game_id':gid,'moves':[m.uci() for m in moves[:length]],'plies':length,'own_baseline_cp':cp,'excluded_previous_pass_and_training':True});seen.add(b.epd())
  if len(starts)==160:break
finally:e.stdin.write('quit\n');e.stdin.flush();e.wait()
assert len(starts)==160
(p/'starts.json').write_text(json.dumps(starts,indent=2)+'\n');print('Prepared160 different human opening games, excluded from all previous opening sets and model fitting')
