from pathlib import Path
import subprocess,json,random,math
import chess
root=Path(__file__).resolve().parent;selection=json.loads((root/'candidate-selection.json').read_text());binaries={'features':root/'features-zero','trained':root/'build-trained/clash-native','half':root/'build-half/clash-native'}
engines={k:subprocess.Popen([str(v)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1) for k,v in binaries.items()}
def query(k,b,cmd):
 p=engines[k];p.stdin.write('position fen '+b.fen()+'\n'+cmd+'\n');p.stdin.flush();return p.stdout.readline().strip()
rng=random.Random(191221);b=chess.Board();checked=0;tolerance_cases=0
try:
 for i in range(2000):
  if b.is_game_over() or b.ply()>180:b=chess.Board()
  b.push(rng.choice(list(b.legal_moves)));v=list(map(float,query('features',b,'features').split()[3:]));base=v[0]*(1 if b.turn else -1);X=v[1:]
  for name in ['trained','half']:
   correction=sum(x*w for x,w in zip(X,selection[name]['deltas']));rounded=math.floor(correction+.5) if correction>=0 else math.ceil(correction-.5);expected=max(-24000,min(24000,int(base)+(1 if b.turn else -1)*rounded));actual=int(query(name,b,'eval'))
   if actual!=expected:
    assert abs(actual-expected)<=1 and abs(abs(correction)%1-.5)<1e-7,(name,b.fen(),actual,expected,correction);tolerance_cases+=1
   mirrored=int(query(name,b.mirror(),'eval'));assert mirrored==actual,(name,b.fen(),actual,mirrored)
  checked+=1
finally:
 for p in engines.values():p.stdin.write('quit\n');p.stdin.flush();p.wait()
(root/'inference-checks.json').write_text(json.dumps({'passed':True,'positions':checked,'models':list(selection.keys() & {'trained','half'}),'native_matches_own_fitted_formula':True,'colour_symmetry':True,'one_cp_feature_print_rounding_tolerance_cases':tolerance_cases},indent=2)+'\n');print('PASS:2000 native fitted-formula and colour symmetry positions for two models')
