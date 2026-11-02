"""Compare search-preserving optimisations against an own-engine reference."""
import argparse,hashlib,json,pathlib,random,time
import chess,chess.engine
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--reference',required=True);p.add_argument('--candidate',required=True);p.add_argument('--label',required=True);p.add_argument('--positions',type=int,default=200);p.add_argument('--depth',type=int,default=4);p.add_argument('--seed',type=int,default=20261102);a=p.parse_args()
output=ROOT/(a.label+'.json');assert not output.exists(),'Use a fresh label'
rng=random.Random(a.seed);board=chess.Board();positions=[]
for i in range(a.positions):
 for _ in range(rng.randint(1,6)):
  if board.is_game_over(claim_draw=True) or board.ply()>140:board=chess.Board()
  board.push(rng.choice(list(board.legal_moves)))
 positions.append(board.copy())
# Retained-table draw/mate edge cases complement varied full move histories.
for fen in ['7k/8/3Q4/6K1/8/8/8/8 w - - 0 1','7k/8/3Q4/6K1/8/8/8/8 w - - 98 1','7k/5Q2/6K1/8/8/8/8/8 w - - 99 1']:
 positions.append(chess.Board(fen))
b=chess.Board()
for move in ['g1f3','g8f6','f3g1','f6g8']*2:b.push_uci(move)
positions.append(b)
rows=[];start=time.monotonic();game=object()
with chess.engine.SimpleEngine.popen_uci(a.reference) as reference,chess.engine.SimpleEngine.popen_uci(a.candidate) as candidate:
 for i,board in enumerate(positions):
  row={'index':i,'fen':board.fen(),'moves_from_root':len(board.move_stack)}
  for label,engine in [('reference',reference),('candidate',candidate)]:
   result=engine.play(board,chess.engine.Limit(depth=a.depth,time=30),game=game,info=chess.engine.INFO_ALL)
   row[label]={'move':result.move.uci() if result.move else None,'depth':result.info.get('depth'),'nodes':result.info.get('nodes'),'score':str(result.info.get('score'))}
  assert row['reference']==row['candidate'],row
  rows.append(row)
report={'passed':True,'positions':len(rows),'random_positions':a.positions,'fixed_edge_cases':4,'depth':a.depth,'seed':a.seed,'reference_sha256':hashlib.sha256(pathlib.Path(a.reference).read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(pathlib.Path(a.candidate).read_bytes()).hexdigest(),'seconds':time.monotonic()-start,'note':'Own-engine differential checks; identical moves, scores, depths and node counts. Finite evidence, not proof over all positions or timed-search outcomes.','cases':rows}
output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='cases'})
