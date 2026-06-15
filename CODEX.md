The BMO Fridge Monitor is a Raspberry Pi 4 based IoT project that turns a
mini fridge into a smart appliance with real time monitoring and inventory
tracking. The physical hardware consists of a DS18B20 waterproof temperature
sensor wired to the Pi's GPIO pins via a breadboard, and a 0.96 inch I2C
OLED display that acts as BMO's face — the small green game console character
from Adventure Time. The screen displays a simple ASCII face, the current
fridge temperature in Fahrenheit, and a live status message that reads
"Normal", "Too Cold!", or "Too Warm!" depending on whether the temp falls
within the ideal fridge range of 32F to 40F.

The software side is built entirely in Python and runs as a single script
called bmo_fridge.py. It is multithreaded so the OLED screen updates every
2 seconds on the main thread while a background thread simultaneously listens
for input from a USB barcode scanner. When an item is scanned, the program
hits the free Open Food Facts API to automatically look up the product name
from the barcode number, then stores it in a local SQLite database with the
quantity, date added, and expiration date. Items can be added or removed via
scanner mode commands typed into the terminal. Every 10 seconds the current
temperature is appended to a CSV log file with a timestamp for historical
tracking, and every 30 seconds the program checks the database for any items
expiring within 3 days and prints a warning to the terminal. The project is
designed to run headlessly on the Pi with graceful fallbacks if the sensor
or screen is not connected, making it easy to develop and test before all
hardware is in hand.