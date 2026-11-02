"""Validate an explicit experimental binary; never replace the production executable."""
import argparse,pathlib,subprocess,os,json,time,hashlib
import chess,chess.engine
here=pathlib.Path(__file__).resolve().parent;repo=here.parents[3]
p=argparse.ArgumentParser();p.add_argument('--binary',type=pathlib.Path,default=here/'build-parallel-original/clash-native');p.add_argument('--label',default='learning-experiment');a=p.parse_args();binary=a.binary.resolve()
assert pathlib.Path(a.label).name==a.label
for name,envname,suffix in [('verify.py','CLASH_VERIFY_REPORT','rules'),('protocol_test.py','CLASH_PROTOCOL_REPORT','protocol')]:
 env=os.environ.copy();env.update(CLASH_NATIVE_BINARY=str(binary),CLASH_TACTICAL_CHECK='1');env[envname]=a.label+'-'+suffix+'.json'
 subprocess.run([os.sys.executable,str(repo/'source/cpp'/name)],env=env,check=True)
rows=[]
with chess.engine.SimpleEngine.popen_uci(str(binary),timeout=10) as e:
 if 'Threads' in e.options:
  workers=min(4,e.options['Threads'].max);e.configure({'Threads':workers})
  for _ in range(4):
   b=chess.Board();t=time.monotonic();r=e.play(b,chess.engine.Limit(time=.5),info=chess.engine.INFO_ALL);elapsed=time.monotonic()-t
   assert r.move in b.legal_moves and elapsed<1
   assert 'root_threads '+str(workers) in r.info.get('string','') if workers>1 else True
   rows.append({'test':'parallel-clock','seconds':elapsed,'depth':r.info.get('depth'),'detail':r.info.get('string')})
  for _ in range(20):
   analysis=e.analysis(chess.Board());time.sleep(.015);t=time.monotonic();analysis.stop();analysis.wait();elapsed=time.monotonic()-t;assert elapsed<.5
   rows.append({'test':'parallel-stop','seconds':elapsed})
report={'passed':True,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'checks':rows,'note':'Finite UCI, rules and concurrency checks. Playing strength requires independent matches.'}
(repo/(a.label+'-concurrency.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
