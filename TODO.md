# BMO Fridge Buddy: Setup and TODO

This file contains the remaining project plan, hardware instructions, test
steps, and commands needed to finish the project.

## Tomorrow: start here

The target for one six-hour work session is a complete Version 1 prototype:
the real probe reports fridge temperature, the outside OLED displays it, the
inventory commands work, and readings are logged. Hardware troubleshooting may
push final testing into a second session; do not rush or connect power to save
time.

When ready, say **"I'm ready to finish BMO Fridge Buddy."** Start with the Pi
unplugged and do not pre-wire anything. Work through one checkpoint at a time:

1. **Parts and photos (30 minutes):** Lay out and photograph the Pi case and
   exposed GPIO header, both sides of the breadboard, sensor labels and wire
   ends, both sides of the OLED, jumper-wire ends, and resistor.
2. **DS18B20 only (60-90 minutes):** Identify every connection, build the
   sensor circuit with power disconnected, review it, enable 1-Wire, and prove
   that it reports a sensible room temperature.
3. **OLED (45-90 minutes):** Shut down and unplug again, add the outside OLED,
   enable I2C, detect its address, and display the BMO face and temperature.
4. **Application (45-60 minutes):** Test help, adding, invalid dates, listing,
   expiring items, removing, quitting, and temperature logging.
5. **Fridge test (30-60 minutes of active work):** Put only the metal probe
   inside, route its cable safely, confirm the door seal, and leave it logging.
6. **Buffer and finish (remaining time):** Troubleshoot, tidy the loose setup,
   capture evidence, update these checkboxes, and commit the tested result.

The fridge can log temperatures unattended while work continues on another
project. Never leave an unverified or unstable electrical setup unattended.

### Have these ready

- Raspberry Pi 4 in its case, USB-C power supply, and a way to use its terminal
- Mini breadboard and female-to-male jumper wires
- Waterproof three-wire DS18B20 sensor and one 4.7 kOhm resistor
- Four-pin I2C SSD1306 OLED
- Keyboard, or a computer that can connect to the Pi through SSH
- Phone camera for wiring checks and final evidence
- Optional USB barcode scanner
- Optional separate fridge thermometer for later accuracy comparison
- Optional dry plastic tray or non-conductive board to keep the loose parts together

Do not peel the breadboard's adhesive backing or permanently mount anything
before the complete circuit works. The Pi can remain in its black case if its
GPIO header is accessible. The breadboard stays outside the case, loose beside
the Pi during testing. It does not need to be glued to the fridge. Afterward,
the Pi, breadboard, and OLED may simply share a portable dry tray, mounting
plate, or ventilated project enclosure outside the fridge.

## Current progress

- [x] Raspberry Pi boots and its fan issue is resolved.
- [x] Project repository exists on GitHub.
- [x] Code is cloned onto the Raspberry Pi.
- [x] Python virtual environment and project dependencies are installed.
- [x] `bmo_fridge.py` runs in terminal mode without hardware connected.
- [x] Invalid expiration dates now prompt again.
- [x] Closed terminal input now requests a clean application shutdown.
- [x] Phone-friendly inventory web app supports barcode lookup, expiration dates, quantities, and removal.
- [x] Phone scanner supports live camera scanning over HTTPS and a barcode-photo fallback.
- [x] Inventory editing and expiration filters are implemented.
- [x] Barcode recognition is bundled for offline use.
- [x] Automatic startup, verified daily backups, and private HTTPS setup are implemented.
- [ ] Install and verify the automatic services and HTTPS flow on the Raspberry Pi and phone.
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

## What goes inside and outside the fridge

The Raspberry Pi is not installed inside the fridge. The breadboard and OLED
also stay outside. They are ordinary electronics and are not protected from
condensation.

