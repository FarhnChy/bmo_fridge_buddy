"""
What it does:
- Reads fridge temperature from a DS18B20 sensor when running on a Raspberry Pi.
- Shows a small BMO-style status screen on an SSD1306 I2C OLED when available.
- Stores scanned food inventory in SQLite.
- Logs temperature history to CSV.
- Lets a USB barcode scanner act like keyboard input.
- Looks up product names with the Open Food Facts API.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import csv
import json
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
import os


APP_NAME = "BMO Fridge"
APP_VERSION = "0.1"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fridge.db"
TEMP_LOG_PATH = BASE_DIR / "temperature_log.csv"

DISPLAY_REFRESH_SECONDS = 2
TEMPERATURE_LOG_SECONDS = 10
EXPIRATION_CHECK_SECONDS = 30
EXPIRING_SOON_DAYS = 3
FRIDGE_MIN_F = 32.0
FRIDGE_MAX_F = 40.0

# Open Food Facts asks API users to send a custom User-Agent with contact info.
OPEN_FOOD_FACTS_USER_AGENT = f"BMOFridge/{APP_VERSION} (https://github.com/FarhnChy/bmo_fridge_buddy)"
OPEN_FOOD_FACTS_URL = (
    "https://world.openfoodfacts.org/api/v3.6/product/{barcode}.json"
    "?fields=code,product_name,product_name_en,generic_name,"
    "abbreviated_product_name,brands,image_front_small_url"
)


def celsius_to_fahrenheit(temperature_c: float) -> float:
    return (temperature_c * (9 / 5)) + 32


@dataclass
class AppState:
    """Small shared state object for the display loop and scanner thread."""

    last_message: str = "BMO is waking up"
    last_temperature_c: float | None = None
    expiring_count: int = 0
    inventory_count: int = 0
    stop_requested: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock)

    def set_message(self, message: str) -> None:
        with self.lock:
            self.last_message = message

    def snapshot(self) -> dict[str, object]:
        with self.lock:
            return {
                "last_message": self.last_message,
                "last_temperature_c": self.last_temperature_c,
                "expiring_count": self.expiring_count,
                "inventory_count": self.inventory_count,
                "stop_requested": self.stop_requested,
            }


class BmoDisplay:
    """
    Wrapper around the OLED screen.

    If the Pi display libraries are not installed, this class uses terminal
    output instead. That keeps development possible before hardware is ready.
    """

    def __init__(self) -> None:
        self.hardware_ready = False
        self.last_terminal_status: str | None = None
        self.display = None
        self.image = None
        self.draw = None
        self.font = None

        try:
            import board
            import busio
            from PIL import Image, ImageDraw, ImageFont
            import adafruit_ssd1306

            i2c = busio.I2C(board.SCL, board.SDA)
            self.display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
            self.display.fill(0)
            self.display.show()

            self.image = Image.new("1", (128, 64))
            self.draw = ImageDraw.Draw(self.image)
            self.font = ImageFont.load_default()
            self.hardware_ready = True
        except Exception as exc:
            print(f"[display] Terminal mode: OLED unavailable ({exc})")

    def render(self, state: dict[str, object]) -> None:
        temperature = state["last_temperature_c"]
        if temperature is None:
            temp_text = "--.- F"
        else:
            temperature_f = celsius_to_fahrenheit(temperature)
            temp_text = f"{temperature_f:.1f} F"
        temp_status = classify_temperature_status(temperature)
        message = str(state["last_message"])[:22]
        inventory_count = state["inventory_count"]
        expiring_count = state["expiring_count"]

        if not self.hardware_ready:
            terminal_status = (
                f"[BMO] temp={temp_text} items={inventory_count} "
                f"expiring={expiring_count} status={temp_status} msg={message}"
            )
            if terminal_status != self.last_terminal_status:
                print(terminal_status)
                self.last_terminal_status = terminal_status
            return

        assert self.display is not None
        assert self.image is not None
        assert self.draw is not None
        assert self.font is not None

        self.draw.rectangle((0, 0, 127, 63), outline=0, fill=0)

        # Simple BMO face: eyes, smile, then status text below it.
        self.draw.rectangle((8, 8, 30, 26), outline=255, fill=0)
        self.draw.rectangle((98, 8, 120, 26), outline=255, fill=0)
        self.draw.arc((44, 12, 84, 42), 20, 160, fill=255)

        self.draw.text((0, 36), f"{temp_text} {temp_status}", font=self.font, fill=255)
        self.draw.text((0, 46), f"Items: {inventory_count}  Soon: {expiring_count}", font=self.font, fill=255)
        self.draw.text((0, 56), message, font=self.font, fill=255)

        self.display.image(self.image)
        self.display.show()


@contextmanager
def connect_db() -> Iterator[sqlite3.Connection]:
    """
    Yield a database connection and always close it afterward.

    Each function opens its own connection so the scanner thread and display
    loop do not share the same SQLite connection object.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    with connect_db() as connection:
        existing_table = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'inventory'"
        ).fetchone()

        # Version 0.1 allowed only one row per barcode. Migrate it in place so
        # different cartons of the same product can keep different dates.
        if existing_table and "barcode TEXT NOT NULL UNIQUE" in existing_table["sql"]:
            connection.execute("ALTER TABLE inventory RENAME TO inventory_legacy")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                expires_on TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS inventory_barcode_expiration
            ON inventory (barcode, COALESCE(expires_on, ''))
            """
        )

        if existing_table and "barcode TEXT NOT NULL UNIQUE" in existing_table["sql"]:
            connection.execute(
                """
                INSERT INTO inventory
                    (barcode, name, quantity, expires_on, created_at, updated_at)
                SELECT barcode, name, quantity, expires_on, created_at, updated_at
                FROM inventory_legacy
                """
            )
            connection.execute("DROP TABLE inventory_legacy")


def add_or_update_item(
    barcode: str,
    name: str,
    expires_on: str | None,
    quantity: int = 1,
) -> str:
    """
    Insert a new item or add one to the quantity if the barcode already exists.
    """

    now = datetime.now().isoformat(timespec="seconds")
    with connect_db() as connection:
        existing = connection.execute(
            "SELECT quantity FROM inventory WHERE barcode = ? AND expires_on IS ?",
            (barcode, expires_on),
        ).fetchone()

        if existing:
            connection.execute(
                """
                UPDATE inventory
                SET quantity = quantity + ?,
                    name = ?,
                    updated_at = ?
                WHERE barcode = ? AND expires_on IS ?
                """,
                (quantity, name, now, barcode, expires_on),
            )
            new_quantity = int(existing["quantity"]) + quantity
            return f"Added {quantity} {name} (qty {new_quantity})"

        connection.execute(
            """
            INSERT INTO inventory (barcode, name, quantity, expires_on, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (barcode, name, quantity, expires_on, now, now),
        )
        return f"Added {quantity} {name}"


