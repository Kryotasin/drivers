# capture tools

Capture the conversation between a working vendor driver and your own device,
then **sanitize** before committing anything to a `captures/` folder.

## USB

### Windows (your current OS)
1. Install [USBPcap](https://desowin.org/usbpcap/) + Wireshark.
2. Start USBPcap on the printer's root hub, print one known-content page.
3. Save as `.pcapng`, then sanitize (below).

### Linux
```sh
sudo modprobe usbmon
# find the bus, then:
sudo tshark -i usbmonX -w capture.pcapng
```

## Network (Canon BJNP etc.)
Canon inkjets often discover over **UDP 8611** and send data over **TCP/UDP
8612**. Capture on the host that runs the vendor driver:
```sh
tshark -i <iface> -f "udp port 8611 or tcp port 8612 or udp port 8612" -w bjnp.pcapng
```

## Sanitize (mandatory before commit)

Run `sanitize.py` to strip network identifiers and flag likely serials. It does
NOT magically remove document content — use a one-page known-content test page,
never a real document.

```sh
python -I sanitize.py bjnp.pcapng
```
