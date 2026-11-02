from pathlib import Path
import chess,json,random,subprocess,time,hashlib
p=Path(__file__).resolve().parent;root=p.parents[3];paths={'baseline':p/'baseline','incremental':p/'build-incremental/clash-native','cached':p/'build-cached/clash-native','activity':p/'build-activity/clash-native','combined':p/'build-combined/clash-native'};engines={n:subprocess.Popen([str(f)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1) for n,f in paths.items()};rng=random.Random(620261102);b=chess.Board();positions=0;started=time.monotonic()
def query(e,b):e.stdin.write('position fen '+b.fen()+'\neval\n');e.stdin.flush();return int(e.stdout.readline())
try:
 for i in range(5000):
  if b.is_game_over() or b.ply()>220:b=chess.Board()
  b.push(rng.choice(list(b.legal_moves)))
  for board in [b,b.mirror()]:
   scores={n:query(e,board) for n,e in engines.items()};assert len(set(scores.values()))==1,(board.fen(),scores);positions+=1
finally:
 for e in engines.values():e.stdin.write('quit\n');e.stdin.flush();e.wait()
r={'passed':True,'positions':positions,'seed':620261102,'binary_sha256':{n:hashlib.sha256(f.read_bytes()).hexdigest() for n,f in paths.items()},'seconds':time.monotonic()-started,'note':'Own original C++ score equality on5000legal random-walk positions and colour mirrors; retains each process cache across positions. Finite evidence, not proof.'};(root/'eval-fast-pass/reproduced-evaluation-equivalence.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
