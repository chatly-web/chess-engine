"""Native rules/evaluation differential tests; python-chess is the rules oracle."""
import pathlib,sys,subprocess,random,time,json,os,hashlib
import chess,chess.engine
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'source'))
from search import Search
BIN=os.environ.get('CLASH_NATIVE_BINARY',str(ROOT/'engine/clash-native'))
p=subprocess.Popen([BIN],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
def query(b,cmd):
 p.stdin.write('position fen '+b.fen()+'\n'+cmd+'\n');p.stdin.flush();return p.stdout.readline().strip()
report={'native_binary_sha256':hashlib.sha256(pathlib.Path(BIN).read_bytes()).hexdigest(),'weights_config_sha256':hashlib.sha256(pathlib.Path(os.environ['CLASH_WEIGHTS']).read_bytes()).hexdigest() if os.environ.get('CLASH_WEIGHTS') else None};start=time.monotonic()
try:
 for fen,d,expected in [(chess.STARTING_FEN,4,197281),('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1',3,97862),('8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1',4,43238)]:
  actual=int(query(chess.Board(fen),'perft '+str(d)));assert actual==expected,(fen,actual,expected)
 report['perft_nodes']=[197281,97862,43238]
 rng=random.Random(177);b=chess.Board();evaluator=Search();mismatches=[]
 for i in range(2000):
  if b.is_game_over() or b.ply()>180:b=chess.Board()
  b.push(rng.choice(list(b.legal_moves)))
  actual=set(query(b,'legal').split());expected={m.uci() for m in b.legal_moves};assert actual==expected,(b.fen(),actual^expected)
  if os.environ.get('CLASH_TACTICAL_CHECK'):
   actual_captures=set(query(b,'legalcaptures').split())
   expected_captures={m.uci() for m in b.legal_moves if b.is_capture(m) or m.promotion}
   assert actual_captures==expected_captures,(b.fen(),actual_captures^expected_captures)
  a=int(query(b,'eval'));e=evaluator.evaluate(b)
  if a!=e:mismatches.append(dict(fen=b.fen(),native=a,python=e))
 report['tactical_move_sets_checked']=bool(os.environ.get('CLASH_TACTICAL_CHECK'));report['legal_positions']=2000;report['evaluation_mismatches']=len(mismatches);report['examples']=mismatches[:5]
finally:p.stdin.write('quit\n');p.stdin.flush();p.wait();p.stdin.close();p.stdout.close()
report['seconds']=time.monotonic()-start
report_name=os.environ.get('CLASH_VERIFY_REPORT','cpp-verification.json')
assert pathlib.Path(report_name).name==report_name
(ROOT/report_name).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not mismatches
