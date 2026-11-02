"""Independent corpus, prefix and split audit; no chess evaluations requested."""
from pathlib import Path
import json,gzip,hashlib,io
import chess.pgn,numpy as np
p=Path(__file__).resolve().parent;root=p.parents[3];human=p.parent/'human_learning';starts=json.loads((p/'starts.json').read_text());ids={r['game_id'] for r in starts};fit=set(np.load(human/'data/train-matrix.npz')['game_ids']);previous=set()
for path in [human/'human-starts.json',p.parent/'architecture/starts.json',p.parent/'strength_first/starts.json',p.parent/'eval_fast/starts.json']:previous.update(r['game_id'] for r in json.loads(path.read_text()))
assert len(ids)==len(starts)==160 and not ids&fit and not ids&previous
raw=gzip.decompress((human/'data/human-clean.pgn.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==json.loads((human/'data/manifest.json').read_text())['clean_sha256'];wanted={r['game_id']:r for r in starts};checked=0;stream=io.StringIO(raw.decode())
while (g:=chess.pgn.read_game(stream)) is not None:
 gid=g.headers['Site'].rstrip('/').split('/')[-1]
 if gid not in wanted:continue
 r=wanted[gid];assert not g.errors and r['moves']==[m.uci() for m in list(g.mainline_moves())[:r['plies']]];checked+=1
assert checked==160
splits=[{r['game_id'] for r in starts[a:b]} for a,b in [(0,16),(16,80),(80,112),(112,144)]];assert all(not a&b for i,a in enumerate(splits) for b in splits[i+1:])
r={'passed':True,'human_games':160,'fitting_overlap':0,'prior_pass_game_overlap':0,'benchmark_direct_external_game_overlap':0,'corpus_sha256':hashlib.sha256(raw).hexdigest(),'split_sizes':list(map(len,splits)),'note':'Game-disjoint human prefixes; positions from separate games can share common opening patterns. Prefixes are offline inputs, not runtime books.'};(root/'history-pass/starting-data-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r)

rep_path=p/'replication-starts.json'
if rep_path.exists():
 rep=json.loads(rep_path.read_text());rep_ids={r['game_id'] for r in rep};assert len(rep)==len(rep_ids)==64 and not rep_ids&(ids|fit|previous)
 wanted={r['game_id']:r for r in rep};checked=0;stream=io.StringIO(raw.decode())
 while (g:=chess.pgn.read_game(stream)) is not None:
  gid=g.headers['Site'].rstrip('/').split('/')[-1]
  if gid in wanted:
   r=wanted[gid];assert not g.errors and r['moves']==[m.uci() for m in list(g.mainline_moves())[:r['plies']]];checked+=1
 assert checked==64
 report={'passed':True,'human_games':64,'original_fitting_previous_overlap':0,'corpus_sha256':hashlib.sha256(raw).hexdigest()};(root/'history-pass/replication-starting-data-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
