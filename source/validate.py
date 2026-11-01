import chess,chess.engine,time,json,sys,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
command=[sys.executable,str(ROOT/'engine/main.py')]
results=[]
def record(name,**kw):
 row=dict(test=name,**kw);results.append(row);print(json.dumps(row),flush=True)
with chess.engine.SimpleEngine.popen_uci(command) as e:
 for name,fen in [('mate','7k/5Q2/6K1/8/8/8/8/8 w - - 0 1'),('promotion','7k/P7/6K1/8/8/8/8/8 w - - 0 1'),('enpassant','7k/8/8/3pP3/8/8/8/K7 w - d6 0 1'),('castling','r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')]:
  b=chess.Board(fen);r=e.play(b,chess.engine.Limit(time=.3));assert r.move in b.legal_moves;b.push(r.move)
  if name=='mate':assert b.is_checkmate()
  record(name,move=r.move.uci(),pass_test=True)
 for clock in [.01,.05,.2,1,180,600]:
  b=chess.Board();start=time.monotonic();r=e.play(b,chess.engine.Limit(white_clock=clock,black_clock=clock,white_inc=0 if clock<2 else 2 if clock==180 else 5,black_inc=0));elapsed=time.monotonic()-start
  assert r.move in b.legal_moves
  record('clock',clock=clock,elapsed=elapsed,legal=True,within_clock=elapsed<clock)
 for base,inc in [(180,2),(600,5)]:
  b=chess.Board();clocks=[float(base),float(base)];start=time.monotonic();maximum=0
  while not b.is_game_over(claim_draw=True) and b.ply()<240:
   side=int(b.turn)
   if b.turn:
    t=time.monotonic();r=e.play(b,chess.engine.Limit(white_clock=clocks[1],black_clock=clocks[0],white_inc=inc,black_inc=inc));spent=time.monotonic()-t;move=r.move
    maximum=max(maximum,spent);assert spent<clocks[side];assert move in b.legal_moves
   else:
    # Original one-ply material opponent; explicitly a weak reliability baseline.
    t=time.monotonic();best=-1e9;move=None
    for m in b.legal_moves:
     b.push(m)
     value=100000 if b.is_checkmate() else sum((1 if p.color==chess.BLACK else -1)*[0,100,315,335,510,950,0][p.piece_type] for p in b.piece_map().values())
     b.pop()
     if value>best:best,move=value,m
    spent=time.monotonic()-t
   clocks[side]+=inc-spent;b.push(move)
  record('full_game',base=base,increment=inc,plies=b.ply(),result=b.result(claim_draw=True),finished=b.is_game_over(claim_draw=True),duration=time.monotonic()-start,max_think=maximum,remaining=clocks,opponent='original greedy material',engine_color='white')
(ROOT/'test-results.json').write_text(json.dumps(results,indent=2))
