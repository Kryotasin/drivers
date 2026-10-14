# netscan

Discover and classify every device on a network **you own or are authorized to
test**, and triage each one by its **de-cloud / local-control potential**.

This is "step 0" of any de-cloud or reverse-engineering effort: you can't work
on a device until you've found it, identified it, and decided whether it's worth
your time. `netscan` does all of that in one pass.

---

## Table of contents
- [What it does](#what-it-does)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running it](#running-it)
- [Command-line options](#command-line-options)
- [Reading the output](#reading-the-output)
- [De-cloud verdict legend](#de-cloud-verdict-legend)
- [How classification works (and how to extend it)](#how-classification-works-and-how-to-extend-it)
- [Platform notes](#platform-notes)
- [Troubleshooting](#troubleshooting)
- [Privacy & output hygiene](#privacy--output-hygiene)
- [Ethics & legal](#ethics--legal)

---

## What it does

In a single run, for one subnet:

1. **Ping sweep** — pings every host in the subnet, in parallel, to populate the
   OS ARP/neighbor table.
2. **Read ARP table** — collects live `IP → MAC` pairs.
3. **Decode vendor (OUI)** — maps each MAC's first 3 octets to its manufacturer,
   offline for common gear or via `api.maclookup.app` online.
4. **Reverse-DNS** — asks for a hostname hint per device.
5. **Classify** — labels each device with a *device guess*, a *de-cloud verdict*,
   and a *concrete next step*, using this repo's knowledge base.

---

## Requirements

- **Python 3.8+**. Nothing else. No `pip install`, no virtualenv.
  - It uses only the standard library (`socket`, `subprocess`, `ipaddress`,
    `concurrent.futures`, `urllib`, …).
- A working `ping` and `arp` (Windows) / `ip` or `arp` (Linux/macOS) — present by
  default on all three platforms.
- Online OUI lookups need outbound HTTPS; otherwise run with `--no-online`.

Check Python:
```sh
python --version        # need 3.8 or higher; use python3 if python is v2
```

---

## Installation

`netscan.py` is a **single self-contained file**. Pick either path.

### A) As part of the repo
```sh
git clone https://github.com/Kryotasin/drivers.git
cd drivers
python tools/netscan/netscan.py
```

### B) Just the one file (no git)
```sh
curl -O https://raw.githubusercontent.com/Kryotasin/drivers/main/tools/netscan/netscan.py
python netscan.py
```

### Optional: make it a command (Linux/macOS)
```sh
chmod +x netscan.py
./netscan.py
```

---

## Running it

Simplest — auto-detect your local /24 and scan it:
```sh
python netscan.py
```

Scan a specific subnet:
```sh
python netscan.py --subnet 192.168.1.0/24
```

Offline (no internet; uses the small built-in OUI map only):
```sh
python netscan.py --no-online
```

Save machine-readable and/or Markdown reports:
```sh
python netscan.py --json scan.json
python netscan.py --markdown scan.md
```

Faster/slower sweep (ping concurrency):
```sh
python netscan.py --workers 128      # faster on a big/quiet subnet
python netscan.py --workers 32       # gentler
```

> Tip: a single sweep sometimes misses a sleeping device. Run it twice, or wake
> the device (open its app) and re-run.

---

## Command-line options

| Flag | Default | Meaning |
|------|---------|---------|
| `--subnet CIDR` | auto-detect | Network to scan, e.g. `192.168.1.0/24`. |
| `--no-online` | off | Skip the OUI web lookup; use the built-in map only. |
| `--workers N` | `96` | Number of concurrent pings during the sweep. |
| `--json FILE` | — | Write results as JSON. |
| `--markdown FILE` | — | Write a Markdown report table. |
| `-h`, `--help` | — | Show usage. |

---

## Reading the output

Terminal output is a table:
```
IP             MAC                VENDOR         DEVICE / VERDICT
192.168.1.1    aa:bb:cc:00:00:01  NETGEAR        Router / gateway / AP [depends]
192.168.1.50   aa:bb:cc:00:00:02  TP-Link        TP-Link (router OR Kasa) [likely]
192.168.1.60   aa:bb:cc:00:00:03  Espressif      Tuya/ESP smart device [yes]
192.168.1.70   aa:bb:cc:00:00:04  Nest Labs      Google / Nest device [no]
```
*(Illustrative — not real devices.)*

- **IP / MAC** — the live address and hardware address.
- **VENDOR** — the OUI (chip/module maker), truncated in the table; full value is
  in `--json` / `--markdown` output.
- **DEVICE** — best guess at what the thing is.
- **[verdict]** — de-cloud potential (see below). The `--json`/`--markdown`
  output also includes a `hint` with the concrete next step (which open project
  to use).

---

## De-cloud verdict legend

| Verdict | Meaning |
|---------|---------|
| `yes` / `likely` | Local control achievable (native local API or reflash). |
| `partial` | Some local control; depends on the exact model. |
| `depends` | Conditional — e.g. a lock needs a Zigbee/Z-Wave/Matter radio; a router needs OpenWrt support. |
| `maybe` | A project supports *some* models (e.g. Valetudo for certain vacuums). |
| `no` | Cloud-locked, no realistic local path. |
| `n/a` | Not an RE target (a printer driver, or your own phone). |
| `unknown` | Identify the product first, then classify. |

---

## How classification works (and how to extend it)

Classification lives in `CLASSIFY_RULES` near the top of `netscan.py`. Each rule
is:

```python
(["substring1", "substring2"],   # matched against "<vendor> <hostname>", case-insensitive
 "Device guess",                 # what it probably is
 "verdict",                      # de-cloud verdict (see legend)
 "Concrete next step / project") # e.g. "python-kasa — local LAN API"
```

**First match wins.** To teach `netscan` a new device, add a rule. Example — say
you identify a new brand of smart plug that de-clouds with ESPHome:

```python
(["mybrand", "newplug"],
 "MyBrand smart plug", "yes",
 "Reflash with ESPHome via tuya-cloudcutter."),
```

Put more specific rules **above** more general ones (the generic "WiFi module"
rule should stay last).

### Why a device may be misidentified
- **OUI = chip/module vendor, not product.** Cheap IoT uses generic modules
  (Espressif, Realtek, FN-Link), so the vendor is a hint, not the brand.
- **Randomized MACs.** Phones/laptops rotate their MAC for privacy. A
  *locally-administered* MAC (second hex digit is `2`, `6`, `A`, or `E`) is
  almost always a personal device, not an IoT target.
- **Reverse-DNS is often empty** on IoT devices; printers are a nice exception
  (an HP printer announces a name like `HPxxxxxx`).

---

## Platform notes

| | Windows | Linux | macOS |
|---|---|---|---|
| Ping flags used | `ping -n 1 -w 300` | `ping -c 1 -W 1` | `ping -c 1 -W 1` |
| ARP source | `arp -a` | `ip neigh` (falls back to `arp -n`) | `arp -a` |
| Admin needed? | No | No | No |

All handled automatically; you don't pass anything platform-specific.

---

## Troubleshooting

**"No devices found" / only the router shows up**
- Some OSes/firewalls drop ICMP. Devices that ignore ping won't enter the ARP
  table from the sweep alone. Fixes: run it again, or generate traffic to the
  device first (open its app, or `ping <device-ip>` manually), then re-run.
- Make sure you're on the same subnet/VLAN as the devices (guest WiFi is
  isolated — your IoT gear won't be visible from it).

**Vendor shows `<unknown>` or `<lookup failed>`**
- You're offline or the OUI API is unreachable. Re-run with internet, or accept
  the built-in offline map (covers only a few common vendors).

**Wrong subnet auto-detected**
- Pass it explicitly: `--subnet 192.168.0.0/24` (check your gateway with
  `ipconfig` on Windows or `ip route` on Linux).

**Scan feels slow**
- Lower the host count (scan a tighter CIDR) or adjust `--workers`. A /24 is 254
  hosts; dead hosts wait for the ping timeout.

**A device appears then disappears between runs**
- It's sleeping/power-saving, or using MAC randomization. Normal for phones and
  battery IoT.

---

## Privacy & output hygiene

A scan report is a **map of your home network** (MACs, IPs, device names). Treat
it as sensitive:

- **Never commit scan output to a public repo.** The repo `.gitignore` already
  excludes `tools/netscan/*.json`, `*.scan.md`, and the OUI cache.
- The tool itself ships with **illustrative example data only** — no real
  devices.

---

## Ethics & legal

Only scan networks you **own** or are **explicitly authorized** to test.
Discovery scanning of networks you don't control may be illegal in your
jurisdiction. `netscan` performs only ICMP ping + ARP reads — nothing intrusive
— but **authorization and intent are what matter**, not how gentle the probe is.

See [../../docs/legal-and-ethics.md](../../docs/legal-and-ethics.md).
