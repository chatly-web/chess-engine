"""Regularised Texel-style fitting: own features, human outcomes, game-disjoint validation."""
from pathlib import Path
import json,hashlib,time
import numpy as np
from scipy.optimize import minimize
root=Path(__file__).resolve().parent;d=np.load(root/'data/train-matrix.npz');X=d['X'];base=d['base'];y=d['y'];train=d['train'];start=time.monotonic()
groups=['material','pawn_pst','minor_pst','major_pst','king_pst','passed_pawns','rook_activity','bishop_pair','doubled_pawns','isolated_pawns','development','king_shelter','king_exposure','king_attack','queen_pressure','thorn_pawns','open_king_files','endgame_king','mobility','tempo','unsafe_mobility']
names=[g+'_'+phase for g in groups for phase in ['mg','eg']]
Xt=X[train];bt=base[train];yt=y[train];Xv=X[~train];bv=base[~train];yv=y[~train]
def sigmoid(v):return 1/(1+np.exp(-np.clip(v,-45,45)))
def mse(cp,target,k):return float(np.mean((sigmoid(cp*k*np.log(10)/400)-target)**2))
# Fit scaling on training data only; it is a calibration constant, not a foreign-engine target.
k=min(np.linspace(.25,2.5,91),key=lambda k:mse(bt,yt,k));a=k*np.log(10)/400
bounds=[]
for i,name in enumerate(names):
 g=i//2
 if g in (0,19) or np.std(Xt[:,i])<1e-9:bounds.append((0.,0.))
 elif g==20:bounds.append((-2.,0.))
 elif g==5:bounds.append((-.8,.8))
 elif g==14:bounds.append((-1.,1.))
 elif g in (11,12,13,15,16):bounds.append((-.7,2.))
 else:bounds.append((-.7,1.5))
baseline={'training_mse':mse(bt,yt,k),'validation_mse':mse(bv,yv,k)};trials=[];best=np.zeros(42);best_valid=baseline['validation_mse']
for regularisation in [.001,.005,.02]:
 def objective(w):
  pred=sigmoid((bt+Xt@w)*a);resid=pred-yt
  loss=np.mean(resid**2)+regularisation*np.mean(w**2)
  gradient=(2*a/len(yt))*(Xt.T@(resid*pred*(1-pred)))+2*regularisation*w/len(w)
  return float(loss),gradient
 result=minimize(objective,np.zeros(42),jac=True,bounds=bounds,method='L-BFGS-B',options={'maxiter':300,'ftol':1e-11,'gtol':1e-8})
 w=result.x;valid=mse(bv+Xv@w,yv,k);trial={'regularisation':regularisation,'training_mse':mse(bt+Xt@w,yt,k),'validation_mse':valid,'iterations':int(result.nit),'optimizer_success':bool(result.success),'message':str(result.message),'deltas':w.tolist()};trials.append(trial)
 if valid<best_valid:best_valid=valid;best=w.copy()
 print(json.dumps({key:value for key,value in trial.items() if key!='deltas'}),flush=True)
model={'method':'Regularised Texel-style squared expected-score fitting','target':'Human final game results only','foreign_engine_evaluations':False,'features':names,'deltas':best.tolist(),'effective_coefficients':[(float(best[i]) if i//2==20 else float(1+best[i])) for i in range(42)],'sigmoid_K':float(k),'baseline':baseline,'selected_validation_mse':best_valid,'relative_validation_error_reduction':1-best_valid/baseline['validation_mse'],'training_positions':int(train.sum()),'validation_positions':int((~train).sum()),'game_split_disjoint':True,'trials':trials,'matrix_sha256':hashlib.sha256((root/'data/train-matrix.npz').read_bytes()).hexdigest(),'seconds':time.monotonic()-start,'note':'Lower outcome-prediction error does not establish stronger chess play. Candidate must pass fresh match validation.'}
encoded=json.dumps(model,sort_keys=True).encode();modelid=hashlib.sha256(encoded).hexdigest()[:16];model['model_id']=modelid
(root/'model.json').write_text(json.dumps(model,indent=2)+'\n')
(root/'learned_scale.h').write_text('// Original weights fitted from permitted human results; no foreign-engine labels.\nconstexpr int MODEL_GROUPS=21;\nconstexpr int MODEL_FEATURES=42;\nconstexpr bool MODEL_ACTIVE=true;\nconstexpr const char*MODEL_ID="human-'+modelid+'";\nconstexpr std::array<double,MODEL_FEATURES>MODEL_DELTAS={'+','.join(format(x,'.17g') for x in best)+'};\n')
print(json.dumps({key:value for key,value in model.items() if key not in ('trials','deltas','scales','features')},indent=2))
