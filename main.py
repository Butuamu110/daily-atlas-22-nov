#!/usr/bin/env python3
"""Hand-in entrypoint for The Daily Atlas (round 3).

The finished artwork lives beside this file as entry.png (produced
earlier by draw.py). At grading time this script simply delivers that
committed file into the directory named by the MAKEFUN_OUTPUT_DIR
environment variable, falling back to /output when it is unset.
Standard library only.
"""
import os
import shutil
from pathlib import Path


def deliver() -> None:
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent / "entry.png"
    shutil.copyfile(source, target_dir / "entry.png")


if __name__ == "__main__":
    deliver()
