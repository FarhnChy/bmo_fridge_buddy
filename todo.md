# BMO Fridge Buddy TODO

Updated: 2026-07-07

## Project Goal

BMO Fridge Buddy is a Raspberry Pi mini-fridge project inspired by BMO from
Adventure Time.

The project should:

- read the real temperature inside a mini fridge
- show a simple BMO-style face on a small OLED screen
- warn when the fridge is too cold or too warm
- scan food items with a USB barcode scanner
- save item names, quantities, and expiration dates
- keep a temperature log that can be opened later in a spreadsheet

## Current Status

- [x] Main app exists in `bmo_fridge.py`.
- [x] Code is kept as one readable Python file.
- [x] Terminal fallback works when OLED/sensor hardware is unavailable.
- [x] SQLite inventory support is implemented.
- [x] Open Food Facts barcode lookup is implemented.
- [x] Temperature CSV logging is implemented.
- [x] Expiring-soon inventory checks are implemented.
- [x] Raspberry Pi dependencies are listed in `requirements-rpi.txt`.
- [x] Generated files are ignored by Git.
- [x] Extra project notes were merged into this TODO file.

## Files

- `bmo_fridge.py`: main program to run on the Pi.
- `README.md`: short project description.
- `todo.md`: setup notes, checklist, and learning notes.
- `requirements-rpi.txt`: Pi-only Python packages for the OLED screen.
- `fridge.db`: local SQLite inventory database created when the app runs.
- `temperature_log.csv`: local temperature history created when the app runs.

Do not commit `fridge.db`, `temperature_log.csv`, or `__pycache__/`. They are
local output files and are already listed in `.gitignore`.

## Do I Need To Make A Separate App?

Not for the first finished version.

The Python script is already the app. The barcode scanner works like keyboard
input, the OLED is the display, and SQLite stores the inventory.

A separate web app or mobile app would only be needed later if you want to view
or edit the fridge inventory from another device. For now, finish the Pi
version first and document it well.

Optional later idea:

- [ ] Add a small web page on the Pi to view inventory and expiration dates from
      a phone or laptop.

## Hardware Parts

Already have:

- [x] Raspberry Pi 4 or compatible Raspberry Pi
- [x] microSD card
- [x] Pi power supply
- [x] mini fridge or test cooler

Still need:

- [ ] 0.96 inch SSD1306 I2C OLED display, 128x64
- [ ] waterproof DS18B20 temperature sensor
- [ ] 4.7k ohm resistor for the DS18B20 data line
- [ ] breadboard or wire connectors
- [ ] jumper wires
- [ ] USB barcode scanner that works as keyboard input
- [ ] Make sure the OLED is the I2C version, not the SPI-only version.
- [ ] Make sure the DS18B20 is the digital 1-Wire sensor, not an analog
      temperature sensor.
- [ ] Install Raspberry Pi OS on the microSD card if it is not already set up.

## Raspberry Pi Setup

- [ ] Clone or copy this repo onto the Raspberry Pi.
- [ ] From the project folder, install the Pi display dependencies:

```bash
python -m pip install -r requirements-rpi.txt
```

`requirements-rpi.txt` is needed because the OLED screen uses packages that are
not built into Python:

- `adafruit-blinka`
- `adafruit-circuitpython-ssd1306`
- `pillow`

- [ ] Enable I2C for the OLED.
- [ ] Enable 1-Wire for the DS18B20.
- [ ] Reboot after enabling hardware interfaces.
- [ ] Confirm the temperature sensor appears at:

```text
/sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
```

## Hardware Test

- [ ] Run the app on the Pi:

```bash
python bmo_fridge.py
```

- [ ] Confirm the OLED shows the BMO-style face.
- [ ] Confirm the OLED shows temperature in Fahrenheit.
- [ ] Confirm temperature status changes correctly:
  - `Normal` from 32 F through 40 F
  - `Too Cold!` below 32 F
  - `Too Warm!` above 40 F
  - `No sensor` when no sensor is detected
- [ ] Confirm `temperature_log.csv` is created and receives readings.
- [ ] Confirm the barcode scanner types the barcode and presses Enter.
- [ ] Scan one item and enter an expiration date.
- [ ] Run `list` and confirm the item appears.
- [ ] Run `expiring` and confirm expiring items appear when expected.
- [ ] Run `remove <barcode>` and confirm the quantity updates.

## Learning Notes

Python is used because Raspberry Pi hardware libraries are mature, and Python
already includes SQLite, CSV writing, dates, threading, and file handling.

The OLED uses I2C because it only needs two communication wires, SDA and SCL.
That is simpler than SPI for a small 128x64 screen.

The DS18B20 temperature sensor uses Raspberry Pi OS 1-Wire support. It is a
good fridge sensor because it is digital and waterproof. The data line needs a
4.7k ohm pull-up resistor.

SQLite stores inventory in `fridge.db`. This is simpler than running a full
database server on the Pi. The file is created automatically when the app runs.

Temperature readings go to `temperature_log.csv` because CSV is easy to open in
Excel, Google Sheets, or another graphing tool.

The scanner uses `input()` because most USB barcode scanners act like keyboards.
The scanner listener runs in a background thread so the display can keep
updating while the app waits for scans.

Open Food Facts is used to look up product names from barcodes. If the API does
not return a product, the app still saves the barcode with an unknown-item name.

## Documentation Checklist

- [ ] Take photos of the parts before wiring.
- [ ] Take photos of the final wiring.
- [ ] Take a photo or short video of the OLED running on the fridge.
- [ ] Save a screenshot or terminal output showing the app running.
- [ ] Document what worked.
- [ ] Document what was difficult or changed during the build.
- [ ] Explain what `requirements-rpi.txt` installs.
- [ ] Explain that `fridge.db` is the local inventory database.
- [ ] Explain that `temperature_log.csv` is the temperature history.
- [ ] Keep the README short and focused on what the project is and why it was
      built.

## Final Git Check

- [ ] Check changed files:

```bash
git status --short
```

- [ ] Make sure generated runtime files are not staged:
  - `fridge.db`
  - `temperature_log.csv`
  - `__pycache__/`
- [ ] Commit final project files:

```bash
git add README.md todo.md bmo_fridge.py requirements-rpi.txt .gitignore
git commit -m "Finish BMO fridge buddy project"
git push
```

## After This Project

- [ ] Start the router project in a separate repo or separate folder.
- [ ] Create a new TODO file for the router project instead of mixing it into
      this fridge project.
