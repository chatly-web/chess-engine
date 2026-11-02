"""Held-out paired matches for a trained native candidate; no external analysis."""
import argparse,pathlib,random,json,time,hashlib,concurrent.futures,math,threading
import chess,chess.engine,chess.pgn
from test_starts import sample_start
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--baseline',required=True);p.add_argument('--pairs',type=int,default=32);p.add_argument('--seed-base',type=int,default=91000);p.add_argument('--workers',type=int,default=4);p.add_argument('--fast-seconds',type=float,default=.05);p.add_argument('--slow-seconds',type=float,default=.1);p.add_argument('--label',default='training-validation');a=p.parse_args();commands=[str(pathlib.Path(v).resolve()) for v in (a.candidate,a.baseline)]
prefix=ROOT/a.label;prefix.parent.mkdir(parents=True,exist_ok=True)
if any(pathlib.Path(str(prefix)+suffix).exists() for suffix in ('.json','.jsonl','.pgn')):p.error('Use a new label; existing validation evidence must not be overwritten')
lock=threading.Lock()
def play_pair(seed):
 rng=random.Random(a.seed_base+seed);initial,attempts=sample_start(rng)
 seconds=a.fast_seconds if seed%2 else a.slow_seconds;rows=[];pgn=[]
 for white in (True,False):
  b=initial.copy()
  with chess.engine.SimpleEngine.popen_uci(commands[0]) as c,chess.engine.SimpleEngine.popen_uci(commands[1]) as base:
   while not b.is_game_over(claim_draw=True) and b.ply()<328:
    r=(c if b.turn==white else base).play(b,chess.engine.Limit(time=seconds),info=chess.engine.INFO_NONE)
    if r.move not in b.legal_moves:raise RuntimeError('Illegal candidate validation move')
    b.push(r.move)
  result=b.result(claim_draw=True);score=None if result=='*' else .5 if result=='1/2-1/2' else float((result=='1-0')==white)
  rows.append(dict(seed=seed,opening_attempts=attempts,candidate_white=white,result=result,score=score,plies=b.ply(),seconds_per_move=seconds))
  g=chess.pgn.Game.from_board(b);g.headers.update(White='Trained' if white else 'Default',Black='Default' if white else 'Trained',Result=result,Event='Held-out validation',ValidationSeed=str(seed),CandidateWhite=str(white));pgn.append(str(g))
 with lock:
  with open(str(prefix)+'.jsonl','a') as f:
   for row in rows:f.write(json.dumps(row)+'\n')
  with open(str(prefix)+'.pgn','a') as f:f.write('\n\n'.join(pgn)+'\n\n')
 return rows,pgn
rows=[];games=[];pair_scores=[];start=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
 for results,pgn in pool.map(play_pair,range(a.pairs)):
  rows+=results;games+=pgn;print(results,flush=True)
  if all(r['score'] is not None for r in results):pair_scores.append(sum(r['score'] for r in results))
# SPRT of conditional decisive-pair win probability: H0=.5, H1=.6.
# A drawn pair contributes no evidence; this is NOT an Elo test.
llr=0;decision='continue';observed=0
for score in pair_scores:
 observed+=1
 if score>1:llr+=math.log(.6/.5)
 elif score<1:llr+=math.log(.4/.5)
 if llr>=math.log(19):decision='accept_h1';break
 if llr<=-math.log(19):decision='accept_h0';break
completed=[r for r in rows if r['score'] is not None]
report=dict(games=rows,completed=len(completed),unfinished=len(rows)-len(completed),wins=sum(r['score']==1 for r in completed),draws=sum(r['score']==.5 for r in completed),losses=sum(r['score']==0 for r in completed),points=sum(r['score'] for r in completed),paired_sprt=dict(decision=decision,llr=llr,pairs_observed=observed,p0=.5,p1=.6,assumptions='Independent sampled starting-position pairs and stationary conditional pair-win probability; drawn pairs ignored. Not an Elo or universal accuracy guarantee.'),promoted=decision=='accept_h1' and len(completed)==len(rows),duration=time.monotonic()-start,candidate_sha256=hashlib.sha256(pathlib.Path(commands[0]).read_bytes()).hexdigest(),baseline_sha256=hashlib.sha256(pathlib.Path(commands[1]).read_bytes()).hexdigest())
(ROOT/(a.label+'.json')).write_text(json.dumps(report,indent=2));(ROOT/(a.label+'.pgn')).write_text('\n\n'.join(games)+'\n');print({k:v for k,v in report.items() if k!='games'},flush=True)
