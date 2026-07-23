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
- Graph recent temperature history with a highlighted 32-40 F safe band.
- Give BMO sleepy, happy, cold, and worried expressions based on temperature.

The main application is [bmo_fridge.py](bmo_fridge.py). Current progress,
remaining setup, wiring, testing, and update instructions are in
[TODO.md](TODO.md).

## Phone inventory and barcode scanner

The phone-friendly web app can scan a product barcode, look up its name with
Open Food Facts, save quantity and expiration date, list the fridge inventory,
remove items, and graph temperature history. Different expiration dates are
kept as separate batches even when the barcode is the same. The phone and OLED
share the same BMO mood rules; the physical OLED expressions still require
verification on the real screen.

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

## Install as an always-on Pi service

After testing both applications manually, install the web app, hardware
monitor, and daily backup timer:

```bash
cd ~/bmo_fridge_buddy
git pull --ff-only
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
bash scripts/install_pi_services.sh
```

The installer starts both applications after every boot and immediately makes
a verified inventory backup. It then keeps 14 daily backups in
`~/bmo_fridge_backups`. Check them with:

```bash
sudo systemctl status bmo-fridge-web bmo-fridge-monitor bmo-fridge-backup.timer
ls -lh ~/bmo_fridge_backups
```

These copies protect against accidental database changes or corruption. They
remain on the same SD card, so occasionally copy the backup folder to another
computer if protection from complete SD-card failure matters.

## Private trusted HTTPS for live scanning

The recommended HTTPS option is Tailscale Serve. It keeps BMO private to your
Tailscale devices, provides a trusted certificate, and lets the web server
listen only on the Pi itself. Install Tailscale on the Pi and phone, sign both
into the same account, then run on the Pi:

```bash
sudo tailscale up
cd ~/bmo_fridge_buddy
bash scripts/enable_tailscale_https.sh
```

The command prints the private `https://...ts.net` address to open on the
phone. Do not enable Tailscale Funnel; this project is intended to remain
private rather than publicly accessible.
