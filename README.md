# BMO Fridge Buddy

BMO Fridge Buddy is a Raspberry Pi mini-fridge monitor with a small BMO-style
OLED status screen.

It reads fridge temperature from a DS18B20 sensor, shows the current status on
an SSD1306 I2C OLED, tracks scanned food inventory in SQLite, and writes
temperature history to a CSV file.

GitHub repo: https://github.com/FarhnChy/bmo_fridge_buddy

## What It Does

- Shows a BMO-style face and fridge status on a 128x64 OLED screen.
- Reads temperature from a waterproof DS18B20 sensor when connected.
- Labels the fridge as `Normal`, `Too Cold!`, `Too Warm!`, or `No sensor`.
- Lets a USB barcode scanner add items by typing a barcode and pressing Enter.
- Looks up scanned products through the Open Food Facts API.
- Stores inventory in `fridge.db`.
- Logs temperature readings to `temperature_log.csv`.
- Runs in terminal mode on a regular computer when Raspberry Pi hardware is not
  connected.

## Main File

The app runs from:

```bash
python bmo_fridge.py
```

Terminal/scanner commands:

```text
<barcode>           scan/add an item
remove <barcode>    remove one item
list                show inventory
expiring            show items expiring soon
help                show commands
quit                stop the program
```

## Raspberry Pi Setup

Install the Pi display dependencies:

```bash
python -m pip install -r requirements-rpi.txt
```

The OLED uses I2C through the Pi SDA/SCL pins. The DS18B20 uses Raspberry Pi OS
1-Wire support and should appear at a path like:

```text
/sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
```

Generated runtime files are ignored by Git:

- `fridge.db`
- `temperature_log.csv`
- `__pycache__/`
