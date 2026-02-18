from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def flatten_conjugations(pack_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in pack_rows:
        formes = row.get("formes", {})
        if isinstance(formes, dict):
            for personne, forme in formes.items():
                out.append(
                    {
                        "infinitif": row["infinitif"],
                        "temps": row["temps"],
                        "personne": personne,
                        "forme": forme,
                        "exemple_fr": f"{personne} {forme} ce verbe ({row['infinitif']}) au {row['temps']}.",
                        "niveau": row["niveau"],
                    }
                )
        elif isinstance(formes, list):
            for entry in formes:
                out.append(
                    {
                        "infinitif": row["infinitif"],
                        "temps": row["temps"],
                        "personne": entry["personne"],
                        "forme": entry["forme"],
                        "exemple_fr": entry.get("exemple_fr", ""),
                        "niveau": row["niveau"],
                    }
                )
    return out


def flatten_lessons(pack_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in pack_rows:
        out.append(
            {
                "category_slug": row["category_slug"],
                "titre": row["titre"],
                "niveau": row["niveau"],
                "resume": row["resume"],
                "contenu_markdown": row["contenu_markdown"],
                "tags_json": json.dumps(row.get("tags", []), ensure_ascii=False),
            }
        )
    return out


def flatten_exercises(pack_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in pack_rows:
        out.append(
            {
                "type": row["type"],
                "theme": row["theme"],
                "niveau": row["niveau"],
                "question": row["question"],
                "options_json": json.dumps(row["options"], ensure_ascii=False),
                "answer_index": row["answer_index"],
                "explication": row["explication"],
                "lesson_category_slug": row.get("lesson_category_slug", ""),
                "lesson_titre": row.get("lesson_titre", ""),
            }
        )
    return out


def flatten_reading_passages(pack_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in pack_rows:
        out.append(
            {
                "titre": row["titre"],
                "niveau": row["niveau"],
                "type_document": row["type_document"],
                "contexte": row["contexte"],
                "duree_recommandee_min": row["duree_recommandee_min"],
                "texte": row["texte"],
            }
        )
    return out


def flatten_reading_questions(pack_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for passage in pack_rows:
        titre = passage["titre"]
        for idx, q in enumerate(passage.get("questions", []), start=1):
            out.append(
                {
                    "passage_titre": titre,
                    "ordre": q.get("ordre", idx),
                    "niveau": q["niveau"],
                    "difficulte": q["difficulte"],
                    "competence": q["competence"],
                    "question": q["question"],
                    "options_json": json.dumps(q["options"], ensure_ascii=False),
                    "answer_index": q["answer_index"],
                    "explication": q["explication"],
                }
            )
    return out


def export_csv(pack: dict[str, Any], out_dir: Path) -> None:
    write_csv(
        out_dir / "categories.csv",
        pack.get("categories", []),
        ["slug", "nom", "description"],
    )
    write_csv(
        out_dir / "lessons.csv",
        flatten_lessons(pack.get("lessons", [])),
        ["category_slug", "titre", "niveau", "resume", "contenu_markdown", "tags_json"],
    )
    write_csv(
        out_dir / "vocabulary.csv",
        pack.get("vocabulary", []),
        ["mot", "definition_fr", "traduction_en", "exemple_fr", "niveau", "theme"],
    )
    write_csv(
        out_dir / "verb_conjugations.csv",
        flatten_conjugations(pack.get("verb_conjugations", [])),
        ["infinitif", "temps", "personne", "forme", "exemple_fr", "niveau"],
    )
    write_csv(
        out_dir / "exercises.csv",
        flatten_exercises(pack.get("exercises", [])),
        [
            "type",
            "theme",
            "niveau",
            "question",
            "options_json",
            "answer_index",
            "explication",
            "lesson_category_slug",
            "lesson_titre",
        ],
    )
    write_csv(
        out_dir / "writing_prompts.csv",
        pack.get("writing_prompts", []),
        ["titre", "tache_tcf", "niveau", "consigne", "min_mots", "max_mots"],
    )
    write_csv(
        out_dir / "reading_passages.csv",
        flatten_reading_passages(pack.get("reading_passages", [])),
        ["titre", "niveau", "type_document", "contexte", "duree_recommandee_min", "texte"],
    )
    write_csv(
        out_dir / "reading_questions.csv",
        flatten_reading_questions(pack.get("reading_passages", [])),
        [
            "passage_titre",
            "ordre",
            "niveau",
            "difficulte",
            "competence",
            "question",
            "options_json",
            "answer_index",
            "explication",
        ],
    )


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Exporte un pack JSON vers CSV.")
    parser.add_argument(
        "--pack",
        type=Path,
        default=root / "content" / "packs" / "tcf_pack_v3.json",
        help="Pack JSON source.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "content" / "csv_pack_template",
        help="Dossier CSV de sortie.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pack = read_json(args.pack)
    export_csv(pack, args.out)
    print(f"Export CSV termine: {args.out}")


if __name__ == "__main__":
    main()
