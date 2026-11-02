from pathlib import Path
import chess,chess.engine,json,time,random,statistics,hashlib
p=Path(__file__).resolve().parent;root=p.parents[3];starts=json.loads((p/'starts.json').read_text())[:32];paths={'baseline':p/'baseline','incremental':p/'build-incremental/clash-native','cached':p/'build-cached/clash-native','activity':p/'build-activity/clash-native','combined':p/'build-combined/clash-native'};rng=random.Random(6202632);engines={n:chess.engine.SimpleEngine.popen_uci(str(f)) for n,f in paths.items()};rows=[]
try:
 for repeat in range(2):
  for i,start in enumerate(starts):
   b=chess.Board()
   for m in start['moves']:b.push_uci(m)
   order=list(engines);rng.shuffle(order);row={'repeat':repeat,'position':i,'human_game_id':start['game_id'],'fen':b.fen(),'measurements':{}}
   for name in order:
    e=engines[name];t=time.perf_counter();r=e.play(b,chess.engine.Limit(depth=6,time=30),game=object(),info=chess.engine.INFO_ALL);elapsed=time.perf_counter()-t;row['measurements'][name]={'seconds':elapsed,'nodes':r.info['nodes'],'depth':r.info['depth'],'move':r.move.uci(),'score':str(r.info.get('score'))}
   ref={k:v for k,v in row['measurements']['baseline'].items() if k!='seconds'}
   for n in paths:assert {k:v for k,v in row['measurements'][n].items() if k!='seconds'}==ref
   rows.append(row)
finally:
 for e in engines.values():e.quit()
ratios={n:[r['measurements']['baseline']['seconds']/r['measurements'][n]['seconds'] for r in rows] for n in paths if n!='baseline'};summary={n:{'median_speed_ratio':statistics.median(v),'total_time_speed_ratio':sum(r['measurements']['baseline']['seconds'] for r in rows)/sum(r['measurements'][n]['seconds'] for r in rows),'pairs':len(v)} for n,v in ratios.items()};chosen=max(summary,key=lambda n:summary[n]['median_speed_ratio']);r={'passed':True,'rows':rows,'summary':summary,'selection':chosen,'binary_sha256':{n:hashlib.sha256(f.read_bytes()).hexdigest() for n,f in paths.items()},'depth':6,'seed':6202632,'note':'Serial wall-time measurements with randomly alternating engine order; identical fixed-depth search results/nodes required. No match outcomes used for selection.'};(root/'eval-fast-pass/reproduced-benchmark.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2),flush=True)
