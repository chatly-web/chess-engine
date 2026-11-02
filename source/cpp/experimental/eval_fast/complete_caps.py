"""Resolve artificial ply caps by one full replay of every affected paired unit."""
from pathlib import Path
import json,subprocess,sys,time,hashlib,statistics,math
import chess.pgn
p=Path(__file__).resolve().parent;root=p.parents[3];workspace=root;folder=root/'eval-fast-pass';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
policy={'reason':'An external game reached the artificial328ply harness cap. It remains unfinished, never a credited draw.','trigger':'Every external unit containing a score=None without technical failure','action':'Replay all four games in each affected unit once from the same full prefix, with the same frozen engines/time/options and600ply cap. No changes to chess code or weights.','original_evidence_retained':True,'own_technical_failure_not_repaired':True,'selection_frozen':json.loads((folder/'selection.json').read_text())['sha256'],'max_replays_per_affected_unit':1,'gate_evidence':'All untouched original units plus all4replayed games per affected unit. Original partial units remain separately published.','no_strength_outcome_selection':True};(folder/'reproduced-external-completion-plan.json').write_text(json.dumps(policy,indent=2)+'\n')
while not (folder/'external.json').exists():time.sleep(2)
d=json.loads((folder/'external.json').read_text());spec=json.loads((p/'external-spec.json').read_text());affected=sorted({r['seed'] for r in d['matches'] if r['score'] is None and not r['failure']});reports=[]
for i,seed in enumerate(affected):
 rows=[r for r in d['matches'] if r['seed']==seed];assert len(rows)==4
 if any(r['failure'] for r in rows):continue
 opponent=rows[0]['opponent'];oi=d['opponent_labels'].index(opponent);index=seed-d['seed_base']-oi*100000;start=spec['starts'][oi*12+index];assert start['game_id']==rows[0]['human_opening_game_id']
 replay_spec={**spec,'opponents':[spec['opponents'][oi]],'starts':[start]};sf=p/f'reproduced-completion-{i}-spec.json';sf.write_text(json.dumps(replay_spec,indent=2)+'\n');label=f'eval-fast-pass/reproduced-completion-{i}'
 with (p/f'reproduced-completion-{i}.log').open('w') as out:subprocess.run(['caffeinate','-i',sys.executable,str(p/'completion_arena.py'),'--spec',str(sf),'--label',label,'--pairs-per-opponent','1','--seconds','.15','--workers','1','--seed-base',str(seed)],cwd=workspace,stdout=out,stderr=subprocess.STDOUT,check=True)
 reports.append(folder/f'reproduced-completion-{i}.json')
def games(path):
 with path.open() as f:
  while (g:=chess.pgn.read_game(f)) is not None:yield g
original_games=list(games(folder/'external.pgn'));assert len(original_games)==len(d['matches']);pairs=[(r,g) for r,g in zip(d['matches'],original_games) if r['seed'] not in affected]
for f in reports:
 v=json.loads(f.read_text());assert v['binary_sha256']==d['binary_sha256'];pg=list(games(f.with_suffix('.pgn')));assert len(pg)==len(v['matches'])==4;pairs.extend(zip(v['matches'],pg))
assert len(pairs)==96
rows=[r for r,g in pairs];resolved={**d,'matches':rows,'summary':{},'comparisons':{},'completion_policy':policy,'original_report_sha256':sha(folder/'external.json'),'completion_reports':{f.name:sha(f) for f in reports},'resolved_unit_seeds':affected,'resolved_report':True,'original_short_games':96,'additional_replay_games':sum(len(json.loads(f.read_text())['matches']) for f in reports)}
for name in spec['engines']:
 resolved['summary'][name]={}
 for op in d['opponent_labels']:
  ss=[r for r in rows if r['engine']==name and r['opponent']==op];done=[r for r in ss if r['score'] is not None];resolved['summary'][name][op]={'games':len(ss),'completed':len(done),'wins':sum(r['score']==1 for r in done),'draws':sum(r['score']==.5 for r in done),'losses':sum(r['score']==0 for r in done),'points':sum(r['score'] for r in done),'unfinished':len(ss)-len(done),'failures':sum(r['failure'] is not None for r in ss)}
diffs=[];per={}
for seed in sorted({r['seed'] for r in rows}):
 rr=[r for r in rows if r['seed']==seed]
 if len(rr)!=4 or any(r['score'] is None for r in rr):continue
 delta=sum(r['score'] for r in rr if r['engine']=='candidate')/2-sum(r['score'] for r in rr if r['engine']=='baseline')/2;diffs.append(delta);per.setdefault(rr[0]['opponent'],[]).append(delta)
mean=statistics.mean(diffs) if diffs else None;se=math.sqrt(statistics.variance(diffs)/len(diffs)) if len(diffs)>1 else None;resolved['comparisons']['candidate']={'matched_units':len(diffs),'mean_point_score_difference':mean,'approximate_95_interval':[mean-1.96*se,mean+1.96*se] if se is not None else None,'per_opponent_difference':{k:statistics.mean(v) for k,v in per.items()}}
(folder/'reproduced-external-resolved.json').write_text(json.dumps(resolved,indent=2)+'\n');(folder/'reproduced-external-resolved.pgn').write_text('\n\n'.join(str(g) for r,g in pairs)+'\n');print(json.dumps({'affected_units':affected,'replay_games':resolved['additional_replay_games'],'resolved_summary':resolved['summary']},indent=2),flush=True)
