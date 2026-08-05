import sqlite3
import unittest
from contextlib import closing
from pathlib import Path

from backup_database import backup_database


class BackupDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".backup_test"
        if self.root.exists():
            self.remove_test_files()
        self.root.mkdir(exist_ok=True)
        self.database = self.root / "fridge.db"
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute("CREATE TABLE inventory (name TEXT)")
            connection.execute("INSERT INTO inventory VALUES ('Milk')")
            connection.commit()

    def tearDown(self):
        self.remove_test_files()

    def remove_test_files(self):
        for path in sorted(self.root.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()

    def test_creates_verified_copy(self):
        destination = backup_database(self.database, self.root / "backups", keep=2)
        with closing(sqlite3.connect(destination)) as connection:
            row = connection.execute("SELECT name FROM inventory").fetchone()
        self.assertEqual(row[0], "Milk")

    def test_rotates_old_backups(self):
        backup_dir = self.root / "backups"
        backup_dir.mkdir(exist_ok=True)
        for index in range(3):
            old = backup_dir / f"fridge-20000101-00000{index}.db"
            old.write_bytes(b"old")
            old.touch()
        backup_database(self.database, backup_dir, keep=2)
        self.assertEqual(len(list(backup_dir.glob("fridge-*.db"))), 2)


if __name__ == "__main__":
    unittest.main()
