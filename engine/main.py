#!/usr/bin/env python3
"""UCI front end: one input reader, one cancellable search worker."""
import pathlib
import sys
import threading
import time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'source'))
import chess
from search import Search, MATE
from clock_budget import budget

output_lock = threading.Lock()
def emit(message):
    with output_lock:
        print(message, flush=True)

def parse_position(tokens):
    boundary = tokens.index('moves') if 'moves' in tokens else len(tokens)
    if tokens[1] == 'startpos':
        candidate = chess.Board()
        if boundary != 2:
            raise ValueError('unexpected startpos arguments')
    elif tokens[1] == 'fen':
        candidate = chess.Board(' '.join(tokens[2:boundary]))
    else:
        raise ValueError('position requires startpos or fen')
    if not candidate.is_valid():
        raise ValueError('invalid chess position')
    for move in tokens[boundary + 1:]:
        candidate.push_uci(move)
    return candidate

def main():
    board = chess.Board()
    worker = None
    search = Search()

    def halt():
        if worker and worker.is_alive():
            search.stop.set()
            worker.join()

    def run(position, current, seconds, depth):
        start = time.monotonic()
        def report(d, value, nodes, move):
            score = f'cp {value}'
            if abs(value) > 29000:
                distance = (MATE - abs(value) + 1) // 2
                score = f'mate {distance if value > 0 else -distance}'
            emit(f'info depth {d} score {score} nodes {nodes} time {int((time.monotonic()-start)*1000)} pv {move.uci()}')
        try:
            move = current.choose(position, seconds, depth, report)
        except Exception as exc:
            print(f'SEARCH FAILURE: {exc!r}', file=sys.stderr, flush=True)
            move = next(iter(position.legal_moves), chess.Move.null())
        emit('bestmove ' + move.uci())

    try:
        for line in sys.stdin:
            tokens = line.split()
            if not tokens:
                continue
            try:
                command = tokens[0]
                if command == 'uci':
                    emit('id name Clash Original 0.3.5')
                    emit('id author AI-assisted development')
                    emit('uciok')
                elif command == 'isready':
                    emit('readyok')
                elif command in ('stop', 'quit', 'ucinewgame'):
                    halt()
                    if command == 'quit':
                        break
                    if command == 'ucinewgame':
                        board = chess.Board()
                        search = Search()
                elif command == 'position':
                    halt()
                    board = parse_position(tokens)
                elif command == 'go':
                    halt()
                    names = {'wtime', 'btime', 'winc', 'binc', 'movetime', 'depth', 'movestogo', 'nodes'}
                    args = {}
                    for i, token in enumerate(tokens[1:], 1):
                        if token in names:
                            args[token] = max(0, int(tokens[i + 1]))
                    seconds = budget(args, board.turn)
                    if 'infinite' in tokens:
                        seconds = 86400
                    search.stop.clear()
                    search.node_limit = args.get('nodes')
                    worker = threading.Thread(target=run, args=(board.copy(), search, seconds, max(1, args.get('depth', 64))))
                    worker.start()
            except (ValueError, IndexError) as exc:
                print(f'INPUT ERROR: {exc}', file=sys.stderr, flush=True)
    finally:
        halt()

if __name__ == '__main__':
    main()
