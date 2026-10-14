# Canon printer — reverse-engineering notes

Living log. Append findings as you decode them. Keep facts, not guesses, in the
"Confirmed" sections; park hunches under "Open questions".

## Device facts

- Model: _TODO_
- Firmware version: _TODO_
- Connection(s): _TODO (USB / Wi-Fi / Ethernet)_
- What the vendor driver runs on (where capture was taken): _TODO_

## Transport

- [ ] USB — interface/endpoint layout: _TODO_
- [ ] Network — protocol + ports: _TODO (BJNP? UDP 8611 discovery / TCP 8612 data?)_

### BJNP (if network) — confirmed

_TODO: discovery packet shape, session open/close, data framing._

## Page / raster format

- [ ] Header / magic: _TODO_
- [ ] Per-page framing: _TODO_
- [ ] Color planes / compression: _TODO_
- [ ] Known-content correlation (single black line → which bytes): _TODO_

## Status / ink queries

_TODO: does the device expose ink levels / status, and how is it requested?_

## Open questions

- _TODO_

## Capture index

| file (in ../captures/) | job described | sanitized? |
|------------------------|---------------|------------|
| _none yet_             |               |            |
