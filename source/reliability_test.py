"""Deterministic reliability regressions; no external chess engine involved."""
import json, pathlib, random, sys, time, unittest, subprocess, queue, threading
import chess, chess.engine
from search import Search, Timeout, MATE
from clock_budget import budget
ROOT=pathlib.Path(__file__).resolve().parents[1]
CMD=[sys.executable,str(ROOT/'engine/main.py')]
METRICS={}
class Reliability(unittest.TestCase):
 def test_clock_budget_grid(self):
  count=0
  for white in (False,True):
   for ms in (0,1,5,10,50,100,200,1000,10000,180000,600000):
    for inc in (0,2000,5000,100000):
     for mtg in (0,1,2,30,100):
      t=budget(dict(wtime=ms,btime=ms,winc=inc,binc=inc,movestogo=mtg),white)
      self.assertGreaterEqual(t,0);self.assertLessEqual(t,ms/1000*.8+1e-9);count+=1
  METRICS['clock_budget_cases']=count
 def test_random_positions(self):
  rng=random.Random(712);b=chess.Board();count=0
  for i in range(400):
   if b.is_game_over() or b.ply()>180:b=chess.Board()
   b.push(rng.choice(list(b.legal_moves)))
   original=b.fen();stack=list(b.move_stack);s=Search()
   move=s.choose(b,.002)
   if not b.is_game_over():self.assertIn(move,b.legal_moves)
   self.assertEqual(b.fen(),original);self.assertEqual(b.move_stack,stack)
   self.assertEqual(s.evaluate(b),s.evaluate(b.mirror()));count+=1
  METRICS['random_positions']=count
 def test_reference_minimax(self):
  # Exhaustive depth-2 search with the SAME leaf quiescence: tests PVS,
  # bounds, ordering and cache against a simpler, independent tree traversal.
  def reference(b,d,s,ply=0):
   moves=list(b.legal_moves)
   if not moves:return -MATE+ply if b.is_check() else 0
   if b.is_insufficient_material() or b.is_fifty_moves() or b.is_repetition(3):return 0
   if d==0:return s.search(b,0,-32000,32000,ply)
   values=[]
   for m in moves:
    b.push(m)
    try:values.append(-reference(b,d-1,s,ply+1))
    finally:b.pop()
   return max(values)
  rng=random.Random(19);b=chess.Board()
  for i in range(12):
   b.push(rng.choice(list(b.legal_moves)))
   s=Search(reductions=False);s.deadline=time.monotonic()+120
   expected=reference(b,2,s)
   actual=s.search(b,2,-32000,32000)
   self.assertEqual(actual,expected,(b.fen(),actual,expected))
   self.assertEqual(s.search(b,2,-32000,32000),expected)
  METRICS['reference_positions']=12
 def test_draw_and_terminal(self):
  positions=[('7k/6Q1/6K1/8/8/8/8/8 b - - 0 1',-MATE),('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1',0),('7k/8/8/8/8/8/8/K7 w - - 0 1',0),('7k/8/8/8/8/8/5R2/K7 w - - 100 60',0)]
  for fen,score in positions:
   s=Search();s.deadline=time.monotonic()+1;self.assertEqual(s.search(chess.Board(fen),2,-32000,32000),score)
  b=chess.Board()
  for move in ['g1f3','g8f6','f3g1','f6g8']*2:b.push_uci(move)
  s=Search();s.deadline=time.monotonic()+1;self.assertEqual(s.search(b,2,-32000,32000),0)
 def test_special_rules(self):
  b=chess.Board('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
  self.assertIn(chess.Move.from_uci('e1g1'),b.legal_moves);self.assertIn(chess.Move.from_uci('e1c1'),b.legal_moves)
  b=chess.Board('k3r3/8/8/3pP3/8/8/8/4K3 w - d6 0 1')
  self.assertNotIn(chess.Move.from_uci('e5d6'),b.legal_moves)
  b=chess.Board('8/k1P5/2K5/8/8/8/8/8 w - - 0 1')
  m=Search().choose(b,1)
  self.assertEqual(m.uci(),'c7c8r')
 def test_generated_mates(self):
  rng=random.Random(412);tested=0
  for attempt in range(20000):
   squares=rng.sample(range(64),3);b=chess.Board(None)
   b.set_piece_at(squares[0],chess.Piece(chess.KING,True))
   b.set_piece_at(squares[1],chess.Piece(chess.QUEEN,True))
   b.set_piece_at(squares[2],chess.Piece(chess.KING,False))
   if not b.is_valid():continue
   mates=[]
   for m in list(b.legal_moves):
    b.push(m)
    if b.is_checkmate():mates.append(m)
    b.pop()
   if not mates:continue
   for position in (b,b.mirror()):
    move=Search().choose(position,2,depth=1)
    position.push(move);self.assertTrue(position.is_checkmate());position.pop()
    tested+=1
   if tested>=60:break
  self.assertEqual(tested,60);METRICS['generated_mate_in_one_positions']=tested
 def test_uci_clock_and_lifecycle(self):
  samples=[]
  with chess.engine.SimpleEngine.popen_uci(CMD) as e:
   for color in (True,False):
    for ms in (5,10,50,200,1000):
     for rep in range(4):
      b=chess.Board()
      if not color:b.push_uci('e2e4')
      start=time.monotonic();r=e.play(b,chess.engine.Limit(white_clock=ms/1000,black_clock=ms/1000,white_inc=2,black_inc=5));elapsed=time.monotonic()-start
      self.assertIn(r.move,b.legal_moves)
      # OS scheduling makes sub-50 ms clocks unsuitable as a hard timing gate.
      if ms>=50:self.assertLess(elapsed,ms/1000)
      samples.append(dict(clock_ms=ms,elapsed_ms=elapsed*1000,within_clock=elapsed<ms/1000))
   for _ in range(12):
    a=e.analysis(chess.Board());time.sleep(.005);t=time.monotonic();a.stop();a.wait();self.assertLess(time.monotonic()-t,.5);e.ping()
   for nodes in (1,10,100):
    self.assertIn(e.play(chess.Board(),chess.engine.Limit(nodes=nodes)).move,chess.Board().legal_moves)
  METRICS['uci_clock_samples']=samples
 def test_malformed_position_atomicity(self):
  p=subprocess.Popen(CMD,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1);q=queue.Queue()
  threading.Thread(target=lambda:[q.put(line.strip()) for line in p.stdout],daemon=True).start()
  def send(x):p.stdin.write(x+'\n');p.stdin.flush()
  try:
   send('uci')
   while q.get(timeout=3)!='uciok':pass
   send('position startpos moves e2e4 BAD')
   send('go nodes 1')
   line=q.get(timeout=3)
   while not line.startswith('bestmove '):line=q.get(timeout=3)
   self.assertIn(chess.Move.from_uci(line.split()[1]),chess.Board().legal_moves)
   send('isready');self.assertEqual(q.get(timeout=3),'readyok')
   send('quit');p.wait(timeout=3)
   self.assertIn('INPUT ERROR',p.stderr.read())
  finally:
   if p.poll() is None:p.kill();p.wait()
   p.stdin.close();p.stdout.close();p.stderr.close()
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Reliability)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 METRICS.update(test_groups=result.testsRun,failures=len(result.failures),errors=len(result.errors))
 (ROOT/'reliability-results.json').write_text(json.dumps(METRICS,indent=2))
 sys.exit(not result.wasSuccessful())
