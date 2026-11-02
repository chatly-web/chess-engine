"""Independently replay finite immediate-mate defence labels, then test a binary."""
from pathlib import Path
import argparse,json,time
import chess,chess.engine
parser=argparse.ArgumentParser();parser.add_argument('--binary',required=True);parser.add_argument('--seconds',type=float,default=.2);args=parser.parse_args()
root=Path(__file__).resolve().parents[4];data=json.loads((root/'counter-memory-pass/king-defence.json').read_text());cases=data['cases']
for case in cases:
 b=chess.Board(case['fen']);assert b.is_valid()
 for text,replies in case['unsafe_move_mating_replies'].items():
  child=b.copy();move=chess.Move.from_uci(text);assert move in child.legal_moves;child.push(move)
  for reply in replies:
   mate=child.copy();m=chess.Move.from_uci(reply);assert m in mate.legal_moves;mate.push(m);assert mate.is_checkmate()
 for text in case['safe_moves']:
  child=b.copy();m=chess.Move.from_uci(text);assert m in child.legal_moves;child.push(m)
  if child.is_game_over(claim_draw=True):continue
  for reply in list(child.legal_moves):
   child.push(reply);assert not child.is_checkmate();child.pop()
rows=[]
with chess.engine.SimpleEngine.popen_uci(str(Path(args.binary).resolve())) as engine:
 for case in cases:
  b=chess.Board(case['fen']);result=engine.play(b,chess.engine.Limit(time=args.seconds),game=object())
  assert result.move in b.legal_moves
  rows.append(result.move.uci() in case['safe_moves'])
print(json.dumps({'passed':sum(rows),'tests':len(rows),'seconds_per_puzzle':args.seconds,'scope':'Finite avoidable immediate mate; not all tactical positions'}))
assert all(rows)
