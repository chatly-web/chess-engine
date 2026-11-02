from pathlib import Path
import json,hashlib,subprocess,shutil
p=Path(__file__).resolve().parent;s=(p/'baseline.cpp').read_text();s='#ifndef CLASH_EVAL_FAST\n#define CLASH_EVAL_FAST 0\n#endif\n'+s
needle=' int king(int c)const{return kingSquares[c>0];}'
insert='''
#if CLASH_EVAL_FAST
 uint64_t occupied=0,pawnBits[2]={0,0};
 int materialMG=0,materialEG=0,rawPhase=0,bishopCount[2]={0,0};
 static int piecePhase(int p){return p==2||p==3?1:p==4?2:p==5?4:0;}
 void changeEvaluation(int square,int piece,int direction){
  if(!piece)return;int type=abs(piece),c=piece>0,sg=c?1:-1,sq=c?square:square^56;
  materialMG+=direction*sg*(PIECE_VALUES_MG[type]+PST_MG[type][sq]);
  materialEG+=direction*sg*(PIECE_VALUES_EG[type]+PST_EG[type][sq]);rawPhase+=direction*piecePhase(type);
  if(type==3)bishopCount[c]+=direction;
  if(direction>0){occupied|=uint64_t(1)<<square;if(type==1)pawnBits[c]|=uint64_t(1)<<square;}
  else{occupied&=~(uint64_t(1)<<square);if(type==1)pawnBits[c]&=~(uint64_t(1)<<square);}
 }
 void rebuildEvaluation(){occupied=0;pawnBits[0]=pawnBits[1]=0;materialMG=materialEG=rawPhase=0;bishopCount[0]=bishopCount[1]=0;for(int s=0;s<64;s++)changeEvaluation(s,b[s],1);}
#endif
'''
assert needle in s;s=s.replace(needle,insert+needle)
a='void setPiece(int square,int piece){int old=b[square];';b='''void setPiece(int square,int piece){int old=b[square];
#if CLASH_EVAL_FAST
 changeEvaluation(square,old,-1);changeEvaluation(square,piece,1);
#endif
''';assert a in s;s=s.replace(a,b)
a='if(verified!=n.pieceHash)throw runtime_error("piece hash mismatch");';b='''if(verified!=n.pieceHash)throw runtime_error("piece hash mismatch");
#if CLASH_EVAL_FAST
 Board fresh=n;fresh.rebuildEvaluation();if(fresh.materialMG!=n.materialMG||fresh.materialEG!=n.materialEG||fresh.rawPhase!=n.rawPhase||fresh.occupied!=n.occupied||fresh.pawnBits[0]!=n.pawnBits[0]||fresh.pawnBits[1]!=n.pawnBits[1]||fresh.bishopCount[0]!=n.bishopCount[0]||fresh.bishopCount[1]!=n.bishopCount[1])throw runtime_error("incremental evaluation mismatch");
#endif
''';assert a in s;s=s.replace(a,b)
a='return b;}\nconst string START=';b='''
#if CLASH_EVAL_FAST
b.rebuildEvaluation();
#endif
return b;}
const string START=''';assert a in s;s=s.replace(a,b)
start=s.index('int evaluate(const Board& b){');end=s.index('\nstruct Halt{};',start);old=s[start:end]
new=old
new=new.replace('int phase=0,mg=0,eg=0;int pawns[2][8]={},bishops[2]={},kings[2]={};PawnSquares pawnSquares[2];','int phase=b.rawPhase,mg=b.materialMG,eg=b.materialEG;int pawns[2][8]={},bishops[2]={b.bishopCount[0],b.bishopCount[1]},kings[2]={b.king(-1),b.king(1)};PawnSquares pawnSquares[2];')
a='for(int s=0;s<64;s++)if(b.b[s]){int p=abs(b.b[s]),c=b.b[s]>0?1:0;if(p==1){pawns[c][file(s)]++;pawnSquares[c].push_back(s);}if(p==6)kings[c]=s;if(p==3)bishops[c]++;phase+=p==2||p==3?1:p==4?2:p==5?4:0;}'
b='for(int c=0;c<2;c++)for(uint64_t bits=b.pawnBits[c];bits;bits&=bits-1){int s=__builtin_ctzll(bits);pawns[c][file(s)]++;pawnSquares[c].push_back(s);}'
assert a in new;new=new.replace(a,b)
a='for(int s=0;s<64;s++)if(b.b[s]){int p=abs(b.b[s]),c=b.b[s]>0?1:0,sg=c?1:-1,sq=c?s:s^56,f=file(s),r=c?rankof(s):7-rankof(s);int m=PIECE_VALUES_MG[p]+PST_MG[p][sq],e=PIECE_VALUES_EG[p]+PST_EG[p][sq];'
b='for(uint64_t bits=b.occupied;bits;bits&=bits-1){int s=__builtin_ctzll(bits);int p=abs(b.b[s]),c=b.b[s]>0?1:0,sg=c?1:-1,f=file(s),r=c?rankof(s):7-rankof(s);int m=0,e=0;'
assert a in new;new=new.replace(a,b)
# The remaining occupied-piece scans retain ascending square order.
new=new.replace('for(int s=0;s<64;s++)if(sign(b.b[s])==-sg&&abs(b.b[s])>1&&abs(b.b[s])<6){','for(uint64_t bits=b.occupied;bits;bits&=bits-1)if(int s=__builtin_ctzll(bits);sign(b.b[s])==-sg&&abs(b.b[s])>1&&abs(b.b[s])<6){')
new=new.replace('for(int t=0;t<64;t++)if(b.b[t]==sg*5){','for(uint64_t bits=b.occupied;bits;bits&=bits-1)if(int t=__builtin_ctzll(bits);b.b[t]==sg*5){')
new=new.replace('for(int from=0;from<64;from++)if(abs(b.b[from])>1&&abs(b.b[from])<6){','for(uint64_t bits=b.occupied;bits;bits&=bits-1)if(int from=__builtin_ctzll(bits);abs(b.b[from])>1&&abs(b.b[from])<6){')
# Pure pawn cache: full pawn bitboards validate every hit, so hash collisions are misses.
cache='''
struct PawnEvaluation{
 uint64_t bits[2]={0,0},passed[2]={0,0};
 unsigned char files[2][8]={};
};
const PawnEvaluation& pawnEvaluation(const Board&b){
 static thread_local array<PawnEvaluation,2048>table{};
 uint64_t key=b.pawnBits[1]^(b.pawnBits[0]*0x9e3779b97f4a7c15ULL);auto&entry=table[(key^(key>>32))&2047];
 if(entry.bits[0]==b.pawnBits[0]&&entry.bits[1]==b.pawnBits[1])return entry;
 entry=PawnEvaluation{};entry.bits[0]=b.pawnBits[0];entry.bits[1]=b.pawnBits[1];
 for(int c=0;c<2;c++)for(uint64_t bits=b.pawnBits[c];bits;bits&=bits-1){int s=__builtin_ctzll(bits);entry.files[c][file(s)]++;bool passed=true;
  for(uint64_t enemy=b.pawnBits[1-c];enemy;enemy&=enemy-1){int t=__builtin_ctzll(enemy);if(abs(file(t)-file(s))<=1&&(c?rankof(t)>rankof(s):rankof(t)<rankof(s))){passed=false;break;}}
  if(passed)entry.passed[c]|=uint64_t(1)<<s;
 }
 return entry;
}
'''
new=new.replace('int evaluate(const Board& b){','int evaluate(const Board& b){\n#if CLASH_EVAL_FAST>=2\n const auto&pawnCache=pawnEvaluation(b);\n#endif')
a='int s=__builtin_ctzll(bits);pawns[c][file(s)]++;pawnSquares[c].push_back(s);'
b='''int s=__builtin_ctzll(bits);
#if CLASH_EVAL_FAST<2
 pawns[c][file(s)]++;
#endif
 pawnSquares[c].push_back(s);''';assert a in new;new=new.replace(a,b)
