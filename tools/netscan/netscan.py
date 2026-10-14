#!/usr/bin/env python3
"""netscan — discover and classify devices on a network you control.

RE "step 0": before you can de-cloud or reverse-engineer a device, you have to
find it and know what it is. netscan does a ping sweep, reads the ARP table,
decodes each MAC's vendor (OUI), does reverse-DNS, and classifies every device
by its de-cloud / local-control potential using this repo's knowledge base.

Dependency-free: Python 3.8+ standard library only. Cross-platform
(Windows / Linux / macOS).

ETHICS: Only scan networks you own or are explicitly authorized to test.
Scanning other people's networks may be illegal. This tool does light host
discovery (ICMP + ARP), nothing intrusive.

Usage:
    python -I netscan.py                      # auto-detect local /24, scan it
    python -I netscan.py --subnet 192.168.1.0/24
    python -I netscan.py --no-online          # skip OUI web lookup (offline)
    python -I netscan.py --json out.json      # machine-readable
    python -I netscan.py --markdown report.md # write a Markdown report
    python -I netscan.py --workers 128        # ping concurrency
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import ipaddress
import json
import platform
import re
import socket
import subprocess
import sys
import urllib.request

IS_WINDOWS = platform.system().lower().startswith("win")

# --- MAC vendor decoding -------------------------------------------------

# Small built-in OUI map so offline mode still classifies common gear. Not
# exhaustive — online lookups (api.maclookup.app) fill in the rest. Prefixes
# are the first 3 octets, lower-case, colon-separated.
BUILTIN_OUI = {
    "34:98:b5": "NETGEAR",
    "38:ca:84": "HP Inc.",
}

_oui_cache: dict[str, str] = {}


def normalize_mac(mac: str) -> str:
    hexd = re.sub(r"[^0-9a-fA-F]", "", mac).lower()
    if len(hexd) != 12:
        return ""
    return ":".join(hexd[i:i + 2] for i in range(0, 12, 2))


def oui_vendor(mac: str, online: bool) -> str:
    mac = normalize_mac(mac)
    if not mac:
        return "<invalid>"
    prefix = mac[:8]
    if prefix in BUILTIN_OUI:
        return BUILTIN_OUI[prefix]
    if mac in _oui_cache:
        return _oui_cache[mac]
    if not online:
        return "<unknown (offline)>"
    try:
        url = f"https://api.maclookup.app/v2/macs/{mac}"
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        vendor = (data.get("company") or "").strip() or "<unknown>"
    except Exception:
        vendor = "<lookup failed>"
    _oui_cache[mac] = vendor
    return vendor


# --- device classification (this repo's knowledge) -----------------------

# Each rule: (vendor/hostname substrings, device guess, de-cloud verdict, hint).
# First match wins; matched case-insensitively against "<vendor> <hostname>".
CLASSIFY_RULES = [
    (["netgear", "asus", "linksys", "ubiquiti", "d-link", "zyxel", "arris",
      "technicolor", "sagemcom"],
     "Router / gateway / AP", "depends",
     "OpenWrt if standalone+supported; else vendor API (e.g. pynetgear). Keep firmware updated."),
    (["tp-link", "tplink"],
     "TP-Link (router OR Kasa smart device)", "likely",
     "If Kasa plug/bulb: python-kasa local LAN API, no cloud. If router: OpenWrt maybe."),
    (["kasa"],
     "Kasa smart device", "yes",
     "python-kasa — native local LAN control, no cloud, no flashing."),
    (["hp inc", "hewlett", "canon", "seiko epson", "epson", "brother"],
     "Printer", "n/a (driver)",
     "Driverless IPP / HPLIP / Gutenprint. Ink chip is DRM (wall)."),
    (["espressif", "tuya", "jinvoo", "smartlife", "shenzhen bilian"],
     "Tuya/ESP smart device", "yes",
     "LocalTuya for local keys, or reflash ESPHome/Tasmota (tuya-convert / tuya-cloudcutter)."),
    (["intellirocks", "govee"],
     "Govee device", "partial",
     "Some models expose a LAN API; else cloud/BLE. Home Assistant Govee integration."),
    (["yale", "august", "assa abloy", "schlage", "allegion"],
     "Smart lock", "depends",
     "Local ONLY if it has Zigbee/Z-Wave/Matter (use Zigbee2MQTT / Z-Wave JS). Keep firmware updated; don't weaken lock auth."),
    (["ecovacs", "roborock", "dreame", "viomi", "xiaomi", "mova"],
     "Robot vacuum", "maybe",
     "Valetudo de-clouds supported chipsets (Roborock/Dreame/Viomi/Mova)."),
    (["nest labs", "google"],
     "Google / Nest device", "no",
     "Locked down. Local only via Matter on newer units; otherwise cloud."),
    (["amazon", "amazon technologies"],
     "Amazon Echo / Fire device", "no",
     "Cloud-locked. Limited local via Matter on newer units."),
    (["roku", "tonly"],
     "Streaming device (Roku/TCL-class)", "partial",
     "Local ECP/REST API exists on Roku for control; not de-cloudable."),
    (["sonos"],
     "Sonos speaker", "partial",
     "Local UPnP/API control; cloud for streaming accounts."),
    (["apple", "lg innotek"],
     "Apple device or LG module (often a phone/tablet/TV)", "n/a",
     "Likely a personal device, not an RE target. Confirm."),
    (["raspberry"],
     "Raspberry Pi", "n/a",
     "Probably your own machine / a hub (Home Assistant?)."),
    (["fn-link", "hunan fn-link", "shenzhen", "hunan", "beken", "realtek"],
     "Generic WiFi IoT module (TV / sensor / cheap IoT)", "unknown",
     "OEM WiFi module — identify the actual product, then classify."),
]


def classify(vendor: str, hostname: str) -> tuple[str, str, str]:
    hay = f"{vendor} {hostname}".lower()
    for subs, guess, verdict, hint in CLASSIFY_RULES:
        if any(s in hay for s in subs):
            return guess, verdict, hint
    return "Unidentified", "unknown", "Identify the product manually, then classify."


# --- discovery -----------------------------------------------------------

def local_subnet() -> str:
    """Best-effort local /24 from the primary outbound interface."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.1.1"
    finally:
        s.close()
    net = ipaddress.ip_network(ip + "/24", strict=False)
    return str(net)


