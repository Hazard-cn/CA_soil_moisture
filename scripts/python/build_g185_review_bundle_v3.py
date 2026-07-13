"""Rebuild the G185 v3 review bundle from an existing run directory."""

from __future__ import annotations

from run_all_g185_v3 import build_bundle, write_checksums


def main() -> None:
    write_checksums()
    build_bundle()
    print("g185_v3_review_bundle.zip rebuilt")


if __name__ == "__main__":
    main()

