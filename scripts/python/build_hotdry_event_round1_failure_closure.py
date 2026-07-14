"""Inventory partial Round-1 runs without modifying their historical directories."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json
from pathlib import Path

def item(path:Path)->dict[str,object]:
 data=path.read_bytes();return {'path':str(path).replace('\\','/'),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();out=a.output_dir.resolve()
 if out.exists() and any(out.iterdir()):raise FileExistsError(out)
 out.mkdir(parents=True,exist_ok=True)
 failures=[]
 specs=[
  ('2026-07-15_compound_event_override_round1_revision_v1','partial results written before strict-window conditional-change layout failure; no traceback file was emitted'),
  ('2026-07-15_compound_event_override_round1_revision_v2','ValueError from list.index while strict separate-model columns were incorrectly treated as joint layout; traceback was console-only'),
  ('2026-07-15_compound_event_override_cross_language_validation_v1','KeyError abs_coef_diff_python_r because the closure builder expected derived columns absent from the comparison CSV; traceback was console-only'),
 ]
 for run_id,reason in specs:
  directory=root/'temp'/run_id
  files=[item(x) for x in sorted(directory.glob('*')) if x.is_file()]
  failures.append({'run_id':run_id,'status':'PARTIAL_FAILED','reason':reason,'files':files,'implementation_identity_note':'exact pre-fix uncommitted source identity was not preserved; current source must not be attributed to this failed run'})
 record={'canonical_id':'compound-event-intensity-duration-override-v1','created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'failures':failures,'non_overwrite_statement':'historical directories were read only and remain unchanged'}
 rp=out/'round1_failure_inventory.json';rp.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 manifest={'contract_version':'run-manifest-v1','canonical_id':record['canonical_id'],'run_id':out.name,'created_utc':record['created_utc'],'status':'STOP','not_for_inference':True,'design_version':'round1-partial-failure-closure-v1','inputs':[entry for f in failures for entry in f['files']],'outputs':[item(rp)],'claims':['failure inventory only; not an inferential run']}
 (out/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');return 0
if __name__=='__main__':raise SystemExit(main())
