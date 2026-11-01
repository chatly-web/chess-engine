"""Full games between two original engine builds at tournament clocks."""
import argparse,pathlib,json,hashlib,time,concurrent.futures
import chess,chess.engine,chess.pgn
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--a',required=True);p.add_argument('--b',required=True);p.add_argument('--label',default='clock-training');p.add_argument('--base',type=float,default=180);p.add_argument('--increment',type=float,default=2);a=p.parse_args()
commands=[str(pathlib.Path(a.a).resolve()),str(pathlib.Path(a.b).resolve())];hashes=[hashlib.sha256(pathlib.Path(c).read_bytes()).hexdigest() for c in commands]
def play(a_white):
 b=chess.Board();clocks={True:a.base,False:a.base};moves=[];failure=None;result='*';start=time.monotonic()
 with chess.engine.SimpleEngine.popen_uci(commands[0]) as first,chess.engine.SimpleEngine.popen_uci(commands[1]) as second:
  while not b.is_game_over(claim_draw=True) and b.ply()<400:
   side=b.turn;t=time.monotonic()
   try:r=(first if side==a_white else second).play(b,chess.engine.Limit(white_clock=clocks[True],black_clock=clocks[False],white_inc=a.increment,black_inc=a.increment),info=chess.engine.INFO_NONE)
   except Exception as exc:failure=type(exc).__name__;result='0-1' if side else '1-0';break
   elapsed=time.monotonic()-t
   if r.move not in b.legal_moves or elapsed>clocks[side]:failure='illegal move' if r.move not in b.legal_moves else 'time forfeit';result='0-1' if side else '1-0';break
   clocks[side]+=a.increment-elapsed;moves.append(dict(move=r.move.uci(),seconds=elapsed,clock=clocks[side]));b.push(r.move)
   (ROOT/(a.label+('-white' if a_white else '-black')+'-progress.json')).write_text(json.dumps(dict(plies=b.ply(),fen=b.fen(),moves=moves)))
  if failure is None:result=b.result(claim_draw=True)
 g=chess.pgn.Game.from_board(b);g.headers.update(White='Clash',Black='Clash',Result=result,TimeControl=f'{a.base:g}+{a.increment:g}',TrainingGroup=a.label,EngineSHA256=':'.join(sorted(hashes)),WhiteVariant=hashes[0] if a_white else hashes[1],BlackVariant=hashes[1] if a_white else hashes[0])
 return dict(a_white=a_white,result=result,failure=failure,plies=b.ply(),base=a.base,increment=a.increment,engine_sha256=hashes,duration=time.monotonic()-start,moves=moves),str(g)
rows=[];pgn=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for row,g in pool.map(play,[True,False]):rows.append(row);pgn.append(g);print({k:v for k,v in row.items() if k!='moves'},flush=True)
(ROOT/(a.label+'.json')).write_text(json.dumps(rows,indent=2));(ROOT/(a.label+'.pgn')).write_text('\n\n'.join(pgn)+'\n')
