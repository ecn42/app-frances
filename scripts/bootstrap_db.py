from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from import_content_pack import import_pack


def resolve_paths() -> tuple[Path, Path, Path, Path]:
    root = Path(__file__).resolve().parents[1]
    db_path = Path(os.getenv("APP_DB_PATH", str(root / "data" / "app.db")))
    schema_path = Path(os.getenv("DB_SCHEMA_PATH", str(root / "data" / "schema.sql")))
    pack_path = Path(
        os.getenv("CONTENT_PACK_PATH", str(root / "content" / "packs" / "tcf_pack_v3.json"))
    )
    dump_path = Path(os.getenv("DB_SQL_DUMP_PATH", str(root / "data" / "bootstrap_dump.sql")))
    return db_path, schema_path, pack_path, dump_path


def table_has_rows(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
    return int(cur.fetchone()[0]) > 0


def needs_bootstrap(db_path: Path) -> bool:
    if not db_path.exists():
        return True
    try:
        with sqlite3.connect(db_path) as conn:
            for table in ("categories", "lessons", "vocabulary", "exercises", "reading_passages"):
                if not table_has_rows(conn, table):
                    return True
    except sqlite3.DatabaseError:
        return True
    return False


def main() -> None:
    db_path, schema_path, pack_path, dump_path = resolve_paths()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    force_reset = os.getenv("BOOTSTRAP_RESET", "0") == "1"
    if not force_reset and not needs_bootstrap(db_path):
        print(f"[bootstrap] Base deja prete, aucune action: {db_path}")
        return

    if dump_path.exists():
        print(f"[bootstrap] Initialisation depuis dump SQL: {dump_path}")
        if db_path.exists():
            db_path.unlink()
        with sqlite3.connect(db_path) as conn:
            sql = dump_path.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.commit()
        print("[bootstrap] Dump SQL importe.")
        return

    print(f"[bootstrap] Initialisation depuis pack de contenu: {db_path}")
    print(f"[bootstrap] Schema: {schema_path}")
    print(f"[bootstrap] Pack: {pack_path}")
    import_pack(
        db_path=db_path,
        pack_path=pack_path,
        schema_path=schema_path,
        reset_schema=True,
        replace_data=False,
    )
    print("[bootstrap] Base importee depuis pack.")


if __name__ == "__main__":
    main()