a=' phase=min(24,phase);';b='''
#if CLASH_EVAL_FAST>=2
 for(int c=0;c<2;c++)for(int f=0;f<8;f++)pawns[c][f]=pawnCache.files[c][f];
#endif
 phase=min(24,phase);''';assert a in new;new=new.replace(a,b)
a='bool passed=true;for(int t:pawnSquares[1-c])if(abs(file(t)-f)<=1&&(c?rankof(t)>rankof(s):rankof(t)<rankof(s)))passed=false;'
b='''bool passed;
#if CLASH_EVAL_FAST>=2
 passed=(pawnCache.passed[c]&(uint64_t(1)<<s))!=0;
#else
 passed=true;for(int t:pawnSquares[1-c])if(abs(file(t)-f)<=1&&(c?rankof(t)>rankof(s):rankof(t)<rankof(s)))passed=false;
#endif
''';assert a in new;new=new.replace(a,b)
s=s[:start]+'#if CLASH_EVAL_FAST\n#if CLASH_EVAL_FAST>=2\n'+cache+'#endif\n'+new+'\n#else\n'+old+'\n#endif'+s[end:]
# Skip evaluation bookkeeping on transient boards used only for legality or SEE.
s=s.replace('void setPiece(int square,int piece){', 'void setPiece(int square,int piece,bool bookkeeping=true){')
s=s.replace('changeEvaluation(square,old,-1);changeEvaluation(square,piece,1);','if(bookkeeping){changeEvaluation(square,old,-1);changeEvaluation(square,piece,1);}')
s=s.replace('Board moved(Move m)const{','Board moved(Move m,bool bookkeeping=true)const{')
s=s.replace('n.setPiece(m.from,0);n.setPiece(m.to,m.promo?side*m.promo:p);','n.setPiece(m.from,0,bookkeeping);n.setPiece(m.to,m.promo?side*m.promo:p,bookkeeping);')
s=s.replace('n.setPiece(m.to-side*8,0);','n.setPiece(m.to-side*8,0,bookkeeping);')
s=s.replace('n.setPiece(rt,n.b[rf]);n.setPiece(rf,0);','n.setPiece(rt,n.b[rf],bookkeeping);n.setPiece(rf,0,bookkeeping);')
s=s.replace('if(fresh.materialMG!=n.materialMG','if(bookkeeping&&(fresh.materialMG!=n.materialMG').replace('fresh.bishopCount[1]!=n.bishopCount[1])throw','fresh.bishopCount[1]!=n.bishopCount[1]))throw')
s=s.replace('moved({from,ep,0}).check(side)','moved({from,ep,0},false).check(side)')
s=s.replace('moved(m).check(side)','moved(m,false).check(side)')
s=s.replace('Board pos=b.moved(m);','Board pos=b.moved(m,false);')
s=s.replace('pos.moved(next).check(pos.side)','pos.moved(next,false).check(pos.side)')
s=s.replace('pos=pos.moved(attacker);','pos=pos.moved(attacker,false);')
s='#ifndef CLASH_ACTIVITY\n#define CLASH_ACTIVITY 0\n#endif\n'+s
s=s.replace('struct Board{','struct PieceActivity {int mobility=0;bool kingThreat=false;};\nstruct Board{')
activity="""
 PieceActivity pieceActivity(int from,uint64_t enemyRing)const{
  PieceActivity a;int p=abs(b[from]),c=sign(b[from]),x=file(from),y=rankof(from);
  auto visit=[&](int sq){a.kingThreat|=(enemyRing&(uint64_t(1)<<sq))!=0;if(sign(b[sq])!=c)a.mobility++;};
  if(p==2){constexpr int offsets[8][2]={{1,2},{2,1},{2,-1},{1,-2},{-1,-2},{-2,-1},{-2,1},{-1,2}};for(auto&d:offsets){int f=x+d[0],r=y+d[1];if(f>=0&&f<8&&r>=0&&r<8)visit(r*8+f);}return a;}
  if(p<3||p>5)return a;
  for(int d=0;d<8;d++){if(p==3&&d<4)continue;if(p==4&&d>=4)continue;int f=x+dirs[d][0],r=y+dirs[d][1];while(f>=0&&f<8&&r>=0&&r<8){int sq=r*8+f;visit(sq);if(b[sq])break;f+=dirs[d][0];r+=dirs[d][1];}}
  return a;
 }
"""
s=s.replace(' bool attacked(int sq,int c)const{',activity+' bool attacked(int sq,int c)const{')
activity_eval="""
#if CLASH_ACTIVITY
 uint64_t kingRings[2]={};int kingPressure[2]={},activityMobility=0;
 if(phase>8)for(int c=0;c<2;c++)for(auto&d:dirs){int f=file(kings[c])+d[0],r=rankof(kings[c])+d[1];if(f>=0&&f<8&&r>=0&&r<8)kingRings[c]|=uint64_t(1)<<(r*8+f);}
 for(int s=0;s<64;s++)if(abs(b.b[s])>1&&abs(b.b[s])<6){int c=b.b[s]>0,type=abs(b.b[s]);auto a=b.pieceActivity(s,kingRings[1-c]);activityMobility+=sign(b.b[s])*a.mobility;if(a.kingThreat)kingPressure[1-c]+=type==5?50:type==4?35:25;}
#endif
"""
s=s.replace(' phase=min(24,phase);',' phase=min(24,phase);'+activity_eval)
a='int attack=0;for(int s=0;s<64;s++)if(sign(b.b[s])==-sg&&abs(b.b[s])>1&&abs(b.b[s])<6){bool hits=false;for(int i=0;i<ringSize;i++)if(b.attacks(s,ring[i])){hits=true;break;}if(hits)attack+=abs(b.b[s])==5?50:abs(b.b[s])==4?35:25;}'
b='int attack=0;for(uint64_t bits=b.occupied;bits;bits&=bits-1)if(int s=__builtin_ctzll(bits);sign(b.b[s])==-sg&&abs(b.b[s])>1&&abs(b.b[s])<6){bool hits=false;for(int i=0;i<ringSize;i++)if(b.attacks(s,ring[i])){hits=true;break;}if(hits)attack+=abs(b.b[s])==5?50:abs(b.b[s])==4?35:25;}'
for old in [a,b]:
 assert old in s;s=s.replace(old,'\n#if CLASH_ACTIVITY\n int attack=kingPressure[c];\n#else\n '+old+'\n#endif\n')
