# BMO Fridge Buddy

BMO Fridge Buddy is a Raspberry Pi project that turns a mini fridge into a
simple smart fridge monitor inspired by BMO from *Adventure Time*.

I wanted to build this project to learn more about Raspberry Pi hardware,
Python, sensors, displays, databases, and working with real electronic
components. It also gives the mini fridge a fun BMO-style face while making it
more useful.

The finished project will:

- Read the fridge temperature with a waterproof DS18B20 sensor.
- Show a BMO face, temperature, and fridge status on an OLED screen.
- Report whether the fridge is too cold, normal, or too warm.
- Accept barcodes typed manually, scanned with a phone, or scanned from an
  optional USB scanner.
- Look up product names using Open Food Facts.
- Store food quantities and expiration dates in a local SQLite database.
- Warn about food that is expiring soon.
- Save temperature history to a CSV file.

The main application is [bmo_fridge.py](bmo_fridge.py). Current progress,
remaining setup, wiring, testing, and update instructions are in
[TODO.md](TODO.md).

## Phone inventory and barcode scanner

The phone-friendly web app can scan a product barcode, look up its name with
Open Food Facts, save quantity and expiration date, list the fridge inventory,
and remove items. Different expiration dates are kept as separate batches even
when the barcode is the same.

On the Raspberry Pi:

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
python web_app.py
```

The terminal prints an address such as `http://192.168.1.25:5000`. Open that
address from a phone on the same private Wi-Fi. Manual barcode entry and the
**Take photo** option work from this local page. The ZXing barcode reader is
stored in this repository, so the scanner itself loads without internet
access. Product-name lookup still needs internet and falls back to an editable
`Unknown item` name when offline. Continuous **Live scan** camera access
requires a trusted HTTPS certificate because mobile browsers block live camera
streams on insecure pages.

For HTTPS, set paths to a trusted certificate and matching private key before
starting the server:

```bash
export BMO_TLS_CERT=/path/to/certificate.pem
export BMO_TLS_KEY=/path/to/private-key.pem
python web_app.py
```

Keep this development server on a trusted home network. Do not expose it
directly to the public internet; Version 2 does not yet include user accounts.
