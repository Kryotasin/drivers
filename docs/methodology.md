# Reverse-engineering methodology

How we go from "this device has no working driver" to a shippable override.
This is the generic loop; each device folder records the device-specific
findings. Nothing here involves cracking DRM or redistributing vendor code —
it's protocol observation and clean reimplementation for interoperability.

## The loop

```
observe → capture → decode → model → implement → verify → document
```

### 1. Observe

Figure out what you're dealing with before touching a wire.

- Identify the exact model and its connection options (USB, Wi-Fi, Ethernet).
- Find out what the device *claims* to speak: IPP? raw 9100? PCL/PostScript?
  a vendor raster format (Canon: BJNP + a proprietary raster)?
- Check what already exists upstream — don't reinvent:
  - OpenPrinting / foomatic database
  - Gutenprint (`gutenprint` supports many Canon models)
  - CUPS' built-in `everywhere` / driverless IPP
  - SANE / gphoto2 for scan/camera

If driverless IPP or Gutenprint already works, the "override" may just be a
tuned PPD — stop early.

### 2. Capture

Record the real conversation between the working vendor driver (on a machine
where it *does* work) and the device. You own the device; you're observing your
own traffic.

- **USB:** `usbmon` + Wireshark (Linux), or USBPcap + Wireshark (Windows).
  Scripts in [`../tools/capture/`](../tools/capture/).
- **Network (Wi-Fi/Ethernet):** Wireshark on the host, or a port mirror. Canon
  inkjets commonly use **BJNP** (UDP/TCP 8611/8612).
- Capture a *minimal* job: one page, known content (a single black line, a
  known color patch) so the bytes are easy to correlate.

**Sanitize** every capture before it goes in `captures/`: strip MAC/IP, serial
numbers, Wi-Fi creds, and any account/cloud tokens. See the sanitize helper in
`tools/capture/`.

### 3. Decode

Turn bytes into structure.

- Separate the *session* (discovery, status, open/close) from the *payload*
  (the actual raster/page data).
- Look for length-prefixed blocks, magic headers, repeated per-page framing.
- Diff two jobs that differ in exactly one variable (1 page vs 2; black vs
  color) to isolate what each field controls.
- Record findings as you go in the device's `reverse-engineering/` folder.

### 4. Model

Write down the protocol as a spec: packet types, field meanings, the raster
format, the state machine. This is the artifact that lets *anyone* reimplement
it — and it's the valuable part even before code exists.

### 5. Implement

Pick the thinnest thing that works:

- **Best case:** a CUPS PPD + `foomatic`/Gutenprint tuning — no new code.
- **Middle:** a CUPS **filter** (reads CUPS raster on stdin, emits the device's
  format on stdout) + a PPD.
- **Full:** a CUPS **backend** (talks the transport, e.g. BJNP) *and* a filter.

Keep it POSIX/CUPS-idiomatic so it drops into OpenPrinting-style setups.

### 6. Verify

A driver that "looks right" but misprints is worthless. Each device's `tests/`
documents:

- A reproducible test page and the expected physical result.
- Edge cases: margins, duplex, color vs grayscale, paper size.
- How to confirm status/ink queries (if implemented) return sane values.

### 7. Document

Update the device README + the root status table. A future user should be able
to go from "plugged in" to "printing" using only the folder.

## Tooling

See [`../tools/`](../tools/):
- `capture/` — traffic capture + sanitize helpers
- `decode/` — parsers that turn captures into structured notes
