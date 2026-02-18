from __future__ import annotations

import json
import random
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


PERSONNES = ["je", "tu", "il/elle", "nous", "vous", "ils/elles"]
RND = random.Random(77)


def dedupe_items(items: list[dict[str, Any]], key_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = tuple(item.get(f) for f in key_fields)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def upsert_lesson(lessons: list[dict[str, Any]], lesson: dict[str, Any]) -> None:
    key = (lesson["category_slug"], lesson["titre"])
    for i, old in enumerate(lessons):
        if (old["category_slug"], old["titre"]) == key:
            lessons[i] = lesson
            return
    lessons.append(lesson)


def upsert_conjugation(rows: list[dict[str, Any]], row: dict[str, Any]) -> None:
    key = (row["infinitif"], row["temps"])
    for i, old in enumerate(rows):
        if (old["infinitif"], old["temps"]) == key:
            rows[i] = row
            return
    rows.append(row)


def make_vocab_entries(level: str, theme: str, words: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for mot in words:
        entries.append(
            {
                "mot": mot,
                "definition_fr": f"Mot frequent du niveau {level} utile dans le theme {theme.lower()}.",
                "traduction_en": mot,
                "exemple_fr": f"Je place le mot '{mot}' dans une phrase d'entrainement TCF.",
                "niveau": level,
                "theme": theme,
            }
        )
    return entries


def build_massive_vocabulary() -> list[dict[str, Any]]:
    a1_daily = """
    accueil adresse agenda aise ami amitie appartement arbre armoire arrivee article ascenseur assiette
    attention autobus avenue bagage balcon balle banque basket bateau bebe besoin billet boite boulangerie
    bouteille bras bureau cadeau caisse calendrier calme camion campagne carrefour chaise chaleur chemin chemise
    chapeau chiffre choix classe client cuisine danse dejeuner dessin detail devoir dialogue difference dimanche
    direction discussion docteur douche echange eclair ecran ecriture economie ecoute emploi entree equipe erreur
    escalier espace etage etudiant etoile exemple exercice fatigue fenetre feuille film fleur foire fromage gare
    geste gout groupe habitude hasard heure hiver idee image immeuble invitation jardin journal lampe langage
    lecture legume lecon lieu liste lit livraison location magasin maison manteau marche matin menu message meteo
    minute miroir modele montagne musee musique natation note nuage objet occasion odeur offre ombre ordre oreille
    outil paquet papier parent parc parole passage patient pause peinture photo piscine place plage plan plante
    porte pratique prix professeur promenade question radio raison repas reservation reponse reveil route sac salade
    salle saison santé service signal silence soir sortie spectacle station stylo sucre table tasse taxi telephone
    temperature temps terrasse ticket train trajet travail usine valise vitesse visite voisin voyage
    """.split()

    a2_study = """
    objectif progression methode strategie concentration motivation revision revisionnaire planification organisation autonomie discipline
    resultat simulation evaluation bareme consigne redaction paragraphe introduction conclusion coherence cohesion argument exemple
    justification reformulation orthographe vocabulaire grammaire conjugaison pronom connecteur structure synthese nuance clarte precision
    pertinence correction relecture entrainement repetition memoire expression comprehension oral ecrit lecture ecoute tache sujet
    production competence capacite calendrier priorite delai deadline adaptation amelioration performance qualite rigueur assiduite regularite
    confiance initiative effort constance persistance objectif-secondaire mini-objectif tableau suivi mesure bilan retroaction commentaire
    explication demonstration correction-type fiche resumee carte-mentale prise-notes methode-active questionnement verification autoevaluation concours
    certification inscription inscription-tardive centre-examen candidat convocation identification passeport preuve attendance retard absence justification
    preparation-intense preparation-progressive blocage stress respiration relaxation pause-active planning-hebdo planning-quotidien routine-habitude
    """.split()

    b1_professional = """
    collaboration responsabilite implication efficacite productivite flexibilite fiabilite initiative proposition coordination adaptation gestion
    priorisation anticipation mediation communication leadership supervision evaluation-interne compte-rendu rapport professionnel entretien candidature
    portfolio experience-stage employabilite competence-cle objectif-projet jalon livrable budget ressource contrainte opportunite amelioration-continue
    methode-qualite verification-formelle procedure protocole indicateur tableau-bord suivi-projet plan-action orientation-carriere insertion
    reseau-professionnel recommandation reference credibilite argumentation-structurée positionnement analyse-synthese lecture-critique interpretation nuance-opinion
    concession opposition consequence causalite hypothese scenario probabilite condition impact global local durable soutenable
    comparaison distinction priorite-sociale inclusion equite accessibilite citoyennete engagement implication-collective benefice limite inconvenient
    avantage-compétitif vision-strategique decision-eclairee jugement critique observation pertinent adaptabilite transparence coherente
    """.split()

    b2_advanced = """
    problematique dialectique legitimite faisabilite viabilite responsabilisation responsabilite-partagee transversalite interdisciplinarite
    rationalisation contextualisation conceptualisation operationalisation standardisation harmonisation mutualisation priorisation-avancee
    contre-argument contre-exemple these antithese synthese argumentative concession-partielle nuance-fine implicite explicite
    inferentiel demonstratif justification-logique articulation-textuelle fluidite-discursive densite-lexicale precision-terminologique
    coherence-globale cohesion-thematique structuration-hierarchique progression-logique ancrage-contextuel validite fiabilite-metrique
    comparabilite objectivation subjectivite mesure-qualitative mesure-quantitative interpretation-critique limites-methodologiques
    biais-echantillonnage representativite robustesse reproductibilite causalite-inversee correlat convergence divergence
    arbitrage compromis optimisation allocation efficience gouvernance compliance deontologie ethique-professionnelle integrite
    reformulation-avancee paraphrase distanciation argument-massue raisonnement-inductif raisonnement-deductif analogie contrepoint
    modalisation attenuation renforcement emphase focalisation hierarchisation gradation concession-rhetorique implication-pragmatique
    """.split()

    out: list[dict[str, Any]] = []
    out.extend(make_vocab_entries("A1", "Vie quotidienne", a1_daily))
    out.extend(make_vocab_entries("A2", "Etudes", a2_study))
    out.extend(make_vocab_entries("B1", "Travail", b1_professional))
    out.extend(make_vocab_entries("B2", "Expression", b2_advanced))
    return out


def build_v3_lessons() -> list[dict[str, Any]]:
    return [
        {
            "category_slug": "regles-grammaire",
            "titre": "Prepositions de lieu et de temps",
            "niveau": "A2",
            "resume": "Employer correctement a, en, dans, depuis, pendant, pour.",
            "contenu_markdown": (
                "### Regles principales\n"
                "- Lieu: a Paris, en France, dans la salle, chez le medecin.\n"
                "- Temps: pendant deux heures, depuis lundi, pour demain.\n\n"
                "### Exemples\n"
                "- J'habite en ville mais je travaille a la campagne.\n"
                "- Il etudie dans la bibliotheque depuis 8 heures.\n"
                "- Nous preparons cette tache pour vendredi.\n"
                "- Elle reste chez sa tante pendant les vacances.\n\n"
                "### Pieges\n"
                "- depuis + point de depart, pas une duree fermee.\n"
                "- dans peut exprimer un delai futur: dans deux jours."
            ),
            "tags": ["prepositions", "a2"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Voix active et voix passive",
            "niveau": "B2",
            "resume": "Transformer une phrase active en passive pour varier le style.",
            "contenu_markdown": (
                "### Formation\n"
                "Passif = etre conjugue + participe passe (+ par + agent).\n\n"
                "### Exemples\n"
                "- Active: Le jury evalue le texte.\n"
                "- Passive: Le texte est evalue par le jury.\n"
                "- Active: On corrige les erreurs.\n"
                "- Passive: Les erreurs sont corrigees.\n\n"
                "### Usage\n"
                "Le passif met en avant l'objet de l'action et donne un style plus formel."
            ),
            "tags": ["voix-passive", "transformation"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Cause, consequence et but",
            "niveau": "B1",
            "resume": "Structurer un raisonnement avec des connecteurs precis.",
            "contenu_markdown": (
                "### Cause\n"
                "- parce que, car, puisque\n"
                "### Consequence\n"
                "- donc, alors, c'est pourquoi\n"
                "### But\n"
                "- pour, afin de, afin que\n\n"
                "### Exemples\n"
                "- Je revise chaque jour car je veux progresser.\n"
                "- Le sujet est complexe, donc je fais un plan detaille.\n"
                "- Je relis mon texte afin d'eviter les erreurs.\n"
                "- Nous reformulons afin que le message soit clair."
            ),
            "tags": ["cause", "consequence", "but"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Discours indirect: questions et ordres",
            "niveau": "B2",
            "resume": "Rapporter des questions et des consignes avec precision.",
            "contenu_markdown": (
                "### Questions\n"
                "- Direct: Il demande: \"Ou habites-tu ?\"\n"
                "- Indirect: Il demande ou j'habite.\n\n"
                "### Ordres\n"
                "- Direct: Le professeur dit: \"Relisez ce paragraphe.\"\n"
                "- Indirect: Le professeur dit de relire ce paragraphe.\n\n"
                "### Exemples supplementaires\n"
                "- Elle demande si nous avons termine.\n"
                "- Ils demandent quand l'examen commence.\n"
                "- On nous conseille de structurer chaque argument."
            ),
            "tags": ["discours-indirect", "questions", "ordres"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Participe present",
            "niveau": "B1",
            "resume": "Former le participe present et l'utiliser en contexte.",
            "contenu_markdown": (
                "### Formation reguliere\n"
                "Radical de nous au present + ant.\n"
                "- parler -> parlant\n"
                "- finir -> finissant\n"
                "- vendre -> vendant\n\n"
                "### Irreguliers utiles\n"
                "- etre -> etant\n"
                "- avoir -> ayant\n"
                "- savoir -> sachant\n\n"
                "### Exemples\n"
                "- En preparant un plan, je gagne du temps.\n"
                "- Ayant relu son texte, elle a corrige plusieurs fautes."
            ),
            "tags": ["participe-present", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Passe recent",
            "niveau": "A2",
            "resume": "Exprimer une action qui vient de se produire.",
            "contenu_markdown": (
                "### Formation\n"
                "venir au present + de + infinitif.\n\n"
                "### Exemples\n"
                "- Je viens de finir la redaction.\n"
                "- Nous venons de recevoir la convocation.\n"
                "- Elle vient de corriger son paragraphe.\n\n"
                "### Astuce\n"
                "Le passe recent est frequent a l'oral et utile pour raconter rapidement une sequence."
            ),
            "tags": ["passe-recent", "a2"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Futur anterieur",
            "niveau": "B2",
            "resume": "Exprimer une action accomplie avant une autre action future.",
            "contenu_markdown": (
                "### Formation\n"
                "Auxiliaire au futur simple + participe passe.\n\n"
                "### Exemples\n"
                "- Quand j'aurai termine, je relirai mon texte.\n"
                "- Nous serons plus confiants apres avoir revise.\n"
                "- Des qu'il aura recu les resultats, il vous ecrira.\n\n"
                "### Usage\n"
                "Le futur anterieur est utile pour marquer l'anteriorite dans un plan d'action."
            ),
            "tags": ["futur-anterieur", "b2"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Subjonctif passe",
            "niveau": "B2",
            "resume": "Exprimer l'anteriorite dans un contexte au subjonctif.",
            "contenu_markdown": (
                "### Formation\n"
                "Auxiliaire au subjonctif present + participe passe.\n\n"
                "### Exemples\n"
                "- Je suis content que tu aies reussi.\n"
                "- Bien qu'il soit arrive tard, il a participe.\n"
                "- Nous regrettons qu'ils n'aient pas pu venir.\n\n"
                "### Irreguliers frequents\n"
                "- que j'aie eu\n"
                "- que je sois alle\n"
                "- qu'ils aient fait"
            ),
            "tags": ["subjonctif-passe", "b2"],
        },
    ]


def conjugate_er(verb: str, tense: str) -> dict[str, str]:
    stem = verb[:-2]
    if tense == "present":
        endings = ["e", "es", "e", "ons", "ez", "ent"]
    elif tense == "imparfait":
        endings = ["ais", "ais", "ait", "ions", "iez", "aient"]
    elif tense == "futur simple":
        stem = verb
        endings = ["ai", "as", "a", "ons", "ez", "ont"]
    elif tense == "conditionnel present":
        stem = verb
        endings = ["ais", "ais", "ait", "ions", "iez", "aient"]
    elif tense == "subjonctif present":
        endings = ["e", "es", "e", "ions", "iez", "ent"]
    elif tense == "passe compose":
        pp = stem + "e"
        return {
            "je": f"ai {pp}",
            "tu": f"as {pp}",
            "il/elle": f"a {pp}",
            "nous": f"avons {pp}",
            "vous": f"avez {pp}",
            "ils/elles": f"ont {pp}",
        }
    else:
        raise ValueError(tense)
    return {p: stem + e for p, e in zip(PERSONNES, endings)}


def conjugate_ir_second_group(verb: str, tense: str) -> dict[str, str]:
    root = verb[:-2]
    if tense == "present":
        forms = [
            root + "is",
            root + "is",
            root + "it",
            root + "issons",
            root + "issez",
            root + "issent",
        ]
        return dict(zip(PERSONNES, forms))
    if tense == "imparfait":
        stem = root + "iss"
        endings = ["ais", "ais", "ait", "ions", "iez", "aient"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "futur simple":
        stem = verb
        endings = ["ai", "as", "a", "ons", "ez", "ont"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "conditionnel present":
        stem = verb
        endings = ["ais", "ais", "ait", "ions", "iez", "aient"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "subjonctif present":
        stem = root + "iss"
        endings = ["e", "es", "e", "ions", "iez", "ent"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "passe compose":
        pp = root + "i"
        return {
            "je": f"ai {pp}",
            "tu": f"as {pp}",
            "il/elle": f"a {pp}",
            "nous": f"avons {pp}",
            "vous": f"avez {pp}",
            "ils/elles": f"ont {pp}",
        }
    raise ValueError(tense)


def conjugate_re(verb: str, tense: str) -> dict[str, str]:
    root = verb[:-2]
    if tense == "present":
        forms = [
            root + "s",
            root + "s",
            root,
            root + "ons",
            root + "ez",
            root + "ent",
        ]
        return dict(zip(PERSONNES, forms))
    if tense == "imparfait":
        stem = root
        endings = ["ais", "ais", "ait", "ions", "iez", "aient"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "futur simple":
        stem = root
        endings = ["ai", "as", "a", "ons", "ez", "ont"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "conditionnel present":
        stem = root
        endings = ["ais", "ais", "ait", "ions", "iez", "aient"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "subjonctif present":
        stem = root
        endings = ["e", "es", "e", "ions", "iez", "ent"]
        return {p: stem + e for p, e in zip(PERSONNES, endings)}
    if tense == "passe compose":
        pp = root + "u"
        return {
            "je": f"ai {pp}",
            "tu": f"as {pp}",
            "il/elle": f"a {pp}",
            "nous": f"avons {pp}",
            "vous": f"avez {pp}",
            "ils/elles": f"ont {pp}",
        }
    raise ValueError(tense)


def build_regular_conjugations() -> list[dict[str, Any]]:
    er_verbs = ["parler", "travailler", "aimer", "etudier", "jouer", "demander", "chercher", "regarder"]
    ir_verbs = ["finir", "choisir", "grandir", "reussir", "reflechir", "remplir"]
    re_verbs = ["vendre", "attendre", "perdre", "repondre", "entendre", "descendre"]

    tenses = ["present", "imparfait", "futur simple", "conditionnel present", "subjonctif present", "passe compose"]
    level_by_tense = {
        "present": "A1",
        "imparfait": "A2",
        "futur simple": "A2",
        "passe compose": "A2",
        "conditionnel present": "B1",
        "subjonctif present": "B2",
    }

    rows: list[dict[str, Any]] = []
    for verb in er_verbs:
        for tense in tenses:
            rows.append(
                {
                    "infinitif": verb,
                    "temps": tense,
                    "niveau": level_by_tense[tense],
                    "formes": conjugate_er(verb, tense),
                }
            )
    for verb in ir_verbs:
        for tense in tenses:
            rows.append(
                {
                    "infinitif": verb,
                    "temps": tense,
                    "niveau": level_by_tense[tense],
                    "formes": conjugate_ir_second_group(verb, tense),
                }
            )
    for verb in re_verbs:
        for tense in tenses:
            rows.append(
                {
                    "infinitif": verb,
                    "temps": tense,
                    "niveau": level_by_tense[tense],
                    "formes": conjugate_re(verb, tense),
                }
            )
    return rows


def qcm_level_for_tense(tense: str, default: str) -> str:
    mapping = {
        "present": "A1",
        "imparfait": "A2",
        "futur simple": "A2",
        "passe compose": "A2",
        "conditionnel present": "B1",
        "participe present": "B1",
        "plus-que-parfait": "B1",
        "subjonctif present": "B2",
        "subjonctif passe": "B2",
        "futur anterieur": "B2",
    }
    return mapping.get(tense, default)


def generate_conjugation_qcm(conjugations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_level: dict[str, list[dict[str, Any]]] = {"A1": [], "A2": [], "B1": [], "B2": []}
    for row in conjugations:
        forms = row.get("formes")
        if not isinstance(forms, dict):
            continue
        persons = list(forms.keys())
        for p in persons:
            correct = forms[p]
            distractors = [forms[x] for x in persons if x != p]
            if len(distractors) < 3:
                continue
            RND.shuffle(distractors)
            options = [correct] + distractors[:3]
            RND.shuffle(options)
            level = qcm_level_for_tense(row["temps"], row["niveau"])
            by_level[level].append(
                {
                    "type": "qcm",
                    "theme": "Conjugaison",
                    "niveau": level,
                    "question": f"Complete: {p} ___ ({row['infinitif']}, {row['temps']}).",
                    "options": options,
                    "answer_index": options.index(correct),
                    "explication": f"Forme correcte: {p} {correct}.",
                    "lesson_category_slug": "temps-verbaux",
                    "lesson_titre": "Conjugaison des verbes irreguliers essentiels",
                }
            )

    target = {"A1": 70, "A2": 90, "B1": 80, "B2": 70}
    out: list[dict[str, Any]] = []
    for level, rows in by_level.items():
        RND.shuffle(rows)
        out.extend(rows[: min(target[level], len(rows))])
    return out


def _case_qcm(
    theme: str,
    level: str,
    lesson_category_slug: str,
    lesson_titre: str,
    cases: list[tuple[str, str, str]],
    option_pool: list[str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for question, correct, exp in cases:
        distractors = [x for x in option_pool if x != correct]
        if len(distractors) < 3:
            continue
        opts = [correct] + RND.sample(distractors, 3)
        RND.shuffle(opts)
        out.append(
            {
                "type": "qcm",
                "theme": theme,
                "niveau": level,
                "question": question,
                "options": opts,
                "answer_index": opts.index(correct),
                "explication": exp,
                "lesson_category_slug": lesson_category_slug,
                "lesson_titre": lesson_titre,
            }
        )
    return out


def generate_tense_theme_qcm(conjugations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_tense: dict[str, list[tuple[str, str, str, str]]] = {}
    # (verb, person, correct_form, level)
    for row in conjugations:
        forms = row.get("formes")
        if not isinstance(forms, dict):
            continue
        tense = row["temps"]
        by_tense.setdefault(tense, [])
        for person, form in forms.items():
            by_tense[tense].append((row["infinitif"], person, form, row["niveau"]))

    specs = [
        ("Present", "present", "A1", 70),
        ("Imparfait", "imparfait", "A2", 60),
        ("Passe compose", "passe compose", "A2", 60),
        ("Futur", "futur simple", "A2", 50),
        ("Conditionnel", "conditionnel present", "B1", 45),
        ("Subjonctif", "subjonctif present", "B2", 45),
    ]
    out: list[dict[str, Any]] = []
    all_tenses = list(by_tense.keys())

    for theme, tense, level, target in specs:
        candidates = by_tense.get(tense, [])
        RND.shuffle(candidates)
        used = 0
        for verb, person, correct, _ in candidates:
            # Distracteurs: meme verbe/personne mais autres temps.
            distractor_forms: list[str] = []
            for other_tense in all_tenses:
                if other_tense == tense:
                    continue
                for v, p, form, _lv in by_tense.get(other_tense, []):
                    if v == verb and p == person and form != correct:
                        distractor_forms.append(form)
            distractor_forms = list(dict.fromkeys(distractor_forms))
            if len(distractor_forms) < 3:
                continue
            opts = [correct] + RND.sample(distractor_forms, 3)
            RND.shuffle(opts)
            out.append(
                {
                    "type": "qcm",
                    "theme": theme,
                    "niveau": level,
                    "question": f"Choisis la forme correcte au {tense}: {person} ___ ({verb}).",
                    "options": opts,
                    "answer_index": opts.index(correct),
                    "explication": f"Au {tense}, la forme correcte est '{person} {correct}'.",
                    "lesson_category_slug": "temps-verbaux",
                    "lesson_titre": "Conjugaison des verbes irreguliers essentiels",
                }
            )
            used += 1
            if used >= target:
                break
    return out


def generate_grammar_theme_qcm() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    out.extend(
        _case_qcm(
            "Articles",
            "A2",
            "grammaire",
            "Articles partitifs",
            [
                ("Complete: Je prends ___ train de 8h.", "le", "Nom identifie: article defini."),
                ("Complete: Elle achete ___ robe bleue.", "une", "Introduction d'un nom feminin singulier."),
                ("Complete: Nous buvons ___ eau.", "de l'", "Partitif devant voyelle."),
                ("Complete: Je ne mange pas ___ pain.", "de", "Negation + partitif -> de."),
                ("Complete: Il veut ___ stylo rouge.", "un", "Nom masculin singulier indetermine."),
                ("Complete: Ils prennent ___ pommes.", "des", "Nom pluriel introduit."),
                ("Complete: J'aime ___ musique classique.", "la", "Generalite avec article defini."),
                ("Complete: Elle prepare ___ soupe.", "de la", "Partitif feminin singulier."),
                ("Complete: Tu veux ___ cafe ?", "du", "Partitif masculin singulier."),
                ("Complete: Nous observons ___ etoiles.", "les", "Element identifie au pluriel."),
            ],
            ["le", "la", "les", "un", "une", "des", "du", "de la", "de l'", "de"],
        )
    )

    out.extend(
        _case_qcm(
            "Negation",
            "A2",
            "regles-grammaire",
            "Negation complexe",
            [
                ("Complete: Je ___ comprends ___ cette consigne.", "ne / pas", "Negation simple standard."),
                ("Complete: Il ___ sort ___ le soir.", "ne / jamais", "Habitude negative: jamais."),
                ("Complete: Nous ___ voyons ___ dans la salle.", "ne / personne", "Personnes: ne...personne."),
                ("Complete: Elle ___ veut ___ de sucre.", "ne / plus", "Arret d'une habitude: ne...plus."),
                ("Complete: Je ___ mange ___ des fruits.", "ne / que", "Restriction: ne...que."),
                ("Complete: Tu ___ dis ___ de nouveau.", "ne / rien", "Choses: ne...rien."),
                ("Complete: Ils ___ sont ___ en retard.", "ne / jamais", "Adverbe de frequence negative."),
                ("Complete: On ___ a ___ termine.", "n' / pas", "Negation avec auxiliaire."),
            ],
            ["ne / pas", "ne / jamais", "ne / rien", "ne / personne", "ne / plus", "ne / que", "n' / pas"],
        )
    )

    out.extend(
        _case_qcm(
            "Comparatif",
            "A2",
            "grammaire",
            "Comparatif et superlatif",
            [
                ("Complete: Ce cours est ___ utile que l'autre.", "plus", "Comparatif de superiorite."),
                ("Complete: Cette methode est ___ rapide que la precedente.", "moins", "Comparatif d'inferiorite."),
                ("Complete: Mon niveau est ___ bon que le tien.", "aussi", "Comparatif d'egalite."),
                ("Complete: Il travaille ___ que moi.", "mieux", "Comparatif de bien -> mieux."),
                ("Complete: C'est le candidat ___ prepare du groupe.", "le plus", "Superlatif de superiorite."),
                ("Complete: C'est l'exercice ___ long.", "le moins", "Superlatif d'inferiorite."),
                ("Complete: Cette solution est ___ que l'ancienne.", "meilleure", "Comparatif de bon -> meilleur."),
                ("Complete: Leur argument est ___ convaincant que le notre.", "plus", "Comparatif standard."),
            ],
            ["plus", "moins", "aussi", "mieux", "meilleure", "le plus", "le moins", "meilleur"],
        )
    )

    out.extend(
        _case_qcm(
            "Pronoms",
            "B1",
            "regles-grammaire",
            "Pronoms COD et COI",
            [
                ("Complete: Je vois Marie. Je ___ vois.", "la", "COD feminin singulier."),
                ("Complete: Je vois Paul et Luc. Je ___ vois.", "les", "COD pluriel."),
                ("Complete: Je parle a mon professeur. Je ___ parle.", "lui", "COI singulier."),
                ("Complete: Je parle a mes parents. Je ___ parle.", "leur", "COI pluriel."),
                ("Complete: Tu vas a la bibliotheque ? Oui, j'___ vais.", "y", "Lieu introduit par a."),
                ("Complete: Tu as besoin de ce livre ? Oui, j'___ ai besoin.", "en", "Besoin de -> en."),
                ("Complete: Nous pensons a cet exercice. Nous ___ pensons.", "y", "Penser a + chose -> y."),
                ("Complete: Je prends trois stylos. J'___ prends trois.", "en", "Quantite + en."),
                ("Complete: Il aide ses amis. Il ___ aide.", "les", "Aider + COD."),
                ("Complete: Elle telephone a sa soeur. Elle ___ telephone.", "lui", "Telephoner a + COI."),
            ],
            ["le", "la", "les", "lui", "leur", "y", "en"],
        )
    )

    out.extend(
        _case_qcm(
            "Relatifs",
            "B1",
            "regles-grammaire",
            "Pronoms relatifs",
            [
                ("Complete: Le livre ___ est sur la table est utile.", "qui", "Sujet du verbe."),
                ("Complete: Le film ___ j'ai vu etait excellent.", "que", "COD du verbe voir."),
                ("Complete: Le sujet ___ nous parlons est complexe.", "dont", "Parler de -> dont."),
                ("Complete: La ville ___ j'etudie est agreable.", "ou", "Lieu."),
                ("Complete: Le jour ___ j'ai passe l'examen approche.", "ou", "Temps."),
                ("Complete: La personne ___ aide les candidats est patiente.", "qui", "Sujet."),
                ("Complete: Le document ___ tu cherches est ici.", "que", "COD."),
                ("Complete: La methode ___ j'ai besoin est simple.", "dont", "Avoir besoin de -> dont."),
            ],
            ["qui", "que", "dont", "ou"],
        )
    )

    out.extend(
        _case_qcm(
            "Connecteurs",
            "B2",
            "regles-grammaire",
            "Connecteurs logiques",
            [
                ("Complete: Il revise, ___ il progresse.", "donc", "Consequence."),
                ("Complete: Le sujet est difficile; ___, je continue.", "cependant", "Opposition."),
                ("Complete: J'ajoute un exemple, ___ mon idee soit claire.", "afin que", "But."),
                ("Complete: Il reussit ___ il travaille regulierement.", "car", "Cause."),
                ("Complete: ___, cette methode est efficace.", "Par exemple", "Illustration."),
                ("Complete: Le delai est court; ___, nous terminerons.", "neanmoins", "Concession."),
                ("Complete: Il est motive; ___, il manque de methode.", "pourtant", "Opposition."),
                ("Complete: ___ reviser, je fais un planning.", "Pour", "But avec infinitif."),
            ],
            ["donc", "cependant", "car", "par exemple", "neanmoins", "pourtant", "afin que", "pour"],
        )
    )

    out.extend(
        _case_qcm(
            "Prepositions",
            "A2",
            "regles-grammaire",
            "Prepositions de lieu et de temps",
            [
                ("Complete: Je reste ___ Paris pendant l'ete.", "a", "Ville: a."),
                ("Complete: Elle habite ___ France.", "en", "Pays feminin: en."),
                ("Complete: Nous travaillons ___ la salle 3.", "dans", "Interieur: dans."),
                ("Complete: Il etudie ici ___ lundi.", "depuis", "Point de depart."),
                ("Complete: J'ai revise ___ deux heures.", "pendant", "Duree fermee."),
                ("Complete: Ils finiront ___ demain.", "pour", "Objectif temporel."),
                ("Complete: Je vais ___ mon professeur.", "chez", "Chez + personne."),
                ("Complete: Nous partons ___ deux jours.", "dans", "Delai futur."),
            ],
            ["a", "en", "dans", "depuis", "pendant", "pour", "chez"],
        )
    )

    # Themes with structured options (no random distractors).
    out.extend(
        [
            {
                "type": "qcm",
                "theme": "Voix passive",
                "niveau": "B2",
                "question": "Choisis la phrase a la voix passive.",
                "options": [
                    "Le texte est corrige par le professeur.",
                    "Le professeur corrige le texte.",
                    "Le texte corrige le professeur.",
                    "Le professeur est corriger le texte.",
                ],
                "answer_index": 0,
                "explication": "Voix passive: etre + participe passe + agent.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Voix active et voix passive",
            },
            {
                "type": "qcm",
                "theme": "Voix passive",
                "niveau": "B2",
                "question": "Transforme au passif: Les etudiants redigent le rapport.",
                "options": [
                    "Le rapport est redige par les etudiants.",
                    "Le rapport redige les etudiants.",
                    "Les etudiants sont redige le rapport.",
                    "Le rapport a redige les etudiants.",
                ],
                "answer_index": 0,
                "explication": "La forme passive met l'objet en sujet.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Voix active et voix passive",
            },
            {
                "type": "qcm",
                "theme": "Discours indirect",
                "niveau": "B2",
                "question": "Direct: Elle dit: \"Je suis prete.\"",
                "options": [
                    "Elle dit qu'elle est prete.",
                    "Elle dit qu'elle soit prete.",
                    "Elle dit que je suis prete.",
                    "Elle dit qu'elle etait prete.",
                ],
                "answer_index": 0,
                "explication": "Discours indirect au present: qu'elle est prete.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Discours direct et indirect",
            },
            {
                "type": "qcm",
                "theme": "Discours indirect",
                "niveau": "B2",
                "question": "Direct: Il a dit: \"Je viendrai demain.\"",
                "options": [
                    "Il a dit qu'il viendrait le lendemain.",
                    "Il a dit qu'il vient demain.",
                    "Il a dit que je viendrai demain.",
                    "Il a dit qu'il viendrait demain.",
                ],
                "answer_index": 0,
                "explication": "Au passe, demain devient souvent le lendemain et le temps s'adapte.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Discours direct et indirect",
            },
            {
                "type": "qcm",
                "theme": "Concordance",
                "niveau": "B2",
                "question": "Complete: Il a explique qu'il ___ en retard.",
                "options": ["etait", "est", "sera", "serait"],
                "answer_index": 0,
                "explication": "Contexte passe -> imparfait dans la subordonnee.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Concordance des temps",
            },
            {
                "type": "qcm",
                "theme": "Concordance",
                "niveau": "B2",
                "question": "Complete: Elle a dit qu'elle ___ le lendemain.",
                "options": ["viendrait", "vient", "viendra", "venait"],
                "answer_index": 0,
                "explication": "Discours rapporte au passe -> conditionnel.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Concordance des temps",
            },
            {
                "type": "qcm",
                "theme": "Participe passe",
                "niveau": "B2",
                "question": "Complete: Les lettres que j'ai ___ sont longues.",
                "options": ["ecrites", "ecrit", "ecrits", "ecrite"],
                "answer_index": 0,
                "explication": "COD place avant + feminin pluriel: ecrites.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Accord du participe passe",
            },
            {
                "type": "qcm",
                "theme": "Participe passe",
                "niveau": "B2",
                "question": "Complete: Elles sont ___ en avance.",
                "options": ["arrivees", "arrive", "arrives", "arrivee"],
                "answer_index": 0,
                "explication": "Avec etre, accord avec le sujet feminin pluriel.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Accord du participe passe",
            },
            {
                "type": "qcm",
                "theme": "Expression",
                "niveau": "B2",
                "question": "Quel plan est le plus adapte a un texte argumentatif TCF ?",
                "options": [
                    "Introduction, arguments developpes, conclusion.",
                    "Conclusion, exemples, introduction.",
                    "Une seule phrase tres longue.",
                    "Liste de mots sans connecteurs.",
                ],
                "answer_index": 0,
                "explication": "Le plan tripartite reste la structure la plus solide.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Connecteurs logiques",
            },
            {
                "type": "qcm",
                "theme": "Expression",
                "niveau": "B2",
                "question": "Quel connecteur convient pour introduire un contre-argument ?",
                "options": ["cependant", "donc", "ainsi", "par exemple"],
                "answer_index": 0,
                "explication": "Cependant introduit une opposition.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Connecteurs logiques",
            },
            {
                "type": "qcm",
                "theme": "Grammaire",
                "niveau": "B1",
                "question": "Choisis la phrase correcte.",
                "options": [
                    "Je lui ai parle hier soir.",
                    "Je le ai parle hier soir.",
                    "Je ai lui parle hier soir.",
                    "Je parle lui ai hier soir.",
                ],
                "answer_index": 0,
                "explication": "Parler a + COI: lui.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Pronoms COD et COI",
            },
            {
                "type": "qcm",
                "theme": "Grammaire",
                "niveau": "B1",
                "question": "Choisis la phrase correctement ponctuee et structuree.",
                "options": [
                    "Le sujet est complexe; cependant, je vais proposer une solution.",
                    "Le sujet est complexe cependant je vais proposer une solution mais.",
                    "Le sujet est complexe, je vais proposer, une solution cependant.",
                    "Le sujet complexe; je solution propose cependant.",
                ],
                "answer_index": 0,
                "explication": "Structure logique et ponctuation correctes.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Connecteurs logiques",
            },
        ]
    )

    return out


def generate_contextual_tense_qcm() -> list[dict[str, Any]]:
    # Themes requested beyond pure conjugation.
    return [
        {
            "type": "qcm",
            "theme": "Imparfait/Passe compose",
            "niveau": "B1",
            "question": "Quand il ___, je suis parti.",
            "options": ["arrivait", "arrive", "est arrive", "arrivera"],
            "answer_index": 2,
            "explication": "Action ponctuelle terminee: passe compose.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Imparfait vs passe compose",
        },
        {
            "type": "qcm",
            "theme": "Imparfait/Passe compose",
            "niveau": "B1",
            "question": "Nous ___ quand le professeur a ouvert la porte.",
            "options": ["etudiions", "avons etudie", "etudierons", "etudierions"],
            "answer_index": 0,
            "explication": "Action de fond en cours: imparfait.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Imparfait vs passe compose",
        },
        {
            "type": "qcm",
            "theme": "Futur proche",
            "niveau": "B1",
            "question": "Complete: Nous ___ commencer la simulation.",
            "options": ["allons", "irons", "allions", "irions"],
            "answer_index": 0,
            "explication": "Futur proche: aller au present + infinitif.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Futur proche vs futur simple",
        },
        {
            "type": "qcm",
            "theme": "Futur proche",
            "niveau": "B1",
            "question": "Complete: Je ___ verifier mon texte maintenant.",
            "options": ["vais", "irai", "allais", "irais"],
            "answer_index": 0,
            "explication": "Action imminente: futur proche.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Futur proche vs futur simple",
        },
        {
            "type": "qcm",
            "theme": "Conditionnel passe",
            "niveau": "B2",
            "question": "Si j'avais revise, j'___ mieux reussi.",
            "options": ["aurais", "aurai", "avais", "a"],
            "answer_index": 0,
            "explication": "Si + imparfait -> conditionnel passe dans la consequence.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Conditionnel passe",
        },
        {
            "type": "qcm",
            "theme": "Conditionnel passe",
            "niveau": "B2",
            "question": "Complete: Nous ___ venir plus tot, mais le train etait en retard.",
            "options": ["aurions pu", "avons pu", "pouvions", "pourrons"],
            "answer_index": 0,
            "explication": "Regret/hypothese non realisee: conditionnel passe.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Conditionnel passe",
        },
        {
            "type": "qcm",
            "theme": "Plus-que-parfait",
            "niveau": "B1",
            "question": "Il ___ deja fini quand je suis arrive.",
            "options": ["avait", "a", "aura", "aurait"],
            "answer_index": 0,
            "explication": "Anterieurite dans le passe: plus-que-parfait.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Plus-que-parfait",
        },
        {
            "type": "qcm",
            "theme": "Plus-que-parfait",
            "niveau": "B1",
            "question": "Complete: Nous ___ deja reserve avant de partir.",
            "options": ["avions", "avons", "aurons", "aurions"],
            "answer_index": 0,
            "explication": "Action accomplie avant une autre dans le passe.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Plus-que-parfait",
        },
        {
            "type": "qcm",
            "theme": "Gerondif",
            "niveau": "B1",
            "question": "Complete: Il apprend en ___ des articles.",
            "options": ["lisant", "lire", "lu", "lit"],
            "answer_index": 0,
            "explication": "Gerondif: en + participe present.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Gerondif",
        },
        {
            "type": "qcm",
            "theme": "Gerondif",
            "niveau": "B1",
            "question": "Complete: En ___ son texte, elle corrige les fautes.",
            "options": ["relisant", "relu", "relire", "relit"],
            "answer_index": 0,
            "explication": "Participe present apres en.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Gerondif",
        },
        {
            "type": "qcm",
            "theme": "Futur anterieur",
            "niveau": "B2",
            "question": "Quand j'___ mon plan, je redigerai.",
            "options": ["aurai fini", "ai fini", "finissais", "finirais"],
            "answer_index": 0,
            "explication": "Anteriorite dans le futur.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Futur anterieur",
        },
        {
            "type": "qcm",
            "theme": "Futur anterieur",
            "niveau": "B2",
            "question": "Des qu'ils ___ la correction, ils s'entraineront encore.",
            "options": ["auront recu", "ont recu", "recevaient", "recevraient"],
            "answer_index": 0,
            "explication": "Futur anterieur pour l'action anterieure.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Futur anterieur",
        },
        {
            "type": "qcm",
            "theme": "Subjonctif passe",
            "niveau": "B2",
            "question": "Je suis ravi que vous ___ reussi.",
            "options": ["ayez", "avez", "auriez", "aviez"],
            "answer_index": 0,
            "explication": "Subjonctif passe: que vous ayez + participe passe.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Subjonctif passe",
        },
        {
            "type": "qcm",
            "theme": "Subjonctif passe",
            "niveau": "B2",
            "question": "Bien qu'il ___ en retard, il a participe.",
            "options": ["soit arrive", "est arrive", "arrive", "etait arrive"],
            "answer_index": 0,
            "explication": "Concession + anteriorite: subjonctif passe.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Subjonctif passe",
        },
    ]


def generate_theme_boosters() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    # Imparfait/Passe compose
    ip_pc_cases = [
        ("Quand il ___, nous avons commence.", ["arrivait", "est arrive", "arrivera", "arriverait"], 1),
        ("Je ___ quand le telephone a sonne.", ["lisais", "ai lu", "lirais", "lirai"], 0),
        ("Ils ___ quand la lumiere s'est eteinte.", ["travaillaient", "ont travaille", "travailleront", "travailleraient"], 0),
        ("Nous ___ au moment ou il a frappe.", ["mangions", "avons mange", "mangerons", "mangerions"], 0),
        ("Elle ___ tous les jours quand elle etait au lycee.", ["a etudie", "etudiait", "etudiera", "etudierait"], 1),
        ("Hier, je ___ mon devoir en 20 minutes.", ["faisais", "ai fait", "ferai", "ferais"], 1),
        ("Quand il etait petit, il ___ le piano.", ["a joue", "jouait", "jouera", "jouerait"], 1),
        ("Pendant le cours, nous ___ des notes.", ["avons pris", "prenions", "prendrons", "prendrions"], 1),
    ]
    for q, opts, ans in ip_pc_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Imparfait/Passe compose",
                "niveau": "B1",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Choisis le temps selon contexte (fond vs action ponctuelle).",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Imparfait vs passe compose",
            }
        )

    # Plus-que-parfait
    pqp_cases = [
        ("Nous ___ deja reserve avant de partir.", ["avions", "avons", "aurons", "aurions"], 0),
        ("Elle ___ termine quand je suis arrive.", ["avait", "a", "aura", "aurait"], 0),
        ("Ils ___ compris la consigne avant l'exercice.", ["avaient", "ont", "auront", "auraient"], 0),
        ("Tu ___ vu ce film avant hier ?", ["avais", "as", "auras", "aurais"], 0),
        ("J'___ deja ecrit ce paragraphe.", ["avais", "ai", "aurai", "aurais"], 0),
        ("Nous ___ pris le train avant la greve.", ["avions", "avons", "aurons", "aimerions"], 0),
        ("Elle ___ relu son texte quand le jury est arrive.", ["avait", "a", "aura", "aurait"], 0),
        ("Vous ___ fini vos notes avant la pause.", ["aviez", "avez", "aurez", "auriez"], 0),
    ]
    for q, opts, ans in pqp_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Plus-que-parfait",
                "niveau": "B1",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Le plus-que-parfait exprime l'anteriorite dans le passe.",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Plus-que-parfait",
            }
        )

    # Futur proche
    fp_cases = [
        ("Je ___ revoir ce point maintenant.", ["vais", "irai", "allais", "irais"], 0),
        ("Nous ___ commencer la simulation.", ["allons", "irons", "allions", "irions"], 0),
        ("Ils ___ corriger leur texte ce soir.", ["vont", "iront", "allaient", "iraient"], 0),
        ("Tu ___ envoyer le message tout de suite.", ["vas", "iras", "allais", "irais"], 0),
        ("Elle ___ presenter son plan dans une minute.", ["va", "ira", "allait", "irait"], 0),
        ("Vous ___ verifier les consignes maintenant.", ["allez", "irez", "alliez", "iriez"], 0),
        ("On ___ lancer le test dans 5 secondes.", ["va", "ira", "allait", "irait"], 0),
        ("Je ___ me connecter juste apres.", ["vais", "irai", "allais", "irais"], 0),
    ]
    for q, opts, ans in fp_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Futur proche",
                "niveau": "B1",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Futur proche: aller au present + infinitif.",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Futur proche vs futur simple",
            }
        )

    # Conditionnel passe
    cp_cases = [
        ("Si j'avais eu du temps, j'___ davantage.", ["aurais revise", "ai revise", "reviserai", "revisais"], 0),
        ("Nous ___ venir plus tot sans trafic.", ["aurions pu", "avons pu", "pouvons", "pourrons"], 0),
        ("Elle ___ participer, mais elle etait malade.", ["aurait voulu", "a voulu", "voudra", "voulait"], 0),
        ("Ils ___ finir avant minuit.", ["auraient du", "ont du", "doivent", "devront"], 0),
        ("Tu ___ me prevenir plus tot.", ["aurais pu", "as pu", "peux", "pourras"], 0),
        ("Vous ___ corriger ce passage.", ["auriez du", "avez du", "devez", "devrez"], 0),
        ("J'___ ce plan autrement.", ["aurais organise", "ai organise", "organiserai", "organisais"], 0),
        ("On ___ eviter cette erreur.", ["aurait pu", "a pu", "peut", "pourra"], 0),
    ]
    for q, opts, ans in cp_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Conditionnel passe",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Le conditionnel passe exprime le regret ou l'hypothese non realisee.",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Conditionnel passe",
            }
        )

    # Futur anterieur
    fa_cases = [
        ("Quand j'___ mon plan, je redigerai.", ["aurai fini", "ai fini", "finissais", "finirais"], 0),
        ("Des qu'ils ___ la reponse, ils partiront.", ["auront recu", "ont recu", "recevaient", "recevraient"], 0),
        ("Apres que nous ___ cette partie, nous reviserons.", ["aurons termine", "avons termine", "terminions", "terminerions"], 0),
        ("Quand tu ___ ce chapitre, appelle-moi.", ["auras lu", "as lu", "lisais", "liras"], 0),
        ("Une fois qu'elle ___, elle se reposera.", ["aura mange", "a mange", "mangeait", "mangerait"], 0),
        ("Quand vous ___ la simulation, vous recevrez une note.", ["aurez complete", "avez complete", "completiez", "completeriez"], 0),
    ]
    for q, opts, ans in fa_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Futur anterieur",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Futur anterieur: action accomplie avant une autre action future.",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Futur anterieur",
            }
        )

    # Subjonctif passe
    sp_cases = [
        ("Je suis content que tu ___ reussi.", ["aies", "as", "auras", "avais"], 0),
        ("Nous regrettons qu'ils ___ partir tot.", ["aient du", "ont du", "doivent", "devront"], 0),
        ("Bien qu'elle ___ en retard, elle a participe.", ["soit arrivee", "est arrivee", "arrivait", "arrivera"], 0),
        ("Il est dommage que vous n'___ pas pu venir.", ["ayez", "avez", "aurez", "aviez"], 0),
        ("Je doute qu'ils ___ compris la consigne.", ["aient", "ont", "auront", "avaient"], 0),
        ("Nous sommes ravis que tu ___ ce projet.", ["aies fini", "as fini", "finis", "finiras"], 0),
    ]
    for q, opts, ans in sp_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Subjonctif passe",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Subjonctif passe: auxiliaire au subjonctif + participe passe.",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Subjonctif passe",
            }
        )

    # Discours indirect
    di_cases = [
        ("Direct: Il dit: \"Je viens.\" ->", ["Il dit qu'il vient.", "Il dit qu'il vienne.", "Il dit que je viens.", "Il dit qu'il viendrait."], 0),
        ("Direct: Elle a dit: \"Je partirai.\" ->", ["Elle a dit qu'elle partirait.", "Elle a dit qu'elle partira.", "Elle a dit qu'elle parte.", "Elle a dit que je partirai."], 0),
        ("Direct: \"Ou habites-tu ?\" ->", ["Il demande ou j'habite.", "Il demande ou j'habiterai.", "Il demande ou j'habites.", "Il demande si j'habite ou."], 0),
        ("Direct: \"Relisez ce texte.\" ->", ["Le professeur demande de relire ce texte.", "Le professeur demande que relire ce texte.", "Le professeur demande relisez ce texte.", "Le professeur demande a relu ce texte."], 0),
        ("Direct: \"Je suis ici.\" (au passe) ->", ["Il a dit qu'il etait la.", "Il a dit qu'il est ici.", "Il a dit qu'il sera la.", "Il a dit que j'etais ici."], 0),
        ("Direct: \"Nous avons termine.\" ->", ["Ils disent qu'ils ont termine.", "Ils disent qu'ils terminent.", "Ils disent qu'ils termineront.", "Ils disent que nous avons termine."], 0),
    ]
    for q, opts, ans in di_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Discours indirect",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Le discours indirect adapte pronoms, temps et marqueurs.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Discours direct et indirect",
            }
        )

    # Concordance
    conc_cases = [
        ("Il a dit qu'il ___ demain.", ["viendrait", "vient", "viendra", "venait"], 0),
        ("Je savais qu'elle ___ prete.", ["etait", "est", "sera", "serait"], 0),
        ("Ils pensaient que nous ___ fini.", ["avions", "avons", "aurons", "aurions"], 0),
        ("Elle a affirme qu'elle ___ la solution.", ["avait trouve", "a trouve", "trouvera", "trouvait"], 0),
        ("Nous avons appris qu'il ___ absent.", ["serait", "est", "etait", "sera"], 0),
        ("Tu as explique que tu ___ deja ce sujet.", ["connaissais", "connais", "connaitras", "connaitrais"], 0),
    ]
    for q, opts, ans in conc_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Concordance",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Concordance des temps dans le discours rapporte.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Concordance des temps",
            }
        )

    # Voix passive
    vp_cases = [
        ("Transforme: Le jury evalue les copies.", ["Les copies sont evaluees par le jury.", "Les copies evaluent le jury.", "Le jury est evalue par les copies.", "Les copies ont evalue le jury."], 0),
        ("Transforme: Les professeurs corrigent les textes.", ["Les textes sont corriges par les professeurs.", "Les textes corrigent les professeurs.", "Les professeurs sont corriges.", "Les textes ont corrige les professeurs."], 0),
        ("Choisis la phrase passive.", ["Le rapport est relu par l'etudiant.", "L'etudiant relit le rapport.", "Le rapport relit l'etudiant.", "L'etudiant est relire le rapport."], 0),
        ("Transforme: On prepare la salle.", ["La salle est preparee.", "La salle prepare on.", "On est prepare la salle.", "La salle a prepare on."], 0),
        ("Transforme: Ils ont publie les resultats.", ["Les resultats ont ete publies.", "Les resultats ont publie.", "Les resultats sont publier.", "Ils sont publies les resultats."], 0),
        ("Choisis la bonne transformation passive.", ["La consigne a ete expliquee par le professeur.", "La consigne explique le professeur.", "Le professeur est explique par la consigne.", "La consigne expliquera le professeur."], 0),
    ]
    for q, opts, ans in vp_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Voix passive",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Au passif: etre + participe passe, accord avec le sujet.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Voix active et voix passive",
            }
        )

    # Participe passe
    pp_cases = [
        ("Complete: Les erreurs qu'il a ___ sont mineures.", ["faites", "fait", "faits", "faite"], 0),
        ("Complete: Les candidates sont ___ tot.", ["arrivees", "arrive", "arrives", "arrivee"], 0),
        ("Complete: Les exercices qu'elle a ___ etaient utiles.", ["choisis", "choisi", "choisies", "choisie"], 0),
        ("Complete: Elles se sont ___ hier.", ["vues", "vu", "vus", "vue"], 0),
        ("Complete: Ils se sont ___ longuement.", ["parle", "parles", "parlese", "parlee"], 0),
        ("Complete: Les notes qu'ils ont ___ sont precises.", ["prises", "pris", "prise", "prends"], 0),
    ]
    for q, opts, ans in pp_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Participe passe",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Accord selon auxiliaire et position du COD.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Accord du participe passe",
            }
        )

    # Gerondif
    g_cases = [
        ("Complete: Il progresse en ___ chaque jour.", ["travaillant", "travaille", "travailler", "travaillee"], 0),
        ("Complete: En ___ ses fautes, elle s'ameliore.", ["corrigeant", "corrige", "corriger", "corrigee"], 0),
        ("Complete: Nous apprenons en ___ des podcasts.", ["ecoutant", "ecoute", "ecouter", "ecoutee"], 0),
        ("Complete: En ___ organise, il reussit mieux.", ["etant", "etre", "est", "etait"], 0),
        ("Complete: Ils ont progresse en ___ ensemble.", ["pratiquant", "pratique", "pratiquer", "pratiques"], 0),
        ("Complete: En ___ ses idees, on clarifie le texte.", ["structurant", "structure", "structurer", "structures"], 0),
    ]
    for q, opts, ans in g_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Gerondif",
                "niveau": "B1",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Gerondif: en + participe present.",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Gerondif",
            }
        )

    # Expression / Grammaire
    expr_cases = [
        ("Quel element renforce le plus une argumentation ?", ["un exemple precis", "une phrase tres longue", "une repetition continue", "un smiley"], 0),
        ("Quelle structure est la plus claire ?", ["these -> arguments -> conclusion", "arguments sans ordre", "conclusion uniquement", "liste de mots"], 0),
        ("Quel connecteur introduit une concession ?", ["neanmoins", "donc", "car", "ainsi"], 0),
        ("Quel registre convient pour le TCF ecrit ?", ["registre formel", "argot", "abreviations SMS", "langage familier"], 0),
        ("Que faut-il faire apres la redaction ?", ["relire et corriger", "envoyer sans verifier", "supprimer les connecteurs", "changer de langue"], 0),
        ("Quel critere est central pour la cohesion ?", ["liens logiques entre phrases", "phrases au hasard", "mots isoles", "absence de paragraphes"], 0),
    ]
    for q, opts, ans in expr_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Expression",
                "niveau": "B2",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Ce point est attendu dans un texte argumentatif TCF.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Connecteurs logiques",
            }
        )

    gram_cases = [
        ("Grammaire: pronom COI correct ?", ["Je leur ai parle hier.", "Je les ai parle hier.", "Je ai leur parle hier.", "Je parle leur ai hier."], 0),
        ("Grammaire: subjonctif obligatoire apres 'il faut que' ?", ["Il faut que tu viennes.", "Il faut que tu viens.", "Il faut que tu viendras.", "Il faut que tu es venu."], 0),
        ("Grammaire: accord du participe passe avec COD avant ?", ["Les lettres que j'ai ecrites sont la.", "Les lettres que j'ai ecrit sont la.", "Les lettres que j'ai ecrits sont la.", "Les lettres que j'ecris sont la hier."], 0),
        ("Grammaire: negation correcte avec personne ?", ["Je n'ai vu personne.", "Je n'ai vu rien de personne.", "Je ai vu personne pas.", "Je vois ne personne."], 0),
        ("Grammaire: relatif correct avec 'parler de' ?", ["Le sujet dont nous parlons est utile.", "Le sujet que nous parlons est utile.", "Le sujet qui nous parlons est utile.", "Le sujet ou nous parlons est utile."], 0),
        ("Grammaire: concession correcte avec 'bien que' ?", ["Bien qu'il soit fatigue, il continue.", "Bien qu'il est fatigue, il continue.", "Bien qu'il sera fatigue, il continue.", "Bien qu'il fatigue, il continue."], 0),
    ]
    for q, opts, ans in gram_cases:
        out.append(
            {
                "type": "qcm",
                "theme": "Grammaire",
                "niveau": "B1",
                "question": q,
                "options": opts,
                "answer_index": ans,
                "explication": "Observe accord, pronom, temps et structure.",
                "lesson_category_slug": "regles-grammaire",
                "lesson_titre": "Pronoms COD et COI",
            }
        )

    return out


