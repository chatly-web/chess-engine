"""Combine frozen-candidate validation batches, keeping colour pairs together."""
import argparse,json,math,pathlib,statistics
p=argparse.ArgumentParser();p.add_argument('reports',nargs='+');p.add_argument('--output',required=True);a=p.parse_args();reports=[json.loads(pathlib.Path(f).read_text()) for f in a.reports]
assert len({r['candidate_sha256'] for r in reports})==len({r['baseline_sha256'] for r in reports})==1,'Do not mix binaries'
rows=[];pairs=[]
for report in reports:
 by_seed={}
 for row in report['games']:rows.append(row);by_seed.setdefault(row['seed'],[]).append(row)
 for seed,group in sorted(by_seed.items()):
  assert len(group)==2 and {g['candidate_white'] for g in group}=={True,False}
  if all(g['score'] is not None for g in group):pairs.append(sum(g['score'] for g in group)/2)
completed=[g for g in rows if g['score'] is not None];mean=statistics.mean(pairs);se=math.sqrt(statistics.variance(pairs)/len(pairs)) if len(pairs)>1 else None
llr=0;cross=None
for i,v in enumerate(pairs,1):
 if v>.5:llr+=math.log(.6/.5)
 elif v<.5:llr+=math.log(.4/.5)
 if cross is None and abs(llr)>=math.log(19):cross={'pair':i,'llr':llr,'decision':'accept_h1' if llr>0 else 'accept_h0'}
interval=[max(0,mean-1.96*se),min(1,mean+1.96*se)] if se is not None else None
result={'input_reports':a.reports,'candidate_sha256':reports[0]['candidate_sha256'],'baseline_sha256':reports[0]['baseline_sha256'],'games':len(rows),'completed':len(completed),'unfinished':len(rows)-len(completed),'complete_pairs':len(pairs),'wins':sum(g['score']==1 for g in completed),'draws':sum(g['score']==.5 for g in completed),'losses':sum(g['score']==0 for g in completed),'points':sum(g['score'] for g in completed),'paired_mean_score':mean,'paired_normal_95_interval':interval,'point_score_above_half':interval is not None and interval[0]>.5,'conditional_decisive_pair_sprt':{'first_crossing':cross,'final_llr':llr,'p0':.5,'p1':.6},'limitations':'Approximate descriptive interval over independently sampled colour pairs. Conditional pair-win SPRT is separate from point score. Concurrent local short-control games; not Elo, Lichess accuracy or tournament-field win probability.'}
pathlib.Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
