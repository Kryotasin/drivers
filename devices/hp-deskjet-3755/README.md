# hp-deskjet-3755

HP DeskJet 3755 (All-in-One inkjet, part of the DeskJet 3700 series).

> **Transport:** USB + Wi-Fi. Speaks **driverless IPP** (AirPrint / Mopria /
> IPP Everywhere) and is fully covered by **HPLIP** on Linux.
> **Stage:** 🟢 already supported upstream — no reverse-engineering needed.

## Reality check: you (almost certainly) don't need a custom driver

The 3755 is one of the best-supported consumer printers for interoperability.
Before writing anything, use one of the paths that already works:

### Windows (your OS)
- Windows 10/11 ship an **IPP class driver**. Add the printer via
  *Settings → Bluetooth & devices → Printers & scanners → Add device*; over
  Wi-Fi it's discovered automatically.
- Or install **HP Smart** (Microsoft Store) for full features (scan, ink).

### macOS / iOS / Android
- **AirPrint** (Apple) / **Mopria** (Android) — zero driver install.

### Linux
- **Driverless:** `lpadmin -p deskjet3755 -E -v ipp://<printer-ip>/ipp/print -m everywhere`
- **HPLIP:** `sudo hp-setup -i` (interactive) — full scan + ink support.

If any of the above prints correctly, there is nothing to build here.

## So why is this folder in the repo?

Two legitimate reasons, both small:
1. **Known-good setup notes** — a reference entry so others with a 3755 land on
   the working path immediately instead of hunting HP forums.
2. **Optional tuned PPD** — if the driverless/HPLIP defaults get margins or
   color wrong for a specific use, a small PPD override can live in `override/`.

This is **not** a reverse-engineering target — the protocol is already open
(HPLIP). For RE practice, pick a device with no upstream support.

## Reset procedures (control-panel has no screen — button combos only)

- **Power reset (fixes most stuck states):** with printer ON, unplug the cord
  from the printer, wait 60s, replug, power on. No settings lost.
- **Wi-Fi/network reset:** hold **Wireless + Cancel (✕)** ~3s until the wireless
  light blinks; reconnect via WPS (hold Wireless ~3s, press WPS on router within
  ~2 min).
- **Full factory reset (also clears EWS admin password):** a Power + buttons
  combo held ~20s — exact sequence not confirmed in official docs; verify
  against HP support for your unit before relying on it.

## Known limitations

- No reverse-engineering notes needed; `reverse-engineering/` is intentionally
  minimal for this device.
