"""Pair-aware descriptive confidence interval and sequential pair-win evidence."""
import argparse,json,math,pathlib,statistics
p=argparse.ArgumentParser();p.add_argument('jsonl');p.add_argument('--output',required=True);a=p.parse_args();rows=[]
for line in pathlib.Path(a.jsonl).read_text().splitlines():
 if line.strip():rows.append(json.loads(line))
by_seed={}
for r in rows:by_seed.setdefault(r['seed'],[]).append(r)
pairs=[]
for seed,group in sorted(by_seed.items()):
 if len(group)==2 and all(g['score'] is not None for g in group):pairs.append((seed,sum(g['score'] for g in group)/2))
values=[v for _,v in pairs];n=len(values);mean=statistics.mean(values) if n else None;se=math.sqrt(statistics.variance(values)/n) if n>1 else None
llr=0;decision='continue';cross=None
for i,(seed,v) in enumerate(pairs,1):
 if v>.5:llr+=math.log(.6/.5)
 elif v<.5:llr+=math.log(.4/.5)
 if cross is None and abs(llr)>=math.log(19):decision='accept_h1' if llr>0 else 'accept_h0';cross=dict(pair=i,seed=seed,llr=llr)
completed=[r for r in rows if r['score'] is not None]
r=dict(games=len(rows),completed_games=len(completed),unfinished_games=len(rows)-len(completed),wins=sum(g['score']==1 for g in completed),draws=sum(g['score']==.5 for g in completed),losses=sum(g['score']==0 for g in completed),points=sum(g['score'] for g in completed),paired_mean_score=mean,paired_normal_95_interval=[max(0,mean-1.96*se),min(1,mean+1.96*se)] if se is not None else None,complete_pairs=n,technical_failures=sum(g['failure'] is not None for g in rows),pair_win_sprt=dict(decision=decision,first_crossing=cross,final_llr=llr,p0=.5,p1=.6),limitations='Approximate descriptive normal interval over independent starting-position pairs; SPRT models stationary conditional decisive-pair win probability, not Elo. Fixed binaries, mixed short controls, concurrent local games. Not a tournament-field win-rate or accuracy guarantee.')
pathlib.Path(a.output).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
