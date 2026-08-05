# BMO Fridge Buddy: Step-By-Step Build Plan

This checklist is the current build guide for finishing BMO Fridge Buddy with
the Gikfun DS18B20 temperature probe kit, Raspberry Pi, breadboard, phone entry,
barcode/inventory features, and the OLED screen.

## What To Do Next

Do these in order. Do not connect the OLED until the temperature probe works.

1. Shut down and unplug the Pi.
2. Plug one Gikfun waterproof probe into one Gikfun adapter board.
3. Use the breadboard as the shared power hub:
   - Pi `3.3V`, physical pin `1` -> breadboard `3.3V` / `+` row
   - Pi `GND`, physical pin `6` -> breadboard `GND` / `-` row
4. Connect the Gikfun adapter:
   - `+` / `VCC` -> breadboard `3.3V` / `+` row
   - `-` / `GND` -> breadboard `GND` / `-` row
   - `S` / `DATA` -> Pi `GPIO4`, physical pin `7`
5. Power the Pi back on.
6. Enable 1-Wire with `sudo raspi-config`, then reboot.
7. Confirm the probe appears with `ls /sys/bus/w1/devices/28-*/w1_slave`.
8. Run `python bmo_fridge.py` and confirm it shows a real temperature.
9. Test barcode entry from the terminal and phone page.
10. Connect and test the OLED using the same breadboard power rows.
11. Mount the probe and electronics safely.

The most important change from the old plan: this new Gikfun kit includes an
adapter module with the pull-up resistor already on the board. Use the adapter
module and do not add the separate `4.7k` resistor unless you remove the adapter
and wire the bare probe directly.

## Tomorrow Build Schedule

Target work window: Thursday, August 6, 2026 morning through late night, with
overflow into early Friday, August 7 if needed.

### Minimum Finish Line

By the end of the build session, aim for this working state:

- [ ] Temperature probe reads a real fridge temperature.
- [ ] `bmo_fridge.py` runs with the real probe connected.
- [ ] OLED shows the BMO face and status text.
- [ ] Phone or terminal barcode entry still works.
- [ ] Metal probe is inside the fridge.
- [ ] Pi, breadboard, Gikfun adapter board, and OLED are outside the fridge.
- [ ] Wires are secured well enough that they do not fall out during normal use.

Do not spend time on automatic startup until the hardware works. Manual startup
is good enough for the first finished version.

### Morning: Temperature Probe

- [ ] Shut down and unplug the Pi.
- [ ] Set up the breadboard shared power rows.
- [ ] Connect only the Gikfun temperature adapter and probe.
- [ ] Power on the Pi.
- [ ] Enable 1-Wire with `sudo raspi-config`.
- [ ] Reboot.
- [ ] Confirm the probe appears:

```bash
ls /sys/bus/w1/devices/28-*/w1_slave
```

- [ ] Confirm the probe reports data:

```bash
cat /sys/bus/w1/devices/28-*/w1_slave
```

Goal before lunch: the first command shows a `28-` device and the second command
shows `YES` plus a `t=` temperature value.

### Afternoon: App With Real Temperature

- [ ] Run the app:

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python bmo_fridge.py
```

- [ ] Confirm the terminal shows a real Fahrenheit temperature, not `No sensor`.
- [ ] Put the probe in the fridge for 10 to 15 minutes.
- [ ] Confirm the temperature moves toward normal fridge range.
- [ ] Confirm `temperature_log.csv` receives readings.

### Late Afternoon: OLED

- [ ] Shut down and unplug the Pi.
- [ ] Add OLED `VCC` to the breadboard `3.3V` / `+` row.
- [ ] Add OLED `GND` to the breadboard `GND` / `-` row.
- [ ] Add OLED `SDA` to Pi GPIO2 physical pin `3`.
- [ ] Add OLED `SCL` to Pi GPIO3 physical pin `5`.
- [ ] Power on the Pi.
- [ ] Enable I2C with `sudo raspi-config`.
- [ ] Reboot.
- [ ] Install I2C tools if needed:

```bash
sudo apt install -y i2c-tools
```

- [ ] Confirm the OLED appears:

```bash
i2cdetect -y 1
```

Expected OLED address: usually `3c` or `3d`.

### Evening: Full App Test

- [ ] Install/update Pi dependencies:

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
python -m py_compile bmo_fridge.py
python bmo_fridge.py
```

