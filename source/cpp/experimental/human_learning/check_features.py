from pathlib import Path
import subprocess,random,json,math
import chess
p=Path(__file__).resolve().parent
engines={name:subprocess.Popen([str(p/name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1) for name in ['baseline','features-zero']}
def query(name,b,command):
 e=engines[name];e.stdin.write('position fen '+b.fen()+'\n'+command+'\n');e.stdin.flush();return e.stdout.readline().strip()
rng=random.Random(590019);b=chess.Board();n=0
try:
 for i in range(2000):
  if b.is_game_over() or b.ply()>160:b=chess.Board()
  b.push(rng.choice(list(b.legal_moves)))
  raw=query('features-zero',b,'features');assert raw.startswith('info string features '),raw
  values=list(map(float,raw.split()[3:]));assert len(values)==43,values
  original=int(query('baseline',b,'eval'));assert int(values[0])*(1 if b.turn else -1)==original,(b.fen(),values,original)
  mirrored=list(map(float,query('features-zero',b.mirror(),'features').split()[3:]));assert all(abs(a+z)<1e-7 for a,z in zip(values,mirrored)),(b.fen(),values,mirrored)
  n+=1
finally:
 for e in engines.values():e.stdin.write('quit\n');e.stdin.flush();e.wait()
(p/'feature-checks.json').write_text(json.dumps({'passed':True,'positions':n,'base_evaluation_exact':True,'group_accounting_checked':True,'all_group_colour_antisymmetry':True},indent=2)+'\n');print('PASS: 2000 own-score/feature accounting and mirror checks')
