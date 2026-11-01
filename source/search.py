import chess, time, threading

# Piece values (centipawns)
PIECE_VALUES_MG = [0, 100, 320, 330, 500, 950, 0]
PIECE_VALUES_EG = [0, 120, 310, 330, 520, 980, 0]
V = PIECE_VALUES_MG
MATE = 30000

# Piece-Square Tables (White perspective; flipped for Black via sq ^ 56)
PAWN_TABLE_MG = [
      0,   0,   0,   0,   0,   0,   0,   0,
      5,  10,  10, -20, -20,  10,  10,   5,
      5,  -5, -10,   0,   0, -10,  -5,   5,
      0,   0,   0,  20,  20,   0,   0,   0,
      5,   5,  10,  25,  25,  10,   5,   5,
     10,  10,  20,  30,  30,  20,  10,  10,
     50,  50,  50,  50,  50,  50,  50,  50,
      0,   0,   0,   0,   0,   0,   0,   0
]
PAWN_TABLE_EG = [
      0,   0,   0,   0,   0,   0,   0,   0,
      0,   0,   0,   0,   0,   0,   0,   0,
     10,  10,  10,  10,  10,  10,  10,  10,
     20,  20,  20,  25,  25,  20,  20,  20,
     35,  35,  35,  40,  40,  35,  35,  35,
     60,  60,  60,  65,  65,  60,  60,  60,
    100, 100, 100, 100, 100, 100, 100, 100,
      0,   0,   0,   0,   0,   0,   0,   0
]

KNIGHT_TABLE_MG = [
    -40, -30, -20, -20, -20, -20, -30, -40,
    -30, -10,   0,   5,   5,   0, -10, -30,
    -20,   5,  15,  20,  20,  15,   5, -20,
    -20,   5,  20,  25,  25,  20,   5, -20,
    -20,   5,  20,  25,  25,  20,   5, -20,
    -20,   5,  15,  20,  20,  15,   5, -20,
    -30, -10,   0,   5,   5,   0, -10, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]
KNIGHT_TABLE_EG = [
    -30, -20, -10, -10, -10, -10, -20, -30,
    -20, -10,   0,   0,   0,   0, -10, -20,
    -10,   0,  10,  15,  15,  10,   0, -10,
    -10,   5,  15,  20,  20,  15,   5, -10,
    -10,   5,  15,  20,  20,  15,   5, -10,
    -10,   0,  10,  15,  15,  10,   0, -10,
    -20, -10,   0,   0,   0,   0, -10, -20,
    -30, -20, -10, -10, -10, -10, -20, -30
]

BISHOP_TABLE_MG = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  15,  15,  10,  10, -10,
    -10,   0,  15,  20,  20,  15,   0, -10,
    -10,   5,  10,  20,  20,  10,   5, -10,
    -10,   0,  10,  15,  15,  10,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
BISHOP_TABLE_EG = [
    -15, -10,  -5,  -5,  -5,  -5, -10, -15,
    -10,   0,   0,   0,   0,   0,   0, -10,
     -5,   0,   5,  10,  10,   5,   0,  -5,
     -5,   5,  10,  15,  15,  10,   5,  -5,
     -5,   5,  10,  15,  15,  10,   5,  -5,
     -5,   0,   5,  10,  10,   5,   0,  -5,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -15, -10,  -5,  -5,  -5,  -5, -10, -15
]

ROOK_TABLE_MG = [
      0,   0,   5,  10,  10,   5,   0,   0,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     20,  20,  20,  20,  20,  20,  20,  20,
      0,   0,   0,   5,   5,   0,   0,   0
]
ROOK_TABLE_EG = [
      0,   0,   5,   5,   5,   5,   0,   0,
      0,   0,   5,   5,   5,   5,   0,   0,
      0,   0,   5,   5,   5,   5,   0,   0,
      0,   0,   5,   5,   5,   5,   0,   0,
      0,   0,   5,   5,   5,   5,   0,   0,
      0,   0,   5,   5,   5,   5,   0,   0,
     25,  25,  25,  25,  25,  25,  25,  25,
      0,   0,   5,   5,   5,   5,   0,   0
]