- [ ] Confirm OLED shows the BMO face.
- [ ] Confirm OLED shows the current temperature.
- [ ] Confirm OLED shows `Too Cold!`, `Normal`, or `Too Warm!`.
- [ ] Test terminal barcode entry.
- [ ] Test phone entry from the printed URL.
- [ ] Run `list`, `expiring`, `remove <barcode>`, and `help`.

### Night: Basic Mounting

- [ ] Keep only the metal probe inside the fridge.
- [ ] Keep all electronics outside the fridge.
- [ ] Route the probe cable without sharply pinching it in the door.
- [ ] Tape or clip the probe around the middle of the fridge area.
- [ ] Secure jumper wires so they cannot tug loose easily.
- [ ] Run the app for 30 minutes.
- [ ] Confirm the temperature changes normally.

### If Time Runs Tight

Prioritize in this order:

1. Temperature probe working.
2. App reading and logging temperature.
3. OLED displaying status.
4. Basic safe mounting.
5. Barcode workflow check.
6. Automatic startup.

Automatic startup is optional and should wait until the rest is stable.

## Current Status

- [x] Raspberry Pi boots and fan issue is resolved.
- [x] Project repository exists on GitHub.
- [x] Code is cloned onto the Raspberry Pi.
- [x] Python virtual environment and dependencies are installed.
- [x] `bmo_fridge.py` runs without hardware connected.
- [x] Terminal/manual barcode entry works.
- [x] Invalid expiration dates ask again.
- [x] Closed terminal input requests a clean shutdown.
- [x] Phone-friendly barcode entry page runs from the Pi on port 8080.
- [x] Gikfun DS18B20 temperature probe kit has arrived.
- [ ] Connect and test the Gikfun DS18B20 temperature probe.
- [ ] Test all software features with the real temperature probe connected.
- [ ] Connect and test the SSD1306 OLED screen.
- [ ] Finish mounting the physical build.
- [ ] Decide whether the app should start automatically when the Pi boots.

## Parts You Have Or Need

Already have:

