#!/usr/bin/env python3
"""Hand-in entrypoint for The Daily Atlas (round 4).

The artwork is finished ahead of time by draw.py and committed
next to this file as entry.png. All this script does at run time
is deliver that file into the output directory named by the
MAKEFUN_OUTPUT_DIR environment variable (falling back to /output
when the variable is not set). Standard library only.
"""
import os
import shutil


def deliver_entry():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    shutil.copyfile(os.path.join(here, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    deliver_entry()
