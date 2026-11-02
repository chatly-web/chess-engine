"""Collect public human PGNs without analysis; no credentials or engine labels."""
import pathlib,urllib.request,urllib.parse,urllib.error,json,time,hashlib,io,collections
import chess.pgn
root=pathlib.Path(__file__).resolve().parent;out=root/'data';out.mkdir(exist_ok=True)
def request(url,accept):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept':accept,'User-Agent':'OriginalChessResearch/1.0'}),timeout=120) as response:return response.read()
  except urllib.error.HTTPError as exc:
   if exc.code!=429:raise
   print(json.dumps({'rate_limited':True,'retry_after_seconds':60}),flush=True);time.sleep(60)
 raise RuntimeError('Rate limit persists')
leaders=json.loads(request('https://lichess.org/api/player/top/20/blitz','application/vnd.lichess.v3+json'))['users'];users=[u for u in leaders if u.get('title')!='BOT'][:12]
until=int(time.time()*1000);seen=set();counts=collections.Counter();manifest={'source':'https://lichess.org/api','leaderboard':'blitz top20','until':until,'evals':False,'literate':False,'accuracy':False,'labels':'human game Result only','minimum_player_elo':2200,'exports':[],'games':[]}
clean=out/'human-clean.pgn';assert not clean.exists(),'Do not overwrite collected corpus'
for index,user in enumerate(users):
 params={'max':800,'until':until,'rated':'true','perfType':'blitz,rapid,classical','moves':'true','tags':'true','clocks':'false','evals':'false','accuracy':'false','opening':'false','literate':'false','ongoing':'false','finished':'true'}
 url='https://lichess.org/api/games/user/'+urllib.parse.quote(user['id'],safe='')+'?'+urllib.parse.urlencode(params)
 raw=request(url,'application/x-chess-pgn');assert b'[%eval' not in raw and b'[%cal' not in raw,'Unexpected analysis annotations'
 (out/f'export-{index:02}.pgn').write_bytes(raw);stream=io.StringIO(raw.decode('utf-8-sig'));accepted=0
 while True:
  game=chess.pgn.read_game(stream)
  if game is None:break
  if game.errors:counts['parse_error']+=1;continue
  h=game.headers;gid=h.get('Site','').rstrip('/').split('/')[-1]
  if not gid or gid in seen:counts['duplicate']+=1;continue
  if h.get('WhiteTitle')=='BOT' or h.get('BlackTitle')=='BOT':counts['bot']+=1;continue
  if h.get('Variant','Standard')!='Standard' or h.get('Result') not in ('1-0','0-1','1/2-1/2'):counts['variant_or_result']+=1;continue
  try:
   if min(int(h.get('WhiteElo','0')),int(h.get('BlackElo','0')))<2200:counts['rating']+=1;continue
   base=int(h.get('TimeControl','0+0').split('+')[0])
   if base<180:counts['clock']+=1;continue
  except ValueError:counts['metadata']+=1;continue
  if game.end().board().ply()<30:counts['short_game']+=1;continue
  # Export without comments or variations, even though evals=false was requested.
  text=game.accept(chess.pgn.StringExporter(headers=True,variations=False,comments=False));assert '[%eval' not in text
  with clean.open('a') as f:f.write(text+'\n\n')
  seen.add(gid);accepted+=1;manifest['games'].append({'id':gid,'result':h['Result'],'white_elo':int(h['WhiteElo']),'black_elo':int(h['BlackElo']),'time_control':h['TimeControl']})
 manifest['exports'].append({'username':user['id'],'url':url,'raw_sha256':hashlib.sha256(raw).hexdigest(),'accepted':accepted})
 manifest['accepted_games']=len(seen);manifest['rejections']=dict(counts);manifest['clean_sha256']=hashlib.sha256(clean.read_bytes()).hexdigest() if clean.exists() else None
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'export':index+1,'accepted_total':len(seen),'accepted_export':accepted,'rejected':dict(counts)}),flush=True)
 if len(seen)>=5000:break
 time.sleep(1)
assert len(seen)>=1000,'Need a sufficiently broad human corpus'
print(json.dumps({'complete':True,'accepted_games':len(seen),'clean_sha256':manifest['clean_sha256']}),flush=True)
