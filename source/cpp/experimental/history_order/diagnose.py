from pathlib import Path
import chess,chess.pgn,chess.engine,json,hashlib
p=Path(__file__).resolve().parent;root=p.parents[3];path=root/'eval-fast-pass/candidate-gnu-180-2-white.pgn'
with path.open() as f:game=chess.pgn.read_game(f)
b=game.board();rows=[];context=object()
with chess.engine.SimpleEngine.popen_uci(str(p/'diagnostic/clash-native')) as e:
 for move in game.mainline_moves():
  if b.turn==chess.WHITE:
   r=e.play(b,chess.engine.Limit(depth=6,time=.5),game=context,info=chess.engine.INFO_ALL);message=r.info.get('string','');values=message.split()
   rows.append({'ply':b.ply(),'fen':b.fen(),'played':move.uci(),'own_replay_choice':r.move.uci(),'depth':r.info.get('depth'),'nodes':r.info.get('nodes'),'history_max':int(values[1]) if values and values[0]=='history_probe' else None,'saturated_entries':int(values[2]) if values and values[0]=='history_probe' else None,'nonzero_entries':int(values[3]) if values and values[0]=='history_probe' else None})
  b.push(move)
report={'source_game':'eval-fast-pass/candidate-gnu-180-2-white.pgn','source_pgn_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'diagnostic_binary_sha256':hashlib.sha256((p/'diagnostic/clash-native').read_bytes()).hexdigest(),'own_engine_only':True,'foreign_analysis_requested':False,'positions':rows,'max_history_observed':max(r['history_max'] or 0 for r in rows),'max_saturated_entries':max(r['saturated_entries'] or 0 for r in rows),'note':'Own fixed-depth replay on the saved loss, with retained own history; not a recreation of original clock/search state or a unique explanation of the loss.'};(root/'history-pass/reproduced-history-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='positions'})
