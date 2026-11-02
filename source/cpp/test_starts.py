"""Deterministic nonterminal random openings for offline test/training harnesses."""
import chess

def sample_start(rng,plies=8):
 if not 0<=plies<=256:raise ValueError('Starting plies must be in [0,256]')
 for attempt in range(1,1001):
  board=chess.Board()
  for _ in range(plies):
   if board.is_game_over(claim_draw=True):break
   board.push(rng.choice(list(board.legal_moves)))
  if board.ply()==plies and not board.is_game_over(claim_draw=True):return board,attempt
 raise RuntimeError('Could not sample a nonterminal opening in 1000 attempts')
