#!/usr/bin/env python3
"""mcp_stdio — a tiny, zero-dependency MCP server over stdio.

Implements just enough of the Model Context Protocol (JSON-RPC 2.0 over
newline-delimited stdin/stdout) for Claude Code to discover and call tools:
`initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call`.

No `pip install` — Python 3.8+ standard library only, matching the rest of this
repo. Each tool's MCP server imports `serve()` from here.

IMPORTANT: stdout carries the protocol. Never `print()` to stdout from a tool
handler — write logs to stderr (`print(..., file=sys.stderr)`).
"""
from __future__ import annotations

import json
import sys

PROTOCOL_FALLBACK = "2024-11-05"


def _send(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _result(mid, result):
    _send({"jsonrpc": "2.0", "id": mid, "result": result})


def _error(mid, code, message):
    _send({"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}})


def serve(name: str, version: str, tools: dict) -> None:
    """Run the MCP stdio loop.

    `tools` maps tool-name -> {
        "description": str,
        "inputSchema": JSON-schema dict,
        "handler": callable(args: dict) -> str | json-serialisable,
    }
    """
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue

        method = msg.get("method")
        mid = msg.get("id")

        if method == "initialize":
            pv = (msg.get("params") or {}).get("protocolVersion") or PROTOCOL_FALLBACK
            _result(mid, {
                "protocolVersion": pv,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": name, "version": version},
            })
        elif method == "ping":
            _result(mid, {})
        elif method == "tools/list":
            _result(mid, {"tools": [
                {"name": n, "description": t["description"], "inputSchema": t["inputSchema"]}
                for n, t in tools.items()
            ]})
        elif method == "tools/call":
            params = msg.get("params") or {}
            tname = params.get("name")
            args = params.get("arguments") or {}
            tool = tools.get(tname)
            if tool is None:
                _error(mid, -32602, f"unknown tool: {tname}")
                continue
            try:
                out = tool["handler"](args)
                text = out if isinstance(out, str) else json.dumps(out, indent=2, default=str)
                _result(mid, {"content": [{"type": "text", "text": text}], "isError": False})
            except Exception as e:  # report errors as tool results, not transport errors
                _result(mid, {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
        elif method and method.startswith("notifications/"):
            pass  # notifications get no response
        elif mid is not None:
            _error(mid, -32601, f"method not found: {method}")
