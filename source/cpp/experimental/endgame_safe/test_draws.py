"""Compile a test-only probe of the actual C++ search and check draw lower bounds.

python-chess independently verifies the available capture ends the game by
insufficient material. The probe is not a competition executable or tablebase.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import chess

parser=argparse.ArgumentParser()
parser.add_argument('--compiler',default='clang++')
parser.add_argument('--mode',type=int,choices=[1,2],default=2)
args=parser.parse_args()
source=Path(__file__).resolve().parent
root=source.parents[3]
cases=json.loads((root/'aggressive-pass/draw-oracle.json').read_text())['cases']
cases+=json.loads((root/'aggressive-pass/draw-fuzz.json').read_text())['cases']
for case in cases:
    board=chess.Board(case['fen'])
    assert board.is_valid() and not board.is_insufficient_material()
    options=case.get('immediate_draw_captures') or [case['capture']]
    for text in options:
        move=chess.Move.from_uci(text)
        assert move in board.legal_moves
        after=board.copy();after.push(move)
        assert after.is_insufficient_material()
flags=['-std=c++17','-O3','-DNDEBUG','-pthread','-DCLASH_SEARCH_V2=2',
       '-DCLASH_TACTICAL_GEN=1','-DCLASH_SEARCH_V3=3','-DCLASH_EVAL_STYLE=3',
       '-DCLASH_EVAL_FAST=1','-DCLASH_ACTIVITY=1','-DCLASH_HISTORY=1',
       '-DCLASH_CAPTURE_LAST=0',f'-DCLASH_ENDGAME_Q={args.mode}']
with tempfile.TemporaryDirectory(prefix='clash-draw-tests-') as temp:
    binary=Path(temp)/'probe'
    subprocess.run([args.compiler,*flags,str(source/'probe.cpp'),'-o',str(binary)],check=True)
    result=subprocess.check_output([str(binary)],input='\n'.join(case['fen'] for case in cases)+'\n',text=True)
scores=[int(line.split()[1]) for line in result.splitlines()]
assert len(scores)==len(cases)==564
for case,score in zip(cases,scores):
    assert score>=0,(case['fen'],score,'A rules-verified immediate draw is available')
print(f'PASS: {len(cases)} rules-verified available draws preserved by actual C++ quiescence search, mode {args.mode}')
