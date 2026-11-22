#!/usr/bin/env python3
"""Hand-in entrypoint: copies the committed entry.png to the output dir.

The artwork is built ahead of time by draw.py and committed as
entry.png; this file only performs the copy, using the
MAKEFUN_OUTPUT_DIR environment variable (never a hardcoded path).
Standard library only.
"""
import os
import shutil
from pathlib import Path


def main() -> None:
    out_dir = Path(os.environ["MAKEFUN_OUTPUT_DIR"])
    out_dir.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).resolve().parent / "entry.png"
    shutil.copyfile(src, out_dir / "entry.png")


if __name__ == "__main__":
    main()
