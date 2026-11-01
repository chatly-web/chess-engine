"""Time-bounded, frozen-binary native validation with durable per-pair records."""
import argparse,concurrent.futures,datetime,hashlib,json,pathlib,random,time,threading
import chess,chess.engine,chess.pgn
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--baseline',required=True);period=p.add_mutually_exclusive_group(required=True);period.add_argument('--until-utc');period.add_argument('--minutes',type=float);p.add_argument('--workers',type=int,default=4);p.add_argument('--label',default='long-pass/sustained');a=p.parse_args()
commands=[str(pathlib.Path(v).resolve()) for v in (a.candidate,a.baseline)];hashes=[hashlib.sha256(pathlib.Path(v).read_bytes()).hexdigest() for v in commands]
end=(time.time()+a.minutes*60) if a.minutes is not None else datetime.datetime.fromisoformat(a.until_utc.replace('Z','+00:00')).timestamp()
if end<=time.time():p.error('The requested end time must be in the future')
a.until_utc=datetime.datetime.fromtimestamp(end,datetime.timezone.utc).isoformat()
lock=threading.Lock();next_seed=0
rows=[];pairs=[];prefix=ROOT/a.label;prefix.parent.mkdir(parents=True,exist_ok=True);started=time.time()
if any(pathlib.Path(str(prefix)+suffix).exists() for suffix in ('.jsonl','.pgn','-summary.json')):
 p.error('Choose a new label: existing result files must not be appended to a fresh run')
def worker(worker_id):
 global next_seed
 while time.time()<end:
  with lock:seed=next_seed;next_seed+=1
  rng=random.Random(1500000+seed);initial=chess.Board()
  for _ in range(8):initial.push(rng.choice(list(initial.legal_moves)))
  seconds=.1 if rng.random()<.5 else .2;result_rows=[];pgn=[]
  for white in (True,False):
   b=initial.copy();failure=None
   with chess.engine.SimpleEngine.popen_uci(commands[0],timeout=10) as c,chess.engine.SimpleEngine.popen_uci(commands[1],timeout=10) as base:
    while not b.is_game_over(claim_draw=True) and b.ply()<328:
     try:r=(c if b.turn==white else base).play(b,chess.engine.Limit(time=seconds),info=chess.engine.INFO_NONE)
     except Exception as exc:failure=type(exc).__name__;break
     if r.move not in b.legal_moves:failure='illegal move';break
     b.push(r.move)
   outcome=b.result(claim_draw=True) if failure is None else '*';score=None if outcome=='*' else .5 if outcome=='1/2-1/2' else float((outcome=='1-0')==white)
   result_rows.append(dict(seed=seed,candidate_white=white,result=outcome,score=score,plies=b.ply(),movetime=seconds,failure=failure))
   g=chess.pgn.Game.from_board(b);g.headers.update(White='Candidate' if white else 'Baseline',Black='Baseline' if white else 'Candidate',Result=outcome);pgn.append(str(g))
  with lock:
   rows.extend(result_rows)
   if all(x['score'] is not None for x in result_rows):pairs.append(sum(x['score'] for x in result_rows))
   with open(str(prefix)+'.jsonl','a') as f:
    for row in result_rows:f.write(json.dumps(row)+'\n')
   with open(str(prefix)+'.pgn','a') as f:f.write('\n\n'.join(pgn)+'\n\n')
   completed=[r for r in rows if r['score'] is not None]
   summary=dict(start_utc=datetime.datetime.fromtimestamp(started,datetime.timezone.utc).isoformat(),elapsed=time.time()-started,games=len(rows),completed=len(completed),unfinished=len(rows)-len(completed),wins=sum(x['score']==1 for x in completed),draws=sum(x['score']==.5 for x in completed),losses=sum(x['score']==0 for x in completed),points=sum(x['score'] for x in completed),technical_failures=sum(x['failure'] is not None for x in rows),binary_sha256=hashes,until_utc=a.until_utc,stationarity_note='Fixed binaries, independent random starting-position pairs, colours reversed; mixed short controls and concurrent local games, not official-clock win-rate evidence.')
   pathlib.Path(str(prefix)+'-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(worker,range(a.workers)))
# Sequential conditional pair-win SPRT, kept separate from point score.
import math
llr=0;decision='continue';observed=0
for v in pairs:
 observed+=1
 if v>1:llr+=math.log(.6/.5)
 elif v<1:llr+=math.log(.4/.5)
 if llr>=math.log(19):decision='accept_h1';break
 if llr<=-math.log(19):decision='accept_h0';break
final=json.loads(pathlib.Path(str(prefix)+'-summary.json').read_text());final['paired_sprt']=dict(decision=decision,llr=llr,pairs_observed=observed,p0=.5,p1=.6);final['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();pathlib.Path(str(prefix)+'-summary.json').write_text(json.dumps(final,indent=2))
