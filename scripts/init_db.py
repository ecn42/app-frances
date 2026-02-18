from __future__ import annotations

import sqlite3
import os
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    db_path = Path(os.getenv("APP_DB_PATH", str(data_dir / "app.db")))
    schema_path = data_dir / "schema.sql"
    seed_path = data_dir / "seed.sql"

    data_dir.mkdir(parents=True, exist_ok=True)

    schema_sql = schema_path.read_text(encoding="utf-8")
    seed_sql = seed_path.read_text(encoding="utf-8")

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        conn.executescript(seed_sql)
        conn.commit()
    finally:
        conn.close()

    print(f"Base initialisee: {db_path}")


if __name__ == "__main__":
    main()
