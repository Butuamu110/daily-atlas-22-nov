#!/usr/bin/env python3
"""Hand-in program for THE DAILY ATLAS (news-image-20261122,
@rojanon11 / GitHub @Butuamu110).

The graded artifact is the finished page in entry.png, committed
beside this file and produced by draw.py (duel-winning layout A,
flat 2D). This program's whole job is delivery: it copies that
committed PNG into the directory the grader names through the
MAKEFUN_OUTPUT_DIR environment variable, then proves the copy
arrived intact by comparing SHA-256 digests before it reports
success. It renders nothing and needs no network.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def target_dir():
    """Where the grader wants the artifact: always the environment
    variable when set; otherwise a local ./output beside this file."""
    named = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if named:
        return named
    return os.path.join(HERE, "output")


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def deliver():
    if not os.path.isfile(SOURCE):
        raise SystemExit("entry.png missing beside main.py: %s" % SOURCE)
    out_dir = target_dir()
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    if os.path.abspath(dest) != os.path.abspath(SOURCE):
        shutil.copyfile(SOURCE, dest)
    if digest(dest) != digest(SOURCE):
        raise SystemExit("copy failed verification: %s" % dest)
    print("delivered", dest, os.path.getsize(dest), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
