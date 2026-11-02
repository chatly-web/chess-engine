"""Fit inputs contain our own evaluator's features and human final results only."""
from pathlib import Path
import hashlib,json,random,subprocess,selectors,time,collections
import numpy as np,chess,chess.pgn
root=Path(__file__).resolve().parent;data=root/'data';manifest=json.loads((data/'manifest.json').read_text());corpus=data/'human-clean.pgn'
assert hashlib.sha256(corpus.read_bytes()).hexdigest()==manifest['clean_sha256'],'Wait for a closed collection snapshot'
p=subprocess.Popen([str(root/'features-zero')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(root/'feature-errors.log').open('w'),text=True,bufsize=1);selector=selectors.DefaultSelector();selector.register(p.stdout,selectors.EVENT_READ)
rows=[];bases=[];targets=[];ids=[];folds=[];rejected=collections.Counter();games=0;start=time.monotonic()
def features(b):
 p.stdin.write('position fen '+b.fen()+'\nfeatures\n');p.stdin.flush()
 assert selector.select(10),'Own feature extractor did not respond'
 line=p.stdout.readline().strip();assert line.startswith('info string features '),line
 v=list(map(float,line.split()[3:]));assert len(v)==43 and all(np.isfinite(v)),v
 return v[0],v[1:]
try:
 with corpus.open() as f:
  while True:
   game=chess.pgn.read_game(f)
   if game is None:break
   if game.errors:rejected['parse']+=1;continue
   if game.headers.get('Termination','Normal')!='Normal':rejected['non_board_termination']+=1;continue
   gid=game.headers['Site'].rstrip('/').split('/')[-1];digest=hashlib.sha256(gid.encode()).digest();rng=random.Random(int.from_bytes(digest[:8],'big'));b=game.board();candidates=[]
   for move in game.mainline_moves():
    b.push(move)
    if b.ply()<16 or b.ply()>160 or b.ply()%2!=digest[9]%2 or b.halfmove_clock>=80 or b.is_check() or b.is_insufficient_material():continue
    if b.is_repetition(2):continue
    if any(b.is_capture(m) or m.promotion for m in b.legal_moves):continue
    candidates.append(b.copy(stack=False))
   if not candidates:rejected['no_quiet_position']+=1;continue
   target={'1-0':1.,'0-1':0.,'1/2-1/2':.5}[game.headers['Result']];used=0
   for board in rng.sample(candidates,min(24,len(candidates))):
    base,x=features(board)
    if abs(base)>1500:rejected['already_decisive_position']+=1;continue
    rows.append(x);bases.append(base);targets.append(target);ids.append(gid);folds.append(digest[8]%5!=0);used+=1
   if used:games+=1
   if games and games%250==0:print(json.dumps({'games':games,'quiet_positions':len(rows)}),flush=True)
finally:
 p.stdin.write('quit\n');p.stdin.flush();p.wait();selector.close()
X=np.asarray(rows,dtype=np.float64);base=np.asarray(bases,dtype=np.float64);y=np.asarray(targets,dtype=np.float64);train=np.asarray(folds,dtype=bool)
assert X.shape[1]==42 and len(X)>5000 and train.any() and (~train).any()
train_ids=set(np.asarray(ids)[train]);valid_ids=set(np.asarray(ids)[~train]);assert not train_ids&valid_ids
np.savez_compressed(data/'train-matrix.npz',X=X,base=base,y=y,train=train,game_ids=np.asarray(ids))
report={'positions':len(X),'human_games_used':games,'train_positions':int(train.sum()),'validation_positions':int((~train).sum()),'train_games':len(train_ids),'validation_games':len(valid_ids),'game_split_disjoint':True,'features':42,'label_source':'Human final Result, no engine analysis','own_feature_binary_sha256':hashlib.sha256((root/'features-zero').read_bytes()).hexdigest(),'clean_corpus_sha256':manifest['clean_sha256'],'filters':['both players >=2200 Lichess','no BOT titles','standard rated >=180 seconds','normal termination','quiet positions: no check, capture or promotion available','plies16..160, no imminent rule draw','maximum24 sampled positions per game'],'rejections':dict(rejected),'seconds':time.monotonic()-start}
(data/'preparation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
