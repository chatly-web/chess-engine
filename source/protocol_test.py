import sys,pathlib,time,chess,chess.engine
cmd=[sys.executable,str(pathlib.Path(__file__).resolve().parents[1]/'engine/main.py')]
with chess.engine.SimpleEngine.popen_uci(cmd) as e:
 b=chess.Board();a=e.analysis(b);time.sleep(.1);t=time.monotonic();a.stop();a.wait();assert time.monotonic()-t<.5
 for fen in ['7k/6Q1/6K1/8/8/8/8/8 b - - 0 1','7k/5Q2/6K1/8/8/8/8/8 b - - 0 1']:
  r=e.play(chess.Board(fen),chess.engine.Limit(time=.01));assert not r.move
 for turn in [chess.WHITE,chess.BLACK]:
  b=chess.Board();b.turn=turn
  for i in range(20):
   r=e.play(b,chess.engine.Limit(time=.01));assert r.move in b.legal_moves;b.push(r.move)
 print('PASS: asynchronous stop, mate/stalemate null move, 40 rapid legal moves across both colours')
