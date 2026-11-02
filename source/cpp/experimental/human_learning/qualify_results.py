from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[4];folder=root/'learning-pass';baseline=hashlib.sha256((root/'engine/clash-native').read_bytes()).hexdigest();recommend='retain-v08';decisions={}
for batch,names in [('confirmation',['candidate','tactical']),('parallel-screen',['parallel']),('parallel-human',['parallel-human'])]:
 p=folder/(batch+'.json')
 if not p.exists():decisions[batch]={'status':'pending'};continue
 d=json.loads(p.read_text())
 for name in names:
  comp=d['comparisons'][name];summary=d['summary'][name];sha=d['binary_sha256'][name];clocks=[]
  for file in folder.glob('*.json'):
   c=json.loads(file.read_text())
   if isinstance(c,dict) and c.get('source_hashes',{}).get('clash-native')==sha and 'base' in c:clocks.append(c)
  ci=comp['approximate_95_interval'];positive=bool(ci and ci[0]>0);gnu=comp['per_opponent_difference'].get('GNUChess6.3',-1)>=0
  controls=all(any(c['base']==base and c['increment']==inc and c.get('finished') and not c['failure'] for c in clocks) for base,inc in [(180,2),(600,5)])
  nonloss=any('GNU Chess' in c.get('opponent',{}).get('name','') and c.get('finished') and not c['failure'] and (c['result']=='1/2-1/2' or (c['result']=='1-0')==(c['our_colour']=='white')) for c in clocks)
  failures=sum(v['failures'] for v in summary.values())+sum(c['failure'] is not None and c.get('failure_side')=='candidate' for c in clocks)
  qualified=positive and gnu and controls and nonloss and not failures
  decisions[batch+'/'+name]={'qualified_on_match_and_clock_gate':bool(qualified),'candidate_sha256':sha,'matched_point_difference':comp['mean_point_score_difference'],'approximate95':ci,'positive_lower_bound':positive,'gnu_nonnegative':gnu,'both_controls_exact_binary_completed':controls,'actual_gnu_nonloss':nonloss,'own_recorded_failures':failures,'note':'Passing these conditions also requires reviewed rules/protocol/tactics/inference/sanitizer checks before deployment.'}
  if qualified:recommend='candidate-qualified-review-required'
report={'recommended_action':recommend,'recommended_binary_sha256':baseline,'decisions':decisions,'finite_evidence_only':True,'accuracy_measured':False,'guaranteed_winner':False}
(folder/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