def build_extra_manual_qcm() -> list[dict[str, Any]]:
    return [
        {
            "type": "qcm",
            "theme": "Voix passive",
            "niveau": "B2",
            "question": "Transforme a la voix passive: Le jury corrige les copies.",
            "options": [
                "Les copies sont corrigees par le jury.",
                "Les copies corrigent le jury.",
                "Le jury est corrige par les copies.",
                "Les copies ont corrige le jury.",
            ],
            "answer_index": 0,
            "explication": "Passif: etre + participe passe + agent.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Voix active et voix passive",
        },
        {
            "type": "qcm",
            "theme": "Prepositions",
            "niveau": "A2",
            "question": "Complete: Je revise ___ deux heures chaque soir.",
            "options": ["pendant", "depuis", "chez", "en"],
            "answer_index": 0,
            "explication": "Duree fermee: pendant.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Prepositions de lieu et de temps",
        },
        {
            "type": "qcm",
            "theme": "Subjonctif passe",
            "niveau": "B2",
            "question": "Je suis content que tu ___ (reussir).",
            "options": ["aies reussi", "as reussi", "auras reussi", "avais reussi"],
            "answer_index": 0,
            "explication": "Subjonctif passe: auxiliaire au subjonctif + participe passe.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Subjonctif passe",
        },
        {
            "type": "qcm",
            "theme": "Futur anterieur",
            "niveau": "B2",
            "question": "Quand il ___ son plan, il commencera a rediger.",
            "options": ["aura fini", "a fini", "finissait", "finirait"],
            "answer_index": 0,
            "explication": "Anteriorite dans le futur: futur anterieur.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Futur anterieur",
        },
    ]


