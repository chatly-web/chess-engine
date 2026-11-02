"""Evaluate the recorded, fixed architecture gate. Never install a candidate."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[4];folder=root/'architecture-pass';selection=json.loads((folder/'selection.json').read_text()) if (folder/'selection.json').exists() else None
report={'recommended_action':'retain-v08','production_sha256':hashlib.sha256((root/'engine/clash-native').read_bytes()).hexdigest(),'candidate':selection,'new_accuracy_measured':False,'guaranteed_winner':False}
if selection and (folder/'confirmation.json').exists():
 d=json.loads((folder/'confirmation.json').read_text());c=d['comparisons']['candidate'];sha=selection['binary_sha256'];assert d['binary_sha256']['candidate']==sha
 clocks=[]
 for p in folder.glob('*.json'):
  v=json.loads(p.read_text())
  if isinstance(v,dict) and v.get('source_hashes',{}).get('clash-native')==sha and 'base' in v:clocks.append(v)
 positive=bool(c['approximate_95_interval'] and c['approximate_95_interval'][0]>0)
 gnu=c['per_opponent_difference'].get('GNUChess6.3',-1)>=0
 failure=sum(s['failures'] for s in d['summary']['candidate'].values())+sum(v['failure'] is not None for v in clocks)
 both=all(any(v['base']==base and v['increment']==inc and v['finished'] and not v['failure'] for v in clocks) for base,inc in [(180,2),(600,5)])
 nonloss=any('GNU Chess' in v['opponent'].get('name','') and v['finished'] and not v['failure'] and (v['result']=='1/2-1/2' or (v['result']=='1-0')==(v['our_colour']=='white')) for v in clocks)
 checks=[]
 for kind in ['rules','protocol']:
  p=root/('architecture-'+selection['chosen']+'-'+kind+'.json');v=json.loads(p.read_text());checks.append(v['native_binary_sha256']==sha and (v.get('passed',True)))
 p=folder/(selection['chosen']+'-mates.json');v=json.loads(p.read_text());checks.append(v['binary_sha256']==sha and v['passed']==v['tests'] and v['failed']==0)
 table=json.loads((folder/'table-budget.json').read_text())[selection['chosen']];checks.append(table['sha256']==sha and table['bytes']==12582912)
 review_path=folder/'mechanism-sanitizer-review.json';review=json.loads(review_path.read_text()) if review_path.exists() else {}
 reviewed=review.get('reviewed',False) and review.get('selected_native_sha256')==sha and review.get('table_test_passed',False) and review.get('null_mechanism',{}).get('passed',False) and review.get('history_checks_passed',False) and review.get('sanitizer_protocol_passed',False)
 passed=positive and gnu and not failure and both and nonloss and all(checks) and reviewed
 report.update({'comparison':c,'positive_lower95':positive,'gnu_nonnegative':gnu,'recorded_failures':failure,'both_exact_clocks_completed':both,'standard_gnu_nonloss':nonloss,'preflight_hashes_and_checks_match':all(checks),'match_clock_gate_passed':bool(passed),'sanitizer_and_mechanism_review_required':not reviewed})
 if passed:report['recommended_action']='candidate-qualified-pending-final-review'
else:report['status']='awaiting-complete-confirmation-and-clock-records'
(folder/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
