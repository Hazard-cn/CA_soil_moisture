"""Render the three Round-1 revised main figures and a self-contained HTML gallery."""
from __future__ import annotations
import argparse,base64,hashlib,json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
def digest(p):return {'path':str(p).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(fig,p):fig.tight_layout();fig.savefig(p,dpi=300,facecolor='white');plt.close(fig)
def main():
 a=argparse.ArgumentParser();a.add_argument('--revision-dir',type=Path,required=True);a.add_argument('--recovery-dir',type=Path,required=True);a.add_argument('--scaled-recovery-dir',type=Path,required=True);a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--html-output',type=Path,required=True);a.add_argument('--markdown-output',type=Path,required=True);x=a.parse_args();out=x.output_dir.resolve();
 if out.exists() and any(out.iterdir()):raise FileExistsError(out)
 out.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.family':'sans-serif','font.size':9})
 d=pd.read_csv(x.revision_dir/'conditional_changes_by_ca.csv');d=d[d.model=='joint'].copy();order=[(z,e) for z in ['NE','HHH','NW','SW','SH'] for e in ['duration','intensity']];d['o']=d.apply(lambda r:order.index((r.zone,r.exposure)),axis=1);d=d.sort_values('o',ascending=False);y=np.arange(len(d));labels=[f'{r.zone}-{r.exposure}' for r in d.itertuples()]
 fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1.35,1]});
 for col,label,color,off in [('low_sr','CA P25','#4c78a8',-.14),('high_sr','CA P75','#e45756',.14)]:
  p=d[f'{col}_percent_change'];lo=d[f'{col}_ci_low_percent'];hi=d[f'{col}_ci_high_percent'];ax1.errorbar(p,y+off,xerr=np.vstack([p-lo,hi-p]),fmt='o',label=label,color=color,capsize=2)
 ax1.axvline(0,color='black',lw=.8);ax1.set_yticks(y,labels);ax1.set_xlabel('Conditional P50-to-P90 yield change (%)');ax1.legend(frameon=False);ax1.grid(axis='x',color='#ddd',lw=.5)
 p=d.high_minus_low_sr_conditional_change_contrast_percent;lo=d.contrast_ci_low_percent;hi=d.contrast_ci_high_percent;ax2.errorbar(p,y,xerr=np.vstack([p-lo,hi-p]),fmt='o',color='#2f4b7c',capsize=2);ax2.axvline(0,color='black',lw=.8);ax2.set_yticks(y,[]);ax2.set_xlabel('High-minus-low SR contrast (%)');ax2.grid(axis='x',color='#ddd',lw=.5);f1=out/'fig1_conditional_changes_and_contrast.png';save(fig,f1)
 sm=pd.read_csv(x.revision_dir/'sm_antecedent_drawdown_overlap_sensitivity.csv');sm=sm[(sm.ca_group.isin(['P25_or_lower','P75_or_higher']))].copy();zones=['NE','HHH','NW','SW','SH'];fig,(a1,a2)=plt.subplots(1,2,figsize=(12,5));
 for ax,var,title in [(a1,'antecedent_smrz_mean','Antecedent SMrz'),(a2,'drawdown_smrz_mean','SMrz drawdown')]:
  xx=np.arange(5);width=.18
  for j,(sample,hatch) in enumerate([('all',''),('exclude_overlap','//')]):
   for k,(group,color) in enumerate([('P25_or_lower','#72b7b2'),('P75_or_higher','#e45756')]):
    q=sm[(sm['sample']==sample)&(sm.ca_group==group)].set_index('zone').loc[zones,var];ax.bar(xx+(j*2+k-1.5)*width,q,width,color=color,hatch=hatch,edgecolor='white',label=f'{sample}: {group}' if ax is a1 else None)
  ax.set_xticks(xx,zones);ax.set_title(title);ax.grid(axis='y',color='#ddd',lw=.5)
 a1.set_ylabel('m3/m3');a1.legend(frameon=False,fontsize=7);f2=out/'fig2_antecedent_drawdown_overlap.png';save(fig,f2)
 # Re-render recovery curves from the frozen machine table.
 c=pd.read_csv(x.recovery_dir/'standardized_recovery_curves.csv');fig,axes=plt.subplots(1,5,figsize=(12,5),sharey=True)
 for ax,z in zip(axes,zones):
  for level,color in [('P25','#4c78a8'),('P75','#e45756')]:
   q=c[(c.zone==z)&(c.ca_level==level)];ax.plot(q.follow_day,q.survival,color=color,label=f'CA {level}');ax.fill_between(q.follow_day,q.ci_low,q.ci_high,color=color,alpha=.15,lw=0)
  ax.set_title(z);ax.set_xlabel('Day');ax.grid(color='#ddd',lw=.5)
 axes[0].set_ylabel('P(not recovered after day t)');axes[-1].legend(frameon=False);f3=out/'fig3_fixed_ipcw_recovery_curves.png';save(fig,f3)
 captions=['Fig. 1. Joint-model CA P25/P75 conditional changes and neutral high-minus-low contrast.','Fig. 2. Antecedent SMrz and drawdown, full sample and excluding overlap with the next event; descriptive only.','Fig. 3. Fixed-IPCW one-step standardized recovery curves; intervals do not propagate censor-model estimation uncertainty.']
 imgs=[]
 for p,cap in zip([f1,f2,f3],captions):imgs.append(f'<h2>{cap}</h2><img src="data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()}" style="width:100%;max-width:1200px">')
 x.html_output.write_text('<!doctype html><meta charset="utf-8"><title>Event override Round-1 figures</title><style>body{font-family:Arial,sans-serif;margin:2rem auto;max-width:1250px}h2{font-size:1rem}</style>'+''.join(imgs),encoding='utf-8')
 manifest={'canonical_id':'compound-event-intensity-duration-override-v1','run_id':out.parent.name,'renderer':digest(Path(__file__).resolve()),'inputs':[digest((x.revision_dir/'run_manifest.json').resolve()),digest((x.revision_dir/'conditional_changes_by_ca.csv').resolve()),digest((x.revision_dir/'sm_antecedent_drawdown_overlap_sensitivity.csv').resolve()),digest((x.recovery_dir/'run_manifest.json').resolve()),digest((x.recovery_dir/'standardized_recovery_curves.csv').resolve()),digest((x.scaled_recovery_dir/'run_manifest.json').resolve()),digest((x.scaled_recovery_dir/'rmst30_scaled_results.csv').resolve())],'figures':[digest(f1),digest(f2),digest(f3)],'html':digest(x.html_output.resolve()),'markdown':digest(x.markdown_output.resolve()),'specification':{'width_inches':12,'height_inches':5,'dpi':300,'background':'white','font':'sans-serif'}};(out.parent/'report_run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');return 0
if __name__=='__main__':raise SystemExit(main())