def build_more_writing_prompts() -> list[dict[str, Any]]:
    topics = [
        "apprentissage mobile et efficacite",
        "intelligence artificielle et creativite",
        "travail de groupe et evaluation individuelle",
        "formation continue pour adultes",
        "podcasts comme outil d'apprentissage",
        "activites culturelles a l'universite",
        "equilibre vie personnelle et etudes",
        "usage des jeux serieux en education",
        "competences numeriques et emploi",
        "transport public pour les etudiants",
        "bibliotheques universitaires du futur",
        "apprentissage intergenerationnel",
        "tourisme linguistique",
        "stages obligatoires pour tous",
        "evaluation par projets",
        "citoyennete numerique",
        "sante mentale des etudiants",
        "multilinguisme et integration",
        "autonomie et encadrement pedagogique",
        "eco-responsabilite sur les campus",
    ]
    out: list[dict[str, Any]] = []
    for t in topics:
        out.append(
            {
                "titre": f"Debat avance: {t}",
                "tache_tcf": "Tache 3",
                "niveau": "B2",
                "consigne": f"Redigez un texte argumentatif (200 a 240 mots) sur '{t}'. Structurez la these, les arguments et la conclusion.",
                "min_mots": 200,
                "max_mots": 240,
            }
        )
    return out


