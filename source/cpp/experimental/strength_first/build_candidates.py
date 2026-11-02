from pathlib import Path
import subprocess,hashlib,json,shutil
p=Path(__file__).resolve().parent;s=(p/'baseline.cpp').read_text()
s='''#ifndef CLASH_QCHECKS
#define CLASH_QCHECKS 0
#endif
#ifndef CLASH_PAWN_THREATS
#define CLASH_PAWN_THREATS 0
#endif
'''+s
needle=' int ordering(const Board&b,Move m,Move preferred,int ply)'
method=''' bool forcingPawn(const Board&b,Move m)const{
  if(abs(b.b[m.from])!=1)return false;
  int advance=b.side>0?rankof(m.to):7-rankof(m.to);if(advance>=5)return true;
  for(int dx:{-1,1}){int to=m.to+b.side*8+dx;if(to<0||to>=64||abs(file(to)-file(m.to))!=1)continue;int piece=b.b[to];if(sign(piece)==-b.side&&abs(piece)>=2&&abs(piece)<=5)return true;}
  return false;
 }
'''
assert needle in s;s=s.replace(needle,method+needle)
a='bool tactical=CLASH_TACTICAL_GEN&&depth<=0&&!check;';b='bool qChecks=CLASH_QCHECKS&&depth<=0&&!check&&qdepth<3;bool tactical=CLASH_TACTICAL_GEN&&depth<=0&&!check&&!qChecks;';assert a in s;s=s.replace(a,b)
a='return !b.b[m.to]&&!m.promo&&!(abs(b.b[m.from])==1&&m.to==b.ep);';b='return !b.b[m.to]&&!m.promo&&!(abs(b.b[m.from])==1&&m.to==b.ep)&&!(qChecks&&b.moved(m).check(-b.side)&&exchange(b,m)>=0);';assert a in s;s=s.replace(a,b)
a='if(m==killers[ply][0])return 850000;';b='if(CLASH_PAWN_THREATS&&forcingPawn(b,m))return 870000;'+a;assert a in s;s=s.replace(a,b)
a='&&quiet&&!check&&!n.check(n.side)?1:0;';b='&&quiet&&!check&&!n.check(n.side)&&!(CLASH_PAWN_THREATS&&forcingPawn(b,m))?1:0;';assert a in s;s=s.replace(a,b)
s=s.replace('Clash Native C++ v0.8 weights ','Clash Native C++ tactical candidate weights ');(p/'engine.cpp').write_text(s)
base=['-std=c++17','-O3','-DNDEBUG','-pthread','-DCLASH_SEARCH_V2=2','-DCLASH_TACTICAL_GEN=1','-DCLASH_EVAL_STYLE=3'];receipts={}
for name,q,threat,tt,v3 in [('control',0,0,2,3),('checks',1,0,2,3),('threats',1,1,2,3),('guarded',1,1,0,2)]:
 out=p/('build-'+name);out.mkdir(exist_ok=True);(out/'engine.cpp').write_text(s);shutil.copy2(p/'tables.h',out/'tables.h');flags=base+[f'-DCLASH_QCHECKS={q}',f'-DCLASH_PAWN_THREATS={threat}',f'-DCLASH_TT_REUSE={tt}',f'-DCLASH_SEARCH_V3={v3}'];subprocess.run(['clang++',*flags,str(out/'engine.cpp'),'-o',str(out/'clash-native')],check=True);receipts[name]={'sha256':hashlib.sha256((out/'clash-native').read_bytes()).hexdigest(),'flags':flags};print(name,receipts[name]['sha256'],flush=True)
(p/'build-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
