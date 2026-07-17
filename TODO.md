# BMO Fridge Buddy TODO

## Do next: safe Pi bring-up

- [ ] Read the exact Raspberry Pi model printed on the board.
- [ ] Identify the fan model/type and its voltage before reconnecting it.
- [ ] With power unplugged, inspect the fan plug and GPIO wiring.
- [ ] Confirm the Pi boots; run `vcgencmd measure_temp` and note the result.
- [ ] Identify a 4.7 kOhm resistor with a multimeter (preferred) or color bands.
- [ ] Confirm the DS18B20 lead/pin order from its label or seller datasheet.
- [ ] Wire only the DS18B20 and its 4.7 kOhm pull-up first.
- [ ] Boot and confirm `/sys/bus/w1/devices/28-*/w1_slave` exists.
- [ ] Power down, add the OLED, boot, and locate it with `i2cdetect -y 1`.

## Put software on the Pi

- [ ] Install Git, `python3-venv`, and `i2c-tools`.
- [ ] Clone `https://github.com/FarhnChy/bmo_fridge_buddy.git`.
- [ ] Create `.venv` and install `requirements-rpi.txt` as shown in README.
- [ ] Enable I2C and 1-Wire in `sudo raspi-config`, then reboot.
- [ ] Run `python -m py_compile bmo_fridge.py` inside the virtual environment.
- [ ] Run `python bmo_fridge.py` and note any `[display]` or `[sensor]` message.

## Functional test

- [ ] OLED shows the BMO face, temperature, item count, soon count, and status.
- [ ] Temperature changes and is appended to `temperature_log.csv`.
- [ ] Test `help`, `list`, `expiring`, `remove <barcode>`, and `quit`.
- [ ] Confirm the USB barcode scanner types a barcode followed by Enter.
- [ ] Scan an item, enter an expiration date, and confirm it persists in SQLite.
- [ ] Confirm `fridge.db` and `temperature_log.csv` remain ignored by Git.

## Deployment and updates

- [ ] Decide whether manual startup is enough for the first demo.
- [ ] After manual testing is stable, add a systemd service for startup on boot.
- [ ] Test the documented `git pull --ff-only` update workflow on the Pi.
- [ ] Back up `fridge.db` before any database/schema migration.

## Project cleanup and proof

- [x] Git remote points to the project repository.
- [x] Open Food Facts User-Agent contains the repository URL.
- [x] README contains wiring, fan safety, installation, and update instructions.
- [ ] Review and commit the current `bmo_fridge.py`, README, and TODO changes.
- [ ] Push the final commit to GitHub before cloning/pulling it on the Pi.
- [ ] Capture a photo/video of the powered, working hardware.
- [ ] Capture terminal output showing the sensor, OLED, and app checks.
