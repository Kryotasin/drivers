# decode tools

Turn sanitized captures into structured protocol notes.

The job here is to separate **session framing** (discovery, open/close, status)
from **payload** (the raster/page data), then isolate what each byte field
means by diffing jobs that differ in exactly one variable.

- `bytediff.py` — align two hex dumps and highlight the bytes that differ.
  Point it at "1 page vs 2 pages" or "black vs color" captures to find the
  field that encodes that variable.

```sh
python -I bytediff.py jobA.hex jobB.hex
```

Record what you learn in the device's `reverse-engineering/NOTES.md`.