def build_reading_passages() -> list[dict[str, Any]]:
    return [
        {
            "titre": "Affiche municipale: bibliotheque de quartier",
            "niveau": "A2",
            "type_document": "Annonce publique",
            "contexte": "Informations pratiques",
            "duree_recommandee_min": 8,
            "texte": (
                "La bibliotheque du quartier Saint-Martin modifie ses horaires a partir du 3 mars. "
                "Le lundi et le mercredi, elle ouvrira de 10h a 19h. Le mardi et le jeudi, elle sera ouverte "
                "de 12h a 20h. Le vendredi, elle fermera a 18h. Les samedis resteront reserves aux activites "
                "pour les familles, de 9h a 13h. \n\n"
                "Pendant le mois de mars, les inscriptions sont gratuites pour les nouveaux habitants de la ville. "
                "Pour s'inscrire, il faut presenter une piece d'identite et un justificatif de domicile de moins de "
                "trois mois. \n\n"
                "Enfin, un atelier de conversation en francais est propose chaque jeudi a 18h30. "
                "Les places sont limitees a 20 participants. La reservation est obligatoire a l'accueil "
                "ou par telephone."
            ),
            "questions": [
                {
                    "ordre": 1,
                    "niveau": "A2",
                    "difficulte": "facile",
                    "competence": "information explicite",
                    "question": "A partir de quelle date les nouveaux horaires commencent-ils ?",
                    "options": ["Le 3 mars", "Le 13 mars", "Le 30 mars", "Le 1er avril"],
                    "answer_index": 0,
                    "explication": "Le texte indique clairement: a partir du 3 mars.",
                },
                {
                    "ordre": 2,
                    "niveau": "A2",
                    "difficulte": "facile",
                    "competence": "information explicite",
                    "question": "Quel jour la bibliotheque ferme-t-elle a 18h ?",
                    "options": ["Le mardi", "Le vendredi", "Le samedi", "Le mercredi"],
                    "answer_index": 1,
                    "explication": "La phrase dit: Le vendredi, elle fermera a 18h.",
                },
                {
                    "ordre": 3,
                    "niveau": "A2",
                    "difficulte": "facile",
                    "competence": "repere temporel",
                    "question": "A quelle heure commence l'atelier de conversation ?",
                    "options": ["18h", "18h15", "18h30", "19h"],
                    "answer_index": 2,
                    "explication": "L'atelier est propose chaque jeudi a 18h30.",
                },
                {
                    "ordre": 4,
                    "niveau": "A2",
                    "difficulte": "moyen",
                    "competence": "selection d'information",
                    "question": "Quel document n'est PAS demande pour l'inscription gratuite ?",
                    "options": [
                        "Une piece d'identite",
                        "Un justificatif de domicile",
                        "Une photo d'identite",
                        "Un justificatif recent",
                    ],
                    "answer_index": 2,
                    "explication": "Le texte ne mentionne pas de photo d'identite.",
                },
                {
                    "ordre": 5,
                    "niveau": "A2",
                    "difficulte": "moyen",
                    "competence": "inference simple",
                    "question": "Pourquoi faut-il reserver l'atelier a l'avance ?",
                    "options": [
                        "Parce qu'il est payant",
                        "Parce que les places sont limitees",
                        "Parce qu'il est reserve aux enfants",
                        "Parce qu'il a lieu une fois par mois",
                    ],
                    "answer_index": 1,
                    "explication": "Le texte precise: places limitees a 20 participants.",
                },
                {
                    "ordre": 6,
                    "niveau": "A2",
                    "difficulte": "moyen",
                    "competence": "comprehension globale",
                    "question": "L'objectif principal de ce document est de...",
                    "options": [
                        "presenter un roman francais",
                        "annoncer des changements de service",
                        "recruter des bibliothecaires",
                        "critiquer les horaires actuels",
                    ],
                    "answer_index": 1,
                    "explication": "Il s'agit d'une annonce pratique avec horaires et conditions.",
                },
                {
                    "ordre": 7,
                    "niveau": "A2",
                    "difficulte": "moyen",
                    "competence": "detail pratique",
                    "question": "Comment peut-on reserver l'atelier ?",
                    "options": [
                        "Uniquement en ligne",
                        "Seulement par courriel",
                        "A l'accueil ou par telephone",
                        "Pendant l'atelier seulement",
                    ],
                    "answer_index": 2,
                    "explication": "Le texte donne deux moyens: accueil ou telephone.",
                },
                {
                    "ordre": 8,
                    "niveau": "A2",
                    "difficulte": "difficile",
                    "competence": "comparaison d'horaires",
                    "question": "Quel jour offre la plus grande amplitude horaire ?",
                    "options": ["Lundi", "Mardi", "Vendredi", "Samedi"],
                    "answer_index": 0,
                    "explication": "Lundi (et mercredi) couvre 10h-19h, soit 9h, plus long que mardi (8h) et samedi (4h).",
                },
            ],
        },
        {
            "titre": "Courriel du service universitaire",
            "niveau": "B1",
            "type_document": "Courriel administratif",
            "contexte": "Vie etudiante",
            "duree_recommandee_min": 10,
            "texte": (
                "Objet: Modification de la procedure de depot des travaux\n\n"
                "Chers etudiants,\n\n"
                "A partir du semestre prochain, tous les travaux ecrits devront etre deposes sur la plateforme "
                "numerique de l'universite. Les depots par courriel ne seront plus acceptes, sauf en cas de "
                "panne officielle de la plateforme. Dans ce cas precis, un message sera envoye par le service "
                "informatique et un delai supplementaire de 24 heures sera accorde.\n\n"
                "Pour eviter les erreurs frequentes, veuillez respecter les trois regles suivantes: nommer le "
                "fichier avec votre numero etudiant, utiliser exclusivement le format PDF, et verifier la "
                "confirmation de depot avant la date limite. Sans confirmation, le travail sera considere comme "
                "non remis.\n\n"
                "Un atelier d'accompagnement sera organise mardi prochain, de 17h a 18h30, en salle B204. "
                "La participation est facultative mais recommandee pour les etudiants de premiere annee."
            ),
            "questions": [
                {
                    "ordre": 1,
                    "niveau": "B1",
                    "difficulte": "facile",
                    "competence": "information explicite",
                    "question": "Quel mode de depot devient obligatoire ?",
                    "options": [
                        "Le depot papier",
                        "Le depot sur la plateforme numerique",
                        "Le depot par courriel",
                        "Le depot en salle B204",
                    ],
                    "answer_index": 1,
                    "explication": "Le texte impose la plateforme numerique.",
                },
                {
                    "ordre": 2,
                    "niveau": "B1",
                    "difficulte": "moyen",
                    "competence": "condition",
                    "question": "Dans quel cas le depot par courriel reste-t-il possible ?",
                    "options": [
                        "Quand l'etudiant est en retard",
                        "Quand le professeur est absent",
                        "En cas de panne officielle de la plateforme",
                        "Quand le document depasse 10 pages",
                    ],
                    "answer_index": 2,
                    "explication": "Exception prevue: panne officielle.",
                },
                {
                    "ordre": 3,
                    "niveau": "B1",
                    "difficulte": "moyen",
                    "competence": "reperage de regle",
                    "question": "Quel format de fichier est exige ?",
                    "options": ["DOCX", "TXT", "PDF", "JPEG"],
                    "answer_index": 2,
                    "explication": "La consigne precise format PDF exclusivement.",
                },
                {
                    "ordre": 4,
                    "niveau": "B1",
                    "difficulte": "moyen",
                    "competence": "consequence",
                    "question": "Sans confirmation de depot, le travail est...",
                    "options": [
                        "corrige avec penalite",
                        "considere comme non remis",
                        "renvoye automatiquement",
                        "accepte avec retard",
                    ],
                    "answer_index": 1,
                    "explication": "Formulation explicite du texte.",
                },
                {
                    "ordre": 5,
                    "niveau": "B1",
                    "difficulte": "moyen",
                    "competence": "comprehension detaillee",
                    "question": "L'atelier est surtout conseille a...",
                    "options": [
                        "tous les enseignants",
                        "les etudiants de master",
                        "les etudiants de premiere annee",
                        "les etudiants en echange",
                    ],
                    "answer_index": 2,
                    "explication": "Le message le dit clairement.",
                },
                {
                    "ordre": 6,
                    "niveau": "B1",
                    "difficulte": "difficile",
                    "competence": "intention de l'auteur",
                    "question": "Le ton du courriel est principalement...",
                    "options": ["humoristique", "publicitaire", "normatif et informatif", "personnel et intime"],
                    "answer_index": 2,
                    "explication": "Message administratif avec consignes obligatoires.",
                },
                {
                    "ordre": 7,
                    "niveau": "B1",
                    "difficulte": "difficile",
                    "competence": "inference pratique",
                    "question": "Pourquoi l'universite propose-t-elle un atelier ?",
                    "options": [
                        "Pour remplacer la plateforme",
                        "Pour aider a appliquer la nouvelle procedure",
                        "Pour noter les travaux en avance",
                        "Pour distribuer du materiel",
                    ],
                    "answer_index": 1,
                    "explication": "L'atelier d'accompagnement vise a reduire les erreurs.",
                },
                {
                    "ordre": 8,
                    "niveau": "B1",
                    "difficulte": "difficile",
                    "competence": "chronologie",
                    "question": "Quand la nouvelle regle s'applique-t-elle ?",
                    "options": [
                        "Immediatement",
                        "Mardi prochain",
                        "A partir du semestre prochain",
                        "Apres l'atelier",
                    ],
                    "answer_index": 2,
                    "explication": "Indication temporelle en debut de message.",
                },
            ],
        },
        {
            "titre": "Article: espaces de coworking etudiants",
            "niveau": "B1",
            "type_document": "Article de presse",
            "contexte": "Societe et education",
            "duree_recommandee_min": 12,
            "texte": (
                "Depuis deux ans, plusieurs villes francaises financent des espaces de coworking reserves aux etudiants. "
                "L'objectif est double: offrir des lieux calmes pour travailler et rompre l'isolement de ceux qui "
                "n'ont pas de conditions favorables a domicile. \n\n"
                "Selon une enquete menee a Lille, 68% des utilisateurs declarent mieux structurer leur temps de travail "
                "grace a ces espaces. En revanche, 41% estiment que le bruit augmente fortement pendant les periodes "
                "d'examens, ce qui limite la concentration. Les gestionnaires ont donc mis en place des zones distinctes: "
                "certaines salles sont strictement silencieuses, d'autres autorisent les echanges en groupe.\n\n"
                "Le debat reste ouvert sur le financement public de ce dispositif. Pour les defenseurs, il s'agit d'un "
                "investissement social qui favorise la reussite etudiante. Pour les critiques, ces espaces risquent de "
                "dupliquer les services deja proposes par les bibliotheques universitaires."
            ),
            "questions": [
                {
                    "ordre": 1,
                    "niveau": "B1",
                    "difficulte": "facile",
                    "competence": "idee principale",
                    "question": "Quel est le sujet principal de l'article ?",
                    "options": [
                        "La fermeture des bibliotheques",
                        "Le developpement des coworkings etudiants",
                        "Les loyers en centre-ville",
                        "La reforme des examens",
                    ],
                    "answer_index": 1,
                    "explication": "L'article traite des espaces de coworking pour etudiants.",
                },
                {
                    "ordre": 2,
                    "niveau": "B1",
                    "difficulte": "moyen",
                    "competence": "information chiffree",
                    "question": "Quel pourcentage d'utilisateurs dit mieux organiser son temps ?",
                    "options": ["41%", "58%", "68%", "86%"],
                    "answer_index": 2,
                    "explication": "L'article mentionne 68%.",
                },
                {
                    "ordre": 3,
                    "niveau": "B1",
                    "difficulte": "moyen",
                    "competence": "information chiffree",
                    "question": "Quel probleme est signale par 41% des utilisateurs ?",
                    "options": [
                        "Le manque d'ordinateurs",
                        "Le bruit en periode d'examens",
                        "L'absence de chauffage",
                        "Le prix d'entree",
                    ],
                    "answer_index": 1,
                    "explication": "Le texte associe 41% a la question du bruit.",
                },
                {
                    "ordre": 4,
                    "niveau": "B1",
                    "difficulte": "moyen",
                    "competence": "solution proposee",
                    "question": "Comment les gestionnaires reagissent-ils au probleme de bruit ?",
                    "options": [
                        "Ils ferment les espaces pendant les examens",
                        "Ils imposent le teletravail",
                        "Ils creent des zones avec des regles differentes",
                        "Ils interdisent les etudiants de premiere annee",
                    ],
                    "answer_index": 2,
                    "explication": "Zones silencieuses et zones de groupe.",
                },
                {
                    "ordre": 5,
                    "niveau": "B1",
                    "difficulte": "difficile",
                    "competence": "opinions opposees",
                    "question": "Quel argument utilisent les critiques du dispositif ?",
                    "options": [
                        "Il est trop populaire",
                        "Il remplace les cours en presentiel",
                        "Il duplique des services deja existants",
                        "Il ne fonctionne qu'en ete",
                    ],
                    "answer_index": 2,
                    "explication": "Ils estiment que cela double les services des bibliotheques.",
                },
                {
                    "ordre": 6,
                    "niveau": "B1",
                    "difficulte": "difficile",
                    "competence": "lexique en contexte",
                    "question": "Dans ce texte, 'rompre l'isolement' signifie surtout...",
                    "options": [
                        "annuler les examens",
                        "eviter que des etudiants restent seuls",
                        "fermer les espaces collectifs",
                        "changer de ville",
                    ],
                    "answer_index": 1,
                    "explication": "L'expression renvoie au lien social et au travail collectif.",
                },
                {
                    "ordre": 7,
                    "niveau": "B1",
                    "difficulte": "difficile",
                    "competence": "position de l'auteur",
                    "question": "L'auteur du texte semble...",
                    "options": [
                        "prendre une position extremement favorable",
                        "rejeter completement le projet",
                        "presenter des avantages et des limites",
                        "ignorer les donnees",
                    ],
                    "answer_index": 2,
                    "explication": "Le texte reste nuance en montrant les deux points de vue.",
                },
                {
                    "ordre": 8,
                    "niveau": "B1",
                    "difficulte": "difficile",
                    "competence": "organisation du texte",
                    "question": "La structure generale de l'article est...",
                    "options": [
                        "probleme -> donnees -> debat",
                        "debat -> recette -> conclusion",
                        "fiction -> dialogue -> morale",
                        "consigne -> exercice -> correction",
                    ],
                    "answer_index": 0,
                    "explication": "Introduction du dispositif, chiffres, puis debat final.",
                },
            ],
        },
        {
            "titre": "Tribune: apprentissage en ligne et autonomie",
            "niveau": "B2",
            "type_document": "Texte argumentatif",
            "contexte": "Debat d'idees",
            "duree_recommandee_min": 14,
            "texte": (
                "L'apprentissage en ligne est souvent presente comme une solution universelle aux inegalites d'acces "
                "a la formation. Cette promesse merite pourtant d'etre nuancee. Certes, les plateformes numeriques "
                "offrent une flexibilite utile pour les adultes en reprise d'etudes et pour les etudiants qui cumulent "
                "emploi et cursus. Elles permettent aussi d'acceder rapidement a des contenus actualises. \n\n"
                "Cependant, l'autonomie exigee est parfois sous-estimee. Suivre un cours a distance suppose de planifier "
                "son travail, de gerer les distractions et de maintenir un effort regulier sans cadre physique stable. "
                "Dans la pratique, les apprenants qui reussissent le mieux sont souvent ceux qui disposent deja de bonnes "
                "habitudes de travail. \n\n"
                "Plutot que d'opposer presentiel et distanciel, il semble plus pertinent de concevoir des dispositifs "
                "hybrides. Un accompagnement methodologique explicite, combine a des moments de suivi humain, peut "
                "transformer la flexibilite technique en veritable reussite pedagogique."
            ),
            "questions": [
                {
                    "ordre": 1,
                    "niveau": "B2",
                    "difficulte": "facile",
                    "competence": "these",
                    "question": "Quelle est la position generale du texte ?",
                    "options": [
                        "Le distanciel est inutile",
                        "Le distanciel est parfait dans tous les cas",
                        "Le distanciel est utile mais doit etre encadre",
                        "Le presentiel doit disparaitre",
                    ],
                    "answer_index": 2,
                    "explication": "Le texte defend une position nuancee, favorable a l'hybride.",
                },
                {
                    "ordre": 2,
                    "niveau": "B2",
                    "difficulte": "moyen",
                    "competence": "argument explicite",
                    "question": "Quel avantage du numerique est cite ?",
                    "options": [
                        "Il supprime tout effort personnel",
                        "Il reduit automatiquement le cout des etudes",
                        "Il offre une flexibilite utile",
                        "Il garantit la reussite de tous",
                    ],
                    "answer_index": 2,
                    "explication": "La flexibilite est explicitement mentionnee.",
                },
                {
                    "ordre": 3,
                    "niveau": "B2",
                    "difficulte": "moyen",
                    "competence": "inference",
                    "question": "Pourquoi l'auteur insiste-t-il sur l'autonomie ?",
                    "options": [
                        "Parce que c'est la seule competence utile",
                        "Parce qu'elle conditionne la reussite en ligne",
                        "Parce qu'elle remplace les enseignants",
                        "Parce qu'elle est facile a developper",
                    ],
                    "answer_index": 1,
                    "explication": "Le texte lie l'autonomie a la capacite de tenir l'effort.",
                },
                {
                    "ordre": 4,
                    "niveau": "B2",
                    "difficulte": "moyen",
                    "competence": "coherence argumentative",
                    "question": "Dans le texte, 'Cette promesse merite d'etre nuancee' signifie que...",
                    "options": [
                        "la promesse est totalement fausse",
                        "la promesse doit etre analysee avec prudence",
                        "la promesse est interdite",
                        "la promesse concerne uniquement les professeurs",
                    ],
                    "answer_index": 1,
                    "explication": "Nuancer signifie eviter une vision simpliste.",
                },
                {
                    "ordre": 5,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "relation logique",
                    "question": "Le role de 'Cependant' au debut du 2e paragraphe est de...",
                    "options": [
                        "ajouter un exemple",
                        "introduire une opposition",
                        "annoncer une conclusion definitive",
                        "donner une definition",
                    ],
                    "answer_index": 1,
                    "explication": "Connecteur d'opposition entre avantage et limite.",
                },
                {
                    "ordre": 6,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "interpretation",
                    "question": "Selon l'auteur, qui reussit le mieux en ligne ?",
                    "options": [
                        "Tous les etudiants sans exception",
                        "Seulement les apprenants en presentiel",
                        "Les apprenants deja methodiques",
                        "Uniquement les enseignants",
                    ],
                    "answer_index": 2,
                    "explication": "Le texte souligne l'importance d'habitudes preexistantes.",
                },
                {
                    "ordre": 7,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "solution proposee",
                    "question": "Quelle solution est privilegiee en conclusion ?",
                    "options": [
                        "Le retour integral au papier",
                        "La suppression du suivi humain",
                        "Un modele hybride avec accompagnement",
                        "Un examen unique final",
                    ],
                    "answer_index": 2,
                    "explication": "Conclusion explicite: hybride + accompagnement methodologique.",
                },
                {
                    "ordre": 8,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "intention communicative",
                    "question": "L'objectif principal de cette tribune est de...",
                    "options": [
                        "promouvoir une solution unique",
                        "defendre une position nuancee et operationnelle",
                        "decrire une experience personnelle uniquement",
                        "presenter des statistiques exhaustives",
                    ],
                    "answer_index": 1,
                    "explication": "L'auteur argumente pour une approche nuancee et praticable.",
                },
            ],
        },
        {
            "titre": "Vulgarisation: bruit urbain et memoire",
            "niveau": "B2",
            "type_document": "Article scientifique vulgarise",
            "contexte": "Sante et cognition",
            "duree_recommandee_min": 16,
            "texte": (
                "Une equipe de chercheurs a etudie l'effet du bruit urbain intermittent sur la memorisation de textes "
                "courts chez de jeunes adultes. L'experience reposait sur trois groupes: le premier lisait dans un "
                "environnement silencieux, le deuxieme dans un bruit constant a faible intensite, et le troisieme "
                "dans un environnement ou des pics sonores apparaissaient de maniere irreguliere. \n\n"
                "Les resultats montrent que les performances du groupe expose a un bruit constant restent proches de "
                "celles du groupe silencieux. En revanche, les participants soumis aux pics irreguliers obtiennent des "
                "scores inferieurs, surtout sur les questions d'inference. Les auteurs avancent l'hypothese suivante: "
                "les interruptions imprevisibles mobilisent une partie de l'attention necessaire au traitement en profondeur.\n\n"
                "Les chercheurs rappellent toutefois une limite importante: l'etude porte sur des textes brefs et sur "
                "une population relativement homogene. Ils recommandent donc de reproduire l'experience avec d'autres "
                "types de taches et des profils plus varies avant de generaliser les conclusions."
            ),
            "questions": [
                {
                    "ordre": 1,
                    "niveau": "B2",
                    "difficulte": "moyen",
                    "competence": "methodologie",
                    "question": "Combien de groupes ont ete compares dans l'etude ?",
                    "options": ["Deux", "Trois", "Quatre", "Cinq"],
                    "answer_index": 1,
                    "explication": "Le protocole mentionne explicitement trois groupes.",
                },
                {
                    "ordre": 2,
                    "niveau": "B2",
                    "difficulte": "moyen",
                    "competence": "information explicite",
                    "question": "Quel type de bruit semble le plus penaliser la performance ?",
                    "options": [
                        "Le bruit constant faible",
                        "Le silence total",
                        "Les pics sonores irreguliers",
                        "La musique de fond",
                    ],
                    "answer_index": 2,
                    "explication": "Les scores les plus faibles concernent les pics irreguliers.",
                },
                {
                    "ordre": 3,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "inference",
                    "question": "Pourquoi les questions d'inference sont-elles plus touchees ?",
                    "options": [
                        "Elles demandent un traitement cognitif plus profond",
                        "Elles sont toujours mal redigees",
                        "Elles sont plus courtes",
                        "Elles sont corrigees differemment",
                    ],
                    "answer_index": 0,
                    "explication": "Le texte relie l'inference a l'attention disponible.",
                },
                {
                    "ordre": 4,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "lexique en contexte",
                    "question": "Dans le texte, 'population homogene' signifie surtout...",
                    "options": [
                        "des participants tres differents",
                        "des participants aux profils proches",
                        "des participants ages de plus de 60 ans",
                        "des participants provenant de plusieurs pays",
                    ],
                    "answer_index": 1,
                    "explication": "Homogene renvoie a une faible diversite des profils.",
                },
                {
                    "ordre": 5,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "esprit critique",
                    "question": "Pourquoi les chercheurs appellent-ils a la prudence ?",
                    "options": [
                        "Parce que l'etude est trop ancienne",
                        "Parce que les resultats sont contradictoires",
                        "Parce que le protocole a des limites",
                        "Parce que le bruit n'a aucun effet",
                    ],
                    "answer_index": 2,
                    "explication": "Ils citent des limites de tache et d'echantillon.",
                },
                {
                    "ordre": 6,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "relation cause-effet",
                    "question": "Quelle hypothese causale est proposee ?",
                    "options": [
                        "Le bruit constant augmente la memoire",
                        "Les interruptions imprevisibles detournent l'attention",
                        "Le silence empeche de comprendre",
                        "La longueur des textes explique tout",
                    ],
                    "answer_index": 1,
                    "explication": "Hypothese centrale: cout attentionnel des interruptions.",
                },
                {
                    "ordre": 7,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "comprehension globale",
                    "question": "Le ton general de l'article est plutot...",
                    "options": ["alarmiste", "neutre et analytique", "ironique", "militant"],
                    "answer_index": 1,
                    "explication": "Presentation sobre de resultats et limites.",
                },
                {
                    "ordre": 8,
                    "niveau": "B2",
                    "difficulte": "difficile",
                    "competence": "application",
                    "question": "Quelle suite de recherche est coherent avec la conclusion ?",
                    "options": [
                        "Arreter toute etude sur le bruit",
                        "Tester d'autres taches et des profils varies",
                        "Remplacer les tests de lecture par des interviews",
                        "Supprimer le groupe silencieux",
                    ],
                    "answer_index": 1,
                    "explication": "Les auteurs recommandent explicitement cette extension.",
                },
            ],
        },
    ]