| Part | Location | Reason |
|---|---|---|
| Waterproof metal DS18B20 probe | Inside the fridge | This is the part that senses the cold air. |
| DS18B20 cable | Runs from inside to outside | It carries power and temperature data between the probe and Pi. |
| Raspberry Pi and power supply | Outside the fridge | They must stay dry and need ventilation and mains power. |
| Breadboard and resistor | Outside, beside the Pi | They make the electrical connections and must stay dry. |
| OLED screen | Outside, where it can be viewed | It is not waterproof and displays the temperature read by the inside probe. |
| Optional USB barcode scanner | Outside | It plugs into the Pi and is used when adding or removing food. |

The finished physical arrangement is:

```text
INSIDE FRIDGE                     OUTSIDE FRIDGE

waterproof metal probe ----cable---- breadboard ---- jumper wires ---- Raspberry Pi
                                      |                                  |
                                 4.7 kOhm resistor                    USB power
                                                                         |
                                                                  OLED and scanner
```

Only the sealed metal probe should be inside. The OLED stays outside so it is
visible without opening the door and so condensation cannot damage it.

The probe does not calculate or display anything itself. It measures
temperature and sends a digital number along its DATA wire. The Python program
on the Pi reads that number, decides whether the fridge is too cold, normal, or
too warm, saves readings, and tells the outside OLED what to draw.

### How the cable leaves the fridge

For a first prototype, gently pass the thin probe cable through the door gasket
and close the door on it. Check that the gasket still seals and that the cable
is not pinched, cut, sharply bent, or pulled tight. Make a small downward
"drip loop" in the cable outside before it reaches the electronics so moisture
cannot run along the cable toward the Pi.

Do not drill a hole in the fridge. Refrigerant tubes and electrical wiring can
be hidden in its walls. If the door cannot close and seal safely around the
cable, stop and choose another non-destructive cable route or a purpose-made
fridge cable pass-through.

## What the breadboard does

The breadboard does not fit into the Pi. It is a separate plastic connection
board that sits next to the Pi. Jumper wires connect holes on the breadboard to
the exposed GPIO pins on top of the Pi.

A breadboard lets several wires meet without soldering:

- Holes along a `+` power rail are electrically connected to each other.
- Holes along a `-` ground rail are electrically connected to each other.
- Each short numbered group of holes in the center is connected together.
- The two sides of the center gap are not connected to each other.

Some small breadboards label or split their rails differently. Confirm the
printed markings or test continuity rather than assuming every rail runs the
full length.

If the waterproof sensor ends in loose, flexible stranded wires, do not force
frayed strands into the breadboard. Use a suitable three-position terminal
adapter, pre-crimped connector, or properly attached male jumper leads. Do not
make these connections while the Pi is powered.

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

In plain language, the three sensor connections are:

```text
Pi physical pin 1 (3.3 V power) ----+---- sensor VCC/red
                                    |
                              4.7 kOhm resistor
                                    |
Pi physical pin 7 (GPIO4 data) -----+---- sensor DATA/yellow

Pi physical pin 6 (ground) -------------- sensor GND/black
```

The resistor is on the breadboard between the power connection and DATA
connection. It is not placed inside the Raspberry Pi or inside the fridge.

### Beginner connection sequence

1. Shut down the Pi, unplug its USB-C power cable, and wait for its lights to go
   out.
2. Place the Pi and breadboard beside each other on a dry, non-metal surface.
3. Identify physical GPIO pins 1, 6, and 7 using a Raspberry Pi 4 pin diagram.
   Physical pin numbers describe positions on the header; `GPIO4` is the signal
   name for physical pin 7.
4. Run a female-to-male jumper from Pi physical pin 1 to the breadboard `+`
   rail. This brings safe 3.3 V power to that rail.
5. Run another jumper from Pi physical pin 6 to the breadboard `-` rail. This
   creates the ground connection.
6. Choose one unused numbered center row as the DATA row. Run a jumper from Pi
   physical pin 7 to that row.
7. Connect sensor VCC/red to the `+` rail, sensor GND/black to the `-` rail, and
   sensor DATA/yellow to the chosen DATA row.
8. Put one leg of the 4.7 kOhm resistor into the DATA row and its other leg into
   the `+` rail. Resistor direction does not matter.
