from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
from pathlib import Path
from typing import Any


CSV_FILES = {
    "categories": "categories.csv",
    "lessons": "lessons.csv",
    "vocabulary": "vocabulary.csv",
    "verb_conjugations": "verb_conjugations.csv",
    "exercises": "exercises.csv",
    "writing_prompts": "writing_prompts.csv",
    "reading_passages": "reading_passages.csv",
    "reading_questions": "reading_questions.csv",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


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


def import_from_folder(db_path: Path, folder: Path, replace: bool) -> None:
    conn = sqlite3.connect(db_path)
    try:
        if replace:
            clear_tables(conn)

        categories = load_csv(folder / CSV_FILES["categories"])
        lessons = load_csv(folder / CSV_FILES["lessons"])
        vocabulary = load_csv(folder / CSV_FILES["vocabulary"])
        conjugations = load_csv(folder / CSV_FILES["verb_conjugations"])
        exercises = load_csv(folder / CSV_FILES["exercises"])
        prompts = load_csv(folder / CSV_FILES["writing_prompts"])
        reading_passages = load_csv(folder / CSV_FILES["reading_passages"])
        reading_questions = load_csv(folder / CSV_FILES["reading_questions"])

        for row in categories:
            conn.execute(
                "INSERT INTO categories (slug, nom, description) VALUES (?, ?, ?)",
                (row["slug"], row["nom"], row["description"]),
            )

        lesson_lookup: dict[tuple[str, str], int] = {}
        for row in lessons:
            tags_raw = row.get("tags_json", "[]")
            try:
                tags = json.loads(tags_raw)
            except json.JSONDecodeError:
                tags = [tag.strip() for tag in tags_raw.split("|") if tag.strip()]
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
                    json.dumps(tags, ensure_ascii=False),
                ),
            )
            lesson_lookup[(row["category_slug"], row["titre"])] = int(cur.lastrowid)

        for row in vocabulary:
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

        for row in conjugations:
            conn.execute(
                """
                INSERT INTO verb_conjugations (infinitif, temps, personne, forme, exemple_fr, niveau)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["infinitif"],
                    row["temps"],
                    row["personne"],
                    row["forme"],
                    row["exemple_fr"],
                    row["niveau"],
                ),
            )

        for row in exercises:
            lesson_id = None
            key = (row.get("lesson_category_slug", ""), row.get("lesson_titre", ""))
            if key in lesson_lookup:
                lesson_id = lesson_lookup[key]

            options_raw = row.get("options_json", "[]")
            try:
                options = json.loads(options_raw)
            except json.JSONDecodeError:
                options = [opt.strip() for opt in options_raw.split("|") if opt.strip()]

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
                    json.dumps(options, ensure_ascii=False),
                    int(row["answer_index"]),
                    row["explication"],
                    lesson_id,
                ),
            )

        for row in prompts:
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
                    int(row["min_mots"]),
                    int(row["max_mots"]),
                ),
            )

        passage_lookup: dict[str, int] = {}
        for row in reading_passages:
            cur = conn.execute(
                """
                INSERT INTO reading_passages (titre, niveau, type_document, contexte, duree_recommandee_min, texte)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["titre"],
                    row["niveau"],
                    row["type_document"],
                    row["contexte"],
                    int(row["duree_recommandee_min"]),
                    row["texte"],
                ),
            )
            passage_lookup[row["titre"]] = int(cur.lastrowid)

        for row in reading_questions:
            passage_id = passage_lookup.get(row["passage_titre"])
            if not passage_id:
                continue
            options_raw = row.get("options_json", "[]")
            try:
                options = json.loads(options_raw)
            except json.JSONDecodeError:
                options = [opt.strip() for opt in options_raw.split("|") if opt.strip()]

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
                    int(row["ordre"]),
                    row["niveau"],
                    row["difficulte"],
                    row["competence"],
                    row["question"],
                    json.dumps(options, ensure_ascii=False),
                    int(row["answer_index"]),
                    row["explication"],
                ),
            )

        conn.commit()
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Importe un pack CSV dans SQLite.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.getenv("APP_DB_PATH", str(root / "data" / "app.db"))),
        help="Chemin vers la base SQLite cible.",
    )
    parser.add_argument(
        "--folder",
        type=Path,
        default=root / "content" / "csv_pack_template",
        help="Dossier contenant les CSV.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Vide les tables avant import.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import_from_folder(db_path=args.db, folder=args.folder, replace=args.replace)
    print(f"Import CSV termine depuis: {args.folder}")


if __name__ == "__main__":
    main()
