"""Own C++ candidate versus own baseline, paired colours on fresh human prefixes."""
from pathlib import Path
import argparse,json,sys,concurrent.futures,random,threading,time,hashlib,statistics,math
import chess,chess.engine,chess.pgn
p=Path(__file__).resolve().parent;root=p.parents[3];folder=root/'history-pass';parser=argparse.ArgumentParser();parser.add_argument('--candidate',required=True);parser.add_argument('--reference',required=True);parser.add_argument('--label',required=True);parser.add_argument('--start',type=int,default=0);parser.add_argument('--pairs',type=int,default=16);parser.add_argument('--seconds',type=float,default=.08);parser.add_argument('--workers',type=int,default=1);parser.add_argument('--seed',type=int,default=63000000);a=parser.parse_args();output=root/a.label;paths={'candidate':Path(a.candidate).resolve(),'baseline':Path(a.reference).resolve()};hashes={n:hashlib.sha256(f.read_bytes()).hexdigest() for n,f in paths.items()};starts=json.loads((p/'replication-starts.json').read_text())[a.start:a.start+a.pairs];lock=threading.Lock();rows=[];t0=time.monotonic();assert not output.with_suffix('.jsonl').exists()
def unit(task):
 i,start=task;colours=[True,False];random.Random(a.seed+i).shuffle(colours)
 for white in colours:
  b=chess.Board()
  for m in start['moves']:b.push_uci(m)
  players={};failure=None;failure_side=None;depths={n:[] for n in paths};own_nodes={n:0 for n in paths};started=time.monotonic()
  try:
   for n,f in paths.items():players[n]=chess.engine.SimpleEngine.popen_uci(str(f),timeout=10)
   while not b.is_game_over(claim_draw=True) and b.ply()<600:
    name='candidate' if b.turn==white else 'baseline'
    try:
     reply=players[name].play(b,chess.engine.Limit(time=a.seconds),info=chess.engine.INFO_BASIC)
     if reply.move not in b.legal_moves:raise ValueError('illegal move')
    except Exception as exc:failure=type(exc).__name__;failure_side=name;break
    if 'depth' in reply.info:depths[name].append(reply.info['depth'])
    own_nodes[name]+=reply.info.get('nodes',0);b.push(reply.move)
  except Exception as exc:failure=type(exc).__name__;failure_side='launch_or_harness'
  finally:
   for e in players.values():
    try:e.timeout=2;e.quit()
    except Exception:e.close()
  result=b.result(claim_draw=True) if not failure else '*';score=None if result=='*' else .5 if result=='1/2-1/2' else float((result=='1-0')==white)
  row={'unit':i,'candidate_white':white,'human_game_id':start['game_id'],'initial_plies':start['plies'],'result':result,'score':score,'plies':b.ply(),'failure':failure,'failure_side':failure_side,'seconds':time.monotonic()-started,'own_depths':{n:{'moves':len(v),'median':statistics.median(v) if v else None,'sum':sum(v)} for n,v in depths.items()},'own_nodes':own_nodes}
  game=chess.pgn.Game.from_board(b);game.headers.update(Event='Frozen C++ candidate vs own baseline',White='candidate' if white else 'baseline',Black='baseline' if white else 'candidate',Result=result,TestUnit=str(i),CandidateSHA256=hashes['candidate'],BaselineSHA256=hashes['baseline'],TimeControl=f'{a.seconds:g}s/move')
  with lock:
   rows.append(row)
   with output.with_suffix('.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
   with output.with_suffix('.pgn').open('a') as f:f.write(str(game)+'\n\n')
   print(json.dumps({'games':len(rows),'unit':i,'result':result,'score':score,'failure':failure}),flush=True)
units=list(enumerate(starts));random.Random(a.seed+1000).shuffle(units)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(unit,units))
paired=[]
for i in range(a.pairs):
 r=[r for r in rows if r['unit']==i]
 if len(r)==2 and all(v['score'] is not None for v in r):paired.append(sum(v['score'] for v in r)/2)
mean=statistics.mean(paired) if paired else None;se=math.sqrt(statistics.variance(paired)/len(paired)) if len(paired)>1 else None;report={'binary_sha256':hashes,'requested_seconds':a.seconds,'workers':a.workers,'games':len(rows),'finished':sum(r['score'] is not None for r in rows),'wins':sum(r['score']==1 for r in rows),'draws':sum(r['score']==.5 for r in rows),'losses':sum(r['score']==0 for r in rows),'failures':sum(r['failure'] is not None for r in rows),'paired_units':len(paired),'paired_mean_point_score':mean,'approximate_95_interval':[mean-1.96*se,mean+1.96*se] if se is not None else None,'matches':rows,'seconds':time.monotonic()-t0,'note':'Own C++ frozen-game comparison. Fresh human-game prefixes exclude fitting and all prior pass prefixes. Both colours; finite concurrent fixed-move games, not Elo, Lichess accuracy or actual-clock evidence.'};assert hashes=={n:hashlib.sha256(f.read_bytes()).hexdigest() for n,f in paths.items()};output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='matches'},indent=2),flush=True)
