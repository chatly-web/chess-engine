"""Performance-only candidate gate against a specified frozen native baseline."""
import sys,argparse,chess,chess.engine,chess.pgn,pathlib,time,random,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--candidate');p.add_argument('--label',default='native-improvement');p.add_argument('--fixed-only',action='store_true');a=p.parse_args();cmds={'candidate':str(pathlib.Path(a.candidate).resolve()) if a.candidate else str(ROOT/'engine/clash-native'),'baseline':str(pathlib.Path(a.baseline).resolve())}
positions=[];rng=random.Random(317);b=chess.Board();positions.append(b.copy())
for i in range(40):
 b.push(rng.choice(list(b.legal_moves)))
 if i in (7,15,23,31,39):positions.append(b.copy())
fixed=[]
for i,b in enumerate(positions):
 pair={}
 for name,cmd in cmds.items():
  with chess.engine.SimpleEngine.popen_uci(cmd) as e:
   t=time.monotonic();r=e.play(b,chess.engine.Limit(depth=4,time=10),info=chess.engine.INFO_ALL);elapsed=time.monotonic()-t
   pair[name]=dict(move=r.move.uci(),score=r.info['score'].relative.score(mate_score=30000),depth=r.info['depth'],nodes=r.info['nodes'],seconds=elapsed)
 assert pair['candidate']['depth']==pair['baseline']['depth']==4
 assert pair['candidate']['move']==pair['baseline']['move'],pair
 assert pair['candidate']['score']==pair['baseline']['score'],pair
 assert pair['candidate']['nodes']==pair['baseline']['nodes'],pair
 fixed.append(dict(position=i,**pair));print(fixed[-1],flush=True)
(ROOT/(a.label+'-fixed.json')).write_text(json.dumps(fixed,indent=2))
if a.fixed_only:sys.exit(0)
games=[];pgn=[]
for seed in range(6):
 rng=random.Random(8700+seed);initial=chess.Board()
 for i in range(4):initial.push(rng.choice(list(initial.legal_moves)))
 for white in (True,False):
  b=initial.copy()
  with chess.engine.SimpleEngine.popen_uci(cmds['candidate']) as candidate,chess.engine.SimpleEngine.popen_uci(cmds['baseline']) as baseline:
   while not b.is_game_over(claim_draw=True) and b.ply()<244:
    r=(candidate if b.turn==white else baseline).play(b,chess.engine.Limit(time=.1));assert r.move in b.legal_moves;b.push(r.move)
  result=b.result(claim_draw=True);score=None if result=='*' else .5 if result=='1/2-1/2' else float((result=='1-0')==white)
  row=dict(seed=seed,candidate_white=white,result=result,score=score,plies=b.ply());games.append(row);print(row,flush=True)
  game=chess.pgn.Game.from_board(b);game.headers.update(White='Candidate' if white else 'v0.5',Black='v0.5' if white else 'Candidate',Result=result);pgn.append(str(game))
(ROOT/(a.label+'-matches.json')).write_text(json.dumps(dict(games=games,baseline_sha256=hashlib.sha256(pathlib.Path(cmds['baseline']).read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(pathlib.Path(cmds['candidate']).read_bytes()).hexdigest()),indent=2));(ROOT/(a.label+'-matches.pgn')).write_text('\n\n'.join(pgn)+'\n')
