# Reclaiming an HP DeskJet 3755 after Instant Ink

Goal: keep the printer working with **your own third-party HP 65XL-compatible
cartridges**, with **no HP account, no HP Smart dependency, and no subscription
re-checks** — while making sure HP firmware can't later lock out non-HP ink.

This is owner-side repair/independence: swapping your own consumables and
turning off cloud features on hardware you own. It does **not** defeat cartridge
authentication or any access control — it works *with* compatible cartridges and
simply declines firmware changes.

## Scope

- Printer: HP DeskJet 3755 (prints fine today; Instant Ink already cancelled).
- Ink going forward: third-party / compatible **HP 65XL** cartridges.
- OS for printing: Windows 11 (driverless IPP). Linux equivalents noted.

---

## 1. Stop firmware from locking out third-party ink (do this FIRST)

HP's *Dynamic Security* firmware can start rejecting non-HP chips after an
update. Since you're running compatible 65XL, disable automatic firmware
updates **before** they can land:

- **HP Smart** (if still installed): *Printer Settings → Advanced / Printer
  Update → set firmware updates to "Do not check" / disable auto-update.*
- **Embedded Web Server (EWS):** browse to the printer's IP (find it via your
  router or print a config page by holding the printer's **Resume**/✕ button —
  see device README). In EWS: *Web Services / Printer Update → disable automatic
  updates.*

> Rule of thumb: never accept a 3755 firmware update while depending on
> compatible ink. An update is the main thing that can brick third-party carts.

## 2. Install the third-party 65XL cartridges

- Remove any remaining Instant Ink cartridges entirely (they're disabled).
- Install your compatible 65XL set.
- Expect a one-time warning like "non-HP / used cartridge" — acknowledge it
  (press the on-printer button it prompts for). A *persistent* reject usually
  means Dynamic Security firmware is already on the unit; see Troubleshooting.

## 3. Cut the cloud tether (Web Services)

Severs the Instant Ink / ePrint link that keeps phoning home:

- In **EWS → Web Services**, choose **Remove Web Services** (or Disable).
- Power-reset after: with printer ON, unplug its power cord, wait 60s, replug.

Your HP account no longer has any hold on the device.

## 4. Print without HP software (driverless IPP)

You do not need HP Smart or an HP account to print.

### Windows 11
1. *Settings → Bluetooth & devices → Printers & scanners → Add device.*
2. Over Wi-Fi the 3755 is discovered and added via the built-in **IPP class
   driver** — no HP download.
3. Print a test page.

(You can uninstall HP Smart if you don't need scanning. If you *do* scan, keep
HP Smart or use Windows Fax & Scan / `WSD`.)

### Linux
```sh
lpadmin -p deskjet3755 -E -v ipp://<printer-ip>/ipp/print -m everywhere
# or full features: sudo hp-setup -i   (HPLIP)
```

## 5. Verify independence

- [ ] Prints a test page over IPP with HP Smart closed / uninstalled.
- [ ] Web Services shows removed/disabled in EWS.
- [ ] Firmware auto-update is OFF.
- [ ] Compatible 65XL cartridges accepted (warning dismissed, printing works).

---

## Troubleshooting

- **"Cartridge problem" / won't accept compatible ink:** Dynamic Security
  firmware is likely present. Options: (a) reseat / try a different compatible
  brand with a newer chip, (b) use genuine HP 65XL, or (c) check whether the
  cartridge vendor ships a firmware-compatible chip revision. Do **not** install
  further firmware hoping to fix it — that typically makes it stricter.
- **Printer keeps re-adding cloud / asking for HP account:** confirm Web
  Services was *removed* (not just signed out) in EWS, then power-reset.
- **Still shows Instant Ink errors:** make sure every Instant Ink cartridge is
  physically removed, then power-reset.

## Notes

- Keeping HP Smart solely for scanning is fine; it doesn't re-enable the
  subscription on its own once Web Services is removed.
- This guide is interoperability/independence only. It does not modify,
  circumvent, or crack cartridge chips or firmware signing.
