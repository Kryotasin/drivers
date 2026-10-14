#!/usr/bin/env python3
"""MCP server for deviceprobe — exposes local-surface probing to Claude Code.

Run by Claude Code via stdio (see repo .mcp.json). Zero dependencies.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                      # for deviceprobe.py (sibling)
sys.path.insert(0, os.path.dirname(_HERE))     # for mcp_stdio.py (tools/)

import deviceprobe                 # noqa: E402
from mcp_stdio import serve        # noqa: E402


def probe_device(args: dict) -> dict:
    host = args["host"]
    timeout = float(args.get("timeout", 1.0))
    return deviceprobe.probe_host(host, timeout)


def probe_subnet(args: dict) -> list:
    subnet = args["subnet"]
    timeout = float(args.get("timeout", 1.0))
    hosts = deviceprobe.discover(subnet)
    return [deviceprobe.probe_host(h, timeout) for h in hosts]


TOOLS = {
    "probe_device": {
        "description": (
            "Probe one device's local-control surface: TCP-connect scan a curated "
            "set of ports and map each open one to a known local API/protocol "
            "(Kasa 9999, Tuya 6668, Chromecast 8008, RTSP 554, printer IPP 631, "
            "NETGEAR SOAP 5043, ...), then summarise de-cloud potential. Only use "
            "on devices the user owns or is authorized to test."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "host": {"type": "string", "description": "IP address to probe."},
                "timeout": {"type": "number", "description": "Per-port connect timeout in seconds (default 1.0)."},
            },
            "required": ["host"],
        },
        "handler": probe_device,
    },
    "probe_subnet": {
        "description": (
            "Discover every live host on a subnet you control and probe each one's "
            "local-control surface. Only use on networks the user owns or is "
            "authorized to test."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "subnet": {"type": "string", "description": "CIDR, e.g. 192.168.1.0/24."},
                "timeout": {"type": "number", "description": "Per-port connect timeout in seconds (default 1.0)."},
            },
            "required": ["subnet"],
        },
        "handler": probe_subnet,
    },
}


if __name__ == "__main__":
    serve("deviceprobe", "1.0.0", TOOLS)