QUEEN_TABLE_MG = [
    -15, -10,  -5,   0,   0,  -5, -10, -15,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   5,   5,  10,  10,   5,   5,  -5,
      0,   5,  10,  15,  15,  10,   5,   0,
      0,   5,  10,  15,  15,  10,   5,   0,
     -5,   5,   5,  10,  10,   5,   5,  -5,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -15, -10,  -5,   0,   0,  -5, -10, -15
]
QUEEN_TABLE_EG = [
    -15, -10,  -5,   0,   0,  -5, -10, -15,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   5,  10,  15,  15,  10,   5,  -5,
      0,   5,  15,  20,  20,  15,   5,   0,
      0,   5,  15,  20,  20,  15,   5,   0,
     -5,   5,  10,  15,  15,  10,   5,  -5,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -15, -10,  -5,   0,   0,  -5, -10, -15
]

KING_TABLE_MG = [
     20,  30,  10,   0,   0,  10,  30,  20,
     15,  20,   0, -10, -10,   0,  20,  15,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]
KING_TABLE_EG = [
    -30, -20, -10, -10, -10, -10, -20, -30,
    -20, -10,   0,   0,   0,   0, -10, -20,
    -10,   0,  15,  20,  20,  15,   0, -10,
    -10,   5,  20,  30,  30,  20,   5, -10,
    -10,   5,  20,  30,  30,  20,   5, -10,
    -10,   0,  15,  20,  20,  15,   0, -10,
    -20, -10,   0,   0,   0,   0, -10, -20,
    -30, -20, -10, -10, -10, -10, -20, -30
]

PST_MG = [None, PAWN_TABLE_MG, KNIGHT_TABLE_MG, BISHOP_TABLE_MG, ROOK_TABLE_MG, QUEEN_TABLE_MG, KING_TABLE_MG]
PST_EG = [None, PAWN_TABLE_EG, KNIGHT_TABLE_EG, BISHOP_TABLE_EG, ROOK_TABLE_EG, QUEEN_TABLE_EG, KING_TABLE_EG]

# Precomputed combined piece-square values for White and Black (White perspecive, Black flipped)
PST_VAL_MG = [[PIECE_VALUES_MG[p] + PST_MG[p][sq] for sq in range(64)] if PST_MG[p] else None for p in range(7)]
PST_VAL_EG = [[PIECE_VALUES_EG[p] + PST_EG[p][sq] for sq in range(64)] if PST_EG[p] else None for p in range(7)]
PST_VAL_MG_B = [[PST_VAL_MG[p][sq ^ 56] for sq in range(64)] if PST_VAL_MG[p] else None for p in range(7)]
PST_VAL_EG_B = [[PST_VAL_EG[p][sq ^ 56] for sq in range(64)] if PST_VAL_EG[p] else None for p in range(7)]

PASSED_PAWN_FILES = [
    (chess.BB_FILES[i] | (chess.BB_FILES[i-1] if i > 0 else 0) | (chess.BB_FILES[i+1] if i < 7 else 0))
    for i in range(8)
]
PASSED_BONUS_MG = [0, 5, 15, 35, 75, 160]
PASSED_BONUS_EG = [0, 20, 50, 110, 220, 420]
ISOLATED_PAWN_FILES = [
    ((chess.BB_FILES[i-1] if i > 0 else 0) | (chess.BB_FILES[i+1] if i < 7 else 0))
    for i in range(8)
]

WHITE_HOME_MINORS = (1 << 1) | (1 << 6) | (1 << 2) | (1 << 5)
BLACK_HOME_MINORS = (1 << 57) | (1 << 62) | (1 << 58) | (1 << 61)

class Timeout(Exception): pass

