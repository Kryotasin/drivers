# deviceprobe

Find a device's **local-control surface** — what you can talk to on it *without*
the vendor cloud. Where [`netscan`](../netscan/) answers "*what* is this device?",
`deviceprobe` answers the decisive follow-up: "*what can I control locally?*"

It TCP-connect scans a curated set of ports and maps each open one to a known
local API/protocol (Kasa, Tuya, Chromecast, RTSP cameras, printer IPP, the
NETGEAR SOAP API, SSH/Telnet, MQTT, …), then summarises how de-cloudable the
device looks.

---

## Table of contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Running it](#running-it)
- [Options](#options)
- [Reading the output](#reading-the-output)
- [What the ports mean](#what-the-ports-mean)
- [The UDP blind spot](#the-udp-blind-spot)
- [Use from Claude Code (MCP)](#use-from-claude-code-mcp)
- [Troubleshooting](#troubleshooting)
- [Ethics & legal](#ethics--legal)

---

## Requirements

- **Python 3.8+**, standard library only. No `pip install`.
- Works on Windows, Linux, macOS.

```sh
python --version        # need 3.8+
```

---

## Installation

Single self-contained file.

```sh
# as part of the repo
git clone https://github.com/Kryotasin/drivers.git
cd drivers
python tools/deviceprobe/deviceprobe.py 192.168.1.1

# or just the one file
curl -O https://raw.githubusercontent.com/Kryotasin/drivers/main/tools/deviceprobe/deviceprobe.py
python deviceprobe.py 192.168.1.1
```

---

## Running it

```sh
python deviceprobe.py 192.168.1.50                 # one host
python deviceprobe.py 192.168.1.50 192.168.1.60    # several hosts
python deviceprobe.py --subnet 192.168.1.0/24      # discover + probe all live hosts
python deviceprobe.py 192.168.1.50 --timeout 1.5   # slower/more reliable
python deviceprobe.py 192.168.1.50 --json out.json # machine-readable
```

Typical flow: run `netscan` first to find devices, then `deviceprobe` the ones
you care about.

---

## Options

| Flag | Default | Meaning |
|------|---------|---------|
| `hosts…` | — | One or more IPs to probe (positional). |
| `--subnet CIDR` | — | Discover every live host in the CIDR and probe each. |
| `--timeout SECONDS` | `1.0` | Per-port connect timeout. Raise it for sleepy/slow devices. |
| `--json FILE` | — | Write results as JSON. |
| `-h`, `--help` | — | Usage. |

---

## Reading the output

```
=== 192.168.1.1 — LOCAL CONTROL LIKELY ===
     80/tcp  HTTP             Web UI / local REST API / printer EWS — inspect it.
    443/tcp  HTTPS            Secure web UI / local API — inspect it.
   5000/tcp  UPnP/HTTP-alt    UPnP or an app API (also Synology) — inspect.
   5043/tcp  NETGEAR SOAP     NETGEAR router API — automate with pynetgear.
```

- Header shows the **verdict** (see below).
- Each line is an open port → service → what it means for local control.
- For web ports (80/443/8443/5000/8008) it also tries to grab a `Server`
  header / page `<title>` as an identity hint.

### Verdicts
| Verdict | Meaning |
|---------|---------|
| `LOCAL CONTROL LIKELY` | A strong local-API port is open (Kasa/Tuya/Cast/RTSP/IPP/SOAP…). |
| `possible local API — inspect` | A web/MQTT port is open; worth inspecting. |
| `limited surface` | Something's open, but nothing obviously controllable. |
| `no TCP surface (cloud-only or UDP-only?)` | No probed TCP ports — likely cloud-only, asleep, or UDP-only. |

---

## What the ports mean

| Port | Service | De-cloud signal |
|------|---------|-----------------|
| 9999 | Kasa | **Local LAN API** — `python-kasa`, no cloud. Strong yes. |
| 6668 | Tuya | **Local protocol** — LocalTuya (needs local key). Strong yes. |
| 8008/8009 | Google Cast | Local control API (limited). |
| 554 | RTSP | Local camera video stream likely available. |
| 631 | IPP | Driverless local printing. |
| 9100 | JetDirect | Raw local printing. |
| 5043 | NETGEAR SOAP | Router automation via `pynetgear`. |
| 1883/8883 | MQTT | Possible local command/telemetry. |
| 80/443/8443/5000 | HTTP(S) | Web UI / local REST / EWS — inspect. |
| 22 | SSH | Shell if you have creds. |
| 23 | Telnet | Often a debug/root console on cheap IoT — notable RE signal. |

The full map lives in `PORTS` at the top of `deviceprobe.py`. Add ports as you
learn new devices.

---

## The UDP blind spot

A TCP connect scan **cannot** see UDP-only local APIs. Several important ones
are UDP:

- **Govee LAN API** — UDP 4001–4003
- **LIFX** — UDP 56700
- **SSDP / UPnP discovery** — UDP 1900
- **mDNS / Bonjour** — UDP 5353
- **Canon BJNP printing** — UDP 8611/8612

So a `no TCP surface` verdict does **not** prove a device is cloud-only — it may
simply speak UDP. deviceprobe prints this reminder after every run.

---

## Use from Claude Code (MCP)

deviceprobe ships an MCP server (`mcp_server.py`) exposing `probe_device` and
`probe_subnet`, so you can ask Claude Code *"probe 192.168.1.1 for local APIs."*
See [../../docs/mcp-servers.md](../../docs/mcp-servers.md).

---

## Troubleshooting

- **A device you know is up shows `no TCP surface`:** it may be asleep (DeskJet
  printers deep-sleep and drop port 80 until woken) — raise `--timeout`, wake it
  (open its app / print something), or remember it may be UDP-only.
- **Everything times out:** you may be on an isolated guest VLAN; join the same
  network as the devices.
- **Slow `--subnet` runs:** a /24 discovers 254 hosts first; probe specific IPs
  instead when you can.

---

## Ethics & legal

Only probe devices on networks you **own** or are **authorized** to test. A
connect scan is light, but it is still a scan — authorization and intent are what
matter. See [../../docs/legal-and-ethics.md](../../docs/legal-and-ethics.md).
