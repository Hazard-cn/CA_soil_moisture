"""Reproduce frozen recovery-v2 inference with an equivalent scaled outcome design."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,sys
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from patsy import build_design_matrices

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/python'))
from hotdry_event_override_models import grouped_scores,rademacher_weights,romano_wolf_stepdown
from run_hotdry_event_override_recovery_v2 import block_codes
from hotdry_event_override_validators import NAMED_ZONES

FORMULA=("recovered_now ~ time_z + time_sq_z + C(zone) + C(year) + ca_z + ca_z:C(zone) "
         "+ antecedent_smrz_z + duration_days_z + event_mean_excess_c_z + onset_doy_z")
CONT=['time','time_sq','ca','antecedent_smrz','duration_days','event_mean_excess_c','onset_doy']
def digest(p:Path)->dict[str,object]:
 b=p.read_bytes();return {'path':str(p).replace('\\','/'),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def standardize(beta,design,events,ca,scale):
 base=events.copy();base['ca_z']=(ca-scale['ca']['mean'])/scale['ca']['sd'];surv=np.ones(len(base));cum=np.zeros((len(base),len(beta)));curve=[];grad=[]
 for day in range(30):
  base['time_z']=(day/30-scale['time']['mean'])/scale['time']['sd'];base['time_sq_z']=((day/30)**2-scale['time_sq']['mean'])/scale['time_sq']['sd']
  x=np.asarray(build_design_matrices([design],base)[0]);eta=x@beta;z=np.exp(np.clip(eta,-40,40));surv*=np.exp(-z);cum+=z[:,None]*x;curve.append(surv.mean());grad.append(np.mean(-surv[:,None]*cum,axis=0))
 curve=np.asarray(curve);grad=np.asarray(grad);return curve,grad,float(curve.sum()),grad.sum(axis=0)
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--recovery-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();src=a.recovery_dir.resolve();out=a.output_dir.resolve()
 if out.exists() and any(out.iterdir()):raise FileExistsError(out)
 out.mkdir(parents=True,exist_ok=True);risk=pd.read_csv(src/'recovery_risk_set.csv.gz');scale={}
 for v in CONT:
  mean=float(risk[v].mean());sd=float(risk[v].std(ddof=0));scale[v]={'mean':mean,'sd':sd};risk[v+'_z']=(risk[v]-mean)/sd
 family=sm.families.Binomial(link=sm.families.links.CLogLog());fit=smf.glm(FORMULA,data=risk,family=family,freq_weights=risk.ipcw).fit(maxiter=200,tol=1e-10)
 h=fit.model.hessian(fit.params);bread=np.linalg.inv(-h);scores=grouped_scores(fit.model.score_obs(fit.params),np.ones(len(risk)),block_codes(risk));w=rademacher_weights(1999,scores.shape[0],seed=42);shocks=(w@scores)@bread.T
 events=risk[risk.follow_day==0].copy();manifest=json.loads((src/'run_manifest.json').read_text(encoding='utf-8'));ca=manifest['ca_quantiles'];rows=[];draws=[];points=[];curves=[]
 for z in NAMED_ZONES:
  ev=events[events.zone==z].copy()
  for v in CONT[3:]:ev[v+'_z']=(ev[v]-scale[v]['mean'])/scale[v]['sd']
  by={}
  for lab,val in [('P25',float(ca['p25'])),('P75',float(ca['p75']))]:
   c,g,r,rg=standardize(fit.params.to_numpy(),fit.model.data.design_info,ev,val,scale);by[lab]=(r,rg)
   for day in range(30):curves.append({'zone':z,'ca_level':lab,'follow_day':day,'survival':c[day]})
  diff=by['P75'][0]-by['P25'][0];gradient=by['P75'][1]-by['P25'][1];d=diff+shocks@gradient;points.append(diff);draws.append(d);rows.append({'zone':z,'events':len(ev),'rmst30_ca_p25':by['P25'][0],'rmst30_ca_p75':by['P75'][0],'rmst30_difference_p75_minus_p25':diff,'ci_low':np.quantile(d,.025),'ci_high':np.quantile(d,.975),'bootstrap_se':np.std(d,ddof=1)})
 matrix=np.column_stack(draws);raw,rw,holm=romano_wolf_stepdown(np.asarray(points),matrix)
 for row,a1,a2,a3 in zip(rows,raw,rw,holm):row.update(p_raw=a1,p_romano_wolf=a2,p_holm=a3)
 result=pd.DataFrame(rows);result.to_csv(out/'rmst30_scaled_results.csv',index=False,encoding='utf-8-sig');pd.DataFrame(curves).to_csv(out/'scaled_curves.csv',index=False,encoding='utf-8-sig');pd.DataFrame(np.cov(matrix,rowvar=False),index=NAMED_ZONES,columns=NAMED_ZONES).to_csv(out/'rmst30_scaled_covariance.csv',encoding='utf-8-sig')
 frozen=pd.read_csv(src/'rmst30_results.csv');merged=result.merge(frozen,on='zone',suffixes=('_scaled','_frozen'));numeric=[c for c in result.columns if c not in {'zone','events'}];comparison={c:float(np.max(np.abs(merged[c+'_scaled']-merged[c+'_frozen']))) for c in numeric};comparison['max_all_reported_fields']=max(comparison.values());comparison['scaled_hessian_condition_number']=float(np.linalg.cond(-h));comparison['blocks']=int(scores.shape[0]);(out/'scaled_inference_comparison.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8')
 outputs=[out/'rmst30_scaled_results.csv',out/'scaled_curves.csv',out/'rmst30_scaled_covariance.csv',out/'scaled_inference_comparison.json'];run={'contract_version':'run-manifest-v1','canonical_id':'compound-event-intensity-duration-override-v1','run_id':out.name,'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'FULL','not_for_inference':False,'design_version':'override-recovery-v2-equivalent-scaled-inference-v1','inputs':[digest(src/'run_manifest.json'),digest(src/'recovery_risk_set.csv.gz'),digest(src/'rmst30_results.csv'),digest(Path(__file__).resolve())],'outputs':[digest(x) for x in outputs],'inference':{'primary':'scaled-parameter fixed-IPCW one-step 2-degree spatial-block wild-score','repetitions':1999,'seed':42},'scaling':scale,'claims':['algebraically equivalent scaled parameterization of frozen recovery-v2 outcome model']};(out/'run_manifest.json').write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding='utf-8');print(result.to_string(index=False));return 0
if __name__=='__main__':raise SystemExit(main())
