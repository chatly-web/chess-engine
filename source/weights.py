"""Validated, relative-path parameter overrides; defaults preserve the source."""
import json,os,pathlib

def overrides(defaults):
 path=os.environ.get('CLASH_WEIGHTS')
 if not path:return dict(defaults)
 p=pathlib.Path(path)
 if not p.is_absolute():p=pathlib.Path(__file__).resolve().parents[1]/'engine'/p
 data=json.loads(p.read_text()).get('weights',{})
 allowed=json.loads((pathlib.Path(__file__).resolve().parents[1]/'default-weights.json').read_text())['weights']
 if set(data)-set(allowed):raise ValueError('Unknown weight name')
 result=dict(defaults)
 for k,v in data.items():
  if k not in defaults:continue
  old=defaults[k]
  if isinstance(old,list):
   if not isinstance(v,list) or len(v)!=len(old):raise ValueError('Wrong table size')
   vals=v
  else:vals=[v]
  if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not -2000<=x<=2000 for x in vals):raise ValueError('Invalid weight')
  result[k]=v
 return result
