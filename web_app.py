"""Phone-friendly web interface for BMO Fridge Buddy."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, render_template, request

import bmo_fridge


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(JSON_SORT_KEYS=False)
    if test_config:
        app.config.update(test_config)

    bmo_fridge.init_db()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/inventory")
    def inventory():
        return jsonify([dict(row) for row in bmo_fridge.list_inventory(limit=500)])

    @app.get("/api/expiring")
    def expiring():
        return jsonify([dict(row) for row in bmo_fridge.get_expiring_items()])

    @app.get("/api/status")
    def status():
        temperature_c = bmo_fridge.read_temperature_c()
        return jsonify(
            {
                "temperature_c": temperature_c,
                "temperature_f": (
                    round(bmo_fridge.celsius_to_fahrenheit(temperature_c), 1)
                    if temperature_c is not None
                    else None
                ),
                "temperature_status": bmo_fridge.classify_temperature_status(temperature_c),
                "inventory_count": bmo_fridge.count_inventory(),
                "expiring_count": len(bmo_fridge.get_expiring_items()),
            }
        )

    @app.post("/api/products/lookup")
    def lookup_product():
        payload = request.get_json(silent=True) or {}
        barcode = normalize_barcode(payload.get("barcode"))
        if barcode is None:
            return jsonify({"error": "Enter a barcode containing 4 to 18 digits."}), 400
        return jsonify({"barcode": barcode, **bmo_fridge.fetch_product_details(barcode)})

    @app.post("/api/inventory")
    def add_inventory():
        payload = request.get_json(silent=True) or {}
        barcode = normalize_barcode(payload.get("barcode"))
        if barcode is None:
            return jsonify({"error": "Enter a barcode containing 4 to 18 digits."}), 400

        expires_on = normalize_expiration(payload.get("expires_on"))
        if expires_on is False:
            return jsonify({"error": "Expiration date must use YYYY-MM-DD."}), 400

        try:
            quantity = int(payload.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 0
        if not 1 <= quantity <= 99:
            return jsonify({"error": "Quantity must be between 1 and 99."}), 400

        name = str(payload.get("name") or "").strip()
        if not name:
            name = bmo_fridge.fetch_product_name(barcode)
        name = name[:160]

        message = bmo_fridge.add_or_update_item(barcode, name, expires_on, quantity)
        return jsonify({"message": message}), 201

    @app.delete("/api/inventory/<int:item_id>")
    def remove_inventory(item_id: int):
        remove_all = request.args.get("all") == "1"
        message = bmo_fridge.remove_item_by_id(item_id, remove_all=remove_all)
        if message is None:
            return jsonify({"error": "Inventory item was not found."}), 404
        return jsonify({"message": message})

    @app.patch("/api/inventory/<int:item_id>")
    def update_inventory(item_id: int):
        payload = request.get_json(silent=True) or {}
        barcode = normalize_barcode(payload.get("barcode"))
        if barcode is None:
            return jsonify({"error": "Enter a barcode containing 4 to 18 digits."}), 400

        name = str(payload.get("name") or "").strip()[:160]
        if not name:
            return jsonify({"error": "Enter an item name."}), 400

        expires_on = normalize_expiration(payload.get("expires_on"))
        if expires_on is False:
            return jsonify({"error": "Expiration date must use YYYY-MM-DD."}), 400

        try:
            quantity = int(payload.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 0
        if not 1 <= quantity <= 99:
            return jsonify({"error": "Quantity must be between 1 and 99."}), 400

        try:
            message = bmo_fridge.update_item_by_id(
                item_id, barcode, name, quantity, expires_on
            )
        except sqlite3.IntegrityError:
            return jsonify(
                {"error": "That barcode and expiration date already exist. Edit the existing batch instead."}
            ), 409
        if message is None:
            return jsonify({"error": "Inventory item was not found."}), 404
        return jsonify({"message": message})

    return app


def normalize_barcode(value: object) -> str | None:
    barcode = str(value or "").strip().replace(" ", "")
    if not barcode.isdigit() or not 4 <= len(barcode) <= 18:
        return None
    return barcode


def normalize_expiration(value: object) -> str | None | bool:
    raw_value = str(value or "").strip()
    if not raw_value:
        return None
    try:
        return datetime.strptime(raw_value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return False


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("BMO_WEB_HOST", "0.0.0.0")
    port = int(os.environ.get("BMO_WEB_PORT", "5000"))
    cert = os.environ.get("BMO_TLS_CERT")
    key = os.environ.get("BMO_TLS_KEY")
    if bool(cert) != bool(key):
        raise SystemExit("Set both BMO_TLS_CERT and BMO_TLS_KEY, or neither.")
    if cert and key:
        app.run(host=host, port=port, debug=False, ssl_context=(cert, key))
    else:
        from waitress import serve

        serve(app, host=host, port=port, threads=4)
