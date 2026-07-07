# BMO Fridge Buddy

BMO Fridge Buddy is a Raspberry Pi mini-fridge project inspired by BMO from
Adventure Time.

The goal is to read the actual temperature inside a mini fridge, show a small
BMO-style face and status screen, and keep a simple inventory of fridge items
with expiration dates.

The project uses:

- a Raspberry Pi
- a DS18B20 temperature sensor
- an SSD1306 I2C OLED screen
- a USB barcode scanner
- SQLite for local inventory
- CSV logging for temperature history

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

If the Raspberry Pi OLED libraries or temperature sensor are not available, the
app runs in terminal mode so the inventory, barcode input, and database logic
can still be tested.

Setup notes and the remaining project checklist are in `todo.md`.
