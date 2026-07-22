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