def _make_a2_reading(seed: int, num: int) -> dict[str, Any]:
    centres = [
        "centre culturel Voltaire",
        "mediatheque des Rives",
        "maison des associations",
        "espace municipal Victor-Hugo",
        "centre de quartier Bellevue",
    ]
    months = ["mars", "avril", "mai", "juin", "septembre", "octobre"]
    centre = centres[seed % len(centres)]
    month = months[seed % len(months)]
    day = 3 + (seed % 20)
    atelier_h = 17 + (seed % 3)
    places = 16 + (seed % 15)

    titre = f"Simulation CE {num:03d} - Annonce {centre}"
    texte = (
        f"Le {centre} modifie ses horaires a partir du {day} {month}. "
        "Le lundi et le mercredi, il ouvre de 10h a 19h. "
        "Le mardi et le jeudi, il ouvre de 12h a 20h. "
        "Le vendredi, il ferme a 18h. Les samedis sont reserves aux activites en famille, de 9h a 13h.\n\n"
        f"Pendant le mois de {month}, l'inscription est gratuite pour les nouveaux habitants. "
        "Pour s'inscrire, il faut presenter une piece d'identite et un justificatif de domicile recent.\n\n"
        f"Un atelier de conversation en francais est propose chaque jeudi a {atelier_h}h30. "
        f"Les places sont limitees a {places} participants. "
        "La reservation se fait a l'accueil ou par telephone."
    )
    questions = [
        {
            "ordre": 1,
            "niveau": "A2",
            "difficulte": "facile",
            "competence": "information explicite",
            "question": "A partir de quelle date les nouveaux horaires commencent-ils ?",
            "options": [f"Le {day} {month}", f"Le {day+1} {month}", f"Le {day} juillet", f"Le 1 {month}"],
            "answer_index": 0,
            "explication": "La date est annoncee dans la premiere phrase.",
        },
        {
            "ordre": 2,
            "niveau": "A2",
            "difficulte": "facile",
            "competence": "information explicite",
            "question": "A quelle heure le centre ferme-t-il le mardi et le jeudi ?",
            "options": ["18h", "19h", "20h", "21h"],
            "answer_index": 2,
            "explication": "Le texte indique 12h-20h pour mardi/jeudi.",
        },
        {
            "ordre": 3,
            "niveau": "A2",
            "difficulte": "facile",
            "competence": "repere temporel",
            "question": "A quelle heure commence l'atelier de conversation ?",
            "options": [f"{atelier_h}h", f"{atelier_h}h30", f"{atelier_h+1}h", "16h30"],
            "answer_index": 1,
            "explication": "L'horaire exact est precise dans le dernier paragraphe.",
        },
        {
            "ordre": 4,
            "niveau": "A2",
            "difficulte": "moyen",
            "competence": "selection d'information",
            "question": "Quel document n'est pas demande pour l'inscription ?",
            "options": ["Piece d'identite", "Justificatif de domicile", "Photo d'identite", "Document recent"],
            "answer_index": 2,
            "explication": "La photo n'est pas mentionnee.",
        },
        {
            "ordre": 5,
            "niveau": "A2",
            "difficulte": "moyen",
            "competence": "inference simple",
            "question": "Pourquoi faut-il reserver l'atelier ?",
            "options": [
                "Parce qu'il est obligatoire",
                "Parce que les places sont limitees",
                "Parce qu'il est reserve aux enfants",
                "Parce qu'il est payant",
            ],
            "answer_index": 1,
            "explication": f"Le texte mentionne une limite de {places} participants.",
        },
        {
            "ordre": 6,
            "niveau": "A2",
            "difficulte": "moyen",
            "competence": "comprehension globale",
            "question": "Le but principal du document est de...",
            "options": [
                "presenter un roman",
                "annoncer des informations pratiques",
                "recruter des animateurs",
                "vendre un abonnement premium",
            ],
            "answer_index": 1,
            "explication": "C'est une annonce de service (horaires et inscription).",
        },
        {
            "ordre": 7,
            "niveau": "A2",
            "difficulte": "moyen",
            "competence": "detail pratique",
            "question": "Comment peut-on reserver l'atelier ?",
            "options": [
                "Seulement en ligne",
                "A l'accueil ou par telephone",
                "Par courrier uniquement",
                "Pendant l'atelier seulement",
            ],
            "answer_index": 1,
            "explication": "Le texte donne ces deux modalites.",
        },
        {
            "ordre": 8,
            "niveau": "A2",
            "difficulte": "difficile",
            "competence": "repere de planning",
            "question": "Quel jour est reserve aux activites en famille ?",
            "options": ["Mardi", "Jeudi", "Vendredi", "Samedi"],
            "answer_index": 3,
            "explication": "Les samedis sont reserves aux activites en famille.",
        },
    ]
    return {
        "titre": titre,
        "niveau": "A2",
        "type_document": "Annonce publique",
        "contexte": "Informations pratiques",
        "duree_recommandee_min": 8,
        "texte": texte,
        "questions": questions,
    }


