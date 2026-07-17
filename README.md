# BMO Fridge Buddy

BMO Fridge Buddy turns a Raspberry Pi 4 into a mini-fridge monitor. It reads a
DS18B20 temperature probe, shows status on a 128x64 SSD1306 I2C OLED, logs
temperatures to CSV, and tracks barcode-scanned food in SQLite.

Repository: https://github.com/FarhnChy/bmo_fridge_buddy

## Before connecting hardware

- Shut the Pi down and unplug USB-C power before moving GPIO wires.
- The GPIO pins are **3.3 V logic** and are not 5 V tolerant. Never put 5 V on
  a data pin.
- Do not power motors or a fan from a GPIO signal pin. The cooling fan is not
  part of the sensor breadboard circuit.
- A breadboard rail is not automatically powered, and some long rails are split
  in the middle. Check continuity and the `+`/`-` markings.
- Use the Pi's **physical pin numbers** in the table below. Count carefully from
  the corner nearest the microSD end, or use `pinout` in the Pi terminal.

### Identify the resistor

The DS18B20 needs a **4.7 kOhm pull-up resistor** between its data wire and
3.3 V. A 4-band 4.7 kOhm resistor is usually **yellow, violet, red, gold**; a
5-band one is usually **yellow, violet, black, brown, brown**. Color bands can
be hard to read, so a multimeter is safer: disconnect the resistor from the
circuit, select resistance/Ohms, and look for roughly `4.7 kOhm` or `4700 Ohm`.
The exact reading may vary by its tolerance. Do not guess with an unknown part.

## Wiring (Pi powered off)

First verify the labels or datasheet for the exact sensor module and OLED you
own. Waterproof DS18B20 cable colors are common conventions, not guarantees.

| Part pin | Raspberry Pi signal | Physical pin |
|---|---|---:|
| DS18B20 VDD (often red) | 3.3 V | 1 |
| DS18B20 DATA (often yellow/white) | GPIO4 | 7 |
| DS18B20 GND (often black) | Ground | 6 |
| OLED VCC | 3.3 V | 1 |
| OLED GND | Ground | 6 |
| OLED SDA | GPIO2 / SDA | 3 |
| OLED SCL | GPIO3 / SCL | 5 |

Place the 4.7 kOhm resistor between the DS18B20 DATA row and the 3.3 V row.
Sharing 3.3 V and ground through correctly connected breadboard rails is fine.

### Cooling fan check

A stopped fan does not necessarily mean the Pi failed to boot.

1. Shut down with `sudo shutdown -h now`, wait for activity to stop, and unplug
   power before checking the fan connector.
2. Identify the fan model and its labels. For a basic **2-wire 5 V fan**, red
   normally goes to 5 V (physical pin 2 or 4) and black to ground (for example
   physical pin 6). Do not rely on color alone.
3. A temperature-controlled fan, official fan accessory, or 3/4-wire fan may
   remain off while the CPU is cool and must use its specified connector or
   configuration. Do not improvise its wiring.
4. Check the CPU temperature with `vcgencmd measure_temp`. If the Pi overheats,
   reports throttling, smells hot, or the fan is meant to be always-on but does
   not spin, shut it down and recheck the fan documentation and connector.

Never connect a 5 V fan to a 3.3 V GPIO signal pin. Do not move its connector
while the Pi is powered.

## Put the code on the Pi

Connect the Pi to the internet, open Terminal, and run:

```bash
sudo apt update
sudo apt install -y git python3-venv i2c-tools
cd ~
git clone https://github.com/FarhnChy/bmo_fridge_buddy.git
cd bmo_fridge_buddy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-rpi.txt
```

If the repository is private, authenticate with GitHub or copy the project from
your computer with SCP instead. Do not clone again over an existing folder.

Enable the hardware interfaces:

```bash
sudo raspi-config
```

In **Interface Options**, enable I2C and 1-Wire, then reboot:

```bash
sudo reboot
```

After reconnecting, verify the devices:

```bash
i2cdetect -y 1
ls /sys/bus/w1/devices/28-*/w1_slave
```

The OLED commonly appears as address `3c` or `3d`. A DS18B20 path starts with
`28-`. If either is missing, power down and recheck wiring before continuing.

Run the application:

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python bmo_fridge.py
```

The program deliberately falls back to terminal output if the OLED or sensor is
not ready. Type `help` for commands and `quit` to exit.

## Update the code later

Commit and push changes from your development computer. On the Pi, stop the
program and run:

```bash
cd ~/bmo_fridge_buddy
git status --short
git pull --ff-only
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
python -m py_compile bmo_fridge.py
python bmo_fridge.py
```

If `git status` shows Pi-side edits, do not discard them blindly; commit/copy
them or resolve the conflict first. `fridge.db` and `temperature_log.csv` are
ignored by Git, so normal pulls do not replace the Pi's inventory or log.

## Why these tools

Python has mature Raspberry Pi hardware libraries and includes SQLite and
threading. I2C uses only SDA and SCL for the display; the DS18B20 uses one data
line. SQLite keeps inventory in one local file, while CSV makes temperature
history easy to graph. The scanner thread can wait for keyboard-style barcode
input without stopping display refreshes. Open Food Facts supplies product
names, with a barcode fallback when the lookup is unavailable.

Generated runtime files are `fridge.db` and `temperature_log.csv`; both are
excluded from Git.
