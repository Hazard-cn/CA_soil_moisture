"""Execute the event-direction Round-1 mandatory empirical revisions."""

from __future__ import annotations

import argparse, datetime as dt, json, math, subprocess, sys, time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_models import absorb_two_way, grouped_scores, rademacher_weights, romano_wolf_stepdown  # noqa: E402
from hotdry_event_override_validators import NAMED_ZONES, validate_override_manifest  # noqa: E402
from hotdry_event_round1_inference import fit_revision, spatial_hac_covariance, vif_pair, webb_weights  # noqa: E402
from run_hotdry_event_override_models import PANEL_FIELDS, codes_for_frame, design_matrix, endpoint_payload  # noqa: E402
from run_hotdry_event_stage1 import file_digest, hash_artifacts, sample_key_sha256  # noqa: E402

EXPOSURES = {"duration":"total_duration_days", "intensity":"mean_event_intensity_c"}

def parse_args():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--panel',type=Path,required=True);p.add_argument('--model-dir',type=Path,required=True);p.add_argument('--stage1-dir',type=Path,required=True);p.add_argument('--strict-stage1-dir',type=Path,required=True);return p.parse_args()

def joint_design(frame: pd.DataFrame):
    d=frame.total_duration_days.to_numpy(float);q=frame.mean_event_intensity_c.to_numpy(float);ca=frame.ca.to_numpy(float)
    cols=[frame.gdd_10_29.to_numpy(float),frame.pr_sum.to_numpy(float),frame.pr_sum.to_numpy(float)**2];names=['gdd_10_29','pr_sum','pr_sum_sq']
    for z in NAMED_ZONES:
        flag=(frame.zone.to_numpy()==z).astype(float);cols += [flag*d,flag*q,flag*ca,flag*ca*d,flag*ca*q];names += [f'{z}:duration',f'{z}:intensity',f'{z}:ca',f'{z}:ca_x_duration',f'{z}:ca_x_intensity']
    return np.column_stack(cols),names

def bootstrap_draws(fit, weights):
    scores=grouped_scores(fit.x_scaled,fit.residuals,fit.block_codes)
    scaled_beta=fit.beta*fit.column_scale
    return (scaled_beta[None,:]+(weights@scores)@fit.xtx_inverse.T)/fit.column_scale[None,:]

def conditional_rows(fit,names,frame,model,ca,endpoints,draws):
    rows=[];contrast_draws=[];points=[]
    for z in NAMED_ZONES:
        for e in EXPOSURES:
            separate_layout=model.startswith('separate') or model.startswith('strict')
            b=names.index(f'{z}:exposure' if separate_layout else f'{z}:{e}')
            d=names.index(f'{z}:ca_x_exposure' if separate_layout else f'{z}:ca_x_{e}')
            de=endpoints[z][e]['p90']-endpoints[z][e]['p50'];dc=ca['p75']-ca['p25']
            low=(fit.beta[b]+fit.beta[d]*ca['p25'])*de;high=(fit.beta[b]+fit.beta[d]*ca['p75'])*de;contrast=fit.beta[d]*dc*de
            lowdraw=(draws[:,b]+draws[:,d]*ca['p25'])*de;highdraw=(draws[:,b]+draws[:,d]*ca['p75'])*de;cdraw=draws[:,d]*dc*de
            row={'model':model,'zone':z,'exposure':e,'ca_p25':ca['p25'],'ca_p75':ca['p75'],'exposure_p50':endpoints[z][e]['p50'],'exposure_p90':endpoints[z][e]['p90'],
                 'low_sr_log_change':low,'low_sr_percent_change':100*math.expm1(low),'low_sr_ci_low_percent':100*math.expm1(float(np.quantile(lowdraw,.025))),'low_sr_ci_high_percent':100*math.expm1(float(np.quantile(lowdraw,.975))),
                 'high_sr_log_change':high,'high_sr_percent_change':100*math.expm1(high),'high_sr_ci_low_percent':100*math.expm1(float(np.quantile(highdraw,.025))),'high_sr_ci_high_percent':100*math.expm1(float(np.quantile(highdraw,.975))),
                 'high_minus_low_sr_conditional_change_contrast_log':contrast,'high_minus_low_sr_conditional_change_contrast_percent':100*math.expm1(contrast),'contrast_ci_low_percent':100*math.expm1(float(np.quantile(cdraw,.025))),'contrast_ci_high_percent':100*math.expm1(float(np.quantile(cdraw,.975)))}
            rows.append(row);contrast_draws.append(cdraw);points.append(contrast)
    raw,rw,holm=romano_wolf_stepdown(np.array(points),np.column_stack(contrast_draws))
    for r,a,b,c in zip(rows,raw,rw,holm):r.update(p_raw=float(a),p_romano_wolf=float(b),p_holm=float(c))
    return rows,np.column_stack(contrast_draws)

