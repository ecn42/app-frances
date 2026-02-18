INSERT INTO categories (slug, nom, description) VALUES
('vocabulaire', 'Vocabulaire', 'Mots essentiels classes par themes et niveaux.'),
('grammaire', 'Grammaire', 'Fiches pratiques pour les structures de base.'),
('regles-grammaire', 'Regles de grammaire', 'Regles detaillees avec exemples et pieges frequents.'),
('temps-verbaux', 'Temps verbaux', 'Usage des temps (present, passe, futur, conditionnel).'),
('conjugaison', 'Conjugaison', 'Conjugaisons par verbe et par temps.'),
('qcm', 'QCM', 'Questions a choix multiple corrigees.'),
('expression-ecrite', 'Expression ecrite', 'Sujets de redaction de style TCF.');

INSERT INTO lessons (category_slug, titre, niveau, resume, contenu_markdown, tags_json) VALUES
(
  'grammaire',
  'Articles definis et indefinis',
  'A2',
  'Savoir choisir entre le/la/les et un/une/des.',
  'Utilise **le/la/les** quand le nom est deja connu.\n\nUtilise **un/une/des** pour introduire une information nouvelle.\n\nExemple: *J''ai achete un livre. Le livre est interessant.*',
  '["articles", "determinants"]'
),
(
  'regles-grammaire',
  'Negation simple et avancee',
  'A2',
  'Construire correctement ne...pas, ne...jamais, ne...personne.',
  'La negation entoure le verbe conjugue.\n\n- Je **ne** comprends **pas**.\n- Il **ne** sort **jamais**.\n- Nous **ne** voyons **personne**.',
  '["negation"]'
),
(
  'temps-verbaux',
  'Imparfait vs passe compose',
  'B1',
  'Differencier le contexte (imparfait) et l''action ponctuelle (passe compose).',
  'Utilise l''**imparfait** pour une habitude ou une description.\n\nUtilise le **passe compose** pour un evenement termine.\n\nExemple: *Il pleuvait quand je suis sorti.*',
  '["imparfait", "passe-compose"]'
),
(
  'grammaire',
  'Pronoms COD et COI',
  'B1',
  'Remplacer un nom sans repeter la phrase.',
  'COD: le, la, les.\n\nCOI: lui, leur.\n\nExemple: *Je parle a mon professeur -> Je lui parle.*',
  '["pronoms", "cod", "coi"]'
);

INSERT INTO vocabulary (mot, definition_fr, traduction_en, exemple_fr, niveau, theme) VALUES
('ameliorer', 'Rendre meilleur, progresser.', 'to improve', 'Je veux ameliorer mon francais ecrit.', 'B1', 'Etudes'),
('enjeu', 'Ce qui est important dans une situation.', 'stake/issue', 'Le principal enjeu de l''examen est la clarte.', 'B2', 'Examens'),
('fiable', 'En qui on peut avoir confiance.', 'reliable', 'Cette source est fiable.', 'B1', 'Travail'),
('epanouissement', 'Developpement personnel positif.', 'fulfillment', 'La lecture contribue a mon epanouissement.', 'B2', 'Societe'),
('rigoureux', 'Tres precis et serieux.', 'rigorous', 'Il faut etre rigoureux en grammaire.', 'B1', 'Etudes'),
('defi', 'Difficulte a surmonter.', 'challenge', 'Le TCF est un defi motivant.', 'A2', 'Examens'),
('objectif', 'But a atteindre.', 'goal', 'Mon objectif est le niveau B2.', 'A2', 'Etudes'),
('pertinent', 'Adapté et utile au sujet.', 'relevant', 'Ton exemple est pertinent.', 'B2', 'Expression'),
('nuancer', 'Exprimer une idee avec precision.', 'to nuance', 'Il faut nuancer son opinion.', 'B2', 'Expression'),
('coherent', 'Logique et bien organise.', 'coherent', 'Ton paragraphe est coherent.', 'B1', 'Expression');

INSERT INTO verb_conjugations (infinitif, temps, personne, forme, exemple_fr, niveau) VALUES
('etre', 'present', 'je', 'suis', 'Je suis motive pour reviser.', 'A1'),
('etre', 'present', 'tu', 'es', 'Tu es pret pour le test.', 'A1'),
('etre', 'present', 'il/elle', 'est', 'Elle est tres concentree.', 'A1'),
('etre', 'present', 'nous', 'sommes', 'Nous sommes en cours.', 'A1'),
('etre', 'present', 'vous', 'etes', 'Vous etes ponctuels.', 'A1'),
('etre', 'present', 'ils/elles', 'sont', 'Ils sont en avance.', 'A1'),
('avoir', 'passe compose', 'je', 'ai eu', 'J''ai eu une bonne note.', 'A2'),
('avoir', 'passe compose', 'nous', 'avons eu', 'Nous avons eu un exercice difficile.', 'A2'),
('aller', 'futur simple', 'je', 'irai', 'J''irai a la bibliotheque demain.', 'A2'),
('aller', 'futur simple', 'nous', 'irons', 'Nous irons au centre de langues.', 'A2'),
('faire', 'conditionnel present', 'je', 'ferais', 'Je ferais plus d''exercices.', 'B1'),
('faire', 'conditionnel present', 'vous', 'feriez', 'Vous feriez mieux de relire.', 'B1');

INSERT INTO exercises (type, theme, niveau, question, options_json, answer_index, explication, lesson_id) VALUES
(
  'qcm',
  'Articles',
  'A2',
  'Je voudrais ___ eau minerale.',
  '["de", "du", "de la", "des"]',
  2,
  'Eau est feminin singulier et non comptable ici: de la.',
  1
),
(
  'qcm',
  'Negation',
  'A2',
  'Nous ne voyons ___ dans la salle.',
  '["rien", "jamais", "personne", "plus"]',
  2,
  'Pour les personnes, on utilise ne...personne.',
  2
),
(
  'qcm',
  'Temps verbaux',
  'B1',
  'Quand j''etais enfant, je ___ beaucoup.',
  '["ai lu", "lisais", "lirais", "lirai"]',
  1,
  'Habitude dans le passe: imparfait.',
  3
),
(
  'qcm',
  'Pronoms',
  'B1',
  'Je parle a mes parents. Je ___ parle tous les soirs.',
  '["les", "leur", "lui", "en"]',
  1,
  'Parler a + personne = COI -> leur.',
  4
),
(
  'qcm',
  'Subjonctif',
  'B2',
  'Il faut que tu ___ ton texte.',
  '["corriges", "corrigeras", "as corrige", "corrigerais"]',
  0,
  'Apres il faut que, on emploie le subjonctif present.',
  NULL
);

INSERT INTO writing_prompts (titre, tache_tcf, niveau, consigne, min_mots, max_mots) VALUES
(
  'Debat: apprentissage en ligne',
  'Tache 3',
  'B2',
  'Donnez votre opinion sur l''apprentissage en ligne. Presentez avantages, limites et votre position personnelle.',
  180,
  220
),
(
  'Message formel',
  'Tache 1',
  'B1',
  'Ecrivez un message a l''administration de votre universite pour demander un report d''examen.',
  60,
  120
),
(
  'Recit personnel',
  'Tache 2',
  'B1',
  'Racontez une situation ou vous avez surmonte une difficulte dans vos etudes.',
  120,
  160
);