- Raspberry Pi
- Pi power supply
- Breadboard
- Jumper wires
- [Gikfun 1M DS18B20 waterproof digital temperature sensor with adapter
  module, Pack of 3 Sets, EK1183](https://www.amazon.com/dp/B08V93CTM2)

Gikfun EK1183 notes from the listing:

- Style: Industrial waterproof DS18B20 temperature sensor with adapter module
- Lead length: `1 meter`
- Item weight: `0.1 kg`
- Working voltage: `3.3V` to `5VDC`
- Maximum supply voltage: `5VDC`
- Output leads: yellow is DATA, red is VCC, black is GND
- Measuring range: `-55 C` to `125 C`
- Cable/lead can withstand up to `85 C`
- Adapter module has the pull-up resistor onboard
- For this Raspberry Pi project, power it from `3.3V`, not `5V`, because Pi
  GPIO data pins are not 5V-safe.

Still needed for the full display build:

- One 0.96-inch, 128x64, SSD1306 I2C OLED with four attached pins

Optional:

- USB barcode scanner, only if you do not want to type barcodes or use the phone
- Small case, tape, zip ties, or cable clips to keep electronics away from
  fridge moisture

## What Each Hardware Part Does

Raspberry Pi:

- Runs `bmo_fridge.py`.
- Reads the temperature probe on GPIO4.
- Hosts the phone barcode page on port `8080`.
- Saves inventory to `fridge.db`.
- Saves temperature history to `temperature_log.csv`.
- Later, sends display text and the BMO face to the OLED.

Breadboard:

- Acts as a wiring hub so the Pi, temperature adapter module, and later OLED
  share the same `3.3V` and `GND` rows without cramped Pi header wiring.
- Makes the connections easier to change while testing.
- Is not the brain of the project. It only joins wires together.

Gikfun DS18B20 probe and adapter module:

- The metal probe goes inside the fridge.
- The little adapter board stays outside the fridge with the Pi and breadboard.
- The adapter board handles the resistor normally needed by a DS18B20 sensor.
- The Pi reads it through Linux 1-Wire.

OLED screen:

- Shows the BMO face, temperature, fridge status, inventory count, and expiring
  count.
- Uses I2C, which is separate from the temperature sensor.

## Safety Rules

- Always shut down and unplug the Raspberry Pi before moving wires.
- Use Raspberry Pi physical pin numbers in this guide.
- Use the Pi's `3.3V` pin for the temperature module, not `5V`.
- Keep the Pi, breadboard, Gikfun adapter board, and OLED outside the fridge.
- Only the metal temperature probe should go inside the fridge.
- Do not crush the sensor cable in the fridge door.
- Do not put the adapter board or breadboard where condensation can drip on it.

## Stage 1: Update And Check The Pi Software

Do this before wiring, so you know the software is still healthy.

```bash
cd ~/bmo_fridge_buddy
git status --short
source .venv/bin/activate
python -m py_compile bmo_fridge.py
python bmo_fridge.py
```

Expected result before hardware:

- The app starts.
- The terminal shows the phone URL.
- Temperature may say `No sensor`.
- The app should not crash.

Stop the app with:

```text
quit
```

## Stage 2: Connect The Gikfun Temperature Probe

Use this stage before connecting the OLED.

The Gikfun kit has two main parts:

- Waterproof metal DS18B20 probe with red/yellow/black wires.
- Small adapter module board. It may be labeled `S`, `+`, and `-`, or similar.

Plug the probe into the adapter module first. Then wire the adapter module to
the Pi through the breadboard.

### Recommended Breadboard Layout

Use the breadboard as a shared power hub:

- One row or rail for `3.3V`
- One row or rail for `GND`
- Optional: one numbered row for the Gikfun `DATA` signal if that makes the
  jumper wire easier to place

Example:

```text
Pi physical pin 1  3.3V  -> breadboard 3.3V/+ row
Pi physical pin 6  GND   -> breadboard GND/- row

breadboard 3.3V/+ row -> Gikfun adapter +
breadboard GND/- row  -> Gikfun adapter -
Pi physical pin 7 GPIO4 -> Gikfun adapter S
```

### Temperature Module Connections

| Gikfun adapter label | Meaning | Connection |
|---|---|---|
| `+` or `VCC` | Power | Breadboard `3.3V` / `+` row |
| `-` or `GND` | Ground | Breadboard `GND` / `-` row |
| `S`, `DAT`, `DQ`, or `DATA` | 1-Wire data | Pi `GPIO4`, physical pin `7` |

Important:

- Do not add a separate `4.7k` resistor when using the Gikfun adapter module.
- If you ever remove the adapter module and use only the bare probe wires, then
  add a `4.7k` resistor between DATA and `3.3V`.
- If your probe wires are exposed directly, use red as VCC, yellow as DATA, and
  black as GND.

## Stage 3: Enable 1-Wire On The Pi

After wiring the temperature module, power the Pi back on.

Run:

```bash
sudo raspi-config
```

Choose:

```text
Interface Options -> 1-Wire -> Enable
```

Then reboot:

```bash
sudo reboot
```

## Stage 4: Test The Temperature Probe By Itself

After the Pi reboots:

```bash
ls /sys/bus/w1/devices/28-*/w1_slave
```

Expected result:

- A path appears with a folder beginning with `28-`.

Then read the probe:

```bash
cat /sys/bus/w1/devices/28-*/w1_slave
```

Expected result:

- The first line ends with `YES`.
- The second line includes `t=` followed by a number.

Example:

```text
... YES
... t=4187
```

That example means `4.187 C`, which is about fridge temperature.

If no `28-` path appears:

- Shut down and unplug the Pi.
- Recheck `+` to pin `1`, `-` to pin `6`, and `S` to pin `7`.
- Make sure the probe is fully plugged into the Gikfun adapter board.
- Make sure the adapter board is outside the fridge and dry.
- Boot again and rerun the `ls` command.

## Stage 5: Run BMO With The Temperature Probe

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python bmo_fridge.py
```

Expected result:

- The app starts normally.
- The terminal prints the phone URL.
- Temperature changes from `No sensor` to a real Fahrenheit reading.
- Status becomes one of:
  - `Too Cold!`
  - `Normal`
  - `Too Warm!`
- `temperature_log.csv` gets new rows every few seconds.

No extra feature setup is needed for temperature. Once the Pi sees the sensor,
the app automatically reads it, classifies it, and logs it.

## Stage 6: Test Inventory And Barcode Features

Keep the app running.

At the terminal prompt, test manual entry:

```text
scan> 012345678905
Expiration date YYYY-MM-DD, or blank: 2026-08-15
```

Then test commands:

```text
list
expiring
remove 012345678905
help
```

Expected result:

- `list` shows saved food items.
- `expiring` shows items close to expiration.
- `remove <barcode>` removes or reduces an item.
- Open Food Facts may fill in product names when the Pi has internet.
- Unknown barcodes should still save without crashing the app.

Files that should exist after testing:

- [ ] `fridge.db`
- [ ] `temperature_log.csv`

## Stage 7: Test Phone Entry

When the app starts, it prints a URL like:

```text
http://192.168.1.25:8080
```

On a phone connected to the same Wi-Fi as the Pi:

1. Open the printed URL.
2. Type a barcode.
3. Enter an expiration date.
4. Submit it.
5. Check the Pi terminal with:

```text
list
```

Expected result:

- The phone entry adds an item to the same inventory database.
- The terminal `list` command shows the item.

Notes:

- Typing the barcode on the phone is the reliable path.
- Camera scanning may depend on browser permissions and whether the phone allows
  camera access for the page.

## Stage 8: Connect The OLED Screen

Only do this after the temperature probe works.

Shut down first:

```bash
sudo shutdown now
```

Unplug the Pi, then add the OLED wiring. Keep the Gikfun temperature adapter
connected. The OLED uses the same breadboard `3.3V` and `GND` rows.

| OLED pin | Connection | Physical pin |
|---|---|---:|
| `VCC` | Breadboard `3.3V` / `+` row | Already fed by Pi pin `1` |
| `GND` | Breadboard `GND` / `-` row | Already fed by Pi pin `6` |
| `SDA` | Pi GPIO2 / SDA | `3` |
| `SCL` | Pi GPIO3 / SCL | `5` |

At this point the shared power rows should have:

- Pi `3.3V` pin `1`, Gikfun `+`, and OLED `VCC` on the same breadboard
  `3.3V` / `+` row.
- Pi `GND` pin `6`, Gikfun `-`, and OLED `GND` on the same breadboard
  `GND` / `-` row.
- Gikfun `S` going to Pi `GPIO4` pin `7`.
- OLED `SDA` going to Pi `GPIO2` pin `3`.
- OLED `SCL` going to Pi `GPIO3` pin `5`.

## Stage 9: Enable And Test I2C For The OLED

Power the Pi back on.

Run:

```bash
sudo raspi-config
```

Choose:

```text
Interface Options -> I2C -> Enable
```

Then reboot:

```bash
sudo reboot
```

Install the I2C tool if needed:

```bash
sudo apt install -y i2c-tools
```

Check the OLED:

```bash
i2cdetect -y 1
```

Expected result:

- The OLED appears at address `3c` or `3d`.

If nothing appears:

- Shut down and unplug the Pi.
- Recheck `VCC`, `GND`, `SDA`, and `SCL`.
- Make sure `SDA` and `SCL` are not swapped.

## Stage 10: Run The Full App

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
python -m py_compile bmo_fridge.py
python bmo_fridge.py
```

Confirm:

- [ ] Terminal shows a real temperature.
- [ ] OLED shows the BMO face.
- [ ] OLED shows `Too Cold!`, `Normal`, or `Too Warm!`.
- [ ] OLED shows inventory count.
- [ ] OLED shows expiring-soon count.
- [ ] Phone page opens from another device on the same Wi-Fi.
- [ ] Phone entry adds an item.
- [ ] Manual terminal entry adds an item.
- [ ] `list` shows saved items.
- [ ] `expiring` works.
- [ ] `remove <barcode>` works.
- [ ] `temperature_log.csv` receives new readings.

## Stage 11: Mount The Physical Build

- [ ] Put only the metal probe inside the fridge.
- [ ] Keep the Pi, breadboard, adapter module, and OLED outside the fridge.
- [ ] Route the probe cable so the fridge door does not sharply pinch it.
- [ ] Tape or clip the probe so it does not sit directly against the freezer
      plate or wall.
- [ ] Put the probe around the middle of the fridge area for a better air
      temperature reading.
- [ ] Secure loose wires with tape, clips, or zip ties.
- [ ] Keep electronics away from spills and condensation.
- [ ] Run the app for at least 30 minutes and confirm the temperature changes
      normally.

## Stage 12: Daily Use

Start the app:

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python bmo_fridge.py
```

Use these terminal commands:

```text
list
expiring
remove <barcode>
help
quit
```

Use the phone page:

- Open the URL printed by the app.
- Add food by barcode and expiration date.
- Check the OLED or terminal for current fridge status.

Temperature status:

- Below `32 F`: `Too Cold!`
- `32 F` through `40 F`: `Normal`
- Above `40 F`: `Too Warm!`

## Troubleshooting

Temperature says `No sensor`:

- Confirm 1-Wire is enabled.
- Confirm the Pi was rebooted after enabling 1-Wire.
- Confirm the Gikfun adapter `S` pin is connected to GPIO4 physical pin `7`.
- Confirm Pi physical pin `1` feeds the breadboard `3.3V` / `+` row.
- Confirm Pi physical pin `6` feeds the breadboard `GND` / `-` row.
- Confirm adapter `+` is connected to the breadboard `3.3V` / `+` row.
- Confirm adapter `-` is connected to the breadboard `GND` / `-` row.
- Try another probe/adapter from the 3-pack.

Temperature looks off:

- Let the probe sit in the fridge for 10 to 15 minutes.
- Compare against another fridge thermometer if available.
- Expect hobby sensors to be close, but not medical/lab accurate.

Phone page does not open:

- Make sure the phone and Pi are on the same Wi-Fi.
- Use the exact URL printed by the app.
- Make sure the app is still running.
- Try `http://<pi-ip-address>:8080`.

OLED does not show:

- Confirm I2C is enabled.
- Confirm `i2cdetect -y 1` shows `3c` or `3d`.
- Confirm OLED `VCC` is connected to the breadboard `3.3V` / `+` row.
- Confirm OLED `GND` is connected to the breadboard `GND` / `-` row.
- Recheck `SDA` physical pin `3` and `SCL` physical pin `5`.

Open Food Facts names do not appear:

- Make sure the Pi has internet.
- Unknown barcodes can still be saved.
- The app should keep running even if lookup fails.

## Update The Pi Later

After pushing new code from the Windows computer, update the Pi with:

```bash
cd ~/bmo_fridge_buddy
git status --short
git pull --ff-only
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
python -m py_compile bmo_fridge.py
python bmo_fridge.py
```

If `git status --short` shows Pi-side edits, preserve or commit them before
pulling. `fridge.db` and `temperature_log.csv` are ignored by Git, so normal
updates should not overwrite the Pi's inventory and temperature history.

## Publish Changes To GitHub

On the Windows computer:

```powershell
git status --short
git add README.md TODO.md bmo_fridge.py
git commit -m "Revise hardware setup checklist for Gikfun sensor kit"
git push
```

Review `git status --short` before committing so unexpected files are not
included.
