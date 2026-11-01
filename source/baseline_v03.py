import chess, time, threading
V=[0,100,315,335,510,950,0]
MATE=30000
class Timeout(Exception): pass
class Search:
 def __init__(self, reductions=True):
  self.reductions=reductions; self.node_limit=None; self.stop=threading.Event(); self.nodes=0; self.tt={}; self.history={}; self.killers={}
 def position_key(self,b):
  # Preserve draw context without serializing FEN or move strings at every node.
  position=(b.pawns,b.knights,b.bishops,b.rooks,b.queens,b.kings,b.occupied_co[0],b.occupied_co[1],b.turn,b.castling_rights,b.ep_square,b.halfmove_clock)
  return (position,tuple(b.move_stack[-b.halfmove_clock:]) if b.halfmove_clock else ())
 def evaluate(self,b):
  phase=min(24,sum(len(b.pieces(p,c))*w for c in chess.COLORS for p,w in [(2,1),(3,1),(4,2),(5,4)]))/24
  score=0
  for c in chess.COLORS:
   s=0; pawns=b.pieces(1,c)
   for p in range(1,7):
    for sq in b.pieces(p,c):
     f=chess.square_file(sq); r=chess.square_rank(sq) if c else 7-chess.square_rank(sq); center=7-abs(2*f-7)-abs(2*r-7)
     bonus=0
     if p==1:
      bonus=r*7+center*2
      if sum(chess.square_file(x)==f for x in pawns)>1: bonus-=12
      if not any(abs(chess.square_file(x)-f)==1 for x in pawns): bonus-=10
      if not any(abs(chess.square_file(x)-f)<=1 and (chess.square_rank(x)>chess.square_rank(sq) if c else chess.square_rank(x)<chess.square_rank(sq)) for x in b.pieces(1,not c)): bonus+=r*r*3
     elif p==2: bonus=center*9
     elif p==3: bonus=center*5+len(b.attacks(sq))*2
     elif p==4: bonus=r*2+(15 if not any(chess.square_file(x)==f for x in pawns) else 0)
     elif p==5: bonus=center*2
     else: bonus=int((1-phase)*center*10+phase*(-center*5-r*8+(25 if r==0 and f in (1,2,6) else 0)))
     s+=V[p]+bonus
   if len(b.pieces(3,c))>=2:s+=28
   score+=s if c else -s
  return (score if b.turn else -score)+8
 def tick(self):
  self.nodes+=1
  if self.stop.is_set() or time.monotonic()>=self.deadline or (self.node_limit is not None and self.nodes>self.node_limit): raise Timeout()
 def ordered(self,b,moves,preferred,ply):
  def key(m):
   if m==preferred:return 1000000
   if b.is_capture(m):return 100000+10*V[b.piece_type_at(m.to_square) or 1]-V[b.piece_type_at(m.from_square)]
   if m.promotion:return 90000+V[m.promotion]
   if m in self.killers.get(ply,[]):return 80000
   return self.history.get((b.turn,m.from_square,m.to_square),0)
  return sorted(moves,key=key,reverse=True)
 def search(self,b,d,a,z,ply=0,q=0):
  self.tick(); check=b.is_check(); moves=list(b.legal_moves)
  if not moves:return -MATE+ply if check else 0
  if b.is_insufficient_material() or b.is_fifty_moves() or b.is_repetition(3):return 0
  if ply>=96:return self.evaluate(b)
  original=a
  # Include reversible history to avoid reusing scores across different draw contexts.
  key=self.position_key(b) if d>0 else None
  entry=self.tt.get(key) if d>0 else None
  if entry and entry[0]>=d and ply:
   _,v,flag,_=entry
   if abs(v)<29000 and (flag==0 or flag==1 and v>=z or flag==-1 and v<=a):return v
  if d<=0 and not check:
   stand=self.evaluate(b)
   if stand>=z:return stand
   a=max(a,stand)
   if q>=12:return a
   moves=[m for m in moves if b.is_capture(m) or m.promotion]
  best=-32000; bm=None
  for i,m in enumerate(self.ordered(b,moves,entry[3] if entry else None,ply)):
   quiet=not b.is_capture(m) and not m.promotion
   b.push(m)
   try:
    nd=d-1
    reduction=1 if self.reductions and d>=3 and i>=4 and quiet and not check and not b.is_check() else 0
    if i==0 or d<=0:v=-self.search(b,nd,-z,-a,ply+1,q+1 if d<=0 else 0)
    else:
     v=-self.search(b,nd-reduction,-a-1,-a,ply+1)
     if v>a and reduction:v=-self.search(b,nd,-a-1,-a,ply+1)
     if a<v<z:v=-self.search(b,nd,-z,-a,ply+1)
   finally:b.pop()
   if v>best:best,bm=v,m
   a=max(a,v)
   if a>=z:
    if quiet:
     self.killers[ply]=[m]+self.killers.get(ply,[])[:1]
     k=(b.turn,m.from_square,m.to_square);self.history[k]=min(70000,self.history.get(k,0)+max(d,1)**2)
    break
  if d>0:
   if len(self.tt)>50000:self.tt.clear()
   self.tt[key]=(d,best, -1 if best<=original else 1 if best>=z else 0,bm)
  return a if d<=0 else best
 def choose(self,b,seconds,depth=64,report=lambda *x:None):
  self.deadline=time.monotonic()+max(0,seconds);self.nodes=0
  legal=list(b.legal_moves);best=legal[0] if legal else chess.Move.null()
  if not legal:return best
  for d in range(1,max(1,depth)+1):
   try:
    score=self.search(b,d,-32000,32000)
    key=self.position_key(b)
    entry=self.tt.get(key)
    if entry and entry[3] in legal:best=entry[3]
    report(d,score,self.nodes,best)
    if abs(score)>29000:break
   except Timeout:break
  return best
