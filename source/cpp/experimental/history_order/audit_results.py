from pathlib import Path
import json,chess,chess.pgn,hashlib,statistics,math
root=Path(__file__).resolve().parents[4];summaries=[]
for path in sorted((root/'history-pass').glob('*.json')):
 d=json.loads(path.read_text())
 if not isinstance(d,dict) or not isinstance(d.get('matches'),list) or 'binary_sha256' not in d or 'opponent_labels' not in d:continue
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
for path in sorted((root/'history-pass').glob('*.json')):
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
direct_audits=[]
for direct_path in sorted((root/'history-pass').glob('*.json')):
 candidate_record=json.loads(direct_path.read_text())
 if not isinstance(candidate_record,dict) or 'paired_mean_point_score' not in candidate_record or 'matches' not in candidate_record:continue
 d=json.loads(direct_path.read_text());count=0
 with direct_path.with_suffix('.pgn').open() as f:
  while (g:=chess.pgn.read_game(f)) is not None:
   r=d['matches'][count];b=g.board();assert not g.errors
   for move in g.mainline_moves():assert move in b.legal_moves;b.push(move)
   assert b.ply()==r['plies'] and g.headers['Result']==r['result'] and int(g.headers['TestUnit'])==r['unit']
   assert g.headers['CandidateSHA256']==d['binary_sha256']['candidate'] and g.headers['BaselineSHA256']==d['binary_sha256']['baseline']
   if r['result']!='*':assert b.result(claim_draw=True)==r['result']
   if r['score'] is not None:assert r['score']==(.5 if r['result']=='1/2-1/2' else float((r['result']=='1-0')==r['candidate_white']))
   count+=1
 assert count==len(d['matches'])==d['games']
 for field,value in [('wins',1),('draws',.5),('losses',0)]:assert d[field]==sum(r['score']==value for r in d['matches'])
 assert d['failures']==sum(r['failure'] is not None for r in d['matches'])
 paired=[]
 for unit in sorted({r['unit'] for r in d['matches']}):
  rows=[r for r in d['matches'] if r['unit']==unit]
  assert len(rows)==2 and {r['candidate_white'] for r in rows}=={True,False}
  if all(r['score'] is not None for r in rows):paired.append(sum(r['score'] for r in rows)/2)
 mean=statistics.mean(paired) if paired else None;se=math.sqrt(statistics.variance(paired)/len(paired)) if len(paired)>1 else None
 assert d['paired_units']==len(paired) and d['paired_mean_point_score']==mean
 assert d['approximate_95_interval']==([mean-1.96*se,mean+1.96*se] if se is not None else None)
 direct_audit={'file':direct_path.name,'games':count,'finished':d['finished'],'failures':d['failures'],'json_sha256':hashlib.sha256(direct_path.read_bytes()).hexdigest(),'pgn_sha256':hashlib.sha256(direct_path.with_suffix('.pgn').read_bytes()).hexdigest()}
 direct_audits.append(direct_audit)
pooled_path=root/'history-pass/fast-replication-summary.json'
if pooled_path.exists():
 pooled=json.loads(pooled_path.read_text());samples=[];seen=set()
 for filename in ['direct-fast.json','replication-fast.json']:
  path=root/'history-pass'/filename;v=json.loads(path.read_text());assert hashlib.sha256(path.read_bytes()).hexdigest()==pooled['source_sha256'][filename]
  ids={r['human_game_id'] for r in v['matches']};assert not ids&seen;seen.update(ids)
  for unit in sorted({r['unit'] for r in v['matches']}):
   rows=[r for r in v['matches'] if r['unit']==unit]
   if all(r['score'] is not None for r in rows):samples.append(sum(r['score'] for r in rows)/2)
 z=statistics.NormalDist().inv_cdf(.9875);mean=statistics.mean(samples);se=math.sqrt(statistics.variance(samples)/len(samples))
 assert pooled['pairs']==len(samples) and pooled['mean_point_score']==mean and pooled['corrected_97_5_interval']==[mean-z*se,mean+z*se]
report={'passed':True,'matches':summaries,'direct':direct_audits,'clock_tests':clocks,'note':'Independent rules-only replay of saved moves/results and clock accounting; no foreign-engine analysis.'}
(root/'history-pass/artifact-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
