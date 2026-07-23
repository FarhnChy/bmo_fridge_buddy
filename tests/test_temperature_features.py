import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import bmo_fridge


class TemperatureFeatureTest(unittest.TestCase):
    def setUp(self):
        self.log_path = Path(__file__).parent / ".temperature_history.csv"
        self.log_path.unlink(missing_ok=True)
        self.path_patch = patch.object(bmo_fridge, "TEMP_LOG_PATH", self.log_path)
        self.path_patch.start()

    def tearDown(self):
        self.path_patch.stop()
        self.log_path.unlink(missing_ok=True)

    def test_bmo_moods_follow_temperature_status(self):
        self.assertEqual(bmo_fridge.get_bmo_mood(None), "sleepy")
        self.assertEqual(bmo_fridge.get_bmo_mood(-1.0), "cold")
        self.assertEqual(bmo_fridge.get_bmo_mood(4.0), "happy")
        self.assertEqual(bmo_fridge.get_bmo_mood(6.0), "worried")

    def test_history_skips_blank_old_and_malformed_rows(self):
        recent = datetime.now() - timedelta(minutes=5)
        old = datetime.now() - timedelta(days=2)
        self.log_path.write_text(
            "timestamp,temperature_c\n"
            f"{old.isoformat(timespec='seconds')},3.000\n"
            f"{recent.isoformat(timespec='seconds')},4.000\n"
            f"{recent.isoformat(timespec='seconds')},\n"
            "not-a-date,not-a-number\n",
            encoding="utf-8",
        )
        points = bmo_fridge.read_temperature_history(hours=24)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0]["temperature_f"], 39.2)
        self.assertEqual(points[0]["status"], "Normal")

    def test_missing_history_is_empty(self):
        self.assertEqual(bmo_fridge.read_temperature_history(), [])


if __name__ == "__main__":
    unittest.main()
