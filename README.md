# French Practice Studio

Streamlit app de preparation TCF (interface 100% francaise), avec base SQLite et sections de pratique.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/generate_content_pack_v3.py
python3 scripts/import_content_pack.py --reset-schema
python3 -m streamlit run app.py
```

Optional local secrets (already ignored by git):

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "..."
OPENAI_MODEL = "gpt-5-mini"
```

## Deploy on Railway

### 1) Push code (including DB migration snapshot)

This repo now includes:

- `scripts/bootstrap_db.py`: initializes DB on first container start.
- `data/bootstrap_dump.sql`: snapshot exported from your current `data/app.db`.

On first Railway boot:
- if `data/bootstrap_dump.sql` exists, it restores from this dump;
- otherwise it falls back to `content/packs/tcf_pack_v3.json`.

### 2) Create Railway service from GitHub

1. Push this repo to GitHub.
2. Create a new Railway project from that repo.
3. Railway will use `railway.toml` and run:

```bash
python run.py
```

### 3) Add a persistent volume (important for SQLite)

Attach a volume to the service and mount it at:

```text
/app/data
```

This keeps `data/app.db` persistent across deploys/restarts.

### 4) Add hidden Railway variables (for OpenAI key)

In Railway service variables, add:

- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-5-mini` (optional)

Optional DB path override (only if you mount elsewhere):

- `APP_DB_PATH=/custom/mount/app.db`

You can copy suggested names from `.env.example`.

### 5) Deploy and open app

After deployment, open the generated Railway URL.

The app uses the server OpenAI key internally (not prefilled in a visible text field).

## DB migration commands

Re-export the latest local DB snapshot any time before deploy:

```bash
python3 scripts/export_sqlite_dump.py --db data/app.db --out data/bootstrap_dump.sql
```

Force a one-time reset/import on Railway (advanced):

- set `BOOTSTRAP_RESET=1`, redeploy once, then remove it.

## Why this setup

- Uses Streamlit 1.54.0, including `st.container(..., horizontal=...)`.
- Uses SQLite (`data/app.db`) for vocabulary, lessons, conjugation, QCM, and writing prompts.
- Includes a dedicated `Comprehension ecrite` module (TCF-style reading texts + graded QCM).
- `scripts/import_content_pack.py` imports the full JSON content pack.
- `scripts/generate_content_pack_v3.py` regenerates the enriched v3 content pack.
- `scripts/export_pack_to_csv.py` exports JSON pack to CSV for spreadsheet editing.
- `scripts/import_csv_pack.py` imports CSV content back into the app DB.
- `docs/database-strategy.md` describes the path to scale from SQLite to Railway PostgreSQL.
- `docs/content-admin.md` documents the content admin workflow.
- `run.py` binds to Railway's injected `PORT`.
- `railway.toml` defines startup and healthcheck configuration.
- `scripts/bootstrap_db.py` safely bootstraps DB only when needed.
