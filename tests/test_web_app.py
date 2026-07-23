import unittest
import sqlite3
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import bmo_fridge
import web_app


class WebAppTest(unittest.TestCase):
    def setUp(self):
        self.db_path = Path(__file__).parent / ".test_inventory.db"
        self.db_path.unlink(missing_ok=True)
        self.db_patch = patch.object(bmo_fridge, "DB_PATH", self.db_path)
        self.db_patch.start()
        self.app = web_app.create_app({"TESTING": True})
        self.client = self.app.test_client()

    def tearDown(self):
        self.db_patch.stop()
        self.db_path.unlink(missing_ok=True)

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Scan a barcode", response.data)

    @patch.object(bmo_fridge, "fetch_product_details")
    def test_lookup_returns_product(self, lookup):
        lookup.return_value = {"found": True, "name": "Test Milk", "image_url": None}
        response = self.client.post("/api/products/lookup", json={"barcode": "012345678905"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Test Milk")

    def test_add_list_and_remove_dated_batches(self):
        first = {"barcode": "012345678905", "name": "Milk", "quantity": 2, "expires_on": "2026-08-01"}
        second = {**first, "quantity": 1, "expires_on": "2026-08-08"}
        self.assertEqual(self.client.post("/api/inventory", json=first).status_code, 201)
        self.assertEqual(self.client.post("/api/inventory", json=second).status_code, 201)

        items = self.client.get("/api/inventory").get_json()
        self.assertEqual(len(items), 2)
        self.assertEqual(sum(item["quantity"] for item in items), 3)

        response = self.client.delete(f"/api/inventory/{items[0]['id']}")
        self.assertEqual(response.status_code, 200)
        remaining = self.client.get("/api/inventory").get_json()
        self.assertEqual(sum(item["quantity"] for item in remaining), 2)

    def test_rejects_invalid_input(self):
        response = self.client.post(
            "/api/inventory",
            json={"barcode": "not-a-barcode", "name": "Bad", "expires_on": "tomorrow"},
        )
        self.assertEqual(response.status_code, 400)

    def test_migrates_existing_inventory_without_losing_items(self):
        self.db_path.unlink(missing_ok=True)
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute(
                """
                CREATE TABLE inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode TEXT NOT NULL UNIQUE,
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
                INSERT INTO inventory
                    (barcode, name, quantity, expires_on, created_at, updated_at)
                VALUES ('12345678', 'Yogurt', 2, '2026-08-01', 'now', 'now')
                """
            )
            connection.commit()
        bmo_fridge.init_db()
        items = self.client.get("/api/inventory").get_json()
        self.assertEqual(items[0]["name"], "Yogurt")
        self.assertEqual(items[0]["quantity"], 2)


if __name__ == "__main__":
    unittest.main()
