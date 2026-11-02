"""Rules-only available-draw lower bounds on the actual C++ quiescence code."""
from pathlib import Path
import argparse,json,subprocess,tempfile
import chess
parser=argparse.ArgumentParser();parser.add_argument('--compiler',default='clang++');parser.add_argument('--counter',choices=[0,1],type=int,default=0);args=parser.parse_args()
source=Path(__file__).resolve().parent;root=source.parents[3]
cases=json.loads((root/'aggressive-pass/draw-oracle.json').read_text())['cases']+json.loads((root/'aggressive-pass/draw-fuzz.json').read_text())['cases']
for case in cases:
 b=chess.Board(case['fen']);assert b.is_valid() and not b.is_insufficient_material()
 for text in case.get('immediate_draw_captures') or [case['capture']]:
  move=chess.Move.from_uci(text);assert move in b.legal_moves;after=b.copy();after.push(move);assert after.is_insufficient_material()
flags=['-std=c++17','-O3','-DNDEBUG','-pthread','-DCLASH_SEARCH_V2=2','-DCLASH_TACTICAL_GEN=1','-DCLASH_SEARCH_V3=3','-DCLASH_EVAL_STYLE=3','-DCLASH_EVAL_FAST=1','-DCLASH_ACTIVITY=1','-DCLASH_HISTORY=1','-DCLASH_CAPTURE_LAST=0','-DCLASH_ENDGAME_Q=1','-DCLASH_HASH_BITS=20',f'-DCLASH_COUNTER={args.counter}']
with tempfile.TemporaryDirectory(prefix='clash-draw-test-') as temp:
 binary=Path(temp)/'probe';subprocess.run([args.compiler,*flags,str(source/'probe.cpp'),'-o',str(binary)],check=True)
 values=subprocess.check_output([str(binary)],input='\n'.join(case['fen'] for case in cases)+'\n',text=True).splitlines()
assert len(values)==len(cases)==564
assert all(int(value.split()[1])>=0 for value in values)
print('PASS: all564 independently verified immediate draws preserved by actual C++ search')
