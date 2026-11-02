"""Check game separation, source snapshot and absence of embedded eval annotations."""
from pathlib import Path
import hashlib,gzip,json
import numpy as np
root=Path(__file__).resolve().parent;matrix=np.load(root/'data/train-matrix.npz');ids=matrix['game_ids'];mask=matrix['train'];train=set(ids[mask]);valid=set(ids[~mask]);assert not train&valid
raw=gzip.decompress((root/'data/human-clean.pgn.gz').read_bytes());manifest=json.loads((root/'data/manifest.json').read_text());assert hashlib.sha256(raw).hexdigest()==manifest['clean_sha256']
assert b'[%eval' not in raw and b'[%clk' not in raw
specs={};sets={}
for name,pairs in [('screen',8),('confirmation',32),('parallel',8),('parallel-human',8)]:
 spec=json.loads((root/(name+'-spec.json')).read_text());starts=spec['starts'][:pairs*len(spec['opponents'])];games={r['game_id'] for r in starts}
 assert not games&(train|valid),(name,'training overlap');assert len(games)==len(starts),(name,'duplicate game')
 for other,old in sets.items():assert not old&games,(name,other,'selection/confirmation overlap')
 sets[name]=games;specs[name]={'human_starting_games':len(games),'fit_game_overlap':0}
report={'passed':True,'training_games':len(train),'validation_games':len(valid),'positions':len(ids),'independent_specs':specs,'clean_corpus_sha256':manifest['clean_sha256'],'note':'Game-level disjointness; human games can still share normal chess positions and openings.'}
print(json.dumps(report,indent=2));(root/'data/split-audit.json').write_text(json.dumps(report,indent=2)+'\n')