def ping(ip: str) -> bool:
    if IS_WINDOWS:
        cmd = ["ping", "-n", "1", "-w", "300", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]
    try:
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=4)
        return r.returncode == 0
    except Exception:
        return False


def ping_sweep(subnet: str, workers: int) -> None:
    hosts = [str(h) for h in ipaddress.ip_network(subnet, strict=False).hosts()]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(ping, hosts))


def read_arp() -> dict[str, str]:
    """Return {ip: mac} from the OS neighbor/ARP table."""
    out = {}
    try:
        if IS_WINDOWS:
            text = subprocess.run(["arp", "-a"], capture_output=True, text=True,
                                  timeout=10).stdout
            for line in text.splitlines():
                m = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]{17})", line)
                if m:
                    out[m.group(1)] = normalize_mac(m.group(2))
        else:
            # Prefer `ip neigh`; fall back to `arp -n`.
            try:
                text = subprocess.run(["ip", "neigh"], capture_output=True,
                                      text=True, timeout=10).stdout
                for line in text.splitlines():
                    m = re.search(r"(\d+\.\d+\.\d+\.\d+).*lladdr\s+([0-9a-fA-F:]{17})", line)
                    if m:
                        out[m.group(1)] = normalize_mac(m.group(2))
            except FileNotFoundError:
                text = subprocess.run(["arp", "-n"], capture_output=True,
                                      text=True, timeout=10).stdout
                for line in text.splitlines():
                    m = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+\w+\s+([0-9a-fA-F:]{17})", line)
                    if m:
                        out[m.group(1)] = normalize_mac(m.group(2))
    except Exception as e:
        print(f"[warn] could not read ARP table: {e}", file=sys.stderr)
    # Drop broadcast / multicast noise.
    return {ip: mac for ip, mac in out.items()
            if mac and not mac.startswith(("ff:", "01:00:5e", "33:33"))
            and not ip.endswith(".255")}


