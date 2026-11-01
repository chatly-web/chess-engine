"""Generate native constants from this project's own parameter file."""
import json,pathlib,argparse
p=argparse.ArgumentParser();p.add_argument('--weights');a=p.parse_args();root=pathlib.Path(__file__).resolve().parents[2]
w=json.loads((root/'default-weights.json').read_text())['weights']
if a.weights:
 custom=json.loads(pathlib.Path(a.weights).read_text())['weights']
 for key,value in custom.items():
  if key not in w:raise ValueError('Unknown parameter: '+key)
  if not isinstance(w[key],list) and value!=w[key]:raise ValueError('Native scalar overrides are not yet supported: '+key)
  if isinstance(w[key],list) and (not isinstance(value,list) or len(value)!=len(w[key]) or any(type(v) is not int or abs(v)>2000 for v in value)):raise ValueError('Invalid table: '+key)
 w.update(custom)
out=['// Generated from this project\'s weights; no external engine data.']
for name in ['PIECE_VALUES_MG','PIECE_VALUES_EG']+[p+'_TABLE_'+s for p in ['PAWN','KNIGHT','BISHOP','ROOK','QUEEN','KING'] for s in ['MG','EG']]+['PASSED_BONUS_MG','PASSED_BONUS_EG']:
 out.append('const int '+name+'[] = {'+','.join(map(str,w[name]))+'};')
out.append('const int* PST_MG[7]={nullptr,PAWN_TABLE_MG,KNIGHT_TABLE_MG,BISHOP_TABLE_MG,ROOK_TABLE_MG,QUEEN_TABLE_MG,KING_TABLE_MG};')
out.append('const int* PST_EG[7]={nullptr,PAWN_TABLE_EG,KNIGHT_TABLE_EG,BISHOP_TABLE_EG,ROOK_TABLE_EG,QUEEN_TABLE_EG,KING_TABLE_EG};')
(root/'source/cpp/tables.h').write_text('\n'.join(out)+'\n')
