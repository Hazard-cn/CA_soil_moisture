"""Configuration for the G185 response-surface v3 run."""

from __future__ import annotations

from pathlib import Path


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ / "quality_reports/agent_runs/2026-06-20_g185_response_surface_v3"
FIGURE_DATA_DIR = RUN_DIR / "figure_data"
FIGURE_DIR = RUN_DIR / "figures"
PREFLIGHT_DIR = RUN_DIR / "preflight"
LOG_DIR = RUN_DIR / "logs"
BUNDLE_PATH = PROJ / "g185_v3_review_bundle.zip"

SEED = 20260620
SCALE_ID = "G185"
REGIONS = ("NE", "HHH", "NW", "SW", "SH")
SCENARIOS = ("DROUGHT_COMMON", "HEAT_COMMON", "JOINT_COMMON")

CLAIMS = {
    "C1_NE_DROUGHT_SURFACE": ("NE", "DROUGHT_COMMON"),
    "C2_HHH_HEAT_SURFACE": ("HHH", "HEAT_COMMON"),
    "C3_HHH_JOINT_SURFACE": ("HHH", "JOINT_COMMON"),
    "C3B_HHH_HOTDRY_VALIDATION": ("HHH", "HOTDRY_COMMON"),
    "C4_HHH_IRRIGATION_BOUNDARY": ("HHH", "IRRIGATION_BOUNDARY"),
    "C5_SOIL_MOISTURE_CONSISTENCY": ("ALL", "SOIL_MOISTURE_CONSISTENCY"),
}

REQUIRED_FIELDS = (
    "grid_id",
    "year",
    "maize_zone",
    "province",
    "latitude",
    "longitude",
    "yield_tons_ha",
    "ln_yield_raw",
    "ca_raw",
    "D_full_raw",
    "W_full_raw",
    "hdd_ge32_raw",
    "HotDryPr_full_raw",
    "gleam_smrz_mean_raw",
    "gleam_sms_mean_raw",
    "irr_frac_raw",
    "aridity_raw",
    "pr_sum_raw",
    "et0_sum_raw",
    "gdd_10_30_raw",
)

C0_CONTROLS = ("W_full_raw", "gdd_10_30_raw")
C1_CONTROLS = (
    "W_full_raw",
    "pr_sum_raw",
    "et0_sum_raw",
    "gdd_10_30_raw",
    "irr_frac_raw",
    "aridity_raw",
)

PROHIBITED_TEXT = (
    "causal effect of straw return",
    "causal mediation",
    "G185 scale",
    "ranking 2",
    "selected from 256 scales",
)