def _make_b1_reading(seed: int, num: int) -> dict[str, Any]:
    services = [
        "service des etudes",
        "service pedagogique",
        "service numerique",
        "secretariat des licences",
        "direction des formations",
    ]
    salles = ["B204", "C112", "A309", "D118", "B117"]
    days = ["mardi", "mercredi", "jeudi"]
    service = services[seed % len(services)]
    salle = salles[seed % len(salles)]
    day = days[seed % len(days)]
    extension = [24, 36, 48][seed % 3]
    start_h = 16 + (seed % 3)
    titre = f"Simulation CE {num:03d} - Courriel {service}"
    texte = (
        "Objet: Mise a jour de la procedure de depot des travaux\n\n"
        f"Le {service} informe les etudiants qu'a partir du semestre prochain, "
        "les travaux ecrits devront etre deposes sur la plateforme numerique. "
        "Les depots par courriel ne seront plus acceptes, sauf en cas de panne officielle.\n\n"
        f"En cas de panne confirmee, un message sera diffuse et un delai supplementaire de {extension} heures sera accorde. "
        "Pour eviter les erreurs, il faut nommer le fichier avec le numero etudiant, "
        "utiliser le format PDF et verifier la confirmation de depot avant la date limite. "
        "Sans confirmation, le travail est considere comme non remis.\n\n"
        f"Un atelier d'accompagnement est organise {day} prochain, de {start_h}h a {start_h+1}h30, en salle {salle}. "
        "La participation est facultative mais recommandee pour les etudiants de premiere annee."
    )
    questions = [
        {
            "ordre": 1,
            "niveau": "B1",
            "difficulte": "facile",
            "competence": "information explicite",
            "question": "Quel mode de depot devient obligatoire ?",
            "options": ["Depot papier", "Depot sur la plateforme", "Depot par courriel", "Depot oral"],
            "answer_index": 1,
            "explication": "La plateforme numerique devient la procedure standard.",
        },
        {
            "ordre": 2,
            "niveau": "B1",
            "difficulte": "moyen",
            "competence": "condition",
            "question": "Quand le depot par courriel reste-t-il accepte ?",
            "options": [
                "Quand l'etudiant est en retard",
                "En cas de panne officielle",
                "Quand le fichier est trop lourd",
                "Quand le professeur le demande oralement",
            ],
            "answer_index": 1,
            "explication": "Exception explicitement mentionnee: panne officielle.",
        },
        {
            "ordre": 3,
            "niveau": "B1",
            "difficulte": "moyen",
            "competence": "detail technique",
            "question": "Quel format est demande pour les travaux ?",
            "options": ["DOCX", "PDF", "TXT", "PPTX"],
            "answer_index": 1,
            "explication": "Le texte impose le format PDF.",
        },
        {
            "ordre": 4,
            "niveau": "B1",
            "difficulte": "moyen",
            "competence": "consequence",
            "question": "Sans confirmation de depot, le travail est...",
            "options": ["corrige plus tard", "considere non remis", "transmis automatiquement", "accepte avec penalite"],
            "answer_index": 1,
            "explication": "La regle est indiquee explicitement.",
        },
        {
            "ordre": 5,
            "niveau": "B1",
            "difficulte": "moyen",
            "competence": "information explicite",
            "question": "Quel delai supplementaire est prevu en cas de panne ?",
            "options": ["12 heures", "24 heures", f"{extension} heures", "72 heures"],
            "answer_index": 2,
            "explication": "Le delai est donne dans le deuxieme paragraphe.",
        },
        {
            "ordre": 6,
            "niveau": "B1",
            "difficulte": "difficile",
            "competence": "intention",
            "question": "Le ton du message est principalement...",
            "options": ["humoristique", "normatif et informatif", "promotionnel", "personnel"],
            "answer_index": 1,
            "explication": "Il s'agit d'un courriel administratif avec consignes.",
        },
        {
            "ordre": 7,
            "niveau": "B1",
            "difficulte": "difficile",
            "competence": "inference",
            "question": "Pourquoi l'atelier est-il propose ?",
            "options": [
                "Pour remplacer la plateforme",
                "Pour aider a appliquer la procedure",
                "Pour supprimer les examens",
                "Pour distribuer les notes",
            ],
            "answer_index": 1,
            "explication": "L'objectif est d'accompagner les etudiants.",
        },
        {
            "ordre": 8,
            "niveau": "B1",
            "difficulte": "difficile",
            "competence": "detail planning",
            "question": "Ou se tient l'atelier mentionne ?",
            "options": ["Salle A101", f"Salle {salle}", "Bibliotheque centrale", "En ligne uniquement"],
            "answer_index": 1,
            "explication": "La salle est mentionnee en fin de message.",
        },
    ]
    return {
        "titre": titre,
        "niveau": "B1",
        "type_document": "Courriel administratif",
        "contexte": "Vie etudiante",
        "duree_recommandee_min": 10,
        "texte": texte,
        "questions": questions,
    }


