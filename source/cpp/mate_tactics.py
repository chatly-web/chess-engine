"""Synthetic forced-mate oracle using rules only, with no external engine analysis."""
import chess,chess.engine,json,pathlib,random,time,hashlib,argparse
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--label',default='long-pass/mate-tactics');a=p.parse_args();rng=random.Random(9690)
def mates(b):
 answer=[]
 for m in list(b.legal_moves):
  b.push(m)
  if b.is_checkmate():answer.append(m)
  b.pop()
 return answer
def mate2(b):
 answer=[]
 for m in list(b.legal_moves):
  b.push(m);replies=list(b.legal_moves);forced=bool(replies)
  for r in replies:
   b.push(r);win=bool(mates(b));b.pop()
   if not win:forced=False;break
  b.pop()
  if forced:answer.append(m)
 return answer
def forced_mate(b,attacker,plies):
 # Independent exhaustive AND/OR rules oracle, only for unexpected moves.
 if b.is_checkmate():return b.turn!=attacker
 if b.is_game_over() or plies==0:return False
 attacking=b.turn==attacker
 for m in list(b.legal_moves):
  b.push(m);wins=forced_mate(b,attacker,plies-1);b.pop()
  if attacking and wins:return True
  if not attacking and not wins:return False
 return not attacking
one=[];two=[];attempts=0;start=time.monotonic()
while (len(one)<30 or len(two)<12) and attempts<20000:
 attempts+=1;bk=rng.choice([0,7,56,63]);wk,q=rng.sample([s for s in range(64) if s!=bk],2)
 if not 2<=chess.square_distance(wk,bk)<=4:continue
 b=chess.Board(None);b.set_piece_at(wk,chess.Piece(chess.KING,True));b.set_piece_at(q,chess.Piece(chess.QUEEN,True));b.set_piece_at(bk,chess.Piece(chess.KING,False))
 if not b.is_valid():continue
 wins=mates(b)
 if wins:
  if len(one)<30:one.append((b,wins,1))
 elif len(two)<12:
  wins=mate2(b)
  if wins:two.append((b,wins,2))
assert len(one)==30 and len(two)==12
rows=[]
with chess.engine.SimpleEngine.popen_uci(str(pathlib.Path(a.binary).resolve())) as e:
 for b,wins,distance in one+two:
  for mirror in (False,True):
   position=b.mirror() if mirror else b.copy();expected=[chess.Move(m.from_square^56,m.to_square^56,m.promotion) for m in wins] if mirror else wins
   result=e.play(position,chess.engine.Limit(time=.25));shortest=result.move in expected
   forced=shortest;verified_distance=distance if shortest else None
   if not shortest and result.move in position.legal_moves:
    after=position.copy();after.push(result.move)
    forced=forced_mate(after,position.turn,4)
    if forced:verified_distance=3
   rows.append(dict(fen=position.fen(),mate_distance=distance,move=result.move.uci(),expected=[m.uci() for m in expected],shortest_mate=shortest,verified_mate_within_moves=verified_distance,passed=forced))
report=dict(binary_sha256=hashlib.sha256(pathlib.Path(a.binary).read_bytes()).hexdigest(),tests=len(rows),shortest_mate_passed=sum(r['shortest_mate'] for r in rows),passed=sum(r['passed'] for r in rows),failed=sum(not r['passed'] for r in rows),seconds=time.monotonic()-start,cases=rows,note='Finite synthetic mate-in-one and mate-in-two positions, both colours; shortest-mate results reported separately. Unexpected choices exhaustively checked for forced mate within three moves by a rules-only oracle. No tablebase used by the engine. This does not establish general accuracy.')
(ROOT/(a.label+'.json')).write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='cases'})
if report['failed']:raise SystemExit(1)
