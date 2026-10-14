#!/usr/bin/env python3
"""deviceprobe — find the local-control surface of a device you own.

netscan answers "what is this device?". deviceprobe answers the follow-up:
"what can I talk to on it *locally*, without the vendor cloud?" It TCP-connect
scans a curated set of ports and maps each open one to a known local-control
API or protocol, then summarises how de-cloudable the device looks.

Dependency-free: Python 3.8+ standard library only. Cross-platform.

ETHICS: Only probe devices on networks you own or are authorized to test. A
connect scan is light but still a scan — authorization is what matters.

Usage:
    python -I deviceprobe.py 192.168.1.50            # probe one host
    python -I deviceprobe.py 192.168.1.50 192.168.1.60
    python -I deviceprobe.py --subnet 192.168.1.0/24 # discover + probe all
    python -I deviceprobe.py 192.168.1.50 --json out.json
    python -I deviceprobe.py 192.168.1.50 --timeout 1.5
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import ipaddress
import json
import re
import socket
import ssl
import subprocess
import sys
import urllib.request

# port -> (service, what it means for local control / de-cloud)
PORTS = {
    22:   ("SSH", "Possible shell access (if creds/keys known)."),
    23:   ("Telnet", "Often a debug/root console on cheap IoT — big RE signal."),
    80:   ("HTTP", "Web UI / local REST API / printer EWS — inspect it."),
    443:  ("HTTPS", "Secure web UI / local API — inspect it."),
    554:  ("RTSP", "Camera: a LOCAL video stream is likely available."),
    631:  ("IPP", "Printer: driverless local printing (CUPS/IPP Everywhere)."),
    1883: ("MQTT", "Message broker — may allow local command/telemetry."),
    5000: ("UPnP/HTTP-alt", "UPnP or an app API (also Synology) — inspect."),
    5043: ("NETGEAR SOAP", "NETGEAR router API — automate with pynetgear."),
    6668: ("Tuya local", "Tuya/Smart Life LOCAL protocol — de-cloud with LocalTuya (needs local key)."),
    8008: ("Google Cast", "Chromecast/Nest LOCAL control API (limited)."),
    8009: ("Google Cast TLS", "Chromecast/Nest LOCAL control (TLS)."),
    8443: ("HTTPS-alt", "Alt web/admin API — inspect."),
    8883: ("MQTT/TLS", "Secure MQTT broker — may allow local control."),
    9100: ("JetDirect", "Printer raw (port 9100) local printing."),
    9999: ("Kasa", "TP-Link Kasa LOCAL API — de-cloud with python-kasa. No cloud needed."),
}

# UDP-based local APIs a TCP connect scan can't see — reported as a hint.
UDP_HINTS = [
    "Govee LAN API (UDP 4001-4003) — not visible to a TCP scan; test with the Govee LAN tool.",
    "LIFX (UDP 56700), SSDP/UPnP (UDP 1900), mDNS (UDP 5353), Canon BJNP (UDP 8611/8612) are UDP-only.",
]

# Open ports that strongly imply local control is achievable.
STRONG_LOCAL = {9999, 6668, 554, 631, 9100, 5043, 8008, 8009}


def tcp_open(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def http_title(host: str, port: int, timeout: float) -> str:
    scheme = "https" if port in (443, 8443) else "http"
    url = f"{scheme}://{host}:{port}/"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "deviceprobe"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(4096).decode("utf-8", "replace")
            server = r.headers.get("Server", "")
        m = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
        title = (m.group(1).strip() if m else "")[:60]
        bits = [b for b in (server, title) if b]
        return " / ".join(bits)
    except Exception:
        return ""


def probe_host(host: str, timeout: float) -> dict:
    open_ports = []
    with cf.ThreadPoolExecutor(max_workers=len(PORTS)) as ex:
        results = {p: ex.submit(tcp_open, host, p, timeout) for p in PORTS}
        for p, fut in results.items():
            if fut.result():
                open_ports.append(p)
    details = []
    for p in sorted(open_ports):
        svc, meaning = PORTS[p]
        extra = ""
        if p in (80, 443, 8443, 5000, 8008):
            t = http_title(host, p, timeout)
            if t:
                extra = f"  → {t}"
        details.append({"port": p, "service": svc, "meaning": meaning, "banner": extra.strip(" →")})
    verdict = local_verdict(open_ports)
    return {"ip": host, "open_ports": open_ports, "details": details, "verdict": verdict}


def local_verdict(open_ports: list[int]) -> str:
    if any(p in STRONG_LOCAL for p in open_ports):
        return "LOCAL CONTROL LIKELY"
    if any(p in (80, 443, 8443, 1883, 8883, 5000) for p in open_ports):
        return "possible local API — inspect"
    if open_ports:
        return "limited surface"
    return "no TCP surface (cloud-only or UDP-only?)"


# --- optional discovery (so you can probe a whole subnet) -----------------

IS_WINDOWS = sys.platform.startswith("win")


def ping(ip: str) -> bool:
    cmd = (["ping", "-n", "1", "-w", "300", ip] if IS_WINDOWS
           else ["ping", "-c", "1", "-W", "1", ip])
    try:
        return subprocess.run(cmd, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, timeout=4).returncode == 0
    except Exception:
        return False


def discover(subnet: str) -> list[str]:
    hosts = [str(h) for h in ipaddress.ip_network(subnet, strict=False).hosts()]
    with cf.ThreadPoolExecutor(max_workers=96) as ex:
        list(ex.map(ping, hosts))
    out = []
    try:
        if IS_WINDOWS:
            text = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10).stdout
            for line in text.splitlines():
                m = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+[0-9a-fA-F-]{17}", line)
                if m and not m.group(1).endswith(".255"):
                    out.append(m.group(1))
        else:
            text = subprocess.run(["ip", "neigh"], capture_output=True, text=True, timeout=10).stdout
            for line in text.splitlines():
                m = re.search(r"(\d+\.\d+\.\d+\.\d+).*lladdr", line)
                if m:
                    out.append(m.group(1))
    except Exception as e:
        print(f"[warn] discovery failed: {e}", file=sys.stderr)
    return sorted(set(out), key=lambda ip: tuple(int(o) for o in ip.split(".")))


# --- reporting ------------------------------------------------------------

def print_report(results: list[dict]) -> None:
    for r in results:
        print(f"\n=== {r['ip']} — {r['verdict']} ===")
        if not r["details"]:
            print("  (no probed TCP ports open)")
        for d in r["details"]:
            line = f"  {d['port']:>5}/tcp  {d['service']:<16} {d['meaning']}"
            print(line)
            if d["banner"]:
                print(f"         ↳ {d['banner']}")
    print("\nUDP note (TCP scans can't see these):")
    for h in UDP_HINTS:
        print(f"  - {h}")
    print()


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Probe a device's local-control surface.")
    ap.add_argument("hosts", nargs="*", help="IP(s) to probe")
    ap.add_argument("--subnet", help="discover + probe every live host in this CIDR")
    ap.add_argument("--timeout", type=float, default=1.0, help="per-port connect timeout (s)")
    ap.add_argument("--json", metavar="FILE", help="write results as JSON")
    args = ap.parse_args(argv)

    targets = list(args.hosts)
    if args.subnet:
        print(f"[*] discovering hosts on {args.subnet} ...", file=sys.stderr)
        targets += discover(args.subnet)
    targets = sorted(set(targets), key=lambda ip: tuple(int(o) for o in ip.split(".")) if ip.count(".") == 3 else (0,))
    if not targets:
        ap.error("give one or more IPs, or --subnet CIDR")

    print(f"[*] probing {len(targets)} host(s), {len(PORTS)} ports each ...", file=sys.stderr)
    results = []
    for t in targets:
        results.append(probe_host(t, args.timeout))
    print_report(results)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"[+] wrote {args.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
