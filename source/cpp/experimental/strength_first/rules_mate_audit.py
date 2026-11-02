"""Rules-only verification of the mating threats seen in the own-game replay."""
import chess,json
from pathlib import Path
row=json.loads((Path(__file__).resolve().parents[4]/'strength-first-pass/queen-loss.json').read_text());root=chess.Board(row['fen']);out=[]
def mates(b):
 result=[]
 for m in list(b.legal_moves):
  b.push(m)
  if b.is_checkmate():result.append(m.uci())
  b.pop()
 return result
for move in ['d7e8','d7e7','d7d6','d7d5']:
 b=root.copy();m=chess.Move.from_uci(move);assert m in b.legal_moves;b.push(m);q=chess.Move.from_uci('e2a6');assert q in b.legal_moves;b.push(q);responses=[]
 for reply in list(b.legal_moves):
  b.push(reply);wins=mates(b);b.pop();assert wins,(move,reply);responses.append({'reply':reply.uci(),'white_mates':wins})
 assert responses;out.append({'black_move':move,'white_check':'e2a6','all_black_replies_mated':responses})
(Path(__file__).resolve().parents[4]/'strength-first-pass/reproduced-mate-threat-oracle.json').write_text(json.dumps({'passed':True,'rules_only':True,'source':'Observed own game position, no external engine analysis','cases':out},indent=2)+'\n');print('Verified queen-retreat alternatives allow mate in2 by legal exhaustive replies')
