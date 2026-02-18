# Database Strategy (TCF App)

## Current choice
- **SQLite local file**: `data/app.db`
- Good for rapid iteration and local edits.
- Seeded with `data/schema.sql` + `data/seed.sql`.

## Tables
- `categories`: navigation/section metadata.
- `lessons`: grammar, rules, and tense lessons.
- `vocabulary`: word bank.
- `verb_conjugations`: conjugation entries.
- `exercises`: QCM items (options stored as JSON).
- `writing_prompts`: writing practice prompts.

## Content scaling path
1. Keep generating content as SQL inserts (or CSV -> import script).
2. Add lightweight admin scripts for bulk import/update.
3. When deploying to Railway for multi-user usage, move to **PostgreSQL**.

## PostgreSQL migration (later)
1. Provision Railway PostgreSQL.
2. Keep same logical schema.
3. Replace `sqlite3` in `db.py` with `psycopg`/`SQLAlchemy`.
4. Add migration tool (`alembic`) and versioned migrations.
5. Move secrets/config to environment variables.
