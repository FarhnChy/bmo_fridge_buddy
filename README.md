## How This Project Was Built

This project was built with a learn-first approach. Rather than copying
boilerplate code, every section was written with a clear understanding of
why each decision was made. Below is a breakdown of the key concepts behind
each part of the codebase so anyone reading this — including future me —
understands the reasoning.

---

### Why Python?
Python is the standard language for Raspberry Pi projects because it has
mature libraries for GPIO hardware control, sensor reading, and I2C display
communication. It also has SQLite and threading built into its standard
library meaning fewer external dependencies.

---

### Why I2C for the OLED screen?
I2C (Inter-Integrated Circuit) is a communication protocol that only needs
2 wires (SDA and SCL) to send data between the Pi and the screen. The
alternative, SPI, is faster but needs 4+ wires. For a small display that
only updates every 2 seconds, I2C is simpler and more than fast enough.

---

### Why DS18B20 for temperature?
The DS18B20 uses the 1-Wire protocol which means it only needs a single
data wire plus power and ground. It is also waterproof and accurate to
±0.5°C which is reliable enough for fridge monitoring. It communicates
digitally so there is no analog to digital conversion needed unlike cheaper
sensors like the DHT11.

---

### Why SQLite for the database?
SQLite is a file based database engine built directly into Python. There is
no server to install or configure. The entire database lives in a single
file called fridge.db sitting right next to the Python script. For a local
project running on one device this is the perfect choice. A full database
server like PostgreSQL or MySQL would be massive overkill here.

---

### Why threading?
The main loop needs to update the OLED screen every 2 seconds without
stopping. The barcode scanner needs to wait for input at any time without
a timer. These two tasks cannot share one loop because input() blocks —
meaning the program would freeze and wait for a barcode scan and the
screen would stop updating. Threading solves this by running the scanner
listener in the background simultaneously so both tasks work at the same
time without blocking each other.

---

### Why try/except on the sensor and screen imports?
The sensor and screen are physical hardware that may not be plugged in
during development. Without try/except the entire program would crash
immediately if either piece of hardware was missing. Wrapping them in
try/except lets the program boot in terminal only mode so you can write
and test all the database and logic code before the hardware arrives.

---

### Why Open Food Facts API?
Manually typing product names every time you scan a barcode would make the
scanner pointless. Open Food Facts is a free, open source food database
with millions of products that requires no API key. Sending a barcode
number returns the full product name automatically. The function falls back
to the raw barcode number if there is no internet connection so the program
never crashes due to a failed API call.

---

### Why log temperature to CSV and not the database?
Temperature readings happen every 10 seconds and are purely historical
data you might want to open in Excel or Google Sheets to visualize as a
graph. CSV is the universal format for that. The SQLite database is for
structured inventory data you need to query and update. Using the right
tool for each type of data keeps both systems clean and simple.

---

### Why check expiration dates every 30 seconds instead of every loop?
The expiration check queries the database on every call. Running a database
query every 2 seconds is unnecessary because expiration dates are measured
in days not seconds. Checking every 30 seconds is frequent enough to catch
warnings quickly while keeping database reads minimal.

---

## Learning Checklist
Use this to test yourself before calling the project done.

- [ ] Can you explain what I2C is and why it was chosen over SPI?
- [ ] Can you explain what 1-Wire is and how the DS18B20 uses it?
- [ ] Can you explain why threading was needed and what blocking means?
- [ ] Can you explain what a daemon thread is and why daemon=True matters?
- [ ] Can you explain why SQLite was chosen over a full database server?
- [ ] Can you explain what state.lock does and why shared state needs it?
- [ ] Can you explain why time.monotonic() is used for repeated timed tasks?
- [ ] Can you explain what the try/except blocks prevent?
- [ ] Can you explain what the Open Food Facts API returns and how it is parsed?
- [ ] Can you explain what .gitignore does and why fridge.db is in it?

---

## Current Code

The main app lives in `bmo_fridge.py`.

Run it on your computer first:

```bash
python bmo_fridge.py
```

The app supports these commands:

```text
<barcode>           scan/add an item
remove <barcode>    remove one item
list                show inventory
expiring            show items expiring soon
help                show commands
quit                stop the program
```

If the Raspberry Pi OLED libraries are not installed, the app automatically
runs in terminal mode. That is intentional. It lets you learn and test the
database, barcode input, API lookup, and timing loop before wiring hardware.

## Raspberry Pi Setup Notes

Install the OLED Python libraries on the Pi:

```bash
python -m pip install -r requirements-rpi.txt
```

The DS18B20 temperature sensor uses Raspberry Pi OS's 1-Wire support. After
1-Wire is enabled, the app looks for a sensor file like this:

```text
/sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
```

The SSD1306 OLED uses I2C. After I2C is enabled, the display code uses the Pi's
SDA and SCL pins through the Adafruit SSD1306 library.

## GitHub Proof Checklist

Use small commits so the repo shows your learning process:

```bash
git init
git add .
git commit -m "Create first BMO fridge buddy script"
```

After creating an empty GitHub repo:

```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

Do not commit `fridge.db` or `temperature_log.csv`. Those files are local output
created by running the program, so they are listed in `.gitignore`.
