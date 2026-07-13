"""
run_all.py — Run the complete data build pipeline
Author: Data Build Pipeline
Date: 2026-03-28
"""

import subprocess
import sys
import time

scripts = [
    ("s01_load_phenology.py", "Load phenology & build panel windows"),
    ("s02_calc_temp_windows.py", "Temperature window aggregation"),
    ("s03_calc_precip_windows.py", "Precipitation window aggregation"),
    ("s04a_calc_sm_gleam.py", "GLEAM SM window aggregation"),
    ("s04d_calc_sm_gleam_rework.py", "GLEAM SM rework aggregation"),
    ("s04b_calc_sm_swsm.py", "SWSM SM window aggregation"),
    ("s04c_calc_sm_era5land.py", "ERA5-Land SM window aggregation"),
    ("s05_calc_et0_windows.py", "ET0 window aggregation"),
    ("s06_calc_vpd_spei.py", "VPD/SPEI window aggregation"),
    ("s07_calc_compound.py", "Compound stress indicators"),
    ("s08_merge_panel.py", "Merge all into final panel"),
    ("fix_pseudo_zeros.py", "Propagate NaN into pseudo-zero indicators"),
    ("s09_quality_check.py", "Data quality check"),
    ("s10_export.py", "Export v3 phenowindows/main/noyield"),
    ("gen_data_dictionary.py", "Generate v3 data dictionary"),
]

def main():
    print("=" * 70)
    print("DATA BUILD PIPELINE — Full Run")
    print("=" * 70)

    t0 = time.time()
    for i, (script, desc) in enumerate(scripts, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(scripts)}] {desc} ({script})")
        print(f"{'='*70}")

        result = subprocess.run(
            [sys.executable, f"scripts/python/{script}"],
            cwd="C:/YangSu/00_Project/CA_mechanism/regression_SR/data_build"
        )

        if result.returncode != 0:
            print(f"\nERROR: {script} failed with return code {result.returncode}")
            print("Pipeline stopped.")
            sys.exit(1)

    total = time.time() - t0
    print(f"\n{'='*70}")
    print(f"PIPELINE COMPLETE — Total time: {total:.0f}s ({total/60:.1f} min)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
