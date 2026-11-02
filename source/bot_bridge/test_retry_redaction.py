"""Offline regression for the separate official lichess-bot utility; no real token/network."""
import argparse,io,json,logging,sys
from pathlib import Path
from unittest.mock import patch
p=argparse.ArgumentParser();p.add_argument('--bridge-root',required=True);a=p.parse_args();sys.path.insert(0,str(Path(a.bridge_root).resolve()))
import requests
from lib.lichess import Lichess,backoff_handler,logger
fixture='dummy-sensitive-value-not-a-real-token';kwargs={'data':fixture};details={'args':('token_test',),'kwargs':kwargs,'wait':.1,'tries':1,'target':'api_post'};stream=io.StringIO();handler=logging.StreamHandler(stream);logger.addHandler(handler);logger.setLevel(logging.DEBUG)
try:backoff_handler(details)
finally:logger.removeHandler(handler)
assert kwargs['data']==fixture,'Logging changed the retry payload'
assert fixture not in stream.getvalue() and '<token redacted>' in stream.getvalue(),'Logging exposed the payload'
seen=[]
def response(scopes='bot:play',missing=False):
 r=requests.Response();r.status_code=200;r.headers['Content-Type']='application/json';r._content=json.dumps({} if missing else {fixture:{'scopes':scopes}}).encode();return r
def transient(_session,_url,**kw):
 seen.append(kw['data'])
 if len(seen)==1:raise requests.exceptions.ReadTimeout('fixture transient timeout')
 return response()
with patch.object(requests.Session,'post',transient):Lichess(fixture,'https://lichess.org','regression-test',logging.WARNING,1)
assert seen==[fixture,fixture],'Retried request did not preserve its original body'
for fixture_response in [response('challenge:write'),response(missing=True)]:
 with patch.object(requests.Session,'post',return_value=fixture_response):
  try:Lichess(fixture,'https://lichess.org','regression-test',logging.WARNING,1)
  except RuntimeError:pass
  else:raise AssertionError('Token/scope validation was bypassed')
print(json.dumps({'passed':True,'redaction_preserves_payload':True,'redaction_hides_secret':True,'transient_retry_preserves_body':True,'scope_and_token_guards_enforced':True,'network_requests':0}))
