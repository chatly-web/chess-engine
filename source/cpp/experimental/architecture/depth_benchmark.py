import pathlib,json,time,hashlib,statistics,chess,chess.engine
p=pathlib.Path(__file__).resolve().parent;starts=json.loads((p/'starts.json').read_text());models={'baseline':p/'baseline',**{name:p/('build-'+name)/'clash-native' for name in ['cluster','safe-null','combined']}};rows=[]
for i in range(12):
 b=chess.Board()
 for m in starts[112+i]['moves']:b.push_uci(m)
 names=list(models);names=names[i%4:]+names[:i%4]
 for name in names:
  with chess.engine.SimpleEngine.popen_uci(str(models[name].resolve())) as e:
   t=time.monotonic();r=e.play(b,chess.engine.Limit(time=.6),info=chess.engine.INFO_ALL);elapsed=time.monotonic()-t;assert r.move in b.legal_moves
   rows.append({'position':i,'engine':name,'depth':r.info.get('depth'),'nodes':r.info.get('nodes'),'seconds':elapsed,'move':r.move.uci(),'own_debug':r.info.get('string')})
report={'binary_sha256':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in models.items()},'requested_seconds':.6,'summary':{name:{'median_depth':statistics.median(r['depth'] for r in rows if r['engine']==name),'median_completed_nodes':statistics.median(r['nodes'] for r in rows if r['engine']==name)} for name in models},'rows':rows,'limitations':'Different selective trees. Timed depth and node counts are diagnostic, not Elo or a win guarantee. Local concurrent screen uses two single-thread games; all own candidates use one search worker and same table byte capacity.'};(p.parents[3]/'architecture-pass/reproduced-depth-benchmark.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary']),flush=True)
