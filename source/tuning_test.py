import json,os,pathlib,subprocess,sys,tempfile,unittest
from sprt import test
from tune import extract,probability
ROOT=pathlib.Path(__file__).resolve().parents[1]
class TuningTests(unittest.TestCase):
 def test_sprt(self):
  self.assertEqual(test([1]*200)['decision'],'accept_h1')
  self.assertEqual(test([0]*200)['decision'],'accept_h0')
  self.assertEqual(test([.5]*200)['decision'],'continue')
  with self.assertRaises(ValueError):test([None])
 def test_sigmoid(self):
  self.assertEqual(probability(0,1),.5)
  self.assertAlmostEqual(probability(100,1)+probability(-100,1),1)
 def test_external_data_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'bad.pgn';p.write_text('[White "Stockfish"]\n[Black "Clash"]\n[Result "1-0"]\n\n1. e4 e5 1-0\n')
   with self.assertRaises(ValueError):extract(p,pathlib.Path(d)/'data.jsonl','selfplay')
 def test_weights_roundtrip(self):
  code='import search,chess; print(search.Search().evaluate(chess.Board()))'
  clean=dict(os.environ);clean.pop('CLASH_WEIGHTS',None)
  default=subprocess.check_output([sys.executable,'-c',code],cwd=ROOT/'source',env=clean)
  clean['CLASH_WEIGHTS']='../default-weights.json'
  self.assertEqual(default,subprocess.check_output([sys.executable,'-c',code],cwd=ROOT/'source',env=clean))
if __name__=='__main__':unittest.main(verbosity=2)
