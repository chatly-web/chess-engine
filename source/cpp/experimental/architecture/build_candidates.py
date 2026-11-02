from pathlib import Path
import subprocess,hashlib,json,shutil
p=Path(__file__).resolve().parent;s=(p/'baseline.cpp').read_text()
s='#ifndef CLASH_CLUSTER_TT\n#define CLASH_CLUSTER_TT 0\n#endif\n#ifndef CLASH_SAFE_NULL\n#define CLASH_SAFE_NULL 0\n#endif\n'+s
old='struct Entry{uint64_t key=0,context=0;Move move;int depth=-1,score=0,flag=0,ruleHalf=0,span=5;};'
new='''#if CLASH_CLUSTER_TT
struct Entry{uint64_t key=0,context=0;Move move;int depth=-1,score=0;int8_t flag=0;int16_t ruleHalf=0,span=5;uint16_t age=0;};
#else
'''+old+'\n#endif'
assert old in s;s=s.replace(old,new)
s=s.replace('struct Engine{','''struct Engine{
 uint16_t generation=0;int verificationNesting=0;
 uint64_t ttProbes=0,ttHits=0,ttReplacements=0,nullAttempts=0,nullCutoffs=0,nullVerifications=0,nullRejected=0;
''',1)
a=' void tick(){';assert a in s;s=s.replace(a,(p/'tt_methods.inc').read_text()+'\n'+a,1)
a='Entry entry=tt[key&(tt.size()-1)];';assert a in s;s=s.replace(a,'Entry entry=probeTT(key,ctx,b.half,nodeUnique);')
s=s.replace('if(!q&&ply&&entry.key==key&&','if(!q&&ply&&!verificationNesting&&entry.key==key&&')
s=s.replace('if((CLASH_SEARCH_V3&1)&&!q&&ply','if((CLASH_SEARCH_V3&1)&&!verificationNesting&&!q&&ply')
a='  if(!q&&depth>=3&&ply&&!check&&allowNull&&beta-alpha==1){'
start=s.index(a);end=s.index('\n  auto&scored=',start);oldnull=s[start:end]
s=s[:start]+'#if CLASH_SAFE_NULL\n'+(p/'safe_null.inc').read_text()+'\n#else\n'+oldnull+'\n#endif'+s[end:]
s=s.replace('if((CLASH_SEARCH_V3&2)&&q&&!check', 'if((CLASH_SEARCH_V3&2)&&!verificationNesting&&q&&!check')
s=s.replace('int reduction=!q&&depth>=3', 'int reduction=!verificationNesting&&!q&&depth>=3')
a='tt[key&(tt.size()-1)]={key,ctx,bm,depth,v,best<=original?-1:best>=beta?1:0,b.half,nodeUnique?quietSpan[ply]:-1};';assert a in s;s=s.replace(a,'storeTT(key,ctx,bm,depth,v,best<=original?-1:best>=beta?1:0,b.half,nodeUnique?quietSpan[ply]:-1);')
s=s.replace('nodes=0;completed=0;safeCutoffs=0;nodeLimit=limit;', 'generation++;ttProbes=ttHits=ttReplacements=nullAttempts=nullCutoffs=nullVerifications=nullRejected=0;nodes=0;completed=0;safeCutoffs=0;nodeLimit=limit;')
a='emit("info string history_guarded_tt_cutoffs "+to_string(safeCutoffs));';assert a in s;s=s.replace(a,'emit("info string architecture tt_probes "+to_string(ttProbes)+" hits "+to_string(ttHits)+" replacements "+to_string(ttReplacements)+" null_attempts "+to_string(nullAttempts)+" cutoffs "+to_string(nullCutoffs)+" verified "+to_string(nullVerifications)+" rejected "+to_string(nullRejected)+" history_guarded_tt_cutoffs "+to_string(safeCutoffs));')
s=s.replace('else if(cmd=="isready")','else if(cmd=="ttstats"){halt();emit("info string tt_entry_bytes "+to_string(sizeof(Entry))+" capacity "+to_string(engine.tt.size())+" bytes "+to_string(sizeof(Entry)*engine.tt.size()));}\n  else if(cmd=="isready")')
s=s.replace('fill(engine.tt.begin(),engine.tt.end(),Entry{});','fill(engine.tt.begin(),engine.tt.end(),Entry{});engine.generation=0;')
s=s.replace('Clash Native C++ v0.8 weights ', 'Clash Native C++ architecture candidate weights ')
(p/'engine.cpp').write_text(s)
receipts={};flags=['-std=c++17','-O3','-DNDEBUG','-pthread','-DCLASH_SEARCH_V2=2','-DCLASH_TACTICAL_GEN=1','-DCLASH_SEARCH_V3=3','-DCLASH_EVAL_STYLE=3']
for name,tt,null in [('control',0,0),('cluster',1,0),('safe-null',0,1),('combined',1,1)]:
 out=p/('build-'+name);out.mkdir(exist_ok=True);(out/'engine.cpp').write_text(s);shutil.copy2(p/'tables.h',out/'tables.h')
 defs=[f'-DCLASH_CLUSTER_TT={tt}',f'-DCLASH_SAFE_NULL={null}'];subprocess.run(['clang++',*flags,*defs,str(out/'engine.cpp'),'-o',str(out/'clash-native')],check=True)
 receipts[name]={'sha256':hashlib.sha256((out/'clash-native').read_bytes()).hexdigest(),'flags':flags+defs};print(name,receipts[name]['sha256'],flush=True)
(p/'build-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
