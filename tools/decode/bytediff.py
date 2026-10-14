#!/usr/bin/env python3
"""Align two byte streams and report where they differ.

Feed it two captures that differ in exactly one variable (1 vs 2 pages, black
vs color, A4 vs Letter). The runs of differing bytes point straight at the
field that encodes that variable.

Input may be a raw binary file or a hex dump (whitespace/':' separated hex,
or a text file containing such). Detection is automatic.

Usage:
    python -I bytediff.py <a> <b>
    python -I bytediff.py <a> <b> --width 16
"""
import argparse
import re
import sys

HEX_TOKEN = re.compile(r"^[0-9A-Fa-f]{2}$")


def load(path: str) -> bytes:
    with open(path, "rb") as fh:
        raw = fh.read()
    # Heuristic: if it looks like printable hex text, parse as hex.
    sample = raw[:4096]
    printable = sum(c in b"0123456789abcdefABCDEF :\r\n\t" for c in sample)
    if sample and printable / len(sample) > 0.95:
        tokens = re.split(r"[\s:]+", raw.decode("ascii", "ignore").strip())
        hexbytes = [t for t in tokens if HEX_TOKEN.match(t)]
        if hexbytes:
            return bytes(int(t, 16) for t in hexbytes)
    return raw


def diff(a: bytes, b: bytes, width: int):
    n = max(len(a), len(b))
    runs = []            # (start, end) offsets of differing regions
    in_run = False
    start = 0
    for i in range(n):
        ba = a[i] if i < len(a) else None
        bb = b[i] if i < len(b) else None
        differ = ba != bb
        if differ and not in_run:
            in_run, start = True, i
        elif not differ and in_run:
            in_run = False
            runs.append((start, i))
    if in_run:
        runs.append((start, n))
    return runs


def hexrow(data: bytes, start: int, width: int) -> str:
    chunk = data[start:start + width]
    return " ".join(f"{c:02x}" for c in chunk)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--width", type=int, default=16)
    args = ap.parse_args(argv)

    a, b = load(args.a), load(args.b)
    print(f"A: {len(a)} bytes   B: {len(b)} bytes")
    if len(a) != len(b):
        print(f"[note] length differs by {abs(len(a) - len(b))} bytes "
              f"— often the encoded variable itself.")

    runs = diff(a, b, args.width)
    if not runs:
        print("[ok] streams are identical.")
        return 0

    print(f"[!] {len(runs)} differing region(s):")
    for start, end in runs:
        print(f"\n  offset 0x{start:x}..0x{end:x} ({end - start} bytes)")
        print(f"    A: {hexrow(a, start, args.width)}")
        print(f"    B: {hexrow(b, start, args.width)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
