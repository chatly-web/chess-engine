from pathlib import Path
import json,chess,chess.pgn,hashlib,statistics,math
root=Path(__file__).resolve().parents[4];summaries=[]
for path in sorted((root/'strength-first-pass').glob('*.json')):
 d=json.loads(path.read_text())
 if not isinstance(d,dict) or not isinstance(d.get('matches'),list) or 'binary_sha256' not in d:continue
 count=0
 with path.with_suffix('.pgn').open() as f:
  while (g:=chess.pgn.read_game(f)) is not None:
   assert not g.errors
   r=d['matches'][count];b=g.board()
   for move in g.mainline_moves():assert move in b.legal_moves;b.push(move)
   assert b.ply()==r['plies']
   assert g.headers['Result']==r['result']
   assert g.headers['EngineSHA256']==d['binary_sha256'][r['engine']]
   if r['result']!='*':assert b.result(claim_draw=True)==r['result'],(path.name,count)
   if r['score'] is not None:
    score=.5 if r['result']=='1/2-1/2' else float((r['result']=='1-0')==r['candidate_white'])
    assert score==r['score']
   count+=1
 assert count==len(d['matches'])
 for name,opponents in d['summary'].items():
  for label,summary in opponents.items():
   selected=[r for r in d['matches'] if r['engine']==name and r['opponent']==label]
   done=[r for r in selected if r['score'] is not None]
   expected={'games':len(selected),'completed':len(done),'wins':sum(r['score']==1 for r in done),'draws':sum(r['score']==.5 for r in done),'losses':sum(r['score']==0 for r in done),'points':sum(r['score'] for r in done),'unfinished':len(selected)-len(done),'failures':sum(r['failure'] is not None for r in selected)}
   assert summary==expected,(path.name,name,label)
 for name,comparison in d['comparisons'].items():
  diffs=[];by_opponent={}
  for seed in sorted({r['seed'] for r in d['matches']}):
   rows=[r for r in d['matches'] if r['seed']==seed and r['engine'] in (name,d['baseline'])]
   if len(rows)!=4 or any(r['score'] is None for r in rows):continue
   delta=sum(r['score'] for r in rows if r['engine']==name)/2-sum(r['score'] for r in rows if r['engine']==d['baseline'])/2
   diffs.append(delta);by_opponent.setdefault(rows[0]['opponent'],[]).append(delta)
  mean=statistics.mean(diffs) if diffs else None
  se=math.sqrt(statistics.variance(diffs)/len(diffs)) if len(diffs)>1 else None
  assert comparison['matched_units']==len(diffs) and comparison['mean_point_score_difference']==mean
  assert comparison['approximate_95_interval']==([mean-1.96*se,mean+1.96*se] if se is not None else None)
  assert comparison['per_opponent_difference']=={k:statistics.mean(v) for k,v in by_opponent.items()}
 summaries.append({'file':path.name,'games':count,'finished':sum(r['score'] is not None for r in d['matches']),'failures':sum(r['failure'] is not None for r in d['matches']),'json_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pgn_sha256':hashlib.sha256(path.with_suffix('.pgn').read_bytes()).hexdigest()})
clocks=[]
for path in sorted((root/'strength-first-pass').glob('*.json')):
 d=json.loads(path.read_text())
 if not isinstance(d,dict) or not isinstance(d.get('moves'),list) or 'base' not in d:continue
 b=chess.Board();clock={True:d['base'],False:d['base']};ownwhite=d['our_colour']=='white'
 for row in d['moves']:
  assert row['side']==('ours' if b.turn==ownwhite else 'opponent')
  assert row['seconds']<=clock[b.turn] if not d.get('movetime') else True
  clock[b.turn]+=d['increment']-row['seconds'];assert abs(clock[b.turn]-row['clock'])<1e-6
  move=chess.Move.from_uci(row['move']);assert move in b.legal_moves;b.push(move)
 assert b.ply()==d['plies']
 if not d['failure']:assert d['result']==b.result(claim_draw=True)
 with path.with_suffix('.pgn').open() as f:g=chess.pgn.read_game(f)
 assert not g.errors and list(g.mainline_moves())==list(b.move_stack)
 assert g.headers['Result']==d['result']
 clocks.append({'file':path.name,'result':d['result'],'finished':d['finished'],'failure':d['failure'],'plies':d['plies'],'base':d['base'],'increment':d['increment'],'json_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
report={'passed':True,'matches':summaries,'clock_tests':clocks,'note':'Independent rules-only replay of saved moves/results and clock accounting; no foreign-engine analysis.'}
(root/'strength-first-pass/artifact-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
