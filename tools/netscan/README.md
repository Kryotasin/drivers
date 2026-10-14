# netscan

Discover and classify devices on a network **you own or are authorized to
test**. This is "step 0" of any de-cloud / reverse-engineering effort: you can't
work on a device until you've found it and know what it is.

What it does, in one pass:

1. **Ping sweep** the subnet (parallel) to populate the ARP table.
2. **Read the ARP/neighbor table** for live IP → MAC pairs.
3. **Decode each MAC's vendor** (OUI) — offline for common gear, else via
   `api.maclookup.app`.
4. **Reverse-DNS** each host for a name hint.
5. **Classify** every device by its *de-cloud / local-control potential* using
   this repo's knowledge base (see [`netscan.py`](netscan.py) `CLASSIFY_RULES`).

## Requirements

Python 3.8+ — **standard library only**, no `pip install`. Works on Windows,
Linux, macOS.

## Usage

```sh
python -I netscan.py                       # auto-detect local /24 and scan
python -I netscan.py --subnet 192.168.1.0/24
python -I netscan.py --no-online           # offline (built-in OUI map only)
python -I netscan.py --json  scan.json     # machine-readable output
python -I netscan.py --markdown scan.md    # Markdown report
python -I netscan.py --workers 128         # ping concurrency (default 96)
```

## Example output (illustrative — not real devices)

```
IP             MAC                VENDOR         DEVICE / VERDICT
192.168.1.1    aa:bb:cc:00:00:01  NETGEAR        Router / gateway / AP [depends]
192.168.1.50   aa:bb:cc:00:00:02  TP-Link        TP-Link (router OR Kasa) [likely]
192.168.1.60   aa:bb:cc:00:00:03  Espressif      Tuya/ESP smart device [yes]
192.168.1.70   aa:bb:cc:00:00:04  Nest Labs      Google / Nest device [no]
```

## De-cloud verdict legend

| Verdict | Meaning |
|---------|---------|
| `yes` / `likely` | Local control achievable (native API or reflash) |
| `partial` | Some local control; depends on model |
| `depends` | Conditional (e.g. lock needs Zigbee/Z-Wave/Matter; router needs OpenWrt support) |
| `maybe` | Supported by a project for *some* models (e.g. Valetudo) |
| `no` | Cloud-locked, no realistic local path |
| `n/a` | Not an RE target (printer driver / personal phone) |
| `unknown` | Identify the product first, then classify |

## How classification works

`CLASSIFY_RULES` in `netscan.py` maps vendor/hostname substrings to a device
guess + de-cloud verdict + a concrete next-step hint (which open project to
use). It encodes what this repo knows. **Add rules** as you learn new devices —
that's how the tool gets smarter. First match wins.

Note: OUI tells you the *chip/module vendor*, not always the product. Cheap IoT
uses generic modules (FN-Link, Espressif, Realtek), and phones use **randomized
MACs** (locally-administered — second hex digit is 2/6/A/E), so some rows need
manual identification.

## ⚠️ Ethics & legal

Only scan networks you own or have explicit permission to test. Host discovery
on someone else's network can be illegal. This tool does ICMP + ARP only —
nothing intrusive — but intent and authorization are what matter.

## Output hygiene

Scan output (`--json` / `--markdown`) contains **your** MACs, IPs, and device
names. Do **not** commit it to a public repo. The repo `.gitignore` already
excludes `tools/netscan/*.json` and `*.scan.md`; keep it that way.