class Search:
    def __init__(self, reductions=True):
        self.reductions = reductions
        self.node_limit = None
        self.stop = threading.Event()
        self.nodes = 0
        self.tt = {}
        self.history = {}
        self.killers = {}
        self.countermoves = {}
        self.deadline = 0

    def position_key(self, b):
        position = (
            b.pawns, b.knights, b.bishops, b.rooks, b.queens, b.kings,
            b.occupied_co[0], b.occupied_co[1], b.turn, b.castling_rights,
            b.ep_square
        )
        hist = tuple(b.move_stack[-b.halfmove_clock:]) if b.halfmove_clock else ()
        return (position, hist)

    def evaluate(self, b):
        w_pawns = b.pawns & b.occupied_co[chess.WHITE]
        b_pawns = b.pawns & b.occupied_co[chess.BLACK]
        all_pawns = b.pawns
        
        # Game phase (0=endgame, 24=opening/middlegame)
        phase = min(24, chess.popcount(b.knights | b.bishops) + 2 * chess.popcount(b.rooks) + 4 * chess.popcount(b.queens))
        
        mg = 0
        eg = 0
        
        # White pieces
        for p, mask in ((1, b.pawns), (2, b.knights), (3, b.bishops), (4, b.rooks), (5, b.queens), (6, b.kings)):
            m_pst = PST_VAL_MG[p]; e_pst = PST_VAL_EG[p]
            for sq in chess.scan_forward(mask & b.occupied_co[chess.WHITE]):
                mg += m_pst[sq]
                eg += e_pst[sq]
                if p == 4: # Rook on open/semi-open file or 7th rank
                    f_mask = chess.BB_FILES[sq & 7]
                    if not (all_pawns & f_mask):
                        mg += 25; eg += 15
                    elif not (w_pawns & f_mask):
                        mg += 15; eg += 10
                    if (sq >> 3) == 6: # 7th rank
                        mg += 30; eg += 35
                elif p == 1: # Passed pawn
                    f = sq & 7; r = sq >> 3
                    if r >= 2:
                        adjacent = PASSED_PAWN_FILES[f]
                        ahead = (chess.BB_ALL << (8 * (r + 1))) & chess.BB_ALL
                        if not (b_pawns & adjacent & ahead):
                            idx = min(5, r - 1)
                            mg += PASSED_BONUS_MG[idx]
                            eg += PASSED_BONUS_EG[idx]

        # Black pieces (pre-flipped tables)
        for p, mask in ((1, b.pawns), (2, b.knights), (3, b.bishops), (4, b.rooks), (5, b.queens), (6, b.kings)):
            m_pst = PST_VAL_MG_B[p]; e_pst = PST_VAL_EG_B[p]
            for sq in chess.scan_forward(mask & b.occupied_co[chess.BLACK]):
                mg -= m_pst[sq]
                eg -= e_pst[sq]
                if p == 4:
                    f_mask = chess.BB_FILES[sq & 7]
                    if not (all_pawns & f_mask):
                        mg -= 25; eg -= 15
                    elif not (b_pawns & f_mask):
                        mg -= 15; eg -= 10
                    if (sq >> 3) == 1: # 7th rank for black
                        mg -= 30; eg -= 35
                elif p == 1:
                    f = sq & 7; r = 7 - (sq >> 3)
                    if r >= 2:
                        adjacent = PASSED_PAWN_FILES[f]
                        ahead = (1 << (8 * (sq >> 3))) - 1
                        if not (w_pawns & adjacent & ahead):
                            idx = min(5, r - 1)
                            mg -= PASSED_BONUS_MG[idx]
                            eg -= PASSED_BONUS_EG[idx]

        # Bishop pairs
        if chess.popcount(b.bishops & b.occupied_co[chess.WHITE]) >= 2:
            mg += 35; eg += 50
        if chess.popcount(b.bishops & b.occupied_co[chess.BLACK]) >= 2:
            mg -= 35; eg -= 50

        # King safety & Pawn shield (critical in MG)
        if phase > 8:
            wk = b.king(chess.WHITE)
            bk = b.king(chess.BLACK)
            if wk is not None and bk is not None:
                w_ring = chess.BB_KING_ATTACKS[wk]
                b_ring = chess.BB_KING_ATTACKS[bk]
                w_att = 0
                for sq in chess.scan_forward(b.occupied_co[chess.WHITE] & ~b.pawns & ~b.kings):
                    if chess.square_distance(sq, bk) <= 3 and (b.attacks(sq) & b_ring):
                        pt = b.piece_type_at(sq)
                        w_att += 50 if pt == chess.QUEEN else (30 if pt == chess.ROOK else 25)
                if w_att >= 50: mg += w_att * 2
                else: mg += w_att

                b_att = 0
                for sq in chess.scan_forward(b.occupied_co[chess.BLACK] & ~b.pawns & ~b.kings):
                    if chess.square_distance(sq, wk) <= 3 and (b.attacks(sq) & w_ring):
                        pt = b.piece_type_at(sq)
                        b_att += 50 if pt == chess.QUEEN else (30 if pt == chess.ROOK else 25)
                if b_att >= 50: mg -= b_att * 2
                else: mg -= b_att

                for q in chess.scan_forward(b.queens & b.occupied_co[chess.WHITE]):
                    d = chess.square_distance(q, bk)
                    if d <= 3: mg += (4 - d) * 35
                    d_own = chess.square_distance(q, wk)
                    if d_own <= 2: mg += 25
                    elif d_own >= 4: mg -= 35
                for q in chess.scan_forward(b.queens & b.occupied_co[chess.BLACK]):
                    d = chess.square_distance(q, wk)
                    if d <= 3: mg -= (4 - d) * 35
                    d_own = chess.square_distance(q, bk)
                    if d_own <= 2: mg -= 25
                    elif d_own >= 4: mg += 35
            if wk is not None:
                wf = wk & 7; wr = wk >> 3
                if wf >= 6 and wr == 0: # Kingside castled (g1, h1)
                    # Check pawn shield on f, g, h
                    shield = chess.popcount(w_pawns & (chess.BB_FILES[5] | chess.BB_FILES[6] | chess.BB_FILES[7]) & (chess.BB_RANKS[1] | chess.BB_RANKS[2]))
                    if shield < 3: mg -= (3 - shield) * 25
                    if not (all_pawns & chess.BB_FILES[6]): mg -= 65
                    elif not (w_pawns & chess.BB_FILES[6]): mg -= 40
                    if not (all_pawns & chess.BB_FILES[7]): mg -= 55
                    elif not (w_pawns & chess.BB_FILES[7]): mg -= 30
                    if not (all_pawns & chess.BB_FILES[5]): mg -= 45
                    elif not (w_pawns & chess.BB_FILES[5]): mg -= 25
                elif wf <= 2 and wr == 0: # Queenside castled
                    shield = chess.popcount(w_pawns & (chess.BB_FILES[0] | chess.BB_FILES[1] | chess.BB_FILES[2]) & (chess.BB_RANKS[1] | chess.BB_RANKS[2]))
                    if shield < 3: mg -= (3 - shield) * 20
                    if not (all_pawns & chess.BB_FILES[1]): mg -= 60
                    elif not (w_pawns & chess.BB_FILES[1]): mg -= 35
                    if not (all_pawns & chess.BB_FILES[2]): mg -= 45
                    elif not (w_pawns & chess.BB_FILES[2]): mg -= 25
                else: # Exposed king in center / uncastled in middlegame
                    mg -= 60
                    if not (all_pawns & chess.BB_FILES[wf]): mg -= 40
                    elif not (w_pawns & chess.BB_FILES[wf]): mg -= 20
                    if not (b.castling_rights & (chess.BB_H1 | chess.BB_A1)): mg -= 40

            bk = b.king(chess.BLACK)
            if bk is not None:
                bf = bk & 7; br = bk >> 3
                if bf >= 6 and br == 7: # Kingside castled (g8, h8)
                    shield = chess.popcount(b_pawns & (chess.BB_FILES[5] | chess.BB_FILES[6] | chess.BB_FILES[7]) & (chess.BB_RANKS[6] | chess.BB_RANKS[5]))
                    if shield < 3: mg += (3 - shield) * 25
                    if not (all_pawns & chess.BB_FILES[6]): mg += 65
                    elif not (b_pawns & chess.BB_FILES[6]): mg += 40
                    if not (all_pawns & chess.BB_FILES[7]): mg += 55
                    elif not (b_pawns & chess.BB_FILES[7]): mg += 30
                    if not (all_pawns & chess.BB_FILES[5]): mg += 45
                    elif not (b_pawns & chess.BB_FILES[5]): mg += 25
                elif bf <= 2 and br == 7: # Queenside castled
                    shield = chess.popcount(b_pawns & (chess.BB_FILES[0] | chess.BB_FILES[1] | chess.BB_FILES[2]) & (chess.BB_RANKS[6] | chess.BB_RANKS[5]))
                    if shield < 3: mg += (3 - shield) * 20
                    if not (all_pawns & chess.BB_FILES[1]): mg += 60
                    elif not (b_pawns & chess.BB_FILES[1]): mg += 35
                    if not (all_pawns & chess.BB_FILES[2]): mg += 45
                    elif not (b_pawns & chess.BB_FILES[2]): mg += 25
                else:
                    mg += 60
                    if not (all_pawns & chess.BB_FILES[bf]): mg += 40
                    elif not (b_pawns & chess.BB_FILES[bf]): mg += 20
                    if not (b.castling_rights & (chess.BB_H8 | chess.BB_A8)): mg += 40

        # Pawn structure: doubled and isolated pawns
        for i in range(8):
            f_mask = chess.BB_FILES[i]
            w_f_cnt = chess.popcount(w_pawns & f_mask)
            b_f_cnt = chess.popcount(b_pawns & f_mask)
            if w_f_cnt > 1: mg -= 15; eg -= 20
            if b_f_cnt > 1: mg += 15; eg += 20
            if w_f_cnt > 0:
                if not (w_pawns & ISOLATED_PAWN_FILES[i]): mg -= 15; eg -= 18
            if b_f_cnt > 0:
                if not (b_pawns & ISOLATED_PAWN_FILES[i]): mg += 15; eg += 18

        # Opening development incentive: penalize minor pieces left on starting squares
        if phase >= 20:
            uw = chess.popcount((b.knights | b.bishops) & b.occupied_co[chess.WHITE] & WHITE_HOME_MINORS)
            ub = chess.popcount((b.knights | b.bishops) & b.occupied_co[chess.BLACK] & BLACK_HOME_MINORS)
            mg -= (uw - ub) * 12

        score = int((mg * phase + eg * (24 - phase)) / 24)
        tempo = 12 if b.turn == chess.WHITE else -12
        return (score + tempo) if b.turn == chess.WHITE else -(score + tempo)

    def tick(self):
        self.nodes += 1
        if self.stop.is_set() or time.monotonic() >= self.deadline or (self.node_limit is not None and self.nodes > self.node_limit):
            raise Timeout()

    def order_moves(self, b, moves, preferred, ply):
        turn = b.turn
        enemy = not turn
        k_list = self.killers.get(ply)
        k0 = k_list[0] if k_list and len(k_list) > 0 else None
        k1 = k_list[1] if k_list and len(k_list) > 1 else None
        prev_m = b.peek() if b.move_stack else None
        cm = self.countermoves.get((prev_m.from_square, prev_m.to_square)) if prev_m else None

        def score_move(m):
            if m == preferred:
                return 2000000
            is_cap = b.is_capture(m)
            if is_cap:
                victim = b.piece_type_at(m.to_square) or 1
                attacker = b.piece_type_at(m.from_square) or 1
                if V[victim] < V[attacker] and b.is_attacked_by(enemy, m.to_square):
                    return 50000 + 10 * V[victim] - V[attacker]
                return 1000000 + 10 * V[victim] - V[attacker]
            if m.promotion:
                return 900000 + V[m.promotion]
            if m == k0:
                return 850000
            if m == k1:
                return 800000
            if m == cm:
                return 750000
            return self.history.get((turn, m.from_square, m.to_square), 0)

        return sorted(moves, key=score_move, reverse=True)

    def quiesce(self, b, a, z, ply):
        self.tick()
        check = b.is_check()
        if check:
            moves = list(b.legal_moves)
            if not moves:
                return -MATE + ply
        else:
            stand = self.evaluate(b)
            if stand >= z:
                return stand
            if stand > a:
                a = stand
            if ply >= 96:
                return a
            # Delta pruning
            if self.reductions and stand + 1100 < a:
                return a
            moves = list(b.generate_legal_captures())
            # Include quiet promotions to Queen when pawn on 7th rank
            p_mask = chess.BB_RANKS[6] if b.turn == chess.WHITE else chess.BB_RANKS[1]
            if (b.pawns & b.occupied_co[b.turn] & p_mask):
                for m in b.legal_moves:
                    if m.promotion == chess.QUEEN and not b.is_capture(m):
                        moves.append(m)
            if not moves:
                return a

        # MVV-LVA for captures
        def cap_key(m):
            victim = b.piece_type_at(m.to_square) or 1
            attacker = b.piece_type_at(m.from_square) or 1
            return 10 * V[victim] - V[attacker]
        moves.sort(key=cap_key, reverse=True)

        enemy = not b.turn
        for m in moves:
            if not check:
                victim = b.piece_type_at(m.to_square) or 1
                attacker = b.piece_type_at(m.from_square) or 1
                if self.reductions and V[victim] < V[attacker] and b.is_attacked_by(enemy, m.to_square):
                    continue
            b.push(m)
            try:
                v = -self.quiesce(b, -z, -a, ply + 1)
            finally:
                b.pop()
            if v >= z:
                return v
            if v > a:
                a = v
        return a

    def search(self, b, d, a, z, ply=0):
        self.tick()
        if d <= 0:
            return self.quiesce(b, a, z, ply)

        check = b.is_check()
        if b.is_insufficient_material() or b.is_fifty_moves() or b.is_repetition(3):
            return 0
        if ply >= 96:
            return self.evaluate(b)

        key = self.position_key(b)
        entry = self.tt.get(key)
        if entry and entry[0] >= d and ply:
            _, v, flag, _ = entry
            if v > 28000: v -= ply
            elif v < -28000: v += ply
            if flag == 0: return v
            if flag == 1 and v >= z: return v
            if flag == -1 and v <= a: return v

        # Reverse Futility Pruning
        if self.reductions and d <= 2 and not check and ply > 0:
            static_eval = self.evaluate(b)
            if static_eval - 120 * d >= z:
                return static_eval

        # Null Move Pruning
        if self.reductions and d >= 3 and not check and ply > 0:
            has_pieces = bool(b.occupied_co[b.turn] & ~b.pawns & ~b.kings)
            if has_pieces:
                b.push(chess.Move.null())
                try:
                    r = 3 if d >= 6 else 2
                    v = -self.search(b, d - 1 - r, -z, -z + 1, ply + 1)
                finally:
                    b.pop()
                if v >= z:
                    return v

        moves = list(b.legal_moves)
        if not moves:
            return -MATE + ply if check else 0

        original_a = a
        best = -32000
        best_move = None
        ordered_moves = self.order_moves(b, moves, entry[3] if entry else None, ply)

        for i, m in enumerate(ordered_moves):
            quiet = not b.is_capture(m) and not m.promotion
            b.push(m)
            try:
                nd = d if (self.reductions and check and d > 0 and ply < 64) else (d - 1)
                reduction = 0
                if self.reductions and d >= 3 and i >= 3 and quiet and not check and not b.is_check() and m not in self.killers.get(ply, ()):
                    reduction = 2 if (d >= 6 and i >= 6) else 1

                if i == 0:
                    v = -self.search(b, nd, -z, -a, ply + 1)
                else:
                    # PVS null-window
                    v = -self.search(b, nd - reduction, -a - 1, -a, ply + 1)
                    if v > a and reduction:
                        v = -self.search(b, nd - 1, -a - 1, -a, ply + 1)
                    if a < v < z:
                        v = -self.search(b, nd, -z, -a, ply + 1)
            finally:
                b.pop()

            if v > best:
                best = v
                best_move = m
            if v > a:
                a = v
            if a >= z:
                if quiet:
                    curr_killers = self.killers.get(ply, [])
                    if not curr_killers or m != curr_killers[0]:
                        self.killers[ply] = [m] + curr_killers[:1]
                    k = (b.turn, m.from_square, m.to_square)
                    self.history[k] = min(70000, self.history.get(k, 0) + d * d)
                    if b.move_stack:
                        prev = b.peek()
                        self.countermoves[(prev.from_square, prev.to_square)] = m
                break

        tt_v = best
        if tt_v > 28000: tt_v += ply
        elif tt_v < -28000: tt_v -= ply
        flag = -1 if best <= original_a else (1 if best >= z else 0)

        # Capacity management
        if len(self.tt) > 200000:
            self.tt = {k: v for k, v in self.tt.items() if v[0] >= 3}
        self.tt[key] = (d, tt_v, flag, best_move)
        return best

    def choose(self, b, seconds, depth=64, report=lambda *x: None):
        self.deadline = time.monotonic() + max(0.001, seconds)
        self.nodes = 0
        legal = list(b.legal_moves)
        if not legal:
            return chess.Move.null()
        if len(legal) == 1:
            report(1, 0, 1, legal[0])
            return legal[0]
        best = legal[0]

        # Iterative deepening
        score = 0
        for d in range(1, max(1, depth) + 1):
            try:
                if d >= 4 and abs(score) < 25000:
                    delta = 40
                    alpha = max(-32000, score - delta)
                    beta = min(32000, score + delta)
                    score = self.search(b, d, alpha, beta)
                    if score <= alpha or score >= beta:
                        score = self.search(b, d, -32000, 32000)
                else:
                    score = self.search(b, d, -32000, 32000)

                key = self.position_key(b)
                entry = self.tt.get(key)
                if entry and entry[3] in legal:
                    best = entry[3]
                report(d, score, self.nodes, best)
                if abs(score) > 29000:
                    break
            except Timeout:
                break
        return best
