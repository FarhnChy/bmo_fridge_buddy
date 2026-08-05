# BMO Fridge Buddy: Final Build TODO

Use this file on Thursday, August 6, 2026. The software is implemented; what
remains is hardware hookup, real-device testing, service install, and final
cleanup.

## Finish Checklist

1. **Inspect the Gikfun DS18B20 kit**
   - [ ] Pi is shut down and unplugged.
   - [ ] Photograph the probe plug, adapter labels, and both sides of the adapter.
   - [ ] Confirm the adapter has an onboard pull-up resistor.
   - [ ] Use the labels printed on the adapter, not assumed wire order.

2. **Connect and prove the temperature probe**
   - [ ] Plug the probe into the adapter.
   - [ ] Wire adapter `VCC`/`+` to Pi physical pin `1` / `3.3V`.
   - [ ] Wire adapter `GND`/`-` to Pi physical pin `6` / `GND`.
   - [ ] Wire adapter `DATA`/`S` to Pi physical pin `7` / `GPIO4`.
   - [ ] Enable 1-Wire with `sudo raspi-config`, then reboot.
   - [ ] Confirm a `28-...` device appears.
   - [ ] Confirm the sensor readout says `YES` and includes `t=`.

3. **Run the main app with the real probe**
   - [ ] Start `bmo_fridge.py`.
   - [ ] Confirm terminal shows a real Fahrenheit temperature, not `No sensor`.
   - [ ] Confirm `temperature_log.csv` gets new rows.
   - [ ] Put the metal probe in the fridge for 10 to 15 minutes and confirm the reading moves toward fridge range.

4. **Connect and prove the OLED**
   - [ ] Shut down and unplug the Pi before wiring.
   - [ ] Wire OLED `VCC` to Pi physical pin `17` / `3.3V`.
   - [ ] Wire OLED `GND` to Pi physical pin `9` / `GND`.
   - [ ] Wire OLED `SDA` to Pi physical pin `3` / `GPIO2`.
   - [ ] Wire OLED `SCL` to Pi physical pin `5` / `GPIO3`.
   - [ ] Enable I2C with `sudo raspi-config`, then reboot.
   - [ ] Confirm `i2cdetect -y 1` shows `3c` or `3d`.
   - [ ] Confirm BMO face, temperature, and status show on the OLED.

5. **Test inventory and phone app**
   - [ ] Terminal commands work: `help`, `list`, `expiring`, `remove <barcode>`, `quit`.
   - [ ] Manual barcode entry saves an item.
   - [ ] Phone web page opens from the printed URL.
   - [ ] Phone manual entry, photo scan, inventory list, edit/remove, expiration filters, and temperature graph work.
   - [ ] Unknown barcode fallback saves without crashing.

6. **Mount and run the real fridge test**
   - [ ] Only the sealed metal probe is inside the fridge.
   - [ ] Pi, power supply, probe adapter, OLED, and scanner stay outside the fridge.
   - [ ] Cable passes through the door gasket without being crushed.
   - [ ] Door still seals.
   - [ ] Cable has a downward drip loop before reaching electronics.
   - [ ] Wires are secured so they cannot tug loose.
   - [ ] Several-hour logging test runs without crashes or unsafe moisture/heat.

7. **Install always-on Pi services**
   - [ ] Install services only after hardware works manually.
   - [ ] Confirm web app, monitor app, and backup timer are active.
   - [ ] Confirm backups appear in `~/bmo_fridge_backups`.
   - [ ] Reboot the Pi and confirm everything starts again.

8. **Enable private HTTPS for live phone scanning**
   - [ ] Install and sign in to Tailscale on the Pi and phone.
   - [ ] Run the Tailscale HTTPS setup script.
   - [ ] Open the printed `https://...ts.net` address from the phone.
   - [ ] Do not enable Tailscale Funnel.

9. **Final cleanup**
   - [ ] Update README/TODO with what actually worked.
   - [ ] Commit final changes.
   - [ ] Push to GitHub.
   - [ ] Pull latest code on the Pi.

## Commands

Check sensor:

```bash
ls /sys/bus/w1/devices/28-*/w1_slave
cat /sys/bus/w1/devices/28-*/w1_slave
```

Run main app:

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
python bmo_fridge.py
```

Check OLED:

```bash
i2cdetect -y 1
```

Run phone web app manually:

```bash
cd ~/bmo_fridge_buddy
source .venv/bin/activate
python web_app.py
```

Install services:

```bash
cd ~/bmo_fridge_buddy
git pull --ff-only
source .venv/bin/activate
python -m pip install -r requirements-rpi.txt
bash scripts/install_pi_services.sh
```

Verify services and backups:

```bash
sudo systemctl status bmo-fridge-web bmo-fridge-monitor bmo-fridge-backup.timer
ls -lh ~/bmo_fridge_backups
```

Enable private HTTPS:

```bash
sudo tailscale up
cd ~/bmo_fridge_buddy
bash scripts/enable_tailscale_https.sh
```

## Done Definition

The project is finished when the real probe reads fridge temperature, the OLED
shows BMO status, terminal and phone inventory both work, history graphs work,
backups run, services survive reboot, the hardware is mounted safely, and the
final code/docs are pushed to GitHub.
