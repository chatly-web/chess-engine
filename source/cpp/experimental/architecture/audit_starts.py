from pathlib import Path
import json,hashlib,gzip
import numpy as np,chess,chess.pgn,io
p=Path(__file__).resolve().parent;old=p.parent/'human_learning';starts=json.loads((p/'starts.json').read_text());prior={r['game_id'] for r in json.loads((old/'human-starts.json').read_text())};fit=set(np.load(old/'data/train-matrix.npz')['game_ids']);ids={r['game_id'] for r in starts}
assert len(ids)==len(starts)==160 and not ids&prior and not ids&fit
raw=gzip.decompress((old/'data/human-clean.pgn.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==json.loads((old/'data/manifest.json').read_text())['clean_sha256']
wanted={r['game_id']:r for r in starts};count=0;f=io.StringIO(raw.decode())
while (g:=chess.pgn.read_game(f)) is not None:
 gid=g.headers['Site'].rstrip('/').split('/')[-1]
 if gid not in wanted:continue
 assert not g.errors;row=wanted[gid];moves=list(g.mainline_moves());assert row['moves']==[m.uci() for m in moves[:row['plies']]];count+=1
assert count==160
report={'passed':True,'human_games':count,'training_validation_overlap':0,'previous_prefix_overlap':0,'screen_games':16,'reserved_confirmation_games':72,'screen_confirmation_overlap':len({r['game_id'] for r in starts[:16]}&{r['game_id'] for r in starts[32:104]}),'note':'Game-disjoint prefixes are offline harness inputs only; normal chess positions can recur between different games.'};print(json.dumps(report,indent=2));(p.parents[3]/'architecture-pass/starting-data-audit.json').write_text(json.dumps(report,indent=2)+'\n')
