"""Build an isolated PGO candidate from original source and supplied training prefixes.

Requires Clang, matching llvm-profdata, Python and python-chess for offline profiling.
Does not change any existing engine, bridge configuration, or release archive.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import chess
import chess.engine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--compiler', default='clang++')
    parser.add_argument('--profdata', default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    plan = json.loads(args.plan.read_text())
    source = root/'source/cpp/experimental/history_order/build-history/engine.cpp'
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(source) == plan['source_sha256'], 'Source differs from profiled plan'
    assert not args.output.exists(), 'Choose a new output; existing engines are never overwritten'
    args.work_dir.mkdir(parents=True, exist_ok=False)
    work = args.work_dir.resolve()
    flags = ['-std=c++17', '-O3', '-DNDEBUG', '-pthread', '-DCLASH_SEARCH_V2=2',
             '-DCLASH_TACTICAL_GEN=1', '-DCLASH_SEARCH_V3=3', '-DCLASH_EVAL_STYLE=3',
             '-DCLASH_EVAL_FAST=1', '-DCLASH_ACTIVITY=1', '-DCLASH_HISTORY=1', '-DCLASH_CAPTURE_LAST=0']
    instrumented = work/'instrumented'
    subprocess.run([args.compiler, *flags, '-fprofile-instr-generate', str(source), '-o', str(instrumented)], check=True)
    env = dict(os.environ, LLVM_PROFILE_FILE=str(work/'training-%p.profraw'))
    engine = chess.engine.SimpleEngine.popen_uci(str(instrumented), env=env)
    try:
        for start in plan['train']:
            board = chess.Board()
            for move in start['moves']:
                board.push_uci(move)
            reply = engine.play(board, chess.engine.Limit(depth=plan['training_depth']), game=object())
            assert reply.move in board.legal_moves
    finally:
        # A normal exit flushes LLVM counters. SimpleEngine.close() may terminate
        # the process before its profile has been written.
        engine.quit()
    profdata = args.profdata or shutil.which('llvm-profdata')
    if profdata is None:
        profdata = subprocess.check_output(['xcrun','--find','llvm-profdata'], text=True).strip()
    subprocess.run([profdata, 'merge', '-o', str(work/'training.profdata'),
                    *map(str, work.glob('training-*.profraw'))], check=True)
    subprocess.run([args.compiler, *flags, '-Werror=profile-instr-unprofiled', '-fprofile-instr-use='+str(work/'training.profdata'),
                    str(source), '-o', str(args.output)], check=True)
    print(json.dumps({'output': str(args.output), 'sha256': digest(args.output),
                      'source_sha256': digest(source), 'runtime_external_data': False}))

if __name__ == '__main__':
    main()
