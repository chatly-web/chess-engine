import chess,chess.engine,json,pathlib,hashlib
p=pathlib.Path(__file__).resolve().parent;rows=[]
for name in ['cluster','safe-null','combined']:
 binary=p/('build-'+name)/'clash-native';game=object()
 with chess.engine.SimpleEngine.popen_uci(str(binary.resolve())) as e:
  for half in [0,98,99,0,99]:
   b=chess.Board(f'7k/5Q2/6K1/8/8/8/8/8 w - - {half} 1');r=e.play(b,chess.engine.Limit(depth=4,time=5),game=game,info=chess.engine.INFO_ALL)
   assert r.move in b.legal_moves;b.push(r.move);assert b.is_checkmate(),(name,half,r)
  b=chess.Board();e.play(b,chess.engine.Limit(depth=4),game=game)
  for m in ['g1f3','g8f6','f3g1','f6g8']*2:b.push_uci(m)
  r=e.play(b,chess.engine.Limit(depth=4),game=game,info=chess.engine.INFO_ALL);assert r.move in b.legal_moves;assert r.info['score'].pov(b.turn).score()==0
  # No-pawn bare-minor material must be adjudicated before stale TT scores.
  b=chess.Board('7k/8/8/8/8/2K5/8/2B5 w - - 0 1');r=e.play(b,chess.engine.Limit(depth=4),game=game,info=chess.engine.INFO_ALL);assert r.move in b.legal_moves;assert r.info['score'].pov(b.turn).score()==0
 rows.append({'engine':name,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'mate_priority_halfmove_cases':5,'retained_table_repetition':True,'insufficient_material':True})
(p.parents[3]/'architecture-pass/reproduced-history-checks.json').write_text(json.dumps({'passed':True,'cases':rows},indent=2)+'\n');print('PASS: mate at rule-clock boundary, repeated history and insufficient material')
