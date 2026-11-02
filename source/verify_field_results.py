"""Replay completed field-test artifacts using rules only; no engine analysis."""
import argparse,json,pathlib
import chess,chess.pgn
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',default='field-strength/artifact-audit.json');a=p.parse_args()
summary=[];clock_summary=[]
for path in sorted((ROOT/'field-strength').glob('*.json')):
 report=json.loads(path.read_text())
 if not isinstance(report,dict) or not isinstance(report.get('matches'),list):continue
 rows=report['matches'];count=0
 with path.with_suffix('.pgn').open() as f:
  while True:
   game=chess.pgn.read_game(f)
   if game is None:break
   assert not game.errors,(path.name,game.errors)
   row=rows[count];board=game.board()
   for move in game.mainline_moves():
    assert move in board.legal_moves,(path.name,count,move)
    board.push(move)
   assert board.ply()==row['plies']
   assert game.headers['Result']==row['result']
   assert game.headers['EngineSHA256']==report['binary_sha256'][row['engine']]
   assert int(game.headers['TestSeed'])==row['seed']
   assert game.headers['White']==(row['engine'] if row['candidate_white'] else row['opponent'])
   if row['failure'] is None and board.result(claim_draw=True)!='*':assert board.result(claim_draw=True)==row['result']
   expected=None if row['result']=='*' else .5 if row['result']=='1/2-1/2' else float((row['result']=='1-0')==row['candidate_white'])
   assert expected==row['score']
   count+=1
 assert count==len(rows)
 summary.append({'report':str(path.relative_to(ROOT)),'games_replayed':count,'unfinished':sum(r['result']=='*' for r in rows),'failures':sum(r['failure'] is not None for r in rows)})
for path in sorted(ROOT.glob('field-*.json')):
 if '-progress' in path.name:continue
 report=json.loads(path.read_text())
 if not isinstance(report,dict) or 'opponent' not in report or 'moves' not in report:continue
 if not report['finished']:assert report['result']=='*' and report['failure'] is None,path.name
 board=chess.Board();clocks={True:report['base'],False:report['base']}
 for row in report['moves']:
  assert 0<=row['seconds']<=clocks[board.turn],(path.name,row)
  clocks[board.turn]+=report['increment']-row['seconds']
  assert abs(clocks[board.turn]-row['clock'])<1e-6,(path.name,row)
  board.push_uci(row['move'])
 assert board.ply()==report['plies']
 if report['failure'] is None:assert board.result(claim_draw=True)==report['result'],path.name
 clock_summary.append({'report':path.name,'result':report['result'],'failure':report['failure'],'colour':report['our_colour'],'base':report['base'],'increment':report['increment'],'plies':board.ply(),'completed':report['finished']})
result={'field_reports':summary,'field_games_replayed':sum(r['games_replayed'] for r in summary),'clock_games':clock_summary,'clock_games_replayed':len(clock_summary),'completed_clock_games':sum(c['completed'] for c in clock_summary),'unfinished_clock_games_excluded':sum(not c['completed'] for c in clock_summary),'unfinished_field_games_excluded':sum(r['unfinished'] for r in summary),'note':'Independent rules replay of retained artifacts, hash associations and clock arithmetic. Completed and capped-game counts are separate; running progress files excluded. No strength or universal reliability claim.'}
(ROOT/a.output).write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k not in ('field_reports','clock_games')})
