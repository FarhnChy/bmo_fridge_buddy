# BMO Fridge Buddy: Setup and TODO

This file contains the remaining project plan, hardware instructions, test
steps, and commands needed to finish the project.

## Current progress

- [x] Raspberry Pi boots and its fan issue is resolved.
- [x] Project repository exists on GitHub.
- [x] Code is cloned onto the Raspberry Pi.
- [x] Python virtual environment and project dependencies are installed.
- [x] `bmo_fridge.py` runs in terminal mode without hardware connected.
- [x] Invalid expiration dates now prompt again.
- [x] Closed terminal input now requests a clean application shutdown.
- [ ] Order/receive the waterproof DS18B20 sensors and SSD1306 OLED screens.
- [ ] Connect and test the temperature sensor.
- [ ] Connect and test the OLED.
- [ ] Test the full inventory workflow and finish the physical build.

## Parts

- Raspberry Pi 4 and power supply
- Mini solderless breadboard
- Jumper wires
- One waterproof, three-wire DS18B20 temperature sensor
- One 4.7 kOhm resistor
- One 0.96-inch, 128x64, SSD1306 I2C OLED with four attached pins
- Optional USB barcode scanner

Selected parts:

- [Hosyond SSD1306 OLED five-pack](https://www.amazon.com/dp/B0BFD4X6YV)
- [WWZMDiB waterproof DS18B20 five-pack](https://www.amazon.com/dp/B0C8J77NJR)

The selected sensor listing documents red as VCC, yellow as DATA, and black as
GND. Check the labels and included instructions again when the actual parts
arrive. Do not assume wire colors for a different sensor.

## Next steps when the parts arrive

1. Keep the Raspberry Pi shut down and unplugged.
2. Photograph and inspect the actual sensor, OLED, resistor, and connectors.
3. Connect and test only the DS18B20 first.
4. Enable 1-Wire and confirm the Pi detects the sensor.
5. Shut down and unplug the Pi again.
6. Add the OLED separately.
7. Enable I2C and confirm the Pi detects the OLED.
8. Run the complete application and test every feature.

Do not open or disassemble the Raspberry Pi. All project connections use its
exposed 40-pin GPIO header and the breadboard.

## Temperature sensor wiring

Always shut down and unplug the Pi before changing wires. Use the physical pin
numbers in this table.

| DS18B20 wire | Breadboard connection | Raspberry Pi connection |
|---|---|---|
| Red / VCC | Positive rail | 3.3 V, physical pin 1 |
| Yellow / DATA | One numbered signal row | GPIO4, physical pin 7 |
| Black / GND | Ground rail | Ground, physical pin 6 |

Place one leg of the 4.7 kOhm resistor in the same numbered row as DATA. Place
the other resistor leg in the 3.3 V positive rail. A resistor has no direction.

The resistor is a pull-up: it holds the DATA line at a stable voltage so the Pi
can reliably communicate with the sensor. Never connect this circuit to a 5 V
GPIO signal, and never move wires while the Pi is powered.

## Enable and test the temperature sensor

After checking the wiring, power on the Pi and run:

```bash
sudo raspi-config
```

Choose **Interface Options**, enable **1-Wire**, and reboot. Then check:

```bash
ls /sys/bus/w1/devices/28-*/w1_slave
```

- [ ] A path beginning with `28-` appears.
- [ ] If no path appears, shut down and recheck wiring before trying again.

## OLED wiring

Add the OLED only after the sensor works. Shut down and unplug the Pi first.
The sensor and OLED may share the breadboard power and ground rails.

| OLED pin | Breadboard/Pi connection | Physical pin |
|---|---|---:|
| VCC | 3.3 V positive rail | 1 |
| GND | Ground rail | 6 |
| SDA | GPIO2 / SDA | 3 |
| SCL | GPIO3 / SCL | 5 |

Enable I2C with `sudo raspi-config`, reboot, and check:

```bash
i2cdetect -y 1
```

- [ ] The OLED appears, normally at address `3c` or `3d`.
- [ ] If it does not appear, shut down and recheck VCC, GND, SDA, and SCL.

## Run the application on the Pi

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python bmo_fridge.py
```

Stop it by typing `quit` at the `scan>` prompt or pressing `Ctrl+C`.

Hardware checks:

- [ ] The terminal shows a real temperature instead of `No sensor`.
- [ ] The OLED shows the BMO face.
- [ ] The OLED shows temperature and `Too Cold!`, `Normal`, or `Too Warm!`.
- [ ] The OLED shows item and expiring-soon counts.
- [ ] `temperature_log.csv` receives new readings.

Inventory checks:

- [ ] `help` prints the available commands.
- [ ] Scan/type a barcode and enter an expiration date as `YYYY-MM-DD`.
- [ ] An invalid date asks again instead of adding the item immediately.
- [ ] `list` shows the saved item.
- [ ] `expiring` shows items expiring soon.
- [ ] `remove <barcode>` reduces the quantity or removes the item.
- [ ] `quit` closes the application cleanly.

## Publish changes to GitHub

On the Windows development computer:

```powershell
git status --short
git add README.md TODO.md bmo_fridge.py
git commit -m "Organize project documentation and input handling"
git push
```

The files will appear on GitHub after the push succeeds. Review `git status`
before committing so unexpected files are not included.

## Update the Raspberry Pi later

After pushing new code from the development computer, stop the app on the Pi:

```bash
cd ~/bmo_fridge_buddy
git status --short
git pull --ff-only
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
python -m py_compile bmo_fridge.py
python bmo_fridge.py
```

If `git status` shows Pi-side edits, preserve or commit them before pulling.
`fridge.db` and `temperature_log.csv` are ignored by Git, so normal updates do
not overwrite the Pi's inventory and temperature history.

## Final project checklist

- [ ] Mount the sensor probe safely inside the fridge without crushing its wire.
- [ ] Keep the Pi, breadboard, and OLED outside moisture and condensation.
- [ ] Decide whether to run the program manually or add automatic startup.
- [ ] Back up `fridge.db` before future database changes.
- [ ] Take a photo or video of the finished working hardware.
- [ ] Capture terminal output showing the detected sensor and OLED.
- [ ] Commit and push the final tested version to GitHub.
