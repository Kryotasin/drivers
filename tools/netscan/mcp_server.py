#!/usr/bin/env python3
"""MCP server for netscan — exposes network discovery to Claude Code.

Run by Claude Code via stdio (see repo .mcp.json). Zero dependencies.

Manual test:
    printf '%s\\n' \\
      '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' \\
      '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \\
      | python tools/netscan/mcp_server.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                      # for netscan.py (sibling)
sys.path.insert(0, os.path.dirname(_HERE))     # for mcp_stdio.py (tools/)

import netscan                      # noqa: E402
from mcp_stdio import serve         # noqa: E402


def scan_network(args: dict) -> dict:
    subnet = args.get("subnet") or netscan.local_subnet()
    online = bool(args.get("online", True))
    workers = int(args.get("workers", 96))
    rows = netscan.scan(subnet, online=online, workers=workers)
    return {"subnet": subnet, "count": len(rows), "devices": rows}


TOOLS = {
    "scan_network": {
        "description": (
            "Discover and classify devices on a network you control. Ping-sweeps "
            "the subnet, reads the ARP table, decodes each MAC's vendor, reverse-"
            "DNS, and classifies each device by de-cloud/local-control potential. "
            "Only use on networks the user owns or is authorized to test."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "subnet": {"type": "string",
                           "description": "CIDR to scan, e.g. 192.168.1.0/24. Omit to auto-detect the local /24."},
                "online": {"type": "boolean",
                           "description": "Use online OUI vendor lookups (default true)."},
                "workers": {"type": "integer",
                            "description": "Ping concurrency (default 96)."},
            },
            "required": [],
        },
        "handler": scan_network,
    },
}


if __name__ == "__main__":
    serve("netscan", "1.0.0", TOOLS)
