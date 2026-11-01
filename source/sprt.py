"""WDL SPRT with a fixed draw probability and explicit statistical assumptions."""
import math,json,argparse

def test(scores,elo0=0,elo1=10,draw=.5,alpha=.05,beta=.05):
 if not elo0<elo1 or not 0<alpha<.5 or not 0<beta<.5 or not 0<=draw<1:raise ValueError('Invalid hypotheses')
 def probs(elo):
  expected=1/(1+10**(-elo/400));p={1.:expected-draw/2,.5:draw,0.:1-expected-draw/2}
  if min(p[0.],p[1.])<=0:raise ValueError('Draw probability incompatible with Elo hypotheses')
  return p
 p0,p1=probs(elo0),probs(elo1);llr=0;lower=math.log(beta/(1-alpha));upper=math.log((1-beta)/alpha)
 decision='continue';count=0
 for score in scores:
  if score not in (0,.5,1):raise ValueError('Only completed game scores are accepted')
  if not p0[score] or not p1[score]:raise ValueError('Observed outcome has zero probability')
  llr+=math.log(p1[score]/p0[score]);count+=1
  if llr>=upper:decision='accept_h1';break
  if llr<=lower:decision='accept_h0';break
 return dict(decision=decision,games=count,llr=llr,lower=lower,upper=upper,elo0=elo0,elo1=elo1,draw_probability=draw,assumptions='Independent WDL observations and fixed draw probability specified before matches; paired-game correlation and misspecified draw rate invalidate nominal error guarantees.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('scores',help='JSON array of completed game scores, 0, 0.5, 1');p.add_argument('--draw',type=float,default=.5);a=p.parse_args();print(json.dumps(test(json.load(open(a.scores)),draw=a.draw),indent=2))
