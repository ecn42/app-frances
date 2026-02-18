PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS user_activity;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS reading_questions;
DROP TABLE IF EXISTS reading_passages;
DROP TABLE IF EXISTS writing_prompts;
DROP TABLE IF EXISTS exercises;
DROP TABLE IF EXISTS verb_conjugations;
DROP TABLE IF EXISTS vocabulary;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    module TEXT NOT NULL,
    event_type TEXT NOT NULL,
    score REAL,
    total REAL,
    meta_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_slug TEXT NOT NULL,
    titre TEXT NOT NULL,
    niveau TEXT NOT NULL,
    resume TEXT NOT NULL,
    contenu_markdown TEXT NOT NULL,
    tags_json TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (category_slug) REFERENCES categories(slug) ON DELETE CASCADE
);

CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mot TEXT NOT NULL,
    definition_fr TEXT NOT NULL,
    traduction_en TEXT NOT NULL,
    exemple_fr TEXT NOT NULL,
    niveau TEXT NOT NULL,
    theme TEXT NOT NULL
);

CREATE TABLE verb_conjugations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    infinitif TEXT NOT NULL,
    temps TEXT NOT NULL,
    personne TEXT NOT NULL,
    forme TEXT NOT NULL,
    exemple_fr TEXT NOT NULL,
    niveau TEXT NOT NULL
);

CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    theme TEXT NOT NULL,
    niveau TEXT NOT NULL,
    question TEXT NOT NULL,
    options_json TEXT NOT NULL,
    answer_index INTEGER NOT NULL,
    explication TEXT NOT NULL,
    lesson_id INTEGER,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL
);

CREATE TABLE writing_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    tache_tcf TEXT NOT NULL,
    niveau TEXT NOT NULL,
    consigne TEXT NOT NULL,
    min_mots INTEGER NOT NULL,
    max_mots INTEGER NOT NULL
);

CREATE TABLE reading_passages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    niveau TEXT NOT NULL,
    type_document TEXT NOT NULL,
    contexte TEXT NOT NULL,
    duree_recommandee_min INTEGER NOT NULL,
    texte TEXT NOT NULL
);

CREATE TABLE reading_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passage_id INTEGER NOT NULL,
    ordre INTEGER NOT NULL,
    niveau TEXT NOT NULL,
    difficulte TEXT NOT NULL,
    competence TEXT NOT NULL,
    question TEXT NOT NULL,
    options_json TEXT NOT NULL,
    answer_index INTEGER NOT NULL,
    explication TEXT NOT NULL,
    FOREIGN KEY (passage_id) REFERENCES reading_passages(id) ON DELETE CASCADE
);

CREATE INDEX idx_lessons_category ON lessons(category_slug);
CREATE INDEX idx_lessons_level ON lessons(niveau);
CREATE INDEX idx_vocab_level ON vocabulary(niveau);
CREATE INDEX idx_vocab_theme ON vocabulary(theme);
CREATE INDEX idx_conjugations_infinitif ON verb_conjugations(infinitif);
CREATE INDEX idx_conjugations_temps ON verb_conjugations(temps);
CREATE INDEX idx_exercises_type ON exercises(type);
CREATE INDEX idx_exercises_level ON exercises(niveau);
CREATE INDEX idx_reading_passages_level ON reading_passages(niveau);
CREATE INDEX idx_reading_questions_passage ON reading_questions(passage_id);
CREATE INDEX idx_user_activity_user ON user_activity(user_id);
CREATE INDEX idx_user_activity_module ON user_activity(module);
