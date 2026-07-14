"""Create a non-overwriting closure run for failed models and historical smoke v2."""
from __future__ import annotations
import argparse,datetime as dt,json,subprocess,sys
from pathlib import Path
import pandas as pd
PROJECT_ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(PROJECT_ROOT/'scripts/python'))
from hotdry_event_override_validators import validate_override_manifest
from run_hotdry_event_stage1 import file_digest,hash_artifacts
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--model-v1',type=Path,required=True);p.add_argument('--model-v2',type=Path,required=True);p.add_argument('--historical-smoke-v2',type=Path,required=True);p.add_argument('--override-smoke',type=Path,required=True);a=p.parse_args();out=a.output_dir.resolve();
 if out.exists() and any(out.iterdir()):raise FileExistsError(out)
 out.mkdir(parents=True,exist_ok=True);base=json.loads((a.override_smoke/'run_manifest.json').read_text(encoding='utf-8'));inputs=[dict(x) for x in base['inputs']]
 inventory=[]
 for label,root in [('models_v1',a.model_v1),('models_v2',a.model_v2),('historical_smoke_v2',a.historical_smoke_v2),('override_smoke',a.override_smoke)]:
  for f in sorted(root.iterdir()):
   if f.is_file():inventory.append({'bundle':label,'role':f'{label}_{f.name}','digest':file_digest(f.resolve())})
 for item in inventory:inputs.append({'role':item['role'],**item['digest']})
 old=pd.read_csv(a.historical_smoke_v2/'event_panel.csv.gz');new=pd.read_csv(a.override_smoke/'event_panel.csv.gz');pd.testing.assert_frame_equal(old,new,check_dtype=False)
 comparison={'historical_v2_rows':len(old),'override_rows':len(new),'field_count':len(old.columns),'equal_all_fields':True,'historical_manifest_sha256':file_digest(a.historical_smoke_v2/'run_manifest.json')['sha256'],'override_manifest_sha256':file_digest(a.override_smoke/'run_manifest.json')['sha256']}
 cp=out/'historical_v2_comparison.json';cp.write_text(json.dumps(comparison,indent=2),encoding='utf-8');ip=out/'closure_inventory.json';ip.write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
 extension={'contract_version':'compound-event-failure-closure-extension-v1','stage':'failure_identity_closure','failure_stage':'historical models v1/v2','failure_reasons':['models v1 numerical absorption failure','models v2 plotting environment failure after partial outputs'],'completed_artifacts':hash_artifacts([cp,ip],out),'yield_model_run':False};(out/'event_run_extension.json').write_text(json.dumps(extension,ensure_ascii=False,indent=2),encoding='utf-8')
 m={**base,'run_id':out.name,'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'STOP','not_for_inference':True,'design_version':'failure-closure-v1','inputs':inputs,'claims':[],'stop_rules_triggered':extension['failure_reasons'],'verification':[{'check':'models v1/v2 content inventory','status':'PASS','detail':f'{len(inventory)} files hashed without modifying source directories'},{'check':'historical smoke v2 equality','status':'PASS','detail':f'{len(old)} rows x {len(old.columns)} fields equal'}]}
 schema=json.loads((PROJECT_ROOT/'docs/contracts/run_manifest.schema.json').read_text(encoding='utf-8'));validate_override_manifest(m,schema,extension=extension);(out/'run_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');return 0
if __name__=='__main__':raise SystemExit(main())
