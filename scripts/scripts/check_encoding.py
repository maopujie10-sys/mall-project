#!/usr/bin/env python3
"""Push — BOMUTF-8"""
import os, sys

root = os.path.dirname(os.path.abspath(__file__))
errors = 0

for dirpath, dirs, files in os.walk(os.path.join(root, "backend")):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(dirpath, f)
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                # Check for BOM
                if data[:3] == b"\xef\xbb\xbf":
                    print(f"BOM: {path}")
                    errors += 1
                # Check valid UTF-8
                try:
                    data.decode("utf-8")
                except UnicodeDecodeError as e:
                    print(f"INVALID UTF-8: {path} — {e}")
                    errors += 1
            except Exception as e:
                print(f"ERROR reading {path}: {e}")
                errors += 1

if errors:
    print(f"\n{errors} errors found. Fix before pushing.")
    sys.exit(1)
else:
    print("All files clean.")