"""Regression: unfinished games must not become draws or points."""
import contextlib,io,json,pathlib,tempfile,unittest
import grind_arena
class Metrics(unittest.TestCase):
 def test_incomplete_game(self):
  outcomes=[1]*9+[.5]*2+[0]*4+[None]
  def game(spec,colour,movetime):
   score=outcomes.pop(0)
   result='*' if score is None else '1/2-1/2' if score==.5 else ('1-0' if (score==1)==(colour=='white') else '0-1')
   return dict(opponent=spec['name'],our_colour=colour,result=result,plies=1,duration=0,failure=None,pgn='')
  old_root,old_game=grind_arena.ROOT,grind_arena.run_game
  try:
   with tempfile.TemporaryDirectory() as d:
    grind_arena.ROOT=pathlib.Path(d);grind_arena.run_game=game
    with contextlib.redirect_stdout(io.StringIO()):grind_arena.main()
    r=json.loads((pathlib.Path(d)/'grind-results.json').read_text())
    self.assertEqual((r['completed_games'],r['unfinished_games'],r['wins'],r['draws'],r['losses']),(15,1,9,2,4))
    self.assertEqual(r['our_score'],10);self.assertEqual(r['win_rate'],.6);self.assertAlmostEqual(r['score_rate'],2/3)
  finally:grind_arena.ROOT,grind_arena.run_game=old_root,old_game
if __name__=='__main__':unittest.main(verbosity=2)