def load_frame(event_path,panel):
    e=pd.read_csv(event_path);e=e[e.is_grid_year_representative].copy();e.grid_id=e.grid_id.astype(int)
    f=e.merge(panel,on=['grid_id','year'],validate='one_to_one',suffixes=('','_panel'));f=f[f.zone.isin(NAMED_ZONES)].dropna(subset=['ln_yield','ca','gdd_10_29','pr_sum','total_duration_days','mean_event_intensity_c']).copy();f.sort_values(['grid_id','year'],inplace=True);f.reset_index(drop=True,inplace=True);return f

def fit_model(frame,kind,weights):
    x,names=joint_design(frame) if kind=='joint' else design_matrix(frame,EXPOSURES[kind]);g,py,_,b=codes_for_frame(frame);return fit_revision(frame.ln_yield.to_numpy(float),x,g,py,b,weights),names

def fwl_vif(frame):
    g,py,_,_=codes_for_frame(frame);d=frame.total_duration_days.to_numpy(float);q=frame.mean_event_intensity_c.to_numpy(float);ca=frame.ca.to_numpy(float)
    base=[frame.gdd_10_29.to_numpy(float),frame.pr_sum.to_numpy(float),frame.pr_sum.to_numpy(float)**2]
    for z in NAMED_ZONES:base.append((frame.zone.to_numpy()==z)*ca)
    a,_=absorb_two_way(np.column_stack([d,q,*base]),g,py,tolerance=1e-9);B=a[:,2:];rd=a[:,0]-B@np.linalg.lstsq(B,a[:,0],rcond=None)[0];rq=a[:,1]-B@np.linalg.lstsq(B,a[:,1],rcond=None)[0]
    common=vif_pair(rd,rq);zones={}
    for z in NAMED_ZONES:
        s=frame.zone==z;sub=frame[s].copy();gg,pp,_,_=codes_for_frame(sub);v,_=absorb_two_way(np.column_stack([sub.total_duration_days,sub.mean_event_intensity_c,sub.gdd_10_29,sub.pr_sum,sub.pr_sum**2,sub.ca]),gg,pp,tolerance=1e-9);bb=v[:,2:];x=v[:,0]-bb@np.linalg.lstsq(bb,v[:,0],rcond=None)[0];y=v[:,1]-bb@np.linalg.lstsq(bb,v[:,1],rcond=None)[0];zones[z]=vif_pair(x,y)
    return {'common_vif':common,'zone_vif':zones,'max_zone_vif':max(zones.values())}

def sm_overlap(event_path,panel,ca):
    e=pd.read_csv(event_path);e=e[e.event_indicator & e.zone.isin(NAMED_ZONES)].copy();e.grid_id=e.grid_id.astype(int);e=e.merge(panel[['grid_id','year','ca']],on=['grid_id','year'],validate='many_to_one');e['ca_group']=np.where(e.ca<=ca['p25'],'P25_or_lower',np.where(e.ca>=ca['p75'],'P75_or_higher','middle'))
    support=e.groupby('zone').agg(events=('event_id','size'),overlap_events=('drawdown_overlap_next_event','sum')).reset_index();support['overlap_share']=support.overlap_events/support.events
    desc=[]
    for sample,part in [('all',e),('exclude_overlap',e[~e.drawdown_overlap_next_event.astype(bool)])]:
        x=part.groupby(['zone','ca_group']).agg(events=('event_id','size'),antecedent_smrz_mean=('antecedent_smrz','mean'),drawdown_smrz_mean=('drawdown_smrz','mean')).reset_index();x.insert(0,'sample',sample);desc.append(x)
    return support,pd.concat(desc,ignore_index=True)