def remove_one_item(barcode: str) -> str:
    with connect_db() as connection:
        item = connection.execute(
            """
            SELECT id, name, quantity FROM inventory
            WHERE barcode = ?
            ORDER BY expires_on IS NULL, expires_on, id
            LIMIT 1
            """,
            (barcode,),
        ).fetchone()

        if item is None:
            return f"Barcode {barcode} is not in inventory"

        if int(item["quantity"]) > 1:
            connection.execute(
                """
                UPDATE inventory
                SET quantity = quantity - 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(timespec="seconds"), item["id"]),
            )
            return f"Removed one {item['name']}"

        connection.execute("DELETE FROM inventory WHERE id = ?", (item["id"],))
        return f"Removed {item['name']}"


def remove_item_by_id(item_id: int, remove_all: bool = False) -> str | None:
    """Remove one unit (or a whole dated batch) for the web interface."""

    with connect_db() as connection:
        item = connection.execute(
            "SELECT id, name, quantity FROM inventory WHERE id = ?",
            (item_id,),
        ).fetchone()
        if item is None:
            return None

        if int(item["quantity"]) > 1 and not remove_all:
            connection.execute(
                """
                UPDATE inventory
                SET quantity = quantity - 1, updated_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(timespec="seconds"), item_id),
            )
            return f"Removed one {item['name']}"

        connection.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        return f"Removed {item['name']}"


