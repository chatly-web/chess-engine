from pathlib import Path
import json,statistics,math,time,hashlib
p=Path(__file__).resolve().parent;root=p.parents[3];folder=root/'history-pass'
while not (folder/'replication-fast.json').exists():time.sleep(2)
a=json.loads((folder/'direct-fast.json').read_text());b=json.loads((folder/'replication-fast.json').read_text());assert a['binary_sha256']==b['binary_sha256'];samples=[];ids=[]
for batch,d in [('initial',a),('replication',b)]:
 game_ids={r['human_game_id'] for r in d['matches']};assert not set(ids)&game_ids;ids.extend(game_ids)
 for unit in sorted({r['unit'] for r in d['matches']}):
  rows=[r for r in d['matches'] if r['unit']==unit];assert len(rows)==2
  if all(r['score'] is not None for r in rows):samples.append({'batch':batch,'unit':unit,'score':sum(r['score'] for r in rows)/2})
z=statistics.NormalDist().inv_cdf(.9875)
def interval(values):
 mean=statistics.mean(values);se=math.sqrt(statistics.variance(values)/len(values));return [mean-z*se,mean+z*se]
values=[r['score'] for r in samples];r={'binary_sha256':a['binary_sha256'],'pairs':len(values),'games':a['games']+b['games'],'finished':a['finished']+b['finished'],'wins':a['wins']+b['wins'],'draws':a['draws']+b['draws'],'losses':a['losses']+b['losses'],'failures':a['failures']+b['failures'],'mean_point_score':statistics.mean(values),'corrected_97_5_interval':interval(values),'initial_corrected_97_5_interval':interval([v['score'] for v in samples if v['batch']=='initial']),'z':z,'looks':2,'source_sha256':{name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in ['direct-fast.json','replication-fast.json']},'paired_samples':samples,'note':'One fixed independent replication after the initial95interval crossed0.5. Approximate paired normal97.5percent intervals provide Bonferroni adjustment for two looks; common opening patterns and concurrent timing still limit inference. No further repetition or parameter changes.'};(folder/'reproduced-fast-replication-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='paired_samples'},indent=2),flush=True)
