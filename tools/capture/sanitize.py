#!/usr/bin/env python3
"""Pre-commit sanitizer for packet captures / hex dumps.

Scans a capture (or any text/hex dump) for identifiers that must NOT land in a
public repo and reports them, with an option to redact in a text/hex context.

This is a *safety net*, not a guarantee. It cannot understand a proprietary
binary format, so for real .pcap/.pcapng files use Wireshark/tshark to export
only the fields you need, then run this over the exported text. Always eyeball
the result before committing.

Usage:
    python -I sanitize.py <file>            # report findings
    python -I sanitize.py <file> --redact   # write <file>.sanitized with redactions
"""
import argparse
import re
import sys

# Patterns for things that should never be published.
PATTERNS = {
    "MAC address":   re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    "IPv4 address":  re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "IPv6 address":  re.compile(r"\b(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4}\b"),
    # Canon-style serials are often long alphanumerics; flag long runs for review.
    "long alnum (serial?)": re.compile(r"\b[0-9A-Za-z]{10,}\b"),
    # Common credential / token words with a value after them.
    "possible secret": re.compile(
        r"(?i)\b(pass(word)?|psk|wpa|ssid|token|secret|apikey|api_key)\b\s*[:=]\s*\S+"
    ),
}

REDACTION = "<redacted>"


def scan(text: str):
    findings = []
    for label, rx in PATTERNS.items():
        for m in rx.finditer(text):
            findings.append((label, m.group(0)))
    return findings


def redact(text: str) -> str:
    for rx in PATTERNS.values():
        text = rx.sub(REDACTION, text)
    return text


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--redact", action="store_true",
                    help="write <file>.sanitized with findings redacted")
    args = ap.parse_args(argv)

    try:
        with open(args.file, "r", errors="replace") as fh:
            text = fh.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    findings = scan(text)
    if findings:
        print(f"[!] {len(findings)} item(s) to review in {args.file}:")
        seen = set()
        for label, value in findings:
            key = (label, value)
            if key in seen:
                continue
            seen.add(key)
            shown = value if len(value) <= 40 else value[:37] + "..."
            print(f"    {label:24} {shown}")
    else:
        print(f"[ok] no obvious identifiers found in {args.file}")

    if args.redact:
        out = args.file + ".sanitized"
        with open(out, "w") as fh:
            fh.write(redact(text))
        print(f"[+] wrote {out} (review it before committing)")

    # Non-zero exit if there are findings, so this can gate a commit hook.
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
