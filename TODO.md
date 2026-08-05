# BMO Fridge Buddy: Setup and TODO

This file contains the remaining project plan, hardware instructions, test
steps, and commands needed to finish the project.

## Start here: remaining hardware work

The software is implemented. The remaining goal is to connect and prove one
pluggable DS18B20 probe and one OLED on the Raspberry Pi 5, then run the final
hardware and application checks. Work through these checkpoints in order:

1. **Inspect the pluggable probe kit:** Photograph the probe plug, adapter
   labels, and both sides of the adapter. Confirm it has an onboard pull-up
   resistor before connecting anything.
2. **Temperature sensor only:** With power disconnected, plug the probe into
   its adapter and connect the adapter directly to three Pi GPIO pins. Get the
   wiring reviewed before applying power. Enable 1-Wire and prove the probe
   reports a sensible room temperature.
3. **OLED:** Shut down and unplug again. Connect the OLED directly to four
   separate Pi GPIO pins, review the wiring, enable I2C, detect the display,
   and show the BMO face and temperature.
4. **Complete application test:** Verify temperature logging, OLED statuses,
   inventory, barcode input, web access, automatic services, and backups.
5. **Fridge test:** Put only the sealed metal probe inside, route its cable
   safely, confirm the door seal, and run a several-hour logging test.

Target build window: Thursday, August 6, 2026, with overflow into Friday,
August 7 if needed. Do not connect the OLED until the temperature probe works.

The fridge can log temperatures unattended while work continues on another
project. Never leave an unverified or unstable electrical setup unattended.

### Minimum finish line

By the end of the build session, aim for this working state:

- [ ] Temperature probe reads a real fridge temperature.
- [ ] `bmo_fridge.py` runs with the real probe connected.
- [ ] OLED shows the BMO face and status text.
- [ ] Phone or terminal barcode entry still works.
- [ ] Metal probe is inside the fridge.
- [ ] Pi, Gikfun adapter board, and OLED are outside the fridge.
- [ ] Wires are secured well enough that they do not fall out during normal use.

Do not spend time on automatic startup until the hardware works. Manual startup
is good enough for the first finished hardware version.

### Parts used in the final build

- Raspberry Pi 5 in its case, correct USB-C power supply, and microSD card
- One pluggable waterproof DS18B20 probe with its matching adapter module
- Three female-to-female jumper wires for the probe adapter
- One four-pin I2C SSD1306 OLED
- Four female-to-female jumper wires for the OLED
- Keyboard, or a computer that can connect to the Pi through SSH
- Phone camera for wiring checks and final evidence
- Optional USB barcode scanner
- Optional separate fridge thermometer for later accuracy comparison
- Optional dry plastic tray or non-conductive board to keep the loose parts together

The mini breadboard, male-to-female jumpers, male-to-male jumpers, and loose
4.7 kOhm resistors are **not used** when the adapter has a verified onboard
pull-up resistor. Keep them as spare prototyping parts. The Pi can remain in
its black case if the GPIO header is accessible. Keep the Pi, adapter, and OLED
on a dry non-conductive surface outside the fridge.

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
- [x] Read-only temperature graphs and shared phone/OLED BMO moods are implemented.
- [x] Receive the Gikfun pluggable DS18B20 probe-and-adapter kit.
- [x] Receive and inspect the OLED screens and original bare-wire DS18B20 probes.
- [ ] Inspect the Gikfun adapter labels and onboard pull-up resistor.
- [ ] Connect and test the temperature sensor.
- [ ] Connect and test the OLED.
- [ ] Verify every BMO expression and the revised layout on the physical OLED.
- [ ] Test the full inventory workflow and finish the physical build.
- [ ] Install and verify the automatic services and HTTPS flow on the Raspberry Pi and phone.

## Selected hardware

- Raspberry Pi 5, case with fan, power supply, and microSD card
- One pluggable waterproof DS18B20 probe and matching adapter module
- Seven female-to-female jumper wires total: three for the probe and four for
  the OLED
- One 0.96-inch, 128x64, SSD1306 I2C OLED with four attached pins
- Optional USB barcode scanner

Selected parts:

