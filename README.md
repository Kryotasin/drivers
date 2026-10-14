# drivers

Community **driver overrides, de-cloud guides, and tools** for consumer hardware
whose vendor software is missing, broken, platform-locked, cloud-dependent, or
abandoned.

Everything here is designed to be **cloned and run with nothing but Python** (or
followed as a written guide). Grab the one project you need and go — each has
its own README. The goal is **interoperability**: making hardware you already
own keep working, locally and across the years after the vendor stops caring.

> Interoperability / repair / privacy work only. We document protocols and build
> drivers/tools for devices people own. We do **not** redistribute vendor
> firmware or binaries, defeat DRM, or help anyone touch hardware they don't
> own. See [LICENSE](LICENSE) (GPL-2.0) and
> [docs/legal-and-ethics.md](docs/legal-and-ethics.md).

---

## Quick start

### Requirements
- **Python 3.8 or newer** — that's it. Every tool here is **standard-library
  only**: no `pip install`, no virtualenv, no build step.
- Check your version:
  ```sh
  python --version      # or: python3 --version
  ```

### Option A — clone the whole repo (recommended)
```sh
git clone https://github.com/Kryotasin/drivers.git
cd drivers

# run a tool, e.g. the network scanner:
python tools/netscan/netscan.py
```

### Option B — download and run a single tool (no git)
Every tool is one self-contained file. You can grab just the one you want:
```sh
# download netscan.py only, then run it
curl -O https://raw.githubusercontent.com/Kryotasin/drivers/main/tools/netscan/netscan.py
python netscan.py
```
Or use **Code → Download ZIP** on GitHub, unzip, and run the script directly.

> On most systems the command is `python`. If that's Python 2 (rare now), use
> `python3` instead. On Windows, `python` works in PowerShell and CMD.

---

## Projects

Each project is independent. Click into its folder for full instructions.

### 🛠 Tools (clone & run)

| Tool | What it does | Run it |
|------|--------------|--------|
| **[netscan](tools/netscan/)** | Discover every device on a network you control, decode each MAC's vendor, and classify it by de-cloud/local-control potential. "RE step 0." | `python tools/netscan/netscan.py` |
| **[capture](tools/capture/)** | Capture + sanitize USB/network traffic from a device (for protocol RE). | see folder README |
| **[decode](tools/decode/)** | Diff two captures to isolate protocol fields. | `python tools/decode/bytediff.py a b` |

### 📠 Devices (guides & overrides)

| Device | What's here | Status |
|--------|-------------|--------|
| **[hp-deskjet-3755](devices/hp-deskjet-3755/)** | Driverless setup + **post-Instant-Ink independence guide** (run on your own ink, no HP cloud). | 🟢 working |

### 📚 Docs (read these)

| Doc | When to read it |
|-----|-----------------|
| **[network-recon.md](docs/network-recon.md)** | Finding + triaging what's on your network (start here) |
| **[methodology.md](docs/methodology.md)** | Reverse-engineering a device from scratch |
| **[contributing.md](docs/contributing.md)** | Adding a device or tool |
| **[legal-and-ethics.md](docs/legal-and-ethics.md)** | The ground rules — read before contributing |

---

## What "override" means here

A device folder can ship any of:

- **PPD / filter overrides** — CUPS PPDs or print filters that make a printer
  work (or work better) than the stock driver.
- **De-cloud guides** — reclaim a device from its vendor cloud/subscription for
  local control (e.g. the HP post-Instant-Ink guide).
- **Protocol notes** — reverse-engineered docs of how a device talks.
- **Tools** — reusable scripts (like `netscan`) that help across many devices.

## Repository layout

```
drivers/
├── tools/
│   ├── netscan/             # device discovery + de-cloud triage (Python, runnable)
│   ├── capture/             # capture + sanitize device traffic
│   └── decode/              # parse captures into protocol notes
├── devices/
│   └── hp-deskjet-3755/     # per-device guides/overrides
│       ├── override/              # the shippable guide/PPD/filter
│       ├── reverse-engineering/   # protocol notes
│       ├── captures/              # sanitized sample captures only
│       └── tests/                 # how we verify it works
├── docs/                    # methodology, recon, contributing, legal/ethics
├── LICENSE                  # GPL-2.0
└── README.md                # you are here
```

## License

GPL-2.0. See [LICENSE](LICENSE). By contributing you agree your contribution is
licensed under the same terms.