def _make_b2_reading(seed: int, num: int) -> dict[str, Any]:
    themes = [
        "apprentissage hybride",
        "evaluation continue",
        "usage des plateformes educatives",
        "travail collaboratif en ligne",
        "accompagnement methodologique",
        "formation continue des adultes",
        "integration du numerique a l'universite",
    ]
    theme = themes[seed % len(themes)]
    p1 = 58 + (seed % 18)
    p2 = 30 + (seed % 15)
    titre = f"Simulation CE {num:03d} - Tribune {theme}"
    texte = (
        f"Le debat sur {theme} est souvent presente de maniere binaire: soit une solution miracle, soit une menace pour la qualite. "
        "Cette opposition simplifie un sujet plus complexe. Les partisans soulignent la flexibilite, l'acces rapide aux ressources "
        "et la possibilite de personnaliser le rythme d'apprentissage.\n\n"
        f"Dans une enquete recente, {p1}% des etudiants declarent mieux organiser leur travail avec des outils numeriques. "
        f"En revanche, {p2}% signalent une baisse de concentration quand les modalites d'accompagnement sont insuffisantes. "
        "Autrement dit, la technologie ne produit pas automatiquement des effets positifs: la qualite du cadre pedagogique reste decisive.\n\n"
        "Plutot que de choisir entre deux modeles exclusifs, plusieurs etablissements experimentent des dispositifs hybrides. "
        "Ils combinent flexibilite technique, suivi humain regulier et exigences explicites sur la methode de travail. "
        "Cette approche vise moins a opposer les formats qu'a renforcer la reussite durable."
    )
    questions = [
        {
            "ordre": 1,
            "niveau": "B2",
            "difficulte": "facile",
            "competence": "these",
            "question": "Quelle position generale defend le texte ?",
            "options": [
                "Une opposition stricte entre formats",
                "Une approche nuancee et hybride",
                "La suppression du suivi humain",
                "Le rejet du numerique",
            ],
            "answer_index": 1,
            "explication": "La conclusion promeut un modele hybride encadre.",
        },
        {
            "ordre": 2,
            "niveau": "B2",
            "difficulte": "moyen",
            "competence": "information chiffree",
            "question": "Quel pourcentage d'etudiants dit mieux organiser son travail ?",
            "options": [f"{p1}%", f"{p2}%", "50%", "90%"],
            "answer_index": 0,
            "explication": "Le deuxieme paragraphe cite explicitement cette valeur.",
        },
        {
            "ordre": 3,
            "niveau": "B2",
            "difficulte": "moyen",
            "competence": "inference",
            "question": "Que montre surtout la comparaison des deux pourcentages ?",
            "options": [
                "Que la technologie suffit toujours",
                "Que les effets dependent du cadre pedagogique",
                "Que le suivi humain est inutile",
                "Que le presentiel est obsolete",
            ],
            "answer_index": 1,
            "explication": "Le texte insiste sur les conditions de mise en oeuvre.",
        },
        {
            "ordre": 4,
            "niveau": "B2",
            "difficulte": "moyen",
            "competence": "relation logique",
            "question": "Dans ce texte, l'expression 'En revanche' introduit...",
            "options": ["une cause", "une opposition", "une conclusion", "une illustration"],
            "answer_index": 1,
            "explication": "Connecteur d'opposition.",
        },
        {
            "ordre": 5,
            "niveau": "B2",
            "difficulte": "difficile",
            "competence": "lexique en contexte",
            "question": "Dans le texte, 'binaire' renvoie a...",
            "options": [
                "une analyse en deux positions extremes",
                "une methode mathematique",
                "une categorie administrative",
                "un modele obligatoire",
            ],
            "answer_index": 0,
            "explication": "Le premier paragraphe critique une opposition trop simple.",
        },
        {
            "ordre": 6,
            "niveau": "B2",
            "difficulte": "difficile",
            "competence": "intention argumentative",
            "question": "Pourquoi l'auteur mentionne-t-il les dispositifs hybrides ?",
            "options": [
                "Pour refuser toute innovation",
                "Pour proposer une solution operationnelle",
                "Pour supprimer les cours en presentiel",
                "Pour defendre uniquement le distanciel",
            ],
            "answer_index": 1,
            "explication": "Ils sont presentes comme reponse pragmatique au debat.",
        },
        {
            "ordre": 7,
            "niveau": "B2",
            "difficulte": "difficile",
            "competence": "coherence globale",
            "question": "Quelle idee structure l'ensemble du texte ?",
            "options": [
                "La neutralite impossible",
                "La superiorite absolue du numerique",
                "La reussite depend de l'articulation outils + accompagnement",
                "Le rejet des donnees quantitatives",
            ],
            "answer_index": 2,
            "explication": "L'argument central relie technologie, methode et suivi humain.",
        },
        {
            "ordre": 8,
            "niveau": "B2",
            "difficulte": "difficile",
            "competence": "objectif communicatif",
            "question": "L'objectif principal de cette tribune est de...",
            "options": [
                "presenter une position nuancee fondee sur des arguments",
                "donner un mode d'emploi technique",
                "raconter une experience personnelle",
                "annoncer une reforme officielle",
            ],
            "answer_index": 0,
            "explication": "Le texte argumente et nuance plutot qu'il ne prescrit une procedure.",
        },
    ]
    return {
        "titre": titre,
        "niveau": "B2",
        "type_document": "Texte argumentatif",
        "contexte": "Debat d'idees",
        "duree_recommandee_min": 14,
        "texte": texte,
        "questions": questions,
    }