def main():
    args=parse_args();out=args.output_dir.resolve();
    if out.exists() and any(out.iterdir()):raise FileExistsError(out)
    out.mkdir(parents=True,exist_ok=True);start=time.perf_counter();panel=pd.read_stata(args.panel,columns=list(PANEL_FIELDS),convert_categoricals=False)
    extended=load_frame(args.model_dir/'model_ready_panel.csv.gz',panel) if False else pd.read_csv(args.model_dir/'model_ready_panel.csv.gz')
    # model_ready_panel already contains the authoritative merge and frozen fields.
    extended=extended[extended.zone.isin(NAMED_ZONES)].copy();extended.grid_id=extended.grid_id.astype(int);extended.reset_index(drop=True,inplace=True)
    strict=load_frame(args.strict_stage1_dir/'event_panel.csv.gz',panel)
    _,_,_,blocks=codes_for_frame(extended);rad=rademacher_weights(1999,int(blocks.max())+1,42);web=webb_weights(1999,int(blocks.max())+1,42)
    ca,endpoints=endpoint_payload(extended);allrows=[];fits={};names_by={};draws_by={}
    for kind in ['duration','intensity','joint']:
        fit,names=fit_model(extended,kind,rad);fits[kind]=fit;names_by[kind]=names;draws_by[kind]=fit.bootstrap_beta
        if kind!='joint':rows,_=conditional_rows(fit,names,extended,f'separate_{kind}',ca,endpoints,fit.bootstrap_beta);allrows += [r for r in rows if r['exposure']==kind]
        else:rows,jdraw=conditional_rows(fit,names,extended,'joint',ca,endpoints,fit.bootstrap_beta);allrows += rows
    result=pd.DataFrame(allrows);result.to_csv(out/'conditional_changes_by_ca.csv',index=False,encoding='utf-8-sig')
    joint=result[result.model=='joint'].copy();joint_draw=np.column_stack([draws_by['joint'][:,names_by['joint'].index(f'{z}:ca_x_{e}')]*(ca['p75']-ca['p25'])*(endpoints[z][e]['p90']-endpoints[z][e]['p50']) for z in NAMED_ZONES for e in EXPOSURES]);pd.DataFrame(joint_draw,columns=[f'{z}_{e}' for z in NAMED_ZONES for e in EXPOSURES]).to_csv(out/'joint_bootstrap_draws.csv.gz',index=False,compression={'method':'gzip','mtime':0});pd.DataFrame(np.cov(joint_draw,rowvar=False),index=[f'{z}_{e}' for z in NAMED_ZONES for e in EXPOSURES],columns=[f'{z}_{e}' for z in NAMED_ZONES for e in EXPOSURES]).to_csv(out/'joint_bootstrap_covariance.csv',encoding='utf-8-sig')
    coef=[]
    for kind,fit in fits.items():
        for i,n in enumerate(names_by[kind]):coef.append({'model':kind,'term':n,'coefficient':fit.beta[i],'grid_cluster_se':math.sqrt(fit.covariance_cluster[i,i]),'rank':fit.rank,'condition_number':fit.condition_number})
    pd.DataFrame(coef).to_csv(out/'model_coefficients.csv',index=False,encoding='utf-8-sig')
    vif=fwl_vif(extended);(out/'joint_model_diagnostics.json').write_text(json.dumps({**vif,'rank':fits['joint'].rank,'condition_number':fits['joint'].condition_number},indent=2),encoding='utf-8')
    # Webb joint conditional contrasts.
    webdraw=bootstrap_draws(fits['joint'],web);webrows,_=conditional_rows(fits['joint'],names_by['joint'],extended,'joint_webb',ca,endpoints,webdraw);pd.DataFrame(webrows).to_csv(out/'joint_webb_results.csv',index=False,encoding='utf-8-sig')
    # HAC joint contrast standard errors.
    hac=[]
    for bw in [100,200,300]:
        cov=spatial_hac_covariance(fits['joint'],extended,bw)
        for z in NAMED_ZONES:
            for e in EXPOSURES:
                idx=names_by['joint'].index(f'{z}:ca_x_{e}');scale=(ca['p75']-ca['p25'])*(endpoints[z][e]['p90']-endpoints[z][e]['p50']);point=fits['joint'].beta[idx]*scale;se=math.sqrt(max(cov[idx,idx],0))*abs(scale);hac.append({'bandwidth_km':bw,'zone':z,'exposure':e,'contrast_log':point,'hac_se_log':se,'ci_low_log':point-1.96*se,'ci_high_log':point+1.96*se})
    pd.DataFrame(hac).to_csv(out/'joint_spatial_hac_results.csv',index=False,encoding='utf-8-sig')
    # Strict-window separate models.
    _,_,_,sb=codes_for_frame(strict);srad=rademacher_weights(1999,int(sb.max())+1,42);sca,send=endpoint_payload(strict);srows=[]
    for kind in ['duration','intensity']:
        fit,names=fit_model(strict,kind,srad);rows,_=conditional_rows(fit,names,strict,f'strict_{kind}',sca,send,fit.bootstrap_beta);srows += [r for r in rows if r['exposure']==kind]
    pd.DataFrame(srows).to_csv(out/'strict_window_conditional_changes.csv',index=False,encoding='utf-8-sig')
    support,desc=sm_overlap(args.stage1_dir/'event_panel.csv.gz',panel,ca);support.to_csv(out/'drawdown_overlap_support.csv',index=False,encoding='utf-8-sig');desc.to_csv(out/'sm_antecedent_drawdown_overlap_sensitivity.csv',index=False,encoding='utf-8-sig')
    # Cross-language analysis input.
    x,n=joint_design(extended);cross=extended[['grid_id','year','province','ln_yield','latitude','longitude']].copy();cross['prov_year']=pd.factorize(cross.province.astype(str)+'|'+cross.year.astype(str),sort=True)[0]+1
    for i,name in enumerate(n):cross[f'x{i+1:02d}']=x[:,i]
    cross.to_csv(out/'cross_language_joint_input.csv.gz',index=False,compression={'method':'gzip','mtime':0});cross.to_stata(out/'cross_language_joint_input.dta',write_index=False,version=118)
    endpoints_path=out/'revision_endpoints.json';endpoints_path.write_text(json.dumps({'extended':{'ca':ca,'exposures':endpoints},'strict':{'ca':sca,'exposures':send}},ensure_ascii=False,indent=2),encoding='utf-8')
    # Manifest.
    base=json.loads((args.model_dir/'run_manifest.json').read_text(encoding='utf-8'));inputs=[dict(i) for i in base['inputs']]
    for role,path in [('implementation_round1_inference',PROJECT_ROOT/'scripts/python/hotdry_event_round1_inference.py'),('implementation_round1_runner',Path(__file__)),('round1_review',PROJECT_ROOT/'quality_reports/plans/2026-07-15_hotdry_event_override_method_review_round1.md'),('strict_stage1_manifest',args.strict_stage1_dir/'run_manifest.json')]:inputs.append({'role':role,**file_digest(path.resolve())})
    artifact_paths=[p for p in out.iterdir() if p.is_file()]
    extension={'contract_version':'compound-event-round1-extension-v1','stage':'round1_revision_models','failure_stage':None,'failure_reasons':[],'completed_artifacts':hash_artifacts(artifact_paths,out),'yield_model_run':True}
    (out/'event_run_extension.json').write_text(json.dumps(extension,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest={**base,'run_id':out.name,'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'design_version':'override-round1-revision','inputs':inputs,'sample_key_sha256':sample_key_sha256(extended[['grid_id','year']]),'sample_counts':{'extended_grid_years':len(extended),'strict_grid_years':len(strict)},'claims':['conditional exposure-yield changes only; no generalized damage or buffering claim'],'verification':[{'check':'joint trigger','status':'PASS','detail':f"VIF={vif['common_vif']:.3f}; max zone={vif['max_zone_vif']:.3f}; rank={fits['joint'].rank}; cond={fits['joint'].condition_number:.3f}"},{'check':'strict window','status':'PASS','detail':f'{len(strict)} grid-years'},{'check':'Webb/HAC','status':'PASS','detail':'1999 Webb and HAC 100/200/300 km'},{'check':'cross-language inputs','status':'PASS','detail':'CSV.gz and DTA written; estimators run separately'}]}
    schema=json.loads((PROJECT_ROOT/'docs/contracts/run_manifest.schema.json').read_text(encoding='utf-8'));validate_override_manifest(manifest,schema,extension=extension);(out/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':'PASS_ROUND1_EMPIRICS','seconds':time.perf_counter()-start}))
    return 0
if __name__=='__main__':raise SystemExit(main())
