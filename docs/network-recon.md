# Network reconnaissance (RE step 0)

Before decoding a protocol or de-clouding a gadget, you need an inventory: what
is on the network, what each thing *is*, and whether it's even worth your time.
This is the recon step, and [`../tools/netscan/`](../tools/netscan/) automates
it.

> Only scan networks you own or are authorized to test. See
> [legal-and-ethics.md](legal-and-ethics.md).

## The recon loop

```
sweep → list MACs → decode vendor → name/guess device → classify → triage
```

### 1. Sweep + list
A ping sweep populates the OS ARP/neighbor table; reading it back gives live
`IP → MAC` pairs. `netscan` does both in one pass.

### 2. Decode the MAC (OUI)
The first 3 octets of a MAC are the **OUI** — the registered
manufacturer/module vendor. Decode it (offline map or an OUI API). Caveats:

- OUI is the **chip/module** vendor, not always the product brand. Cheap IoT
  ships generic modules (Espressif, Realtek, FN-Link), so "Espressif" really
  means "some ESP-based smart device."
- **Randomized MACs:** phones/laptops rotate MACs for privacy. A
  locally-administered MAC (2nd hex digit is `2`, `6`, `A`, or `E`) usually
  means a personal device, not an IoT target.

### 3. Name / guess
Reverse-DNS and NetBIOS names sometimes reveal the product (e.g. an HP printer
announces `HPxxxxxx`). Combine with the OUI to guess.

### 4. Classify by de-cloud potential
This is the triage that matters. Map each device to one of:

| Verdict | Act on it? |
|---------|-----------|
| `yes` / `likely` | 🟢 Local control achievable — do it |
| `partial` / `maybe` / `depends` | 🟡 Conditional — check the model |
| `no` | 🔴 Cloud-locked — skip |
| `n/a` | Printer driver / personal device — not a target |

The verdict + a concrete next step (which open project) is baked into
`netscan`'s `CLASSIFY_RULES`. Extend those rules as you identify new hardware.

### 5. Triage
Spend effort where the verdict is `yes`/`likely`. Don't burn days pioneering a
`no` (cloud-locked) device when a supported alternative exists.

## From recon to action

Once a device is classified `yes`/`likely`, move to the right workflow:

- **Local-API devices** (Kasa, Roku, Sonos) → talk to the existing API.
- **Reflashable** (ESP/Tuya) → ESPHome/Tasmota (tuya-convert / tuya-cloudcutter).
- **Radio devices** (Zigbee/Z-Wave/Matter) → a local hub (Zigbee2MQTT / Z-Wave JS).
- **Unknown protocol** → capture + decode via [methodology.md](methodology.md).

## Output hygiene

A scan report is a map of your home network. Keep `--json`/`--markdown` output
out of any public repo (the repo `.gitignore` already excludes it).
