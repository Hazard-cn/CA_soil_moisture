"""Export a compact Stata panel for final story-line verification."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from expanded_scale_story_search import add_full_interactions, load_panel, unique_variants  # noqa: E402


OUT_DIR = PROJ / "temp/2026-06-18_story_stata_verify"
OUT_DTA = OUT_DIR / "story_verify_panel.dta"
MANIFEST = OUT_DIR / "story_verify_panel_manifest.csv"
SCALES = ("G057", "G185")

KEEP_COLS = [
    "grid_code",
    "year_code",
    "ln_yield_raw",
    "D_full_raw",
    "W_full_raw",
    "hdd_ge32_raw",
    "HotDryPr_full_raw",
    "ca_raw",
    "SR_x_D_full_raw",
    "SR_x_Heat_full_raw",
    "SR_x_HotDryPr_full_raw",
    "gleam_smrz_mean_raw",
    "pr_sum_raw",
    "et0_sum_raw",
    "gdd_10_30_raw",
    "irr_frac_raw",
    "aridity_raw",
    "drought_x_irr",
    "heat_x_irr",
    "hotdry_x_irr",
    "SR_x_irr",
    "SR_x_drought_x_irr",
    "SR_x_heat_x_irr",
    "SR_x_hotdry_x_irr",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = add_full_interactions(load_panel())
    variants = {str(meta["sample_id"]): meta for meta in unique_variants(panel)}
    manifest_rows = []
    for scale in SCALES:
        if scale not in variants:
            raise KeyError(scale)
        mask = variants[scale]["mask"]
        panel[f"sample_{scale}"] = mask.astype("int8")
        manifest_rows.append(
            {
                key: value
                for key, value in variants[scale].items()
                if key != "mask"
            }
        )
    cols = KEEP_COLS + [f"sample_{scale}" for scale in SCALES]
    out = panel.loc[:, cols].copy()
    for col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out.to_stata(OUT_DTA, write_index=False, version=118)
    pd.DataFrame(manifest_rows).to_csv(MANIFEST, index=False, encoding="utf-8-sig")
    print({"dta": str(OUT_DTA), "rows": int(len(out)), "cols": int(len(out.columns))})


if __name__ == "__main__":
    main()
