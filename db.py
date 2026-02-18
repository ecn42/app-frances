from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("APP_DB_PATH", str(ROOT_DIR / "data" / "app.db")))


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def database_exists() -> bool:
    return DB_PATH.exists()


def ensure_auth_tables() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module TEXT NOT NULL,
                event_type TEXT NOT NULL,
                score REAL,
                total REAL,
                meta_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_activity_user ON user_activity(user_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_activity_module ON user_activity(module)"
        )
        conn.commit()


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(query, params).fetchone()
    return dict(row) if row else None


def count_rows(table: str) -> int:
    row = fetch_one(f"SELECT COUNT(*) AS total FROM {table}")
    return int(row["total"]) if row else 0


def list_levels_for_table(table: str, column: str = "niveau") -> list[str]:
    rows = fetch_all(
        f"SELECT DISTINCT {column} AS value FROM {table} WHERE {column} != '' ORDER BY {column}"
    )
    return [row["value"] for row in rows]


def list_themes_vocab() -> list[str]:
    rows = fetch_all("SELECT DISTINCT theme FROM vocabulary ORDER BY theme")
    return [row["theme"] for row in rows]


def list_themes_qcm() -> list[str]:
    rows = fetch_all("SELECT DISTINCT theme FROM exercises WHERE type = 'qcm' ORDER BY theme")
    return [row["theme"] for row in rows]


def list_verbs() -> list[str]:
    rows = fetch_all("SELECT DISTINCT infinitif FROM verb_conjugations ORDER BY infinitif")
    return [row["infinitif"] for row in rows]


def list_tenses_for_verb(verb: str) -> list[str]:
    rows = fetch_all(
        "SELECT DISTINCT temps FROM verb_conjugations WHERE infinitif = ? ORDER BY temps",
        (verb,),
    )
    return [row["temps"] for row in rows]


def search_lessons(category_slug: str, search: str, level: str) -> list[dict[str, Any]]:
    query = """
        SELECT id, titre, niveau, resume, contenu_markdown, tags_json
        FROM lessons
        WHERE category_slug = ?
    """
    params: list[Any] = [category_slug]
    if level != "Tous":
        query += " AND niveau = ?"
        params.append(level)
    if search.strip():
        query += " AND (lower(titre) LIKE ? OR lower(resume) LIKE ? OR lower(contenu_markdown) LIKE ?)"
        like = f"%{search.lower()}%"
        params.extend([like, like, like])
    query += " ORDER BY niveau, titre"

    rows = fetch_all(query, tuple(params))
    for row in rows:
        try:
            row["tags"] = json.loads(row["tags_json"])
        except json.JSONDecodeError:
            row["tags"] = []
    return rows


def search_vocabulary(search: str, level: str, theme: str, limit: int = 100) -> list[dict[str, Any]]:
    query = """
        SELECT mot, definition_fr, traduction_en, exemple_fr, niveau, theme
        FROM vocabulary
        WHERE 1 = 1
    """
    params: list[Any] = []
    if level != "Tous":
        query += " AND niveau = ?"
        params.append(level)
    if theme != "Tous":
        query += " AND theme = ?"
        params.append(theme)
    if search.strip():
        query += " AND (lower(mot) LIKE ? OR lower(definition_fr) LIKE ? OR lower(exemple_fr) LIKE ?)"
        like = f"%{search.lower()}%"
        params.extend([like, like, like])

    query += " ORDER BY mot LIMIT ?"
    params.append(limit)
    return fetch_all(query, tuple(params))


