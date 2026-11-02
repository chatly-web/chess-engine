from pathlib import Path
import json,gzip,hashlib,io
import chess.pgn,numpy as np
p=Path(__file__).resolve().parent;human=p.parent/'human_learning';arch=p.parent/'architecture';starts=json.loads((p/'starts.json').read_text());ids={r['game_id'] for r in starts};fit=set(np.load(human/'data/train-matrix.npz')['game_ids']);previous={r['game_id'] for r in json.loads((human/'human-starts.json').read_text())}|{r['game_id'] for r in json.loads((arch/'starts.json').read_text())};assert len(ids)==len(starts)==160 and not ids&fit and not ids&previous
raw=gzip.decompress((human/'data/human-clean.pgn.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==json.loads((human/'data/manifest.json').read_text())['clean_sha256'];wanted={r['game_id']:r for r in starts};f=io.StringIO(raw.decode());checked=0
while (g:=chess.pgn.read_game(f)) is not None:
 gid=g.headers['Site'].rstrip('/').split('/')[-1]
 if gid not in wanted:continue
 r=wanted[gid];assert not g.errors and r['moves']==[m.uci() for m in list(g.mainline_moves())[:r['plies']]];checked+=1
assert checked==160
report={'passed':True,'human_games':checked,'fitting_overlap':0,'prior_prefix_overlap':0,'screen_confirmation_overlap':len({r['game_id'] for r in starts[:16]}&{r['game_id'] for r in starts[32:104]})};assert report['screen_confirmation_overlap']==0;(p.parents[3]/'strength-first-pass/starting-data-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