def reverse_dns(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""


# --- reporting -----------------------------------------------------------

def scan(subnet: str, online: bool, workers: int) -> list[dict]:
    print(f"[*] sweeping {subnet} ...", file=sys.stderr)
    ping_sweep(subnet, workers)
    arp = read_arp()
    print(f"[*] {len(arp)} host(s) in ARP table; decoding ...", file=sys.stderr)
    rows = []
    for ip, mac in sorted(arp.items(), key=lambda kv: tuple(int(o) for o in kv[0].split("."))):
        vendor = oui_vendor(mac, online)
        host = reverse_dns(ip)
        guess, verdict, hint = classify(vendor, host)
        rows.append({"ip": ip, "mac": mac, "vendor": vendor, "hostname": host,
                     "device_guess": guess, "decloud": verdict, "hint": hint})
    return rows


def print_table(rows: list[dict]) -> None:
    if not rows:
        print("No devices found.")
        return
    w_ip = max(len(r["ip"]) for r in rows)
    w_vn = min(24, max(len(r["vendor"]) for r in rows))
    print(f"\n{'IP':<{w_ip}}  {'MAC':<17}  {'VENDOR':<{w_vn}}  DEVICE / VERDICT")
    print("-" * (w_ip + w_vn + 50))
    for r in rows:
        vn = (r["vendor"][:w_vn])
        print(f"{r['ip']:<{w_ip}}  {r['mac']:<17}  {vn:<{w_vn}}  "
              f"{r['device_guess']} [{r['decloud']}]")
    print(f"\n{len(rows)} device(s). de-cloud legend: yes/likely/partial/"
          f"depends/maybe/no/unknown/n-a\n")


def to_markdown(rows: list[dict], subnet: str) -> str:
    lines = [f"# Network scan — {subnet}", "",
             f"{len(rows)} device(s) discovered.", "",
             "| IP | MAC | Vendor | Device guess | De-cloud | Notes |",
             "|----|-----|--------|--------------|----------|-------|"]
    for r in rows:
        lines.append(f"| {r['ip']} | `{r['mac']}` | {r['vendor']} | "
                     f"{r['device_guess']} | {r['decloud']} | {r['hint']} |")
    lines += ["", "> Generated by netscan. Contains network identifiers — keep "
              "this file OUT of any public repo (it's gitignored by default)."]
    return "\n".join(lines) + "\n"


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Discover + classify devices on a network you control.")
    ap.add_argument("--subnet", help="CIDR to scan (default: auto-detect local /24)")
    ap.add_argument("--no-online", action="store_true", help="skip OUI web lookups")
    ap.add_argument("--workers", type=int, default=96, help="ping concurrency")
    ap.add_argument("--json", metavar="FILE", help="write results as JSON")
    ap.add_argument("--markdown", metavar="FILE", help="write a Markdown report")
    args = ap.parse_args(argv)

    subnet = args.subnet or local_subnet()
    rows = scan(subnet, online=not args.no_online, workers=args.workers)
    print_table(rows)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"subnet": subnet, "devices": rows}, fh, indent=2)
        print(f"[+] wrote {args.json}", file=sys.stderr)
    if args.markdown:
        with open(args.markdown, "w", encoding="utf-8") as fh:
            fh.write(to_markdown(rows, subnet))
        print(f"[+] wrote {args.markdown}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
