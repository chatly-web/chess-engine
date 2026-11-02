from pathlib import Path
import subprocess,hashlib,json,shutil
p=Path(__file__).resolve().parent;s=(p/'baseline.cpp').read_text();s='#ifndef CLASH_HISTORY\n#define CLASH_HISTORY 0\n#endif\n#ifndef CLASH_CAPTURE_LAST\n#define CLASH_CAPTURE_LAST 0\n#endif\n'+s
needle=' int ordering(const Board&b,Move m,Move preferred,int ply)';method=''' void updateHistory(int&score,int bonus){bonus=max(-1000,min(1000,bonus));score+=bonus-score*abs(bonus)/10000;score=max(-10000,min(10000,score));}
''';assert needle in s;s=s.replace(needle,method+needle)
s=s.replace('base-=950000;','base-=CLASH_CAPTURE_LAST?1200000:950000;')
a='if(quiet){killers[ply][1]=killers[ply][0];killers[ply][0]=m;auto&h=history[b.side>0][m.from][m.to];h=min(70000,h+max(1,depth)*max(1,depth));}'
b='''if(quiet&&(!CLASH_HISTORY||!q)){killers[ply][1]=killers[ply][0];killers[ply][0]=m;auto&h=history[b.side>0][m.from][m.to];if(CLASH_HISTORY){int bonus=min(1000,16*max(1,depth)*max(1,depth));updateHistory(h,bonus);for(int j=0;j<i;j++){Move failed=moves[j];if(!b.b[failed.to]&&!failed.promo&&!(abs(b.b[failed.from])==1&&failed.to==b.ep))updateHistory(history[b.side>0][failed.from][failed.to],-bonus/2);}}else h=min(70000,h+max(1,depth)*max(1,depth));}'''
assert a in s;s=s.replace(a,b)
a='nodes=0;completed=0;safeCutoffs=0;';b='nodes=0;completed=0;safeCutoffs=0;if(CLASH_HISTORY)for(auto&side:history)for(auto&from:side)for(int&value:from)value/=2;';assert a in s;s=s.replace(a,b)
(p/'engine.cpp').write_text(s);flags=['-std=c++17','-O3','-DNDEBUG','-pthread','-DCLASH_SEARCH_V2=2','-DCLASH_TACTICAL_GEN=1','-DCLASH_SEARCH_V3=3','-DCLASH_EVAL_STYLE=3','-DCLASH_EVAL_FAST=1','-DCLASH_ACTIVITY=1'];receipts={}
for name,h,c in [('control',0,0),('history',1,0),('captures',0,1),('combined',1,1)]:
 d=p/('build-'+name);d.mkdir(exist_ok=True);(d/'engine.cpp').write_text(s);shutil.copy2(p/'tables.h',d/'tables.h');f=flags+[f'-DCLASH_HISTORY={h}',f'-DCLASH_CAPTURE_LAST={c}'];subprocess.run(['clang++',*f,str(d/'engine.cpp'),'-o',str(d/'clash-native')],check=True);receipts[name]={'flags':f,'sha256':hashlib.sha256((d/'clash-native').read_bytes()).hexdigest()};print(name,receipts[name]['sha256'],flush=True)
(p/'build-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