- [Hosyond SSD1306 OLED five-pack](https://www.amazon.com/dp/B0BFD4X6YV)
- [Gikfun pluggable DS18B20 probes with adapter modules](https://www.amazon.com/dp/B08V93CTM2)

The original
[WWZMDiB bare-wire probe pack](https://www.amazon.com/dp/B0C8J77NJR) is
electrically compatible, but its fine stranded leads do not stay securely in
the mini breadboard. Do not tape those leads into place or power that unstable
connection. Return that pack if practical or keep it only for a future project
with properly crimped, soldered, or screw-terminal connections.

The replacement listing describes a pluggable probe, matching adapter, and an
onboard pull-up resistor. Verify the actual labels and adapter after delivery;
do not rely only on listing photos or wire order.

## What goes inside and outside the fridge

The Raspberry Pi is not installed inside the fridge. The probe adapter and OLED
also stay outside. They are ordinary electronics and are not protected from
condensation.

| Part | Location | Reason |
|---|---|---|
| Waterproof metal DS18B20 probe | Inside the fridge | This is the part that senses the cold air. |
| DS18B20 cable | Runs from inside to outside | It carries power and temperature data between the probe and Pi. |
| Raspberry Pi and power supply | Outside the fridge | They must stay dry and need ventilation and mains power. |
| Probe adapter | Outside, beside the Pi | It connects the probe and provides the required pull-up resistor. |
| OLED screen | Outside, where it can be viewed | It is not waterproof and displays the temperature read by the inside probe. |
| Optional USB barcode scanner | Outside | It plugs into the Pi and is used when adding or removing food. |

The finished physical arrangement is:

```text
INSIDE FRIDGE                     OUTSIDE FRIDGE

waterproof metal probe ----cable/plug---- adapter ---- jumper wires ---- Raspberry Pi
                                             |                              |
                                   onboard pull-up resistor             USB power
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

## Why the breadboard is no longer used

The original plan used a breadboard and a loose 4.7 kOhm resistor because the
original probe ended in three bare wires. Those stranded leads proved too thin
and flexible to make a secure breadboard connection. Tape is not an acceptable
electrical connection.

The replacement probe plugs into an adapter module. The adapter provides solid
header pins and the required pull-up resistor, so it connects directly to the
Pi with female-to-female jumpers. This removes the breadboard, separate
resistor, and male-ended jumper wires from the finished design.

## Next steps when the pluggable probe arrives

1. Keep the Raspberry Pi shut down and unplugged.
2. Photograph the probe plug, adapter labels, and both sides of the adapter.
3. Confirm the adapter has an onboard pull-up resistor.
4. Connect and test only the DS18B20 and adapter first.
5. Enable 1-Wire and confirm the Pi detects the sensor.
6. Shut down and unplug the Pi again.
7. Add the OLED using its own power and ground pins.
8. Enable I2C and confirm the Pi detects the OLED.
9. Run the complete application and test every feature.

Do not disassemble the Raspberry Pi. All project connections use its exposed
40-pin GPIO header. Leave the separate four-wire Pi 5 fan connector alone.

## Temperature sensor wiring: adapter directly to Raspberry Pi 5

Always shut down and unplug the Pi before changing wires. First plug the probe
into its matching adapter. Follow the **printed adapter labels**, not an assumed
left-to-right order.

| Adapter label | Raspberry Pi connection | Physical pin |
|---|---|---:|
| `VCC`, `+`, or `3V3` | 3.3 V power | 1 |
| `GND` or `-` | Ground | 6 |
| `DATA`, `DAT`, `DQ`, or `S` | GPIO4 / 1-Wire data | 7 |

Use three female-to-female jumpers. The adapter end fits its male output pins;
the other end fits over the Pi's male GPIO pins. Do not use the breadboard,
male-to-female jumpers, male-to-male jumpers, or a separate 4.7 kOhm resistor
when the adapter's onboard pull-up resistor has been verified.

### Raspberry Pi 5 header orientation

With the GPIO header above the heatsink and the case edge above the header,
start at the end beside the round yellow mounting hole, away from the fan plug:

```text
Case edge / outside row
Pin 2 (5 V)   Pin 4 (5 V)   Pin 6 (GND)   Pin 8
Pin 1 (3.3 V) Pin 3         Pin 5         Pin 7 (GPIO4)
Heatsink / inside row
```

Connect one wire at a time with power disconnected:

1. Adapter `VCC`/`+` to physical pin 1.
2. Adapter `GND`/`-` to physical pin 6.
3. Adapter `DATA`/`S` to physical pin 7.
4. Photograph the complete adapter and GPIO wiring for review.
5. Confirm VCC is **not** connected to either neighboring 5 V pin 2 or 4.
6. Leave the metal probe at room temperature for the first test.

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

Then read the probe:

```bash
cat /sys/bus/w1/devices/28-*/w1_slave
```

- [ ] The first line ends with `YES`.
- [ ] The second line includes `t=` followed by a number.

Example:

```text
... YES
... t=4187
```

That example means `4.187 C`, which is about fridge temperature.

## OLED wiring

Add the OLED only after the sensor works. Shut down and unplug the Pi first.
The OLED connects directly to separate Pi power and ground pins so no
breadboard or wire splitting is necessary. Only the waterproof metal probe
goes inside the fridge.

| OLED pin | Raspberry Pi connection | Physical pin |
|---|---|---:|
| VCC | 3.3 V | 17 |
| GND | Ground | 9 |
| SDA | GPIO2 / SDA | 3 |
| SCL | GPIO3 / SCL | 5 |

Use four female-to-female jumpers and follow the labels printed on the OLED;
OLED pin order varies between boards. Photograph the complete wiring before
applying power. Never use a 5 V pin for this build.

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
python -m pip install -r requirements-rpi.txt
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

### Parked roadmap: only after the hardware prototype works

Do not let these ideas delay the original BMO hardware goal. First prove the
real DS18B20, OLED face, temperature status, logging, and inventory workflow.
After that Version 1 checkpoint, possible Version 2 work includes:

- Show a larger animated BMO face and personality in the phone app.
- Add sustained warm-temperature, disconnected-sensor, and expiration alerts.
- Finish the installable phone PWA experience with icons and offline guidance.
- Add a backup restore workflow and a hardware/service health page.

The next active milestone remains hardware verification, not these features.

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

## Final project checklist

- [ ] Prove the DS18B20 reports a sensible room temperature before using the fridge.
- [ ] Position the sensor probe safely inside the fridge without crushing its wire.
- [ ] Confirm the door gasket still seals around the probe cable.
- [ ] Add a drip loop and secure the cable so it cannot pull on the probe adapter.
- [ ] Keep the Pi, power supply, probe adapter, OLED, and scanner outside moisture and condensation.
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
