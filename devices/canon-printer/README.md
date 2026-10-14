# canon-printer

Override driver for Canon inkjet/PIXMA-class printers that lack a good
cross-platform driver.

> **Model:** _TODO — fill in exact model, e.g. Canon PIXMA G3010_
> **Transport:** _TODO — USB and/or network (Canon inkjets often use BJNP over
> UDP/TCP 8611/8612)_
> **Stage:** 🟡 reverse-engineering

## Why this exists

_TODO: one line on what's broken — e.g. "vendor driver is Windows-only / 32-bit
only / missing on this OS / drops color profiles."_

## Before anything: check if you even need this

Try the no-code paths first (see [../../docs/methodology.md](../../docs/methodology.md) step 1):

- **Driverless IPP:** `lpadmin -p canon -E -v ipp://<printer>/ipp/print -m everywhere`
- **Gutenprint:** many Canon models already supported — check
  `lpinfo -m | grep -i canon`.

If one of those prints correctly, your "override" may just be a tuned PPD and
you can skip the hard part. Record the result in `reverse-engineering/`.

## Layout

- `reverse-engineering/` — protocol notes, decoded raster format, findings
- `captures/` — **sanitized** sample captures only
- `override/` — the shippable PPD / CUPS filter / backend
- `tests/` — test page + expected physical result

## Current findings

_Nothing decoded yet. See [reverse-engineering/NOTES.md](reverse-engineering/NOTES.md)._

## Install / usage

_TODO once `override/` has something runnable._

## Known limitations

_TODO._
