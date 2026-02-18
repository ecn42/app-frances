from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Exporte une base SQLite en dump SQL.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("APP_DB_PATH", str(root / "data" / "app.db"))),
        help="Chemin vers la base SQLite source.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "data" / "bootstrap_dump.sql",
        help="Chemin du fichier SQL genere.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.db.exists():
        raise FileNotFoundError(f"Base introuvable: {args.db}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(args.db) as conn:
        dump_sql = "\n".join(conn.iterdump()) + "\n"

    args.out.write_text(dump_sql, encoding="utf-8")
    print(f"Dump exporte: {args.out}")


if __name__ == "__main__":
    main()