def get_conjugations(verb: str, tense: str) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT personne, forme, exemple_fr, niveau
        FROM verb_conjugations
        WHERE infinitif = ? AND temps = ?
        ORDER BY CASE personne
            WHEN 'je' THEN 1
            WHEN 'tu' THEN 2
            WHEN 'il/elle' THEN 3
            WHEN 'nous' THEN 4
            WHEN 'vous' THEN 5
            WHEN 'ils/elles' THEN 6
            ELSE 99
        END
        """,
        (verb, tense),
    )


def get_qcm(theme: str, level: str) -> list[dict[str, Any]]:
    query = """
        SELECT id, question, options_json, answer_index, explication, niveau, theme
        FROM exercises
        WHERE type = 'qcm'
    """
    params: list[Any] = []
    if level != "Tous":
        query += " AND niveau = ?"
        params.append(level)
    if theme != "Tous":
        query += " AND theme = ?"
        params.append(theme)
    query += " ORDER BY id"

    rows = fetch_all(query, tuple(params))
    for row in rows:
        row["options"] = json.loads(row["options_json"])
    return rows


def get_writing_prompts(level: str) -> list[dict[str, Any]]:
    if level == "Tous":
        return fetch_all(
            "SELECT id, titre, tache_tcf, niveau, consigne, min_mots, max_mots FROM writing_prompts ORDER BY id"
        )
    return fetch_all(
        """
        SELECT id, titre, tache_tcf, niveau, consigne, min_mots, max_mots
        FROM writing_prompts
        WHERE niveau = ?
        ORDER BY id
        """,
        (level,),
    )


def _make_password_hash(password: str, salt: str | None = None) -> str:
    use_salt = salt or os.urandom(16).hex()
    digest = hashlib.sha256(f"{use_salt}:{password}".encode("utf-8")).hexdigest()
    return f"{use_salt}${digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    if "$" not in stored_hash:
        return False
    salt, expected = stored_hash.split("$", 1)
    candidate = _make_password_hash(password, salt).split("$", 1)[1]
    return hmac.compare_digest(candidate, expected)


def create_user(username: str, password: str) -> tuple[bool, str]:
    username_clean = username.strip().lower()
    if len(username_clean) < 3:
        return False, "Le nom d'utilisateur doit contenir au moins 3 caracteres."
    if len(password) < 4:
        return False, "Le mot de passe doit contenir au moins 4 caracteres."

    password_hash = _make_password_hash(password)
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username_clean, password_hash),
            )
            conn.commit()
        return True, "Compte cree."
    except sqlite3.IntegrityError:
        return False, "Nom d'utilisateur deja utilise."


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    username_clean = username.strip().lower()
    row = fetch_one("SELECT id, username, password_hash FROM users WHERE username = ?", (username_clean,))
    if not row:
        return None
    if not _verify_password(password, row["password_hash"]):
        return None
    return {"id": row["id"], "username": row["username"]}


def record_user_activity(
    user_id: int,
    module: str,
    event_type: str,
    score: float | int | None = None,
    total: float | int | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    meta_json = json.dumps(meta or {}, ensure_ascii=False)
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_activity (user_id, module, event_type, score, total, meta_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, module, event_type, score, total, meta_json),
        )
        conn.commit()


def get_user_stats(user_id: int) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT
            module,
            COUNT(*) AS tentatives,
            AVG(CASE WHEN total > 0 AND score IS NOT NULL THEN (score * 100.0 / total) END) AS moyenne_pct
        FROM user_activity
        WHERE user_id = ?
        GROUP BY module
        """,
        (user_id,),
    )
    out: dict[str, Any] = {}
    for row in rows:
        out[row["module"]] = {
            "tentatives": int(row["tentatives"]),
            "moyenne_pct": round(float(row["moyenne_pct"]), 1) if row["moyenne_pct"] is not None else None,
        }
    return out


def get_user_recent_activity(user_id: int, limit: int = 8) -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT module, event_type, score, total, meta_json, created_at
        FROM user_activity
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    for row in rows:
        try:
            row["meta"] = json.loads(row["meta_json"])
        except json.JSONDecodeError:
            row["meta"] = {}
    return rows


def list_reading_levels() -> list[str]:
    rows = fetch_all("SELECT DISTINCT niveau FROM reading_passages ORDER BY niveau")
    return [row["niveau"] for row in rows]


def get_reading_passages(level: str) -> list[dict[str, Any]]:
    if level == "Tous":
        return fetch_all(
            """
            SELECT p.id, p.titre, p.niveau, p.type_document, p.contexte, p.duree_recommandee_min, p.texte,
                   COUNT(q.id) AS nb_questions
            FROM reading_passages p
            LEFT JOIN reading_questions q ON q.passage_id = p.id
            GROUP BY p.id
            ORDER BY p.id
            """
        )
    return fetch_all(
        """
        SELECT p.id, p.titre, p.niveau, p.type_document, p.contexte, p.duree_recommandee_min, p.texte,
               COUNT(q.id) AS nb_questions
        FROM reading_passages p
        LEFT JOIN reading_questions q ON q.passage_id = p.id
        WHERE p.niveau = ?
        GROUP BY p.id
        ORDER BY p.id
        """,
        (level,),
    )


def get_reading_questions(passage_id: int) -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT id, ordre, niveau, difficulte, competence, question, options_json, answer_index, explication
        FROM reading_questions
        WHERE passage_id = ?
        ORDER BY ordre, id
        """,
        (passage_id,),
    )
    for row in rows:
        row["options"] = json.loads(row["options_json"])
    return rows
