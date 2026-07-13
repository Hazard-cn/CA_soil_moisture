from pathlib import Path

import pandas as pd


PROJDIR = Path(r"C:\YangSu\00_Project\CA_mechanism\regression_SR")
PARQUET_PATH = PROJDIR / "data_build" / "data" / "processed" / "data_v3_main.parquet"
OUT_PATH = PROJDIR / "temp" / "2026-04-23_newSMsplit" / "v6gleambl_md_event_sidecar.dta"


WINDOW_CODE = {
    "v3pre30": "p30",
    "v3he": "v3h",
    "hema": "hma",
    "fullnew": "fn",
}

SOURCE_CODE = {
    "gleam_sms": "gss",
    "gleam_smrz": "gsr",
}

DRY_STUB = {
    "mdduration_dry": "mdd_d",
    "mddurshare_dry": "mds_d",
    "mdseverity_dry": "mdv_d",
}

WET_STUB = {
    "mdduration_wet": "mdd_w",
    "mddurshare_wet": "mds_w",
    "mdseverity_wet": "mdv_w",
}


def build_alias_map() -> dict[str, str]:
    alias = {}
    for family, stub in DRY_STUB.items():
        for source, src_code in SOURCE_CODE.items():
            for window, win_code in WINDOW_CODE.items():
                orig = f"{family}_{source}_{window}"
                alias[orig] = f"{stub}_{src_code}_{win_code}"
    for family, stub in WET_STUB.items():
        for source, src_code in SOURCE_CODE.items():
            for window, win_code in WINDOW_CODE.items():
                orig = f"{family}_{source}_{window}"
                alias[orig] = f"{stub}_{src_code}_{win_code}"
    return alias


def main() -> None:
    alias_map = build_alias_map()
    cols = ["grid_id", "year", *alias_map.keys()]
    df = pd.read_parquet(PARQUET_PATH, columns=cols)
    df = df.rename(columns=alias_map)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_stata(OUT_PATH, write_index=False, version=118)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
