# Contributing

Thanks for helping keep hardware alive. Read
[legal-and-ethics.md](legal-and-ethics.md) first — the boundaries there are
non-negotiable.

## Adding a new device

1. Copy the structure of an existing device folder under `devices/`:
   ```
   devices/<vendor>-<type>/
   ├── README.md              # model(s), status, how to use
   ├── reverse-engineering/   # protocol notes, decoded findings
   ├── captures/              # SANITIZED sample captures only
   ├── override/              # the shippable PPD/filter/backend
   └── tests/                 # test page + expected result
   ```
2. Use `<vendor>-<type>` naming (e.g. `canon-printer`, `canon-camera`,
   `epson-scanner`). If one driver covers many models, list them in the README.
3. Follow [methodology.md](methodology.md) for the capture → decode → implement
   loop.

## Device README must answer

- Which exact models this covers.
- What transport/protocol it uses.
- Current stage (reverse-engineering / partial / working).
- Install + usage steps for an end user.
- Known limitations.

## PR expectations

- One device (or one fix) per PR where practical.
- Captures sanitized; no vendor binaries/firmware.
- Update the status table in the root [README](../README.md).
- State how you tested it (which model, what printed).

## Status labels

- 🔴 **planned** — folder/notes only, nothing works yet.
- 🟡 **reverse-engineering** — protocol being decoded.
- 🟢 **working** — produces correct output on at least one real device.