a='int mobility=0;for(int from=0;from<64;from++)if(abs(b.b[from])>1&&abs(b.b[from])<6){mobility+=sign(b.b[from])*b.mobility(from);}'
b='int mobility=0;for(uint64_t bits=b.occupied;bits;bits&=bits-1)if(int from=__builtin_ctzll(bits);abs(b.b[from])>1&&abs(b.b[from])<6){mobility+=sign(b.b[from])*b.mobility(from);}'
for old in [a,b]:
 assert old in s;s=s.replace(old,'\n#if CLASH_ACTIVITY\n int mobility=activityMobility;\n#else\n '+old+'\n#endif\n')
(p/'engine.cpp').write_text(s)
flags=['-std=c++17','-O3','-DNDEBUG','-pthread','-DCLASH_SEARCH_V2=2','-DCLASH_TACTICAL_GEN=1','-DCLASH_SEARCH_V3=3','-DCLASH_EVAL_STYLE=3'];receipts={}
for label,mode,activity in [('control',0,0),('incremental',1,0),('cached',2,0),('activity',0,1),('combined',1,1)]:
 d=p/('build-'+label);d.mkdir(exist_ok=True);(d/'engine.cpp').write_text(s);shutil.copy2(p/'tables.h',d/'tables.h');f=flags+[f'-DCLASH_EVAL_FAST={mode}',f'-DCLASH_ACTIVITY={activity}'];subprocess.run(['clang++',*f,str(d/'engine.cpp'),'-o',str(d/'clash-native')],check=True);receipts[label]={'flags':f,'sha256':hashlib.sha256((d/'clash-native').read_bytes()).hexdigest()};print(label,receipts[label],flush=True)
(p/'build-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
