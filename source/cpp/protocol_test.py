import pathlib,sys,time,json,subprocess,queue,threading,os,hashlib
import chess,chess.engine
ROOT=pathlib.Path(__file__).resolve().parents[2];BIN=os.environ.get('CLASH_NATIVE_BINARY',str(ROOT/'engine/clash-native'));rows=[]
with chess.engine.SimpleEngine.popen_uci(BIN) as e:
 for name,fen in [('mate','7k/5Q2/6K1/8/8/8/8/8 w - - 0 1'),('underpromotion','8/k1P5/2K5/8/8/8/8/8 w - - 0 1'),('ep','7k/8/8/3pP3/8/8/8/K7 w - d6 0 1')]:
  b=chess.Board(fen);r=e.play(b,chess.engine.Limit(time=.1));assert r.move in b.legal_moves
  if name=='mate':b.push(r.move);assert b.is_checkmate()
  if name=='underpromotion':assert r.move.uci()=='c7c8r'
  rows.append(dict(test=name,move=r.move.uci()))
 for color in (True,False):
  for ms in (5,10,50,200,1000):
   for _ in range(3):
    b=chess.Board()
    if not color:b.push_uci('e2e4')
    t=time.monotonic();r=e.play(b,chess.engine.Limit(white_clock=ms/1000,black_clock=ms/1000,white_inc=2,black_inc=5));elapsed=time.monotonic()-t
    assert r.move in b.legal_moves
    if ms>=50:assert elapsed<ms/1000
    rows.append(dict(test='clock',clock_ms=ms,elapsed_ms=elapsed*1000,within_clock=elapsed<ms/1000))
 for _ in range(20):
  a=e.analysis(chess.Board());time.sleep(.005);e.ping();t=time.monotonic();a.stop();a.wait();assert time.monotonic()-t<.5
 for fen in ['7k/6Q1/6K1/8/8/8/8/8 b - - 0 1','7k/5Q2/6K1/8/8/8/8/8 b - - 0 1']:
  assert not e.play(chess.Board(fen),chess.engine.Limit(time=.01)).move
 for nodes in (0,1,100):assert e.play(chess.Board(),chess.engine.Limit(nodes=nodes)).move in chess.Board().legal_moves
# Raw protocol test: draw root after previous search must never reuse a stale move.
p=subprocess.Popen([BIN],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1);q=queue.Queue();threading.Thread(target=lambda:[q.put(l.strip()) for l in p.stdout],daemon=True).start()
def send(s):p.stdin.write(s+'\n');p.stdin.flush()
def best():
 while True:
  s=q.get(timeout=5)
  if s.startswith('bestmove'):return chess.Move.from_uci(s.split()[1])
send('position startpos moves e2e4');send('go depth 2');best()
send('position startpos moves g1f3 g8f6 f3g1 f6g8 g1f3 g8f6 f3g1 f6g8');send('go depth 2');assert best() in chess.Board().legal_moves
send('position startpos moves e2e4 BAD');send('go nodes 1');assert best() in chess.Board().legal_moves
send('quit');p.wait(timeout=3);assert 'input error' in p.stderr.read();p.stdin.close();p.stdout.close();p.stderr.close()
report_name=os.environ.get('CLASH_PROTOCOL_REPORT','cpp-protocol.json')
assert pathlib.Path(report_name).name==report_name
(ROOT/report_name).write_text(json.dumps(dict(passed=True,native_binary_sha256=hashlib.sha256(pathlib.Path(BIN).read_bytes()).hexdigest(),clock_samples=rows,interrupted_searches=20),indent=2));print('PASS: native UCI, special moves, 30 clock samples, 20 stops, terminal roots, node caps, malformed input recovery')
