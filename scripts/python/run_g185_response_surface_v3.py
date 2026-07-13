"""Response-surface module entrypoint.

Use `run_all_g185_v3.py` for the complete reproducible run. This wrapper runs
the full pipeline in quick mode so the response-surface module can be smoke
tested independently.
"""

from __future__ import annotations

from run_all_g185_v3 import run


if __name__ == "__main__":
    run("quick")

