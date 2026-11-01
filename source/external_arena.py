"""External opponents are benchmark-only. Never import their evaluations."""
import argparse,json,pathlib,sys,time,hashlib
import chess,chess.engine,chess.pgn
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--native',action='store_true');p.add_argument('--opponent',required=True);p.add_argument('--opponent-arg',action='append',default=[]);p.add_argument('--protocol',choices=['uci','xboard'],default='uci');p.add_argument('--base',type=float,default=180);p.add_argument('--increment',type=float,default=2);p.add_argument('--colour',choices=['white','black'],default='white');p.add_argument('--label',required=True);p.add_argument('--movetime',type=float);p.add_argument('--skill-level',type=int,default=None);a=p.parse_args()
 our_command=[str(ROOT/'engine/clash-native')] if a.native else [sys.executable,str(ROOT/'engine/main.py')]
 sources=[ROOT/'source/cpp/engine.cpp',ROOT/'source/cpp/tables.h',ROOT/'engine/clash-native'] if a.native else [ROOT/'source/search.py',ROOT/'source/clock_budget.py',ROOT/'engine/main.py']
 hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}
 ours=chess.engine.SimpleEngine.popen_uci(our_command,timeout=30)
 other=(chess.engine.SimpleEngine.popen_uci if a.protocol=='uci' else chess.engine.SimpleEngine.popen_xboard)([a.opponent]+a.opponent_arg,timeout=30)
 options={k:v for k,v in {'Threads':1,'Hash':64,'Ponder':False}.items() if k in other.options and not other.options[k].is_managed()}
 if a.skill_level is not None and 'Skill Level' in other.options: options['Skill Level']=a.skill_level
 other.configure(options)
 opponent_id=dict(other.id);white=a.colour=='white';b=chess.Board();clocks={True:a.base,False:a.base};log=[];failure=None;result='*';start=time.monotonic()
 try:
  while not b.is_game_over(claim_draw=True) and b.ply()<300:
   side=b.turn;e=ours if side==white else other
   limit=chess.engine.Limit(time=a.movetime) if a.movetime else chess.engine.Limit(white_clock=clocks[True],black_clock=clocks[False],white_inc=a.increment,black_inc=a.increment)
   t=time.monotonic()
   # INFO_NONE: opponent scores/PVs are never requested or stored for learning.
   try:r=e.play(b,limit,info=chess.engine.INFO_NONE);elapsed=time.monotonic()-t
   except Exception as exc:failure=type(exc).__name__;result='0-1' if side else '1-0';break
   if r.move not in b.legal_moves:failure='illegal move';result='0-1' if side else '1-0';break
   if not a.movetime and elapsed>clocks[side]:failure='time forfeit';result='0-1' if side else '1-0';break
   clocks[side]+=a.increment-elapsed
   log.append(dict(ply=b.ply()+1,side='ours' if side==white else 'opponent',move=r.move.uci(),seconds=elapsed,clock=clocks[side]));b.push(r.move)
   (ROOT/(a.label+'-progress.json')).write_text(json.dumps(dict(plies=b.ply(),last=log[-1],moves=log,fen=b.fen())))
  if failure is None:result=b.result(claim_draw=True)
 finally:
  for engine in (ours,other):
   try:
    engine.timeout=2
    engine.quit()
   except Exception as exc:print("Opponent cleanup: "+type(exc).__name__,file=sys.stderr)
   finally:engine.close()
 report=dict(opponent=opponent_id,skill_level=a.skill_level,opponent_options=options,our_colour=a.colour,base=a.base,increment=a.increment,movetime=a.movetime,result=result,failure=failure,finished=result!='*',plies=b.ply(),seconds=time.monotonic()-start,moves=log,source_hashes=hashes)
 (ROOT/(a.label+'.json')).write_text(json.dumps(report,indent=2));g=chess.pgn.Game.from_board(b);g.headers.update(White='Clash' if white else opponent_id.get('name','Opponent'),Black=opponent_id.get('name','Opponent') if white else 'Clash',Result=result,TimeControl=f'{a.base}+{a.increment}' if not a.movetime else f'{a.movetime}s/move');(ROOT/(a.label+'.pgn')).write_text(str(g)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('moves','source_hashes')}),flush=True)
if __name__=='__main__':main()
