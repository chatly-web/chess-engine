"""Apply the recorded field-test release gates without changing any engine."""
import hashlib,json,pathlib,statistics
ROOT=pathlib.Path(__file__).resolve().parents[1];DIR=ROOT/'field-strength'
def read(path):
 p=ROOT/path
 return json.loads(p.read_text()) if p.exists() else None
def check_phase(report_path,binary_hash,prefix,mate,history,clock_labels,sanitizer_prefix=None):
 report=read(report_path)
 if report is None:return {'state':'pending','reason':'Independent batch incomplete'}
 comparison=report['comparisons']['candidate'];interval=comparison['approximate_95_interval'];opponents=comparison['per_opponent_difference'];rows=[r for r in report['matches'] if r['engine']=='candidate']
 rules=read(prefix+'-rules.json');protocol=read(prefix+'-protocol.json');tactics=read(mate);hist=read(history);clocks=[read(label+'.json') for label in clock_labels]
 checks={'frozen_hash':report['binary_sha256']['candidate']==binary_hash,'positive_matched_lower_bound':bool(interval and interval[0]>0),'skill5_positive':opponents.get('Stockfish19-Skill5',-1)>0,'gnu_nonnegative':opponents.get('GNUChess6.3',-1)>=0,'no_recorded_game_failures':all(r['failure'] is None for r in rows),'rules_and_symmetry':bool(rules and rules.get('native_binary_sha256')==binary_hash and rules.get('legal_positions')==2000 and rules.get('colour_symmetry_positions')==2000 and rules.get('perft_nodes')==[197281,97862,43238]),'protocol':bool(protocol and protocol.get('passed') and protocol.get('native_binary_sha256')==binary_hash),'mate_subset':bool(tactics and tactics.get('binary_sha256')==binary_hash and tactics.get('passed')==84 and tactics.get('failed')==0),'history_subset':bool(hist and hist.get('passed') and any(r['sha256']==binary_hash for r in hist['engines']))}
 if not all(clocks):return {'state':'pending','reason':'Planned exact-binary clock games incomplete','checks_so_far':checks,'comparison':comparison}
 def own_failure(c):
  if c['failure'] is None:return False
  side=c.get('failure_side')
  if side is None:side='candidate' if (c['plies']%2==0)==(c['our_colour']=='white') else 'opponent'
  return side!='opponent'
 checks['exact_clock_hashes']=all(binary_hash in c['source_hashes'].values() for c in clocks)
 completed_clocks=[c for c in clocks if c['finished'] and c['result']!='*'];checks['completed_clock_evidence']=bool(completed_clocks)
 checks['no_own_clock_or_protocol_failure']=not any(own_failure(c) for c in clocks)
 checks['both_competition_controls']={(c['base'],c['increment']) for c in completed_clocks}>={(180,2),(600,5)}
 sanitizer_prefix=sanitizer_prefix or prefix;sanitizer=read(sanitizer_prefix+'-sanitizer-protocol.json');sanrules=read(sanitizer_prefix+'-sanitizer-rules.json');manifest=read('field-strength/v08-reproducibility.json' if prefix=='field-v08' else 'field-strength/reproducibility.json');checks['sanitizer_checks']=bool(sanitizer and sanitizer.get('passed') and sanrules and sanrules.get('legal_positions')==2000 and manifest and sanitizer.get('native_binary_sha256')==sanrules.get('native_binary_sha256')==manifest.get('sanitizer_binary_sha256'))
 return {'state':'qualified' if all(checks.values()) else 'not_qualified','checks':checks,'comparison':comparison,'candidate_completed_games':sum(r['score'] is not None for r in rows),'candidate_unfinished_games':sum(r['score'] is None for r in rows),'candidate_field_failures':sum(r['failure'] is not None for r in rows),'clock_games':len(completed_clocks),'unfinished_clock_games_excluded':len(clocks)-len(completed_clocks)}
phase1_hash=read('field-strength/selection.json')['candidate_binary_sha256'];final_hash=read('field-strength/final-selection.json')['binary_sha256']
phase1=check_phase('field-strength/confirmation.json',phase1_hash,'field-blendclock-fast','field-strength/final-mate-tactics.json','field-strength/final-history-checks.json',[f'field-final-gnu-{tc}-{colour}' for tc in ['blitz','rapid'] for colour in ['white','black']]+['field-final-sf5-blitz-white','field-final-sf5-rapid-white','field-final-sf5-rapid-black'],sanitizer_prefix='field-final')
final=check_phase('field-strength/final-confirmation.json',final_hash,'field-v08','field-strength/v08-mate-tactics.json','field-strength/v08-history-checks.json',['field-v08-gnu-blitz-white','field-v08-gnu-rapid-black','field-v08-sf5-blitz-black','field-v08-sf5-rapid-white'])
control_difference=None;report=read('field-strength/final-confirmation.json')
if report:
 diffs=[]
 for seed in sorted({r['seed'] for r in report['matches']}):
  rows=[r for r in report['matches'] if r['seed']==seed and r['engine'] in ('candidate','control')]
  if len(rows)==4 and all(r['score'] is not None for r in rows):diffs.append(sum(r['score'] for r in rows if r['engine']=='candidate')/2-sum(r['score'] for r in rows if r['engine']=='control')/2)
 control_difference=statistics.mean(diffs) if diffs else None
recommended=None
if final['state']=='qualified' and not (phase1['state']=='qualified' and control_difference is not None and control_difference<0):recommended='v08'
elif phase1['state']=='qualified':recommended='phase1'
elif phase1['state']!='pending' and final['state']!='pending':recommended='retain_published_baseline'
result={'phase1':phase1,'final':final,'final_minus_phase1_matched_point_score':control_difference,'recommended':recommended,'note':'Predeclared finite field gate; unfinished clock games are excluded, and both controls require completed exact-binary evidence. Approximate descriptive intervals apply to sampled-opening short games, not Elo, accuracy or a first-prize guarantee. The phase1-control comparison is secondary descriptive evidence.'}
(DIR/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
