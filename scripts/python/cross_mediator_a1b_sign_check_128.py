"""
Cross-mediator sign check for mechanism legs a1 and b.

Scope:
- fixed sample base: main_sample == 1 and ggcp10_maize_frac >= 0.05
- 128 unique parallel-rule variants
- full-season hazards only, no window screen
- mediators: mean_root and dry_mdf_p10_sfc
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ggcp10_parallel_rules_69038_search import fit_fe_ols, load_panel, rhs_for
from bio_window_filter_128 import OUT_DIR, unique_variants


PREFIX = "cross_mediator_a1b_sign_128"
MEDIATORS = {
    "mean_root": ("mean", "gleam_smrz_mean"),
    "dry_mdf_p10_sfc": ("dry", "v6mdf_p10_fn_gss"),
}
HAZARDS = ("drought", "heat", "hotdry")
TRANSFORMS = ("raw", "w")


def expected_signs(mediator_tag: str) -> tuple[int, int]:
    if mediator_tag == "mean_root":
        return -1, 1
    if mediator_tag == "dry_mdf_p10_sfc":
        return 1, -1
    raise ValueError(mediator_tag)


def sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def main() -> None:
    df = load_panel()
    variants = unique_variants(df)
    rows: list[dict[str, object]] = []

    for i, meta in enumerate(variants, start=1):
        sub = df.loc[meta["mask"]].copy()
        for transform in TRANSFORMS:
            sx = "w" if transform == "w" else "raw"
            for hazard in HAZARDS:
                for mediator_tag, (branch, mediator_base) in MEDIATORS.items():
                    mediator = f"{mediator_base}_{sx}"
                    y, ca, mediator_rhs, outcome_rhs, hazard_var, sr_var = rhs_for(hazard, sx, mediator)
                    mres = fit_fe_ols(sub, mediator, mediator_rhs)
                    yres = fit_fe_ols(sub, y, outcome_rhs)
                    a1 = mres[f"b:{hazard_var}"]
                    a1_p = mres[f"p:{hazard_var}"]
                    b = yres[f"b:{mediator}"]
                    b_p = yres[f"p:{mediator}"]
                    ea1, eb = expected_signs(mediator_tag)
                    rows.append(
                        {
                            "sample_id": meta["sample_id"],
                            "transform": "winsor_1_99" if sx == "w" else "raw",
                            "hazard": hazard,
                            "branch": branch,
                            "mediator_tag": mediator_tag,
                            "mediator": mediator,
                            "a1": a1,
                            "a1_p": a1_p,
                            "b": b,
                            "b_p": b_p,
                            "a1_sign": sign(a1),
                            "b_sign": sign(b),
                            "expected_a1_sign": ea1,
                            "expected_b_sign": eb,
                            "expected_pair_pass": bool(sign(a1) == ea1 and sign(b) == eb),
                            "expected_pair_sig005": bool(sign(a1) == ea1 and a1_p < 0.05 and sign(b) == eb and b_p < 0.05),
                            "ie_sign": sign(a1 * b),
                            "ie_negative": bool(a1 * b < 0),
                            "a1_sig005": bool(a1_p < 0.05),
                            "b_sig005": bool(b_p < 0.05),
                            "N_sample": meta["N_sample"],
                            "N_model_m": int(mres["N"]),
                            "N_model_y": int(yres["N"]),
                            "N_grids_sample": meta["N_grids_sample"],
                            "N_grids_m": int(mres["clusters"]),
                            "N_grids_y": int(yres["clusters"]),
                            **{k: meta[k] for k in meta if k not in ("mask", "sample_id", "N_sample", "N_grids_sample")},
                        }
                    )
        if i % 16 == 0:
            print(f"processed {i}/{len(variants)} variants")

    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / f"{PREFIX}_detail.csv", index=False, encoding="utf-8-sig")

    summary = (
        out.groupby(["hazard", "transform", "mediator_tag"])
        .agg(
            n=("sample_id", "size"),
            expected_pair_pass=("expected_pair_pass", "sum"),
            expected_pair_sig005=("expected_pair_sig005", "sum"),
            ie_negative=("ie_negative", "sum"),
            a1_expected_sign=("a1_sign", lambda s: int((s == out.loc[s.index, "expected_a1_sign"]).sum())),
            b_expected_sign=("b_sign", lambda s: int((s == out.loc[s.index, "expected_b_sign"]).sum())),
            a1_sig005=("a1_sig005", "sum"),
            b_sig005=("b_sig005", "sum"),
            a1_median=("a1", "median"),
            b_median=("b", "median"),
        )
        .reset_index()
    )
    summary.to_csv(OUT_DIR / f"{PREFIX}_summary.csv", index=False, encoding="utf-8-sig")

    paired = (
        out.pivot_table(
            index=["sample_id", "hazard", "transform"],
            columns="mediator_tag",
            values=["expected_pair_pass", "expected_pair_sig005", "ie_negative", "a1", "b"],
            aggfunc="first",
        )
        .reset_index()
    )
    paired.columns = ["_".join([str(x) for x in col if str(x) != ""]).strip("_") for col in paired.columns]
    paired["both_expected_pair_pass"] = paired["expected_pair_pass_mean_root"].astype(bool) & paired[
        "expected_pair_pass_dry_mdf_p10_sfc"
    ].astype(bool)
    paired["both_expected_pair_sig005"] = paired["expected_pair_sig005_mean_root"].astype(bool) & paired[
        "expected_pair_sig005_dry_mdf_p10_sfc"
    ].astype(bool)
    paired["both_ie_negative"] = paired["ie_negative_mean_root"].astype(bool) & paired[
        "ie_negative_dry_mdf_p10_sfc"
    ].astype(bool)
    paired.to_csv(OUT_DIR / f"{PREFIX}_paired.csv", index=False, encoding="utf-8-sig")

    paired_summary = (
        paired.groupby(["hazard", "transform"])
        .agg(
            n=("sample_id", "size"),
            both_expected_pair_pass=("both_expected_pair_pass", "sum"),
            both_expected_pair_sig005=("both_expected_pair_sig005", "sum"),
            both_ie_negative=("both_ie_negative", "sum"),
        )
        .reset_index()
    )
    paired_summary.to_csv(OUT_DIR / f"{PREFIX}_paired_summary.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Cross-mediator a1/b sign check, 128 variants",
        "",
        "固定样本：`main_sample == 1` 且 `ggcp10_maize_frac >= 0.05`；其余 8 个规则平行组合去重为 128 个样本版本。",
        "窗口维度不参与；hazard 使用 full-season 定义。",
        "",
        "语义一致性定义：`mean_root` 预期 `a1<0, b>0`；`dry_mdf_p10_sfc` 预期 `a1>0, b<0`。",
        "两者符号相反但语义一致；共同含义是 hazard 经由水分状态给出负向 IE。",
        "",
        "## Paired summary",
        "",
        "| hazard | transform | both expected signs | both expected signs p<0.05 | both IE negative |",
        "|---|---|---:|---:|---:|",
    ]
    for r in paired_summary.to_dict("records"):
        lines.append(
            f"| {r['hazard']} | {r['transform']} | {int(r['both_expected_pair_pass'])}/128 | "
            f"{int(r['both_expected_pair_sig005'])}/128 | {int(r['both_ie_negative'])}/128 |"
        )
    lines.extend(
        [
            "",
            "## By mediator",
            "",
            "| hazard | transform | mediator | expected signs | expected signs p<0.05 | IE negative | median a1 | median b |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for r in summary.to_dict("records"):
        lines.append(
            f"| {r['hazard']} | {r['transform']} | {r['mediator_tag']} | "
            f"{int(r['expected_pair_pass'])}/128 | {int(r['expected_pair_sig005'])}/128 | "
            f"{int(r['ie_negative'])}/128 | {r['a1_median']:.6g} | {r['b_median']:.6g} |"
        )
    lines.extend(
        [
            "",
            "## Output files",
            "",
            f"- `{PREFIX}_detail.csv`",
            f"- `{PREFIX}_summary.csv`",
            f"- `{PREFIX}_paired.csv`",
            f"- `{PREFIX}_paired_summary.csv`",
            f"- `{PREFIX}_summary.md`",
            "",
        ]
    )
    (OUT_DIR / f"{PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
