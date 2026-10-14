# drivers

Community **driver overrides** for consumer hardware whose vendor drivers are
missing, broken, platform-locked, or abandoned.

Each device lives in its own folder under [`devices/`](devices/) and is designed
to be usable on its own — grab the one you need, follow its README, done. The
goal is **interoperability**: making hardware you already own keep working,
across operating systems and across the years after the vendor stops caring.

> This is interoperability / repair work. We document protocols and build
> drivers so people can use devices they own. We do **not** redistribute
> vendor firmware, vendor driver binaries, or anything we don't have the right
> to share. See [LICENSE](LICENSE) (GPL-2.0) and
> [docs/legal-and-ethics.md](docs/legal-and-ethics.md).

## What "override" means here

A device folder can ship any of:

- **PPD / filter overrides** — CUPS PPDs, `foomatic` snippets, or print filters
  that make a printer work (or work *better*) than the stock driver.
- **Protocol notes** — reverse-engineered documentation of how the device
  talks (USB, BJNP, PTP, raster formats, status/ink queries).
- **Quirk patches** — small patches/udev rules/config that fix a specific
  broken behavior.
- **Standalone drivers** — a full filter/backend when nothing upstream exists.

## Layout

```
drivers/
├── devices/
│   └── hp-deskjet-3755/      # reference entry (already supported upstream)
│       ├── reverse-engineering/   # protocol notes, decoded dumps
│       ├── captures/              # sanitized sample captures
│       ├── override/              # the shippable driver/PPD/filter
│       └── tests/                 # how we verify it actually prints
├── tools/
│   ├── capture/              # scripts to capture USB/network traffic
│   └── decode/              # scripts to parse captures into notes
├── docs/                    # shared methodology + legal/ethics
└── LICENSE                  # GPL-2.0
```

## Status

| Device         | Stage               | Works? |
|----------------|---------------------|--------|
| hp-deskjet-3755 | 🟢 de-subscription / local-only guide | yes — driverless |

## Getting started

- Reverse-engineering a device from scratch → [docs/methodology.md](docs/methodology.md)
- Contributing a device or fix → [docs/contributing.md](docs/contributing.md)
- The ground rules → [docs/legal-and-ethics.md](docs/legal-and-ethics.md)

## License

GPL-2.0. See [LICENSE](LICENSE). By contributing you agree your contribution is
licensed under the same terms.
