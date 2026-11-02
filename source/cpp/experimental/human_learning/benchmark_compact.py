import pathlib,chess,chess.engine,json,time,hashlib,statistics,random
p=pathlib.Path(__file__).resolve().parent;starts=json.loads((p/'human-starts.json').read_text());rows=[]
models={'baseline':p/'baseline','compact':p/'build-compact/clash-native'}
for i in range(8):
 b=chess.Board()
 for m in starts[112+i]['moves']:b.push_uci(m)
 for repeat in range(4):
  record={'position':i,'repeat':repeat}
  for name in list(models)[(i+repeat)%2:]+list(models)[:(i+repeat)%2]:
   path=models[name]
   with chess.engine.SimpleEngine.popen_uci(str(path.resolve()),timeout=30) as e:
    t=time.monotonic();r=e.play(b,chess.engine.Limit(depth=7,time=30),info=chess.engine.INFO_ALL);elapsed=time.monotonic()-t
    assert r.move in b.legal_moves
    record[name]=dict(seconds=elapsed,depth=r.info.get('depth'),nodes=r.info.get('nodes'),score=str(r.info.get('score')),move=r.move.uci())
  for key in ['depth','nodes','score','move']:assert record['baseline'][key]==record['compact'][key],record
  record['speed_ratio']=record['baseline']['seconds']/record['compact']['seconds'];rows.append(record)
ratios=[statistics.median(r['speed_ratio'] for r in rows if r['position']==i) for i in range(8)]
report={'binary_sha256':{n:hashlib.sha256(f.read_bytes()).hexdigest() for n,f in models.items()},'depth':7,'repeats':4,'positions':8,'median_position_speed_ratio':statistics.median(ratios),'position_speed_ratios':ratios,'rows':rows,'limitations':'Limited alternating-order fixed-tree timing sample under concurrent local match load. Not Elo, universal speedup or proof of stronger timed play.'}
(p.parents[3]/'learning-pass/reproduced-compact-speed.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'}),flush=True)
