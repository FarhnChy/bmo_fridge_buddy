# BMO Fridge Buddy TODO

Updated: 2026-07-02
Hardware pickup target: 2026-07-03

## Current Status

- [x] Main app exists in `bmo_fridge.py`.
- [x] Local terminal fallback works when OLED/sensor hardware is unavailable.
- [x] SQLite inventory support is implemented.
- [x] Open Food Facts barcode lookup is implemented.
- [x] Temperature CSV logging is implemented.
- [x] Expiring-soon inventory checks are implemented.
- [x] Raspberry Pi OLED dependencies are listed in `requirements-rpi.txt`.
- [x] Generated files are ignored by Git.

## Before Getting Hardware

- [ ] Confirm parts list:
  - Raspberry Pi 4 or compatible Raspberry Pi
  - microSD card with Raspberry Pi OS
  - Pi power supply
  - 0.96 inch SSD1306 I2C OLED display, 128x64
  - waterproof DS18B20 temperature sensor
  - 4.7k ohm resistor for the DS18B20 data line
  - breadboard or wire connectors
  - jumper wires
  - USB barcode scanner that works as keyboard input
  - mini fridge or test cooler
- [ ] Make sure the OLED is the I2C version, not the SPI-only version.
- [ ] Make sure the DS18B20 is the digital 1-Wire sensor, not an analog
  temperature sensor.

## Raspberry Pi Setup

- [ ] Clone or copy this repo onto the Raspberry Pi.
- [ ] Install dependencies:

```bash
python -m pip install -r requirements-rpi.txt
```

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

## Final Submission Check

- [ ] Check changed files:

```bash
git status --short
```

- [ ] Do not commit generated runtime files:
  - `fridge.db`
  - `temperature_log.csv`
  - `__pycache__/`
- [ ] Commit final project files:

```bash
git add README.md CODEX.md TODO.md bmo_fridge.py requirements-rpi.txt
git commit -m "Finish BMO fridge buddy project"
git push
```

- [ ] Take a photo or short video of the wired project running.
- [ ] Save terminal output or a screenshot showing the app running.
