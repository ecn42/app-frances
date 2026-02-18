from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path
from typing import Any


PERSONNES = ["je", "tu", "il/elle", "nous", "vous", "ils/elles"]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Le pack JSON doit etre un objet.")
    return data


def apply_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    schema_sql = schema_path.read_text(encoding="utf-8")
    conn.executescript(schema_sql)


def clear_tables(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM reading_questions")
    conn.execute("DELETE FROM reading_passages")
    conn.execute("DELETE FROM writing_prompts")
    conn.execute("DELETE FROM exercises")
    conn.execute("DELETE FROM verb_conjugations")
    conn.execute("DELETE FROM vocabulary")
    conn.execute("DELETE FROM lessons")
    conn.execute("DELETE FROM categories")


def insert_categories(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO categories (slug, nom, description)
            VALUES (?, ?, ?)
            """,
            (row["slug"], row["nom"], row["description"]),
        )


def insert_lessons(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> dict[tuple[str, str], int]:
    mapping: dict[tuple[str, str], int] = {}
    for row in rows:
        tags_json = json.dumps(row.get("tags", []), ensure_ascii=False)
        cur = conn.execute(
            """
            INSERT INTO lessons (category_slug, titre, niveau, resume, contenu_markdown, tags_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["category_slug"],
                row["titre"],
                row["niveau"],
                row["resume"],
                row["contenu_markdown"],
                tags_json,
            ),
        )
        lesson_id = int(cur.lastrowid)
        mapping[(row["category_slug"], row["titre"])] = lesson_id
    return mapping


def insert_vocabulary(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO vocabulary (mot, definition_fr, traduction_en, exemple_fr, niveau, theme)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["mot"],
                row["definition_fr"],
                row["traduction_en"],
                row["exemple_fr"],
                row["niveau"],
                row["theme"],
            ),
        )


def _example_for_conjugation(infinitif: str, temps: str, personne: str, forme: str) -> str:
    return f"{personne} {forme} ce verbe ({infinitif}) au {temps}."


def insert_conjugations(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        infinitif = row["infinitif"]
        temps = row["temps"]
        niveau = row["niveau"]
        formes = row["formes"]

        if isinstance(formes, dict):
            for personne in PERSONNES:
                forme = formes.get(personne)
                if not forme:
                    continue
                exemple = _example_for_conjugation(infinitif, temps, personne, forme)
                conn.execute(
                    """
                    INSERT INTO verb_conjugations (infinitif, temps, personne, forme, exemple_fr, niveau)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (infinitif, temps, personne, forme, exemple, niveau),
                )
            continue

        if isinstance(formes, list):
            for entry in formes:
                personne = entry["personne"]
                forme = entry["forme"]
                exemple = entry.get("exemple_fr") or _example_for_conjugation(
                    infinitif, temps, personne, forme
                )
                conn.execute(
                    """
                    INSERT INTO verb_conjugations (infinitif, temps, personne, forme, exemple_fr, niveau)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (infinitif, temps, personne, forme, exemple, niveau),
                )
            continue

        raise ValueError(f"Champ 'formes' invalide pour {infinitif} - {temps}")


def insert_exercises(
    conn: sqlite3.Connection,
    rows: list[dict[str, Any]],
    lesson_lookup: dict[tuple[str, str], int],
) -> None:
    for row in rows:
        lesson_id = None
        if row.get("lesson_category_slug") and row.get("lesson_titre"):
            lesson_id = lesson_lookup.get((row["lesson_category_slug"], row["lesson_titre"]))

        options_json = json.dumps(row["options"], ensure_ascii=False)
        conn.execute(
            """
            INSERT INTO exercises (type, theme, niveau, question, options_json, answer_index, explication, lesson_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["type"],
                row["theme"],
                row["niveau"],
                row["question"],
                options_json,
                row["answer_index"],
                row["explication"],
                lesson_id,
            ),
        )


def insert_writing_prompts(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO writing_prompts (titre, tache_tcf, niveau, consigne, min_mots, max_mots)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["titre"],
                row["tache_tcf"],
                row["niveau"],
                row["consigne"],
                row["min_mots"],
                row["max_mots"],
            ),
        )


def insert_reading_passages(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    for passage in rows:
        cur = conn.execute(
            """
            INSERT INTO reading_passages (titre, niveau, type_document, contexte, duree_recommandee_min, texte)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                passage["titre"],
                passage["niveau"],
                passage["type_document"],
                passage["contexte"],
                int(passage["duree_recommandee_min"]),
                passage["texte"],
            ),
        )
        passage_id = int(cur.lastrowid)

        for idx, question in enumerate(passage.get("questions", []), start=1):
            ordre = int(question.get("ordre", idx))
            options_json = json.dumps(question["options"], ensure_ascii=False)
            conn.execute(
                """
                INSERT INTO reading_questions (
                    passage_id, ordre, niveau, difficulte, competence,
                    question, options_json, answer_index, explication
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    passage_id,
                    ordre,
                    question["niveau"],
                    question["difficulte"],
                    question["competence"],
                    question["question"],
                    options_json,
                    int(question["answer_index"]),
                    question["explication"],
                ),
            )


def count_table(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def import_pack(
    db_path: Path,
    pack_path: Path,
    schema_path: Path,
    reset_schema: bool,
    replace_data: bool,
) -> None:
    data = read_json(pack_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        if reset_schema:
            apply_schema(conn, schema_path)
        elif replace_data:
            clear_tables(conn)

        lesson_lookup: dict[tuple[str, str], int] = {}

        insert_categories(conn, data.get("categories", []))
        lesson_lookup = insert_lessons(conn, data.get("lessons", []))
        insert_vocabulary(conn, data.get("vocabulary", []))
        insert_conjugations(conn, data.get("verb_conjugations", []))
        insert_exercises(conn, data.get("exercises", []), lesson_lookup)
        insert_writing_prompts(conn, data.get("writing_prompts", []))
        insert_reading_passages(conn, data.get("reading_passages", []))

        conn.commit()
    finally:
        conn.close()

    conn = sqlite3.connect(db_path)
    try:
        print(f"Import termine depuis: {pack_path}")
        for table in [
            "categories",
            "lessons",
            "vocabulary",
            "verb_conjugations",
            "exercises",
            "writing_prompts",
            "reading_passages",
            "reading_questions",
        ]:
            print(f"- {table}: {count_table(conn, table)}")
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Importe un pack de contenu JSON dans SQLite.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("APP_DB_PATH", str(root / "data" / "app.db"))),
        help="Chemin vers la base SQLite cible.",
    )
    parser.add_argument(
        "--pack",
        type=Path,
        default=root / "content" / "packs" / "tcf_pack_v3.json",
        help="Chemin vers le pack JSON.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=root / "data" / "schema.sql",
        help="Chemin vers schema.sql.",
    )
    parser.add_argument(
        "--reset-schema",
        action="store_true",
        help="Recree completement la base via schema.sql avant import.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Vide les tables existantes avant import (sans recreer le schema).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import_pack(
        db_path=args.db,
        pack_path=args.pack,
        schema_path=args.schema,
        reset_schema=args.reset_schema,
        replace_data=args.replace,
    )


if __name__ == "__main__":
    main()
