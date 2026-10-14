# Legal & ethics

This project exists to keep hardware people own working. That intent sets hard
boundaries on what goes in this repo.

## What this project is

- **Interoperability and repair.** Documenting how a device communicates and
  writing a clean, independent driver so the owner can use it. In many
  jurisdictions reverse-engineering for interoperability is explicitly
  permitted (e.g. EU Software Directive Art. 6; US DMCA §1201 has
  interoperability and repair exemptions). This is the same tradition as CUPS,
  Gutenprint, SANE, gphoto2, and Nouveau.

## What we will NOT do / accept

- **No redistributing vendor material.** No vendor firmware images, no vendor
  driver binaries, no decompiled vendor source, no extracted vendor data files
  (color tables, firmware blobs) pasted into this repo.
- **No DRM/access-control circumvention.** We observe protocols on hardware we
  own; we don't defeat signing, licensing locks, or region/cartridge DRM to
  enable unauthorized access.
- **No secrets in captures.** Every capture committed here must be sanitized:
  no serial numbers, MAC/IP, Wi-Fi/cloud credentials, account tokens, or
  personal document content. Use a one-page known-content test, not a real
  document.
- **Clean-room where it matters.** Protocol *facts* (field X is the page count)
  are fine to record. Copying expression from decompiled vendor code is not.

## Contributor checklist

Before you open a PR, confirm:

- [ ] I own (or am authorized to use) the device I captured.
- [ ] No vendor binaries/firmware/decompiled source are included.
- [ ] Captures are sanitized (no serials, network IDs, creds, personal docs).
- [ ] My contribution is my own work, licensed GPL-2.0.

If you're unsure whether something crosses a line, open an issue and ask before
committing it.
