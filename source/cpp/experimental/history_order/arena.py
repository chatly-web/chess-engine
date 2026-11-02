"""Matched external-opponent screening. Opponent moves/results only, no analysis labels."""
import argparse,concurrent.futures,hashlib,json,math,pathlib,random,statistics,sys,threading,time
import chess,chess.engine,chess.pgn
ROOT=pathlib.Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source/cpp'))
from test_starts import sample_start
p=argparse.ArgumentParser();p.add_argument('--spec',required=True);p.add_argument('--label',required=True);p.add_argument('--pairs-per-opponent',type=int,default=8);p.add_argument('--seconds',type=float,default=.08);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed-base',type=int,default=4100000);a=p.parse_args()
spec=json.loads(pathlib.Path(a.spec).read_text());engines=spec['engines'];baseline=spec['baseline'];opponents=spec['opponents'];assert baseline in engines
prefix=ROOT/a.label;prefix.parent.mkdir(parents=True,exist_ok=True)
if any(pathlib.Path(str(prefix)+x).exists() for x in ('.json','.jsonl','.pgn')):p.error('Use a fresh result label')
hashes={name:hashlib.sha256(pathlib.Path(cmd).read_bytes()).hexdigest() for name,cmd in engines.items()};lock=threading.Lock();rows=[];started=time.monotonic()
def play_unit(task):
 oi,seed=task;config=opponents[oi];rng=random.Random(a.seed_base+oi*100000+seed);opening=spec['starts'][oi*a.pairs_per_opponent+seed];initial=chess.Board();
 for move in opening['moves']:initial.push_uci(move)
 attempts=1;unit=[]
 slots=[(name,white) for name in engines for white in (True,False)];rng.shuffle(slots)
 for name,white in slots:
  b=initial.copy();failure=None;failure_side=None;result='*';termination=None;identity={};options={};t0=time.monotonic();own=other=None
  try:
   own=chess.engine.SimpleEngine.popen_uci(str(pathlib.Path(engines[name]).resolve()),timeout=10)
   own.configure(spec.get('own_options',{}).get(name,{}));other=chess.engine.SimpleEngine.popen_uci(config['command'],timeout=10);identity=dict(other.id)
   options={k:v for k,v in {'Threads':1,'Hash':64,'OwnBook':False,**config.get('options',{})}.items() if k in other.options and not other.options[k].is_managed()};other.configure(options)
   while not b.is_game_over(claim_draw=True) and b.ply()<600:
    side=b.turn;player=own if side==white else other
    try:move=player.play(b,chess.engine.Limit(time=a.seconds),info=chess.engine.INFO_NONE)
    except Exception as exc:failure=type(exc).__name__;failure_side='candidate' if side==white else 'opponent';break
    if move.resigned:result='0-1' if side else '1-0';termination='resignation';break
    if move.move not in b.legal_moves:failure='illegal move';failure_side='candidate' if side==white else 'opponent';break
    b.push(move.move)
   if failure is None and termination is None:result=b.result(claim_draw=True)
  except Exception as exc:failure=type(exc).__name__;failure_side='launch_or_harness'
  finally:
   for player in (own,other):
    if player:
     try:player.quit()
     except Exception:player.close()
  score=None if result=='*' else .5 if result=='1/2-1/2' else float((result=='1-0')==white)
  row=dict(seed=a.seed_base+oi*100000+seed,opponent=config['label'],engine=name,candidate_white=white,result=result,score=score,plies=b.ply(),failure=failure,failure_side=failure_side,seconds=time.monotonic()-t0,requested_seconds_per_move=a.seconds,opening_attempts=attempts,initial_plies=opening['plies'],human_opening_game_id=opening['game_id'],opponent_id=identity,opponent_options=options,own_options=spec.get('own_options',{}).get(name,{}));unit.append(row)
  g=chess.pgn.Game.from_board(b);g.headers.update(White=name if white else config['label'],Black=config['label'] if white else name,Result=result,Event='Matched independent human-prefix screening',TestSeed=str(row['seed']),EngineSHA256=hashes[name],TimeControl=f'{a.seconds:g}s/move')
  with lock:
   rows.append(row)
   with open(str(prefix)+'.jsonl','a') as f:f.write(json.dumps(row)+'\n')
   with open(str(prefix)+'.pgn','a') as f:f.write(str(g)+'\n\n')
   print(json.dumps({'games':len(rows),'engine':name,'opponent':config['label'],'result':result,'failure':failure}),flush=True)
 return unit
units=[(oi,seed) for oi in range(len(opponents)) for seed in range(a.pairs_per_opponent)];random.Random(a.seed_base+1001).shuffle(units)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(play_unit,units))
summary={}
for name in engines:
 summary[name]={}
 for config in opponents:
  selected=[r for r in rows if r['engine']==name and r['opponent']==config['label']];done=[r for r in selected if r['score'] is not None]
  summary[name][config['label']]={'games':len(selected),'completed':len(done),'wins':sum(r['score']==1 for r in done),'draws':sum(r['score']==.5 for r in done),'losses':sum(r['score']==0 for r in done),'points':sum(r['score'] for r in done),'unfinished':len(selected)-len(done),'failures':sum(r['failure'] is not None for r in selected)}
comparisons={}
for name in engines:
 if name==baseline:continue
 diffs=[];by_opponent={}
 for oi,seed in units:
  key=a.seed_base+oi*100000+seed;group=[r for r in rows if r['seed']==key and r['engine'] in (name,baseline)]
  if len(group)==4 and all(r['score'] is not None for r in group):
   delta=sum(r['score'] for r in group if r['engine']==name)/2-sum(r['score'] for r in group if r['engine']==baseline)/2;diffs.append(delta);by_opponent.setdefault(opponents[oi]['label'],[]).append(delta)
 mean=statistics.mean(diffs) if diffs else None;se=math.sqrt(statistics.variance(diffs)/len(diffs)) if len(diffs)>1 else None
 comparisons[name]={'matched_units':len(diffs),'mean_point_score_difference':mean,'approximate_95_interval':[mean-1.96*se,mean+1.96*se] if se is not None else None,'per_opponent_difference':{k:statistics.mean(v) for k,v in by_opponent.items()}}
assert hashes=={name:hashlib.sha256(pathlib.Path(cmd).read_bytes()).hexdigest() for name,cmd in engines.items()},'Frozen binary changed during screening'
report={'workers':a.workers,'harness_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'opponent_binary_sha256':{o['label']:hashlib.sha256(pathlib.Path(o['command'][0]).read_bytes()).hexdigest() for o in opponents},'baseline':baseline,'binary_sha256':hashes,'opponent_labels':[o['label'] for o in opponents],'pairs_per_opponent':a.pairs_per_opponent,'seed_base':a.seed_base,'seconds_per_move':a.seconds,'summary':summary,'comparisons':comparisons,'matches':rows,'duration_seconds':time.monotonic()-started,'limitations':'Short fixed move limits, balanced human opening prefixes excluded from all fitting/hyperparameter validation, both colours. No agent opening book is used. Opponent random skill choices are not seeded. Concurrent local tests; approximate descriptive paired-unit intervals, not Elo, move accuracy or official-clock evidence. Failures/unfinished games are not credited as wins/draws.'};pathlib.Path(str(prefix)+'.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['matches','limitations']},indent=2))
