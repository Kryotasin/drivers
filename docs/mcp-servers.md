# MCP servers (use the tools from Claude Code)

Every runnable tool in this repo also ships as a **Model Context Protocol (MCP)
server**, so you can drive it conversationally from Claude Code instead of
typing CLI flags — e.g. *"scan my network and tell me what's de-cloudable"* or
*"probe 192.168.1.1 for local APIs."*

Like everything here, the MCP servers are **zero-dependency** — pure Python 3.8+
standard library (a tiny stdio JSON-RPC implementation in
[`../tools/mcp_stdio.py`](../tools/mcp_stdio.py)). No `pip install mcp`, no SDK.

---

## What's exposed

| Server | Tool(s) | Does |
|--------|---------|------|
| **netscan** | `scan_network` | Discover + classify devices on a subnet you control. |
| **deviceprobe** | `probe_device`, `probe_subnet` | Map a device's (or whole subnet's) local-control surface. |

---

## Enabling them in Claude Code

### Option A — project scope (automatic, recommended)
This repo ships a [`.mcp.json`](../.mcp.json) at its root. When you open the repo
in Claude Code:

```sh
git clone https://github.com/Kryotasin/drivers.git
cd drivers
claude            # launch Claude Code in the repo
```

Claude Code detects `.mcp.json` and prompts you to approve the `netscan` and
`deviceprobe` servers. Approve them and they're live for this project. Check with:

```
/mcp
```

> The relative paths in `.mcp.json` resolve from the repo root, so launch Claude
> Code from the repo directory.

### Option B — add manually via the CLI (any scope)
```sh
# from the repo root; use an ABSOLUTE path if adding at user scope
claude mcp add netscan     -- python "$(pwd)/tools/netscan/mcp_server.py"
claude mcp add deviceprobe -- python "$(pwd)/tools/deviceprobe/mcp_server.py"
```
Scopes: add `-s user` (available everywhere) or `-s project` (shared via
`.mcp.json`). Default is local to the current project.

### Windows note
If `python` isn't the right launcher on your system, use `py`:
```json
{ "command": "py", "args": ["tools/netscan/mcp_server.py"] }
```

---

## Example prompts once enabled

- "Use netscan to scan 192.168.1.0/24 and group devices by de-cloud verdict."
- "Probe my router at 192.168.1.1 — does it expose a local API?"
- "Scan the network, then probe every device you classified as 'yes' or 'likely'."

Claude Code calls the MCP tool, gets structured JSON back, and reasons over it.

---

## Security

These tools scan networks/devices. The MCP tool descriptions explicitly tell the
model to only use them on networks **you own or are authorized to test** — but
*you* are still the authorization. MCP servers run locally on your machine with
your permissions; they make no outbound connections except the optional OUI
vendor lookup (`api.maclookup.app`), which you can disable.

---

## How it works (and adding your own)

- [`tools/mcp_stdio.py`](../tools/mcp_stdio.py) implements the MCP stdio loop:
  `initialize`, `tools/list`, `tools/call`, `ping`. It speaks newline-delimited
  JSON-RPC 2.0 over stdin/stdout.
- Each server (e.g. [`tools/netscan/mcp_server.py`](../tools/netscan/mcp_server.py))
  imports the tool's own functions, wraps them as handlers, and calls
  `serve(name, version, TOOLS)`.

To expose a new tool, add a `mcp_server.py` next to it:

```python
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                    # your tool module
sys.path.insert(0, os.path.dirname(_HERE))   # mcp_stdio
import mytool
from mcp_stdio import serve

def run(args: dict):
    return mytool.do_something(args["foo"])

TOOLS = {
  "do_something": {
    "description": "What it does and when to use it (the model reads this).",
    "inputSchema": {"type": "object",
                    "properties": {"foo": {"type": "string"}},
                    "required": ["foo"]},
    "handler": run,
  },
}
if __name__ == "__main__":
    serve("mytool", "1.0.0", TOOLS)
```

Then add it to [`.mcp.json`](../.mcp.json).

> **Golden rule:** a handler must never `print()` to stdout — stdout carries the
> protocol. Log to stderr (`print(..., file=sys.stderr)`).

---

## Troubleshooting

**Server doesn't appear in `/mcp`**
- Launch Claude Code from the repo root (relative paths in `.mcp.json`).
- Make sure you approved it when prompted.

**"command not found: python"**
- Use `python3` or (Windows) `py` in `.mcp.json` / the `claude mcp add` command.

**Tool call hangs on a big subnet**
- A /24 sweep pings 254 hosts; give it a few seconds, or scan a tighter CIDR.

**Manual smoke test (no Claude Code needed)**
```sh
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
 | python tools/netscan/mcp_server.py
```
You should get two JSON-RPC lines back (server info, then the tool list).
