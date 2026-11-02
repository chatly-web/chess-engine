from pathlib import Path
import chess,subprocess,random,json,time,hashlib
p=Path(__file__).resolve().parent;root=p.parents[3];e=subprocess.Popen([str(p/'attack-map')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1);rng=random.Random(640261102);b=chess.Board();count=0;t=time.monotonic()
try:
 for i in range(2500):
  if b.is_game_over() or b.ply()>220:b=chess.Board()
  b.push(rng.choice(list(b.legal_moves)))
  for board in [b,b.mirror()]:
   e.stdin.write(board.fen()+'\n');e.stdin.flush();actual=list(map(int,e.stdout.readline().split()));expected=[sum(1<<sq for sq in range(64) if board.is_attacked_by(c,sq)) for c in [False,True]];assert actual==expected,(board.fen(),actual,expected);count+=1
finally:e.stdin.close();e.wait()
r={'passed':True,'positions':count,'target_squares_per_position':64,'colours_per_position':2,'checks':count*128,'seed':640261102,'diagnostic_sha256':hashlib.sha256((p/'attack-map').read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((p/'build-candidate/clash-native').read_bytes()).hexdigest(),'seconds':time.monotonic()-t,'note':'All attacked squares compared with chess rules library, including friendly occupied endpoints and colour mirrors; no engine analysis.'};(root/'bit-attacks-pass/reproduced-attack-map-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