def update_item_by_id(
    item_id: int,
    barcode: str,
    name: str,
    quantity: int,
    expires_on: str | None,
) -> str | None:
    """Update one dated inventory batch from the web interface."""

    with connect_db() as connection:
        existing = connection.execute(
            "SELECT id FROM inventory WHERE id = ?",
            (item_id,),
        ).fetchone()
        if existing is None:
            return None

        connection.execute(
            """
            UPDATE inventory
            SET barcode = ?, name = ?, quantity = ?, expires_on = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                barcode,
                name,
                quantity,
                expires_on,
                datetime.now().isoformat(timespec="seconds"),
                item_id,
            ),
        )
        return f"Updated {name}"


def list_inventory(limit: int = 10) -> list[sqlite3.Row]:
    with connect_db() as connection:
        return connection.execute(
            """
            SELECT id, barcode, name, quantity, expires_on
            FROM inventory
            ORDER BY expires_on IS NULL, expires_on, name
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def count_inventory() -> int:
    with connect_db() as connection:
        row = connection.execute("SELECT COALESCE(SUM(quantity), 0) AS total FROM inventory").fetchone()
        return int(row["total"])


def classify_temperature_status(temperature_c: float | None) -> str:
    if temperature_c is None:
        return "No sensor"

    temperature_f = celsius_to_fahrenheit(temperature_c)
    if temperature_f < FRIDGE_MIN_F:
        return "Too Cold!"
    if temperature_f > FRIDGE_MAX_F:
        return "Too Warm!"
    return "Normal"


def get_expiring_items(days: int = EXPIRING_SOON_DAYS) -> list[sqlite3.Row]:
    today = date.today()
    cutoff = today + timedelta(days=days)
    with connect_db() as connection:
        return connection.execute(
            """
            SELECT id, barcode, name, quantity, expires_on
            FROM inventory
            WHERE expires_on IS NOT NULL
              AND date(expires_on) <= date(?)
            ORDER BY expires_on, name
            """,
            (cutoff.isoformat(),),
        ).fetchall()


def fetch_product_details(barcode: str) -> dict[str, object]:
    """
    Ask Open Food Facts for a product name.

    Network failure or an unknown barcode should not crash the fridge buddy, so
    every failure path falls back to a readable barcode-based name.
    """

    encoded_barcode = urllib.parse.quote(barcode)
    url = OPEN_FOOD_FACTS_URL.format(barcode=encoded_barcode)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": OPEN_FOOD_FACTS_USER_AGENT,
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[api] Open Food Facts lookup failed: {exc}")
        return {"found": False, "name": f"Unknown item {barcode}", "image_url": None}

    product = payload.get("product") or {}
    product_name = (
        product.get("product_name")
        or product.get("product_name_en")
        or product.get("generic_name")
        or product.get("abbreviated_product_name")
    )
    brands = product.get("brands")

    if product_name and brands:
        name = f"{brands} {product_name}".strip()
    elif product_name:
        name = str(product_name).strip()
    else:
        name = f"Unknown item {barcode}"

    return {
        "found": bool(product_name),
        "name": name,
        "image_url": product.get("image_front_small_url"),
    }


def fetch_product_name(barcode: str) -> str:
    return str(fetch_product_details(barcode)["name"])


def parse_expiration_date(raw_value: str) -> str | None:
    raw_value = raw_value.strip()
    if not raw_value:
        return None

    try:
        parsed = datetime.strptime(raw_value, "%Y-%m-%d").date()
    except ValueError:
        print("Use expiration format YYYY-MM-DD, or leave it blank.")
        return None

    return parsed.isoformat()


def read_temperature_c() -> float | None:
    """
    Read a DS18B20 sensor through Linux's 1-Wire filesystem interface.

    On Raspberry Pi OS, enabled 1-Wire sensors usually appear at:
    /sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
    """

    device_root = Path("/sys/bus/w1/devices")
    if not device_root.exists():
        return None

    sensor_paths = sorted(device_root.glob("28-*/w1_slave"))
    if not sensor_paths:
        return None

    try:
        lines = sensor_paths[0].read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"[sensor] Could not read DS18B20: {exc}")
        return None

    if len(lines) < 2 or "YES" not in lines[0]:
        return None

    marker = "t="
    temperature_index = lines[1].find(marker)
    if temperature_index == -1:
        return None

    try:
        milli_celsius = int(lines[1][temperature_index + len(marker) :])
    except ValueError:
        return None

    return milli_celsius / 1000.0


