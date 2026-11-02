"""Independent legal-rules oracle for avoiding an opponent's mate-in-one."""
from pathlib import Path
import chess,chess.engine,json,random,time,hashlib
p=Path(__file__).resolve().parent;rng=random.Random(2026110237);cases=[];start=time.monotonic()
def mates(b):
 result=[]
 for m in list(b.legal_moves):
  b.push(m)
  if b.is_checkmate():result.append(m)
  b.pop()
 return result
for attempt in range(10000):
 bk=rng.choice([0,7,56,63]);wk,q,r=rng.sample([x for x in range(64) if x!=bk],3)
 if not 2<=chess.square_distance(wk,bk)<=4 or chess.square_distance(q,bk)>4:continue
 b=chess.Board(None);b.turn=chess.BLACK
 for sq,piece in [(bk,chess.Piece(chess.KING,False)),(wk,chess.Piece(chess.KING,True)),(q,chess.Piece(chess.QUEEN,True)),(r,chess.Piece(chess.ROOK,False))]:b.set_piece_at(sq,piece)
 if not b.is_valid() or b.is_check() or b.is_game_over():continue
 n=b.copy();n.turn=chess.WHITE
 if not any(not n.is_capture(m) for m in mates(n)):continue
 safe=[];unsafe=[]
 for move in list(b.legal_moves):
  child=b.copy();child.push(move)
  (unsafe if not child.is_game_over() and mates(child) else safe).append(move.uci())
 if not safe or not unsafe:continue
 cases.append({'fen':b.fen(),'safe':safe,'unsafe':unsafe})
 if len(cases)==12:break
assert len(cases)>=8,len(cases)
rows=[]
for name,path in {'baseline':p/'baseline',**{n:p/('build-'+n)/'clash-native' for n in ['checks','threats','guarded']}}.items():
 with chess.engine.SimpleEngine.popen_uci(str(path.resolve()),timeout=10) as e:
  for i,c in enumerate(cases):
   for mirror in [False,True]:
    b=chess.Board(c['fen']);safe=c['safe']
    if mirror:
     b=b.mirror();safe=[chess.Move(m.from_square^56,m.to_square^56,m.promotion).uci() for m in map(chess.Move.from_uci,safe)]
    result=e.play(b,chess.engine.Limit(depth=1,time=2),game=object(),info=chess.engine.INFO_ALL);assert result.move in b.legal_moves
    rows.append({'engine':name,'case':i,'mirror':mirror,'move':result.move.uci(),'avoids_mate_in_one':result.move.uci() in safe,'depth':result.info.get('depth'),'own_score':str(result.info.get('score'))})
summary={n:{'passes':sum(r['avoids_mate_in_one'] for r in rows if r['engine']==n),'tests':sum(r['engine']==n for r in rows)} for n in ['baseline','checks','threats','guarded']}
report={'binary_sha256':{n:hashlib.sha256((p/'baseline' if n=='baseline' else p/('build-'+n)/'clash-native').read_bytes()).hexdigest() for n in ['baseline','checks','threats','guarded']},'oracle':'Only legal moves and exhaustive opponent mate-in-one replies; no foreign-engine scores','requested_nominal_depth':1,'cases':cases,'rows':rows,'summary':summary,'seconds':time.monotonic()-start,'note':'Purpose-built finite king-defence/horizon cases, both colours. Not overall accuracy or match strength. Added quiescence checks search beyond nominal main depth.'};(p.parents[3]/'strength-first-pass/reproduced-king-defence.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary),flush=True)
