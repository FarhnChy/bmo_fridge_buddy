"""Create verified, rotating backups of the BMO inventory database."""

from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3


def backup_database(database: Path, output_dir: Path, keep: int = 14) -> Path:
    if not database.exists():
        raise FileNotFoundError(f"Inventory database does not exist: {database}")
    if keep < 1:
        raise ValueError("keep must be at least 1")

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    destination = output_dir / f"fridge-{timestamp}.db"

    with closing(sqlite3.connect(database)) as source, closing(sqlite3.connect(destination)) as backup:
        source.backup(backup)
        result = backup.execute("PRAGMA integrity_check").fetchone()
        if result is None or result[0] != "ok":
            raise RuntimeError("Backup failed SQLite integrity verification")

    backups = sorted(output_dir.glob("fridge-*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
    for expired_backup in backups[keep:]:
        expired_backup.unlink()
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--keep", type=int, default=14)
    args = parser.parse_args()
    destination = backup_database(args.database, args.output, args.keep)
    print(f"Created verified backup: {destination}")


if __name__ == "__main__":
    main()