def log_temperature(timestamp: datetime, temperature_c: float | None) -> None:
    file_exists = TEMP_LOG_PATH.exists()
    with TEMP_LOG_PATH.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(["timestamp", "temperature_c"])
        writer.writerow(
            [
                timestamp.isoformat(timespec="seconds"),
                "" if temperature_c is None else f"{temperature_c:.3f}",
            ]
        )


def print_help() -> None:
    print()
    print("Commands:")
    print("  <barcode>           scan/add an item")
    print("  remove <barcode>    remove one item")
    print("  list                show the next inventory items")
    print("  expiring            show items expiring soon")
    print("  help                show this help")
    print("  quit                stop the program")
    print()


def handle_barcode_scan(barcode: str, state: AppState) -> None:
    product_name = fetch_product_name(barcode)

    while True:
        try:
            raw_expiration = input("Expiration date YYYY-MM-DD, or blank: ")
        except EOFError:
            with state.lock:
                state.last_message = "Input closed"
                state.stop_requested = True
            return

        expires_on = parse_expiration_date(raw_expiration)
        if not raw_expiration.strip() or expires_on is not None:
            break

    message = add_or_update_item(barcode, product_name, expires_on)
    print(message)
    state.set_message(message)


def scanner_listener(state: AppState) -> None:
    """
    Listen for barcode scanner input.

    Most USB barcode scanners act like keyboards: they type the barcode and
    press Enter. That means input() is enough for a first version.
    """

    print_help()
    while True:
        try:
            raw_command = input("scan> ").strip()
        except EOFError:
            with state.lock:
                state.last_message = "Input closed"
                state.stop_requested = True
            return

        if not raw_command:
            continue

        command = raw_command.lower()
        if command in {"quit", "exit"}:
            with state.lock:
                state.stop_requested = True
            return

        if command == "help":
            print_help()
            continue

        if command == "list":
            rows = list_inventory()
            if not rows:
                print("Inventory is empty.")
            for row in rows:
                expires = row["expires_on"] or "no date"
                print(f"{row['quantity']}x {row['name']} | expires {expires} | {row['barcode']}")
            continue

        if command == "expiring":
            rows = get_expiring_items()
            if not rows:
                print("No items expiring soon.")
            for row in rows:
                print(f"{row['quantity']}x {row['name']} expires {row['expires_on']}")
            continue

        if command.startswith("remove "):
            barcode = raw_command.split(maxsplit=1)[1].strip()
            message = remove_one_item(barcode)
            print(message)
            state.set_message(message)
            continue

        handle_barcode_scan(raw_command, state)


def update_counts(state: AppState) -> None:
    expiring_items = get_expiring_items()
    inventory_count = count_inventory()

    with state.lock:
        state.expiring_count = len(expiring_items)
        state.inventory_count = inventory_count

    if expiring_items:
        first = expiring_items[0]
        state.set_message(f"Soon: {first['name']}")


def main() -> None:
    init_db()
    state = AppState()
    display = BmoDisplay()

    if os.environ.get("BMO_TERMINAL_INPUT", "1") != "0":
        listener = threading.Thread(
            target=scanner_listener,
            args=(state,),
            daemon=True,
        )
        listener.start()

    next_temperature_log = 0.0
    next_expiration_check = 0.0

    try:
        while True:
            snapshot = state.snapshot()
            if snapshot["stop_requested"]:
                break

            now = time.monotonic()
            temperature_c = read_temperature_c()
            with state.lock:
                state.last_temperature_c = temperature_c

            if now >= next_temperature_log:
                log_temperature(datetime.now(), temperature_c)
                next_temperature_log = now + TEMPERATURE_LOG_SECONDS

            if now >= next_expiration_check:
                update_counts(state)
                next_expiration_check = now + EXPIRATION_CHECK_SECONDS

            display.render(state.snapshot())
            time.sleep(DISPLAY_REFRESH_SECONDS)
    except KeyboardInterrupt:
        state.set_message("BMO shutting down")
    finally:
        print(f"{APP_NAME} stopped.")


if __name__ == "__main__":
    main()
