# HP DeskJet 3755 — notes

Not a reverse-engineering target. The protocol is already open:

- **Driverless IPP** (AirPrint / Mopria / IPP Everywhere) — works with no vendor
  driver on Windows, macOS, iOS, Android, and modern Linux/CUPS.
- **HPLIP** — HP's open-source Linux driver stack fully supports this model
  (print + scan + ink status).

There is nothing to capture or decode here. If this printer misbehaves it's a
setup/spooler/network issue, not a missing driver. See the device README for
the working setup paths and reset procedures.

For actual reverse-engineering practice, pick a device with NO upstream support
(an abandoned scanner, an odd label/receipt printer, a camera with no Linux
tethering). Then use ../../../docs/methodology.md.
