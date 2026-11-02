from pathlib import Path
import shutil,json,hashlib,subprocess
p=Path(__file__).resolve().parent;s=(p/'baseline.cpp').read_text();s='#ifndef CLASH_BIT_ATTACKS\n#define CLASH_BIT_ATTACKS 0\n#endif\n'+s
needle='struct Board{';insert='''
#if CLASH_BIT_ATTACKS
uint64_t rayMasks[64][8]={},knightMasks[64]={},kingMasks[64]={},pawnSources[2][64]={};
void initializeAttackMasks(){
 for(int sq=0;sq<64;sq++){
  int x=file(sq),y=rankof(sq);
  for(int d=0;d<8;d++){int f=x+dirs[d][0],r=y+dirs[d][1];while(f>=0&&f<8&&r>=0&&r<8){rayMasks[sq][d]|=uint64_t(1)<<(r*8+f);f+=dirs[d][0];r+=dirs[d][1];}f=x+dirs[d][0];r=y+dirs[d][1];if(f>=0&&f<8&&r>=0&&r<8)kingMasks[sq]|=uint64_t(1)<<(r*8+f);}
  for(int dx:{-2,-1,1,2})for(int dy:{-2,-1,1,2})if(abs(dx)+abs(dy)==3){int f=x+dx,r=y+dy;if(f>=0&&f<8&&r>=0&&r<8)knightMasks[sq]|=uint64_t(1)<<(r*8+f);}
  for(int c=0;c<2;c++)for(int dx:{-1,1}){int f=x+dx,r=y+(c?1:-1);if(f>=0&&f<8&&r>=0&&r<8)pawnSources[c][r*8+f]|=uint64_t(1)<<sq;}
 }
}
#endif
''';assert needle in s;s=s.replace(needle,insert+needle)
a='void setPiece(int square,int piece,bool bookkeeping=true){int old=b[square];';b='''void setPiece(int square,int piece,bool bookkeeping=true){int old=b[square];
#if CLASH_BIT_ATTACKS
 updateGeometry(square,old,piece);
#endif
''';assert a in s;s=s.replace(a,b)
a='  if(direction>0){occupied|=uint64_t(1)<<square;if(type==1)pawnBits[c]|=uint64_t(1)<<square;}\n  else{occupied&=~(uint64_t(1)<<square);if(type==1)pawnBits[c]&=~(uint64_t(1)<<square);}'
assert a in s;s=s.replace(a,'#if !CLASH_BIT_ATTACKS\n'+a+'\n#endif')
needle=' void rebuildEvaluation(){';insert='''
#if CLASH_BIT_ATTACKS
 uint64_t knightBits[2]={0,0};
 void updateGeometry(int square,int old,int piece){
  uint64_t bit=uint64_t(1)<<square;occupied&=~bit;
  if(abs(old)==1)pawnBits[old>0]&=~bit;if(abs(old)==2)knightBits[old>0]&=~bit;
  if(piece){occupied|=bit;if(abs(piece)==1)pawnBits[piece>0]|=bit;if(abs(piece)==2)knightBits[piece>0]|=bit;}
 }
 void rebuildGeometry(){occupied=0;pawnBits[0]=pawnBits[1]=knightBits[0]=knightBits[1]=0;for(int sq=0;sq<64;sq++)updateGeometry(sq,0,b[sq]);}
#endif
''';assert needle in s;s=s.replace(needle,insert+needle)
a='for(int s=0;s<64;s++)changeEvaluation(s,b[s],1);}';b='''for(int s=0;s<64;s++)changeEvaluation(s,b[s],1);
#if CLASH_BIT_ATTACKS
 rebuildGeometry();
#endif
 }''';assert a in s;s=s.replace(a,b)
a=' bool attacked(int sq,int c)const{';b=''' bool attacked(int sq,int c)const{
#if CLASH_BIT_ATTACKS
  int colour=c>0;if(pawnSources[colour][sq]&pawnBits[colour])return true;
  if(knightMasks[sq]&knightBits[colour])return true;int enemyKing=king(c);if(enemyKing>=0&&(kingMasks[sq]&(uint64_t(1)<<enemyKing)))return true;
  for(int d=0;d<8;d++){uint64_t blocked=rayMasks[sq][d]&occupied;if(!blocked)continue;bool increasing=dirs[d][0]+8*dirs[d][1]>0;int hit=increasing?__builtin_ctzll(blocked):63-__builtin_clzll(blocked);int piece=b[hit];if(sign(piece)==c){int type=abs(piece);if(type==5||(d<4&&type==4)||(d>=4&&type==3))return true;}}
  return false;
#else
''';assert a in s;s=s.replace(a,b)
a='  return false;\n }\n bool check(int c)';b='  return false;\n#endif\n }\n bool check(int c)';assert a in s;s=s.replace(a,b)
a='Board fresh=n;fresh.rebuildEvaluation();';b='''Board fresh=n;fresh.rebuildEvaluation();
#if CLASH_BIT_ATTACKS
 if(fresh.occupied!=n.occupied||fresh.pawnBits[0]!=n.pawnBits[0]||fresh.pawnBits[1]!=n.pawnBits[1]||fresh.knightBits[0]!=n.knightBits[0]||fresh.knightBits[1]!=n.knightBits[1])throw runtime_error("geometry bitmaps mismatch");
#endif
''';assert a in s;s=s.replace(a,b)
a='if(s!=8||wk!=1||bk!=1';b='''
#if CLASH_BIT_ATTACKS
 b.rebuildEvaluation();
#endif
 if(s!=8||wk!=1||bk!=1''';assert a in s;s=s.replace(a,b)
a=' Board board=fen(START);';b='''
#if CLASH_BIT_ATTACKS
 initializeAttackMasks();
#endif
 Board board=fen(START);''';assert a in s;s=s.replace(a,b)
(p/'engine.cpp').write_text(s);flags=['-std=c++17','-O3','-DNDEBUG','-pthread','-DCLASH_SEARCH_V2=2','-DCLASH_TACTICAL_GEN=1','-DCLASH_SEARCH_V3=3','-DCLASH_EVAL_STYLE=3','-DCLASH_EVAL_FAST=1','-DCLASH_ACTIVITY=1'];receipts={}
for name,bit in [('control',0),('candidate',1)]:
 d=p/('build-'+name);d.mkdir(exist_ok=True);(d/'engine.cpp').write_text(s);shutil.copy2(p/'tables.h',d/'tables.h');f=flags+[f'-DCLASH_BIT_ATTACKS={bit}'];subprocess.run(['clang++',*f,str(d/'engine.cpp'),'-o',str(d/'clash-native')],check=True);receipts[name]={'flags':f,'sha256':hashlib.sha256((d/'clash-native').read_bytes()).hexdigest()};print(name,receipts[name],flush=True)
(p/'build-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