9. Before restoring power, trace every connection from beginning to end. Make
   sure nothing is connected to a 5 V pin and no loose wire strands touch a
   neighboring connection.
10. Leave the probe outside the fridge for the first software test. Put it
    inside only after the Pi detects it and reports a sensible room temperature.

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
The sensor and OLED may share the breadboard power and ground rails. The OLED
stays outside the fridge beside the Pi; only the waterproof temperature probe
goes inside.

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

## How the barcode scanner works

A normal USB barcode scanner in keyboard or HID mode does not require a phone
app. Plug it into the Pi, place the terminal at the `scan>` prompt, and scan a
package. The scanner types the barcode digits and usually presses Enter just as
a keyboard would. The program then looks up the product with Open Food Facts,
asks for an expiration date, and saves it in SQLite.

The product barcode normally does not contain its expiration date. For Version
1, type that date with a keyboard when prompted. A scanner is optional for the
first hardware test: manually typing the printed barcode tests the same program
flow.

Barcode checks:

- [ ] Type a real barcode manually and confirm the product lookup/fallback works.
- [ ] Plug in the scanner and confirm it can type into a plain terminal.
- [ ] Scan at `scan>` and confirm it submits the complete barcode once.
- [ ] Enter an expiration date and confirm the item appears in `list`.
- [ ] Disconnect the internet and confirm an unknown-item fallback is saved.

## Version 1 versus future features

Version 1 does not require a mobile app. It is complete when the physical
sensor, outside OLED, terminal inventory workflow, local database, and CSV log
work reliably. A monitor/keyboard or SSH connection is acceptable for entering
expiration dates.

The Version 2 phone-friendly web dashboard is implemented for inventory. It
reuses the Python application and SQLite database, scans barcodes through the
phone camera, looks up product names, and records quantities and expiration
dates. Live camera scanning needs trusted HTTPS; the barcode-photo and manual
entry paths can be tested over ordinary local HTTP. Automatic startup,
verified rotating backups, a production web server, and a private Tailscale
HTTPS setup are implemented but still need device-side installation and
testing. Tailscale provides private-device access in place of a separate BMO
login. Temperature graphs and alerts remain future improvements.

## Publish changes to GitHub

On the Windows development computer:

```powershell
git status --short
git add README.md TODO.md bmo_fridge.py
git commit -m "Finish and document BMO Fridge Buddy prototype"
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
python -m py_compile bmo_fridge.py web_app.py backup_database.py
python -m unittest discover -s tests -v
bash scripts/install_pi_services.sh
```

If `git status` shows Pi-side edits, preserve or commit them before pulling.
`fridge.db` and `temperature_log.csv` are ignored by Git, so normal updates do
not overwrite the Pi's inventory and temperature history.

## Final project checklist

- [ ] Prove the DS18B20 reports a sensible room temperature before using the fridge.
- [ ] Position the sensor probe safely inside the fridge without crushing its wire.
- [ ] Confirm the door gasket still seals around the probe cable.
- [ ] Add a drip loop and secure the cable so it cannot pull on the breadboard.
- [ ] Keep the Pi, power supply, breadboard, resistor, OLED, and scanner outside moisture and condensation.
- [ ] Keep the outside parts together on a dry portable tray, plate, or ventilated enclosure; no fridge glue is required.
- [ ] Compare the sensor with another thermometer if one is available.
- [ ] Run a several-hour temperature logging test without errors or unsafe heat/moisture.
- [ ] Run the complete hardware, inventory, and barcode checklists above.
- [x] Add optional automatic startup for the monitor and phone web app.
- [x] Add verified rotating backups for `fridge.db`.
- [ ] Install and verify automatic startup and backups on the Pi.
- [ ] Activate and test private Tailscale HTTPS on the Pi and phone.
- [ ] Take a photo or video of the finished working hardware.
- [ ] Capture terminal output showing the detected sensor and OLED.
- [ ] Update README and TODO so they describe what actually worked.
- [ ] Commit and push the final tested version to GitHub.
