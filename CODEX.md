# BMO Fridge Buddy Project Notes

This file keeps the design choices, learning notes, and implementation context
for the project. The public README is intentionally shorter.

## Project Summary

BMO Fridge Buddy is a Raspberry Pi 4 based IoT project that turns a mini fridge
into a simple smart appliance. It combines a temperature sensor, a small OLED
screen, barcode scanner input, a local inventory database, and a temperature log.

The main program is `bmo_fridge.py`. It is written as one readable Python script
so the full project flow stays easy to understand while learning.

## Hardware Plan

- Raspberry Pi 4 or compatible Raspberry Pi
- Raspberry Pi OS
- 0.96 inch SSD1306 I2C OLED display, 128x64
- waterproof DS18B20 temperature sensor
- 4.7k ohm resistor for the DS18B20 data line
- breadboard or wire connectors
- jumper wires
- USB barcode scanner that acts like a keyboard
- mini fridge or test cooler

## What The App Shows

The display shows a simple BMO-style face plus:

- current temperature in Fahrenheit
- temperature status
- total inventory count
- number of items expiring soon
- latest status message from scanner or expiration checks

Temperature status rules:

- `Normal` for 32 F through 40 F
- `Too Cold!` below 32 F
- `Too Warm!` above 40 F
- `No sensor` when no DS18B20 reading is available

## Why Python

Python is the standard choice for many Raspberry Pi projects because it has
mature hardware libraries and useful built-in modules. This project uses Python
for hardware access, SQLite, threading, CSV writing, date handling, and API
requests.

Keeping the project in one Python file also makes it easier to explain during a
demo. The tradeoff is that a larger production app would eventually be split
into modules.

## Why I2C For The OLED

The OLED screen uses I2C because it only needs two communication wires: SDA and
SCL. SPI can be faster, but it uses more wires and is unnecessary for a tiny
128x64 status display that updates every 2 seconds.

The Pi display dependency list is kept in `requirements-rpi.txt`:

```text
adafruit-blinka
adafruit-circuitpython-ssd1306
pillow
```

## Why DS18B20 For Temperature

The DS18B20 is a good fridge sensor because it is digital, waterproof, and
commonly used with Raspberry Pi projects. It uses 1-Wire, so it needs power,
ground, and one data line. The data line also needs a 4.7k ohm pull-up resistor.

When 1-Wire is enabled on Raspberry Pi OS, the sensor should appear under:

```text
/sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
```

The app reads that file directly in `read_temperature_c()`.

## Why SQLite

SQLite is built into Python and stores the whole inventory database in one local
file, `fridge.db`. There is no database server to install, which fits a project
running on one Raspberry Pi.

Inventory rows store:

- barcode
- product name
- quantity
- expiration date
- created timestamp
- updated timestamp

## Why CSV Temperature Logging

Temperature readings are written to `temperature_log.csv` because CSV is easy to
open in Excel, Google Sheets, or a plotting tool. Inventory needs updates and
queries, so it belongs in SQLite. Temperature history is simpler as append-only
log data.

## Why Threading

The barcode scanner is handled with `input()`, because most USB barcode scanners
act like keyboards. The problem is that `input()` blocks while waiting for a
scan.

The app uses a background daemon thread for scanner input so the main loop can
keep updating the display, reading temperature, logging CSV data, and checking
expiration dates.

Shared display state is kept in `AppState`. A `threading.Lock` protects that
state because both the main loop and scanner thread can read or update it.

## Why Hardware Fallbacks

The app catches OLED import/setup failures and falls back to terminal output.
The temperature reader returns `None` when the DS18B20 is not available.

That lets the software be developed and tested before the physical hardware is
ready. It also prevents a missing wire or missing Pi library from crashing the
entire app during a demo.

## Why Open Food Facts

Open Food Facts gives barcode-based food product data without requiring an API
key. When a barcode is scanned, the app asks Open Food Facts for a product name.
If the request fails or the barcode is unknown, the app still saves the item
with a fallback name like `Unknown item <barcode>`.

The app sends a custom User-Agent that includes the GitHub repo URL, which is
good API behavior and makes the project easier to identify.

## Timing Choices

- Display refresh: every 2 seconds
- Temperature CSV log: every 10 seconds
- Expiration check: every 30 seconds
- Expiring soon window: 3 days

The code uses `time.monotonic()` for repeated timing so the loop is not confused
if the system clock changes.

## Generated Files

These files are created while running the app and should stay out of Git:

- `fridge.db`
- `temperature_log.csv`
- `__pycache__/`

They are listed in `.gitignore`.

## Learning Checklist

- [ ] Explain why I2C was chosen for the OLED.
- [ ] Explain how the DS18B20 uses 1-Wire.
- [ ] Explain why the DS18B20 needs a 4.7k ohm resistor.
- [ ] Explain why SQLite fits this project.
- [ ] Explain why temperature history is logged to CSV.
- [ ] Explain what `input()` blocking means.
- [ ] Explain why a scanner thread is used.
- [ ] Explain what `daemon=True` does for the scanner thread.
- [ ] Explain why `AppState.lock` is needed.
- [ ] Explain why hardware fallback mode is useful.
- [ ] Explain what Open Food Facts does in the app.
- [ ] Explain why generated files should not be committed.
