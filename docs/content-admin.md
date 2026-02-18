# Content Admin Workflow

## 1) Import JSON pack into SQLite
```bash
python3 scripts/import_content_pack.py --reset-schema
```

Options:
- `--pack <path>`: use a different JSON pack.
- `--db <path>`: target a different SQLite file.
- `--replace`: clear data without recreating schema.

## 2) Export JSON pack to CSV (for spreadsheet editing)
```bash
python3 scripts/export_pack_to_csv.py
```

Default output folder:
- `content/csv_pack_template/`

## 3) Re-import edited CSV files
```bash
python3 scripts/import_csv_pack.py --folder content/csv_pack_template --replace
```

Required CSV files:
- `categories.csv`
- `lessons.csv`
- `vocabulary.csv`
- `verb_conjugations.csv`
- `exercises.csv`
- `writing_prompts.csv`
- `reading_passages.csv`
- `reading_questions.csv`

## Pack file used by default
- `content/packs/tcf_pack_v3.json`

## Regenerate v3 pack
```bash
python3 scripts/generate_content_pack_v3.py
```