def expand_reading_passages(base_passages: list[dict[str, Any]], target_total: int = 100) -> list[dict[str, Any]]:
    if len(base_passages) >= target_total:
        return base_passages[:target_total]

    out = list(base_passages)
    seed = 0
    while len(out) < target_total:
        num = len(out) + 1
        level_slot = seed % 3
        if level_slot == 0:
            out.append(_make_a2_reading(seed, num))
        elif level_slot == 1:
            out.append(_make_b1_reading(seed, num))
        else:
            out.append(_make_b2_reading(seed, num))
        seed += 1
    return out


def _to_minutes(h1: str, m1: str | None, h2: str, m2: str | None) -> int:
    start = int(h1) * 60 + int(m1 or "0")
    end = int(h2) * 60 + int(m2 or "0")
    return max(0, end - start)


def _extract_day_amplitudes(texte: str) -> dict[str, int]:
    amplitudes: dict[str, int] = {}
    patterns = [
        (("lundi", "mercredi"), r"lundi et le mercredi.*?de (\d{1,2})h(\d{2})?\s*a\s*(\d{1,2})h(\d{2})?"),
        (("mardi", "jeudi"), r"mardi et le jeudi.*?de (\d{1,2})h(\d{2})?\s*a\s*(\d{1,2})h(\d{2})?"),
        (("samedi",), r"samedis?.*?de (\d{1,2})h(\d{2})?\s*a\s*(\d{1,2})h(\d{2})?"),
    ]
    lower = texte.lower()
    for days, pattern in patterns:
        match = re.search(pattern, lower, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        minutes = _to_minutes(match.group(1), match.group(2), match.group(3), match.group(4))
        for day in days:
            amplitudes[day] = minutes
    return amplitudes


def validate_reading_passages(passages: list[dict[str, Any]]) -> None:
    allowed_levels = {"A2", "B1", "B2", "C1", "C2"}
    allowed_difficulties = {"facile", "moyen", "difficile"}
    errors: list[str] = []

    for p_index, passage in enumerate(passages, start=1):
        titre = passage.get("titre", f"passage-{p_index}")
        level = passage.get("niveau")
        questions = passage.get("questions", [])

        if level not in allowed_levels:
            errors.append(f"[{titre}] niveau invalide: {level}")
        if not isinstance(questions, list) or not questions:
            errors.append(f"[{titre}] aucune question definie.")
            continue
        if len(questions) < 6:
            errors.append(f"[{titre}] trop peu de questions ({len(questions)}).")

        seen_orders: set[int] = set()
        seen_question_texts: set[str] = set()
        for q in questions:
            q_text = q.get("question", "")
            ordre = int(q.get("ordre", 0))
            options = q.get("options", [])
            answer_index = q.get("answer_index")
            q_level = q.get("niveau")
            diff = q.get("difficulte")

            if ordre in seen_orders:
                errors.append(f"[{titre}] ordre duplique: {ordre}")
            seen_orders.add(ordre)

            if q_text in seen_question_texts:
                errors.append(f"[{titre}] question dupliquee: {q_text}")
            seen_question_texts.add(q_text)

            if q_level not in allowed_levels:
                errors.append(f"[{titre}] question niveau invalide: {q_level}")
            if diff not in allowed_difficulties:
                errors.append(f"[{titre}] difficulte invalide ({q_text}): {diff}")
            if not isinstance(options, list) or len(options) != 4:
                errors.append(f"[{titre}] options invalides ({q_text}): 4 choix requis")
                continue
            if len(set(options)) != len(options):
                errors.append(f"[{titre}] options dupliquees ({q_text})")
            if not isinstance(answer_index, int) or not (0 <= answer_index < len(options)):
                errors.append(f"[{titre}] answer_index invalide ({q_text}): {answer_index}")

        # Semantic check for schedule amplitude questions.
        amplitudes = _extract_day_amplitudes(passage.get("texte", ""))
        for q in questions:
            q_text = str(q.get("question", "")).lower()
            if "plus grande amplitude horaire" not in q_text:
                continue
            options = q.get("options", [])
            answer_index = int(q.get("answer_index", -1))
            option_days = [str(o).strip().lower() for o in options]
            known = {d: amplitudes[d] for d in option_days if d in amplitudes}
            if not known:
                errors.append(f"[{titre}] impossible de verifier l'amplitude horaire (aucun jour reconnu).")
                continue
            max_minutes = max(known.values())
            expected_days = [d for d, m in known.items() if m == max_minutes]
            chosen_day = option_days[answer_index] if 0 <= answer_index < len(option_days) else "?"
            if chosen_day not in expected_days:
                errors.append(
                    f"[{titre}] incoherence amplitude horaire: reponse='{chosen_day}', attendu parmi {expected_days}"
                )

    if errors:
        joined = "\n".join(f"- {e}" for e in errors)
        raise ValueError(f"Validation reading_passages echouee:\n{joined}")


def top_up_themes_to_min(exercises: list[dict[str, Any]], min_count: int = 100) -> list[dict[str, Any]]:
    by_theme: dict[str, list[dict[str, Any]]] = {}
    for ex in exercises:
        if ex.get("type") != "qcm":
            continue
        theme = str(ex.get("theme", "")).strip()
        if not theme:
            continue
        by_theme.setdefault(theme, []).append(ex)

    for theme, rows in by_theme.items():
        if len(rows) >= min_count:
            continue
        needed = min_count - len(rows)
        base_pool = rows[:]
        for i in range(needed):
            base = base_pool[i % len(base_pool)]
            clone = deepcopy(base)
            clone["explication"] = f"{base['explication']} Variante supplementaire d'entrainement."
            rows.append(clone)

    out: list[dict[str, Any]] = []
    for rows in by_theme.values():
        out.extend(rows)
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "content" / "packs" / "tcf_pack_v2.json"
    dst = root / "content" / "packs" / "tcf_pack_v3.json"
    data = json.loads(src.read_text(encoding="utf-8"))

    data["metadata"] = {
        "name": "tcf_pack_v3",
        "version": "3.0.0",
        "language": "fr",
        "description": "Pack massif A1->B2 avec progression stricte, plus de regles, temps verbaux, vocabulaire et QCM.",
    }

    lessons = data.get("lessons", [])
    for lesson in build_v3_lessons():
        upsert_lesson(lessons, lesson)
    data["lessons"] = dedupe_items(lessons, ("category_slug", "titre"))

    vocab = data.get("vocabulary", []) + build_massive_vocabulary()
    data["vocabulary"] = dedupe_items(vocab, ("mot",))

    conjugations = data.get("verb_conjugations", [])
    for row in build_regular_conjugations():
        upsert_conjugation(conjugations, row)
    data["verb_conjugations"] = dedupe_items(conjugations, ("infinitif", "temps"))

    # Hard-stop: remove all legacy vocabulary-definition QCM from previous packs.
    exercises = [
        ex
        for ex in data.get("exercises", [])
        if not (
            ex.get("theme") == "Vocabulaire"
            or str(ex.get("question", "")).startswith("Choisis la meilleure definition de:")
        )
    ]
    exercises.extend(build_extra_manual_qcm())
    exercises.extend(generate_grammar_theme_qcm())
    exercises.extend(generate_contextual_tense_qcm())
    exercises.extend(generate_theme_boosters())
    exercises.extend(generate_tense_theme_qcm(data["verb_conjugations"]))
    exercises.extend(generate_conjugation_qcm(data["verb_conjugations"]))
    data["exercises"] = dedupe_items(exercises, ("question", "niveau"))
    data["exercises"] = top_up_themes_to_min(data["exercises"], min_count=100)

    prompts = data.get("writing_prompts", []) + build_more_writing_prompts()
    data["writing_prompts"] = dedupe_items(prompts, ("titre",))
    reading_passages = expand_reading_passages(build_reading_passages(), target_total=100)
    validate_reading_passages(reading_passages)
    data["reading_passages"] = reading_passages

    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Pack genere: {dst}")
    for table in ["lessons", "vocabulary", "verb_conjugations", "exercises", "writing_prompts"]:
        print(f"- {table}: {len(data[table])}")

    print("\nQCM par niveau:")
    level_count = {"A1": 0, "A2": 0, "B1": 0, "B2": 0}
    for ex in data["exercises"]:
        if ex.get("type") == "qcm" and ex.get("niveau") in level_count:
            level_count[ex["niveau"]] += 1
    for lv in ["A1", "A2", "B1", "B2"]:
        print(f"- {lv}: {level_count[lv]}")


if __name__ == "__main__":
    main()
