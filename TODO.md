# BMO Fridge Project TODO

Due today: 2026-06-15

## 1. Create and Connect the GitHub Repo

- [ ] Create a new empty GitHub repository for this project.
- [ ] Copy the repo URL.
- [ ] Initialize Git locally:

```bash
git init
git branch -M main
```

- [ ] Confirm generated local files are ignored:

```bash
git status --short
```

Expected: `fridge.db`, `temperature_log.csv`, and `__pycache__/` should not appear.

- [ ] Make the first commit:

```bash
git add .gitignore README.md CODEX.md bmo_fridge.py requirements-rpi.txt TODO.md
git commit -m "Create BMO fridge monitor project"
```

- [ ] Connect the local repo to GitHub:

```bash
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 2. Update Project Identity

- [ ] Replace the placeholder Open Food Facts user agent contact text in `bmo_fridge.py` after the GitHub repo exists.
- [ ] Add the actual GitHub repo URL to `README.md`.
- [ ] Fix broken special characters in `README.md` and `CODEX.md` if punctuation or degree symbols display incorrectly.

## 3. Local Software Check

- [ ] Run the syntax check:

```bash
python -m py_compile bmo_fridge.py
```

- [ ] Run the app locally:

```bash
python bmo_fridge.py
```

- [ ] Test these commands in terminal mode:
  - [ ] `help`
  - [ ] `list`
  - [ ] scan/type a barcode
  - [ ] enter an expiration date as `YYYY-MM-DD`
  - [ ] `expiring`
  - [ ] `remove <barcode>`
  - [ ] `quit`

- [ ] Confirm `fridge.db` and `temperature_log.csv` are created locally but still ignored by Git.

## 4. Raspberry Pi Setup

- [ ] Copy or clone the repo onto the Raspberry Pi.
- [ ] Install dependencies on the Pi:

```bash
python -m pip install -r requirements-rpi.txt
```

- [ ] Enable I2C for the SSD1306 OLED display.
- [ ] Enable 1-Wire for the DS18B20 temperature sensor.
- [ ] Reboot the Pi after enabling hardware interfaces.
- [ ] Confirm the DS18B20 appears under `/sys/bus/w1/devices/28-*/w1_slave`.
- [ ] Run the app on the Pi and confirm it does not fall back to terminal-only display mode.

## 5. Hardware Verification

- [ ] Confirm the OLED shows:
  - [ ] BMO face
  - [ ] temperature
  - [ ] item count
  - [ ] expiring-soon count
  - [ ] status message

- [ ] Confirm the temperature reading changes and logs to `temperature_log.csv`.
- [ ] Confirm the USB barcode scanner types a barcode and presses Enter automatically.
- [ ] Confirm a scanned item is saved to SQLite.
- [ ] Confirm removing an item updates the quantity or deletes the row.

## 6. Final Proof for Submission

- [ ] Take a photo or short video of the wired hardware running.
- [ ] Take a screenshot of the GitHub repo with the committed files.
- [ ] Take a screenshot or terminal output showing the app running.
- [ ] Make one final commit if README or code changed:

```bash
git add README.md CODEX.md bmo_fridge.py TODO.md
git commit -m "Document setup and finish project checklist"
git push
```

## Must Be Done Today

- [ ] GitHub repo created.
- [ ] Local project committed and pushed.
- [ ] Placeholder repo/contact text updated.
- [ ] Local terminal test completed.
- [ ] README cleaned up enough for someone else to run the project.

## Can Move Past Today If Hardware Is Not Ready

- [ ] Raspberry Pi dependency install.
- [ ] OLED display test.
- [ ] DS18B20 sensor test.
- [ ] Barcode scanner test on the Pi.
- [ ] Final hardware demo photo/video.
