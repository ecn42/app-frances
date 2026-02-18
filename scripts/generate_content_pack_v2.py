from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


PERSONNES = ["je", "tu", "il/elle", "nous", "vous", "ils/elles"]


def upsert_lesson(lessons: list[dict[str, Any]], lesson: dict[str, Any]) -> None:
    key = (lesson["category_slug"], lesson["titre"])
    for idx, existing in enumerate(lessons):
        if (existing["category_slug"], existing["titre"]) == key:
            lessons[idx] = lesson
            return
    lessons.append(lesson)


def upsert_conjugation(rows: list[dict[str, Any]], row: dict[str, Any]) -> None:
    key = (row["infinitif"], row["temps"])
    for idx, existing in enumerate(rows):
        if (existing["infinitif"], existing["temps"]) == key:
            rows[idx] = row
            return
    rows.append(row)


def generate_conjugation_qcm(rows: list[dict[str, Any]], n: int = 90) -> list[dict[str, Any]]:
    rnd = random.Random(42)
    out: list[dict[str, Any]] = []
    candidates: list[tuple[str, str, str, str, str]] = []

    for row in rows:
        temps = row["temps"]
        if temps not in {"present", "imparfait", "futur simple", "conditionnel present", "subjonctif present"}:
            continue
        formes = row["formes"]
        if not isinstance(formes, dict):
            continue
        for personne, forme in formes.items():
            candidates.append((row["infinitif"], temps, row["niveau"], personne, forme))

    rnd.shuffle(candidates)
    for infinitif, temps, niveau, personne, correcte in candidates[:n]:
        # Distracteurs: autres formes du meme verbe au meme temps
        formes = next(
            r["formes"] for r in rows if r["infinitif"] == infinitif and r["temps"] == temps and isinstance(r["formes"], dict)
        )
        distracteurs = [f for p, f in formes.items() if p != personne]
        rnd.shuffle(distracteurs)
        options = [correcte] + distracteurs[:3]
        rnd.shuffle(options)
        out.append(
            {
                "type": "qcm",
                "theme": "Conjugaison",
                "niveau": niveau,
                "question": f"Complete: {personne} ___ ({infinitif}, {temps}).",
                "options": options,
                "answer_index": options.index(correcte),
                "explication": f"Avec '{personne}', la forme correcte de '{infinitif}' au {temps} est '{correcte}'.",
                "lesson_category_slug": "temps-verbaux",
                "lesson_titre": "Conjugaison des verbes irreguliers essentiels",
            }
        )
    return out


def build_extra_lessons() -> list[dict[str, Any]]:
    return [
        {
            "category_slug": "regles-grammaire",
            "titre": "Accord du participe passe",
            "niveau": "B2",
            "resume": "Regles d'accord avec etre, avoir et verbes pronominaux.",
            "contenu_markdown": (
                "### Regle\n"
                "- Avec **etre**, le participe passe s'accorde avec le sujet.\n"
                "- Avec **avoir**, accord seulement si le COD est place avant.\n"
                "- Avec les verbes pronominaux, l'accord depend de la fonction du pronom.\n\n"
                "### Exemples\n"
                "- Elles sont arrivees tot.\n"
                "- Les lettres que j'ai ecrites sont sur la table.\n"
                "- Ils se sont parle (COI: pas d'accord).\n"
                "- Elles se sont vues (COD: accord).\n\n"
                "### Pieges\n"
                "- Confondre COD et COI avec les pronominaux.\n"
                "- Oublier l'accord en genre/nombre avec etre."
            ),
            "tags": ["participe-passe", "accord", "b2"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Negation complexe",
            "niveau": "B1",
            "resume": "Maitriser ne...jamais, ne...plus, ne...rien, ne...personne, ne...que.",
            "contenu_markdown": (
                "### Structures\n"
                "- ne ... jamais\n"
                "- ne ... plus\n"
                "- ne ... rien\n"
                "- ne ... personne\n"
                "- ne ... que (restriction)\n\n"
                "### Exemples\n"
                "- Je ne sors jamais tard.\n"
                "- Il ne fume plus.\n"
                "- Nous ne comprenons rien.\n"
                "- Je n'ai vu personne.\n"
                "- Elle ne mange que des legumes.\n\n"
                "### Conseil TCF\n"
                "Varie les structures de negation dans tes redactions pour montrer de la precision."
            ),
            "tags": ["negation", "structure"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Discours direct et indirect",
            "niveau": "B2",
            "resume": "Transformer une citation en discours rapporte.",
            "contenu_markdown": (
                "### Regle\n"
                "Au discours indirect, on adapte les pronoms, les marqueurs de temps et parfois les temps verbaux.\n\n"
                "### Exemples\n"
                "- Direct: Il dit: \"Je viens demain.\"  \n"
                "  Indirect: Il dit qu'il vient demain.\n"
                "- Direct: Elle a dit: \"Je partirai.\"  \n"
                "  Indirect: Elle a dit qu'elle partirait.\n"
                "- Direct: \"Je suis ici.\"  \n"
                "  Indirect: Il dit qu'il est la.\n\n"
                "### Points sensibles\n"
                "- demain -> le lendemain\n"
                "- ici -> la\n"
                "- maintenant -> alors"
            ),
            "tags": ["discours-indirect", "concordance"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Futur proche vs futur simple",
            "niveau": "B1",
            "resume": "Choisir entre intention immediate et projection plus neutre.",
            "contenu_markdown": (
                "### Formation\n"
                "- Futur proche: **aller au present + infinitif**.\n"
                "- Futur simple: **radical futur + terminaisons** (ai, as, a, ons, ez, ont).\n\n"
                "### Usage\n"
                "- Futur proche: action imminente ou decidee.\n"
                "- Futur simple: prediction, plan, style plus formel.\n\n"
                "### Exemples\n"
                "- Je vais commencer maintenant.\n"
                "- Je commencerai demain matin.\n"
                "- Nous allons revoir le chapitre 3.\n"
                "- Nous reverrons ce point en classe."
            ),
            "tags": ["futur", "registre"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Conditionnel passe",
            "niveau": "B2",
            "resume": "Exprimer un regret, une hypothese non realisee ou une information non confirmee.",
            "contenu_markdown": (
                "### Formation\n"
                "Auxiliaire au conditionnel present + participe passe.\n\n"
                "### Exemples\n"
                "- J'aurais revise davantage.\n"
                "- Elle serait venue plus tot.\n"
                "- Nous aurions compris avec plus d'exemples.\n\n"
                "### Cas frequents au TCF\n"
                "- Regret: J'aurais du verifier l'orthographe.\n"
                "- Hypothese non realisee: Si j'avais eu plus de temps, j'aurais termine."
            ),
            "tags": ["conditionnel-passe", "hypothese"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Conjugaison des verbes irreguliers essentiels",
            "niveau": "B2",
            "resume": "Memoriser les formes frequentes de etre, avoir, aller, faire, venir, pouvoir, devoir, vouloir.",
            "contenu_markdown": (
                "### Verbes a prioriser\n"
                "- etre, avoir, aller, faire\n"
                "- venir, pouvoir, devoir, vouloir, prendre, savoir\n\n"
                "### Strategie\n"
                "1. Apprendre les formes du present.\n"
                "2. Ajouter imparfait et futur simple.\n"
                "3. Automatiser conditionnel et subjonctif.\n\n"
                "### Exemples\n"
                "- Il faut que je **sois** ponctuel.\n"
                "- Nous **aurons** plus de temps demain.\n"
                "- Je **voudrais** clarifier cette idee.\n"
                "- Bien qu'il **vienne** tard, il participe."
            ),
            "tags": ["irreguliers", "conjugaison"],
        },
    ]


def enrich_specific_lessons(lessons: list[dict[str, Any]]) -> None:
    enriched = [
        {
            "category_slug": "regles-grammaire",
            "titre": "Pronoms COD et COI",
            "niveau": "B1",
            "resume": "Distinguer et placer correctement les pronoms complements.",
            "contenu_markdown": (
                "### Regle\n"
                "- COD: le, la, les\n"
                "- COI: lui, leur\n"
                "- Les pronoms se placent avant le verbe conjugue.\n\n"
                "### Exemples\n"
                "- Je vois Marie -> Je la vois.\n"
                "- Je vois Paul et Luc -> Je les vois.\n"
                "- Je parle a Marie -> Je lui parle.\n"
                "- Je parle a mes parents -> Je leur parle.\n"
                "- Je vais telephoner a mon professeur -> Je vais lui telephoner.\n\n"
                "### Pieges\n"
                "- *Parler* prend un COI (a quelqu'un).\n"
                "- *Voir* prend un COD (quelqu'un).\n"
                "- A l'imperatif affirmatif: Donne-le-moi."
            ),
            "tags": ["pronoms", "cod", "coi"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Pronoms y et en",
            "niveau": "B1",
            "resume": "Remplacer les complements de lieu, de chose et de quantite.",
            "contenu_markdown": (
                "### Regle\n"
                "- **y**: lieu ou complement introduit par a (chose).\n"
                "- **en**: complement introduit par de, ou quantite.\n\n"
                "### Exemples\n"
                "- Tu vas a la bibliotheque ? Oui, j'y vais.\n"
                "- Tu penses a cet exercice ? Oui, j'y pense.\n"
                "- Tu as besoin de cette fiche ? Oui, j'en ai besoin.\n"
                "- Tu veux des exemples ? Oui, j'en veux trois.\n"
                "- Tu viens du cours ? Oui, j'en viens.\n\n"
                "### Pieges\n"
                "- Pour une personne, on prefere souvent un pronom tonique: Je pense a elle.\n"
                "- Avec une quantite, on conserve le nombre: J'en prends deux."
            ),
            "tags": ["y", "en", "pronoms"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Pronoms relatifs",
            "niveau": "B1",
            "resume": "Structurer des phrases plus riches avec qui, que, dont, ou.",
            "contenu_markdown": (
                "### Roles\n"
                "- qui: sujet\n"
                "- que: COD\n"
                "- dont: de + nom/verbe\n"
                "- ou: lieu ou temps\n\n"
                "### Exemples\n"
                "- Le livre qui est sur la table est a moi.\n"
                "- Le film que j'ai vu etait excellent.\n"
                "- Le sujet dont nous parlons est complexe.\n"
                "- La ville ou j'etudie est dynamique.\n"
                "- Le jour ou je passe l'examen approche.\n\n"
                "### Pieges\n"
                "- Apres *parler de*, *avoir besoin de*, utiliser souvent *dont*.\n"
                "- Ne pas supprimer *que* dans les phrases ecrites formelles."
            ),
            "tags": ["relatifs", "phrase-complexe"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Concordance des temps",
            "niveau": "B2",
            "resume": "Maintenir la coherence temporelle dans les subordonnees.",
            "contenu_markdown": (
                "### Principe\n"
                "Le temps du verbe principal influence le temps de la subordonnee selon le sens.\n\n"
                "### Exemples\n"
                "- Il dit qu'il vient.\n"
                "- Il a dit qu'il viendrait.\n"
                "- Je savais qu'elle etait prete.\n"
                "- Elle pensait que nous avions fini.\n"
                "- Il a explique qu'il etait arrive en retard.\n\n"
                "### Conseil\n"
                "Relis chaque phrase complexe et verifie la logique chronologique."
            ),
            "tags": ["concordance", "b2"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Declencheurs du subjonctif",
            "niveau": "B2",
            "resume": "Identifier les contextes qui exigent le subjonctif.",
            "contenu_markdown": (
                "### Expressions frequentes\n"
                "- il faut que\n"
                "- bien que\n"
                "- pour que\n"
                "- avant que\n"
                "- je veux que\n\n"
                "### Exemples\n"
                "- Il faut que tu revises ce chapitre.\n"
                "- Bien qu'il soit fatigue, il continue.\n"
                "- Je veux que vous soyez prets.\n"
                "- Avant que nous partions, verifions la consigne.\n"
                "- Pour que l'idee soit claire, donne un exemple.\n\n"
                "### Irreguliers utiles\n"
                "etre -> que je sois\n"
                "avoir -> que j'aie\n"
                "faire -> que je fasse\n"
                "aller -> que j'aille"
            ),
            "tags": ["subjonctif"],
        },
        {
            "category_slug": "regles-grammaire",
            "titre": "Connecteurs logiques",
            "niveau": "B2",
            "resume": "Ameliorer la cohesion et la progression argumentative.",
            "contenu_markdown": (
                "### Fonctions\n"
                "- Addition: de plus, en outre\n"
                "- Opposition: cependant, pourtant\n"
                "- Cause: car, puisque\n"
                "- Consequence: donc, ainsi\n"
                "- Illustration: par exemple\n\n"
                "### Exemples\n"
                "- Le cours est dense; cependant, il est tres utile.\n"
                "- J'ai peu de temps, donc je fais un plan rapide.\n"
                "- Cette methode est efficace, car elle est progressive.\n"
                "- Par exemple, je revise les verbes tous les soirs.\n"
                "- En outre, je fais une simulation hebdomadaire.\n\n"
                "### Conseil TCF\n"
                "Evite de commencer toutes les phrases par *mais* ou *donc*."
            ),
            "tags": ["connecteurs", "argumentation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Present de l'indicatif",
            "niveau": "A1",
            "resume": "Formation des verbes reguliers et reperes pour les irreguliers frequents.",
            "contenu_markdown": (
                "### Formation des verbes reguliers\n"
                "- Verbes en **-er**: e, es, e, ons, ez, ent (parler)\n"
                "- Verbes en **-ir**: is, is, it, issons, issez, issent (finir)\n"
                "- Verbes en **-re**: s, s, -, ons, ez, ent (vendre)\n\n"
                "### Irreguliers essentiels\n"
                "- etre: je suis, nous sommes\n"
                "- avoir: j'ai, nous avons\n"
                "- aller: je vais, nous allons\n"
                "- faire: je fais, nous faisons\n\n"
                "### Exemples\n"
                "- Je parle avec mon professeur.\n"
                "- Nous finissons ce module aujourd'hui.\n"
                "- Ils vendent leurs anciens livres.\n"
                "- Je vais a la bibliotheque."
            ),
            "tags": ["present", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Passe compose",
            "niveau": "A2",
            "resume": "Former le passe compose avec avoir/etre et accorder correctement.",
            "contenu_markdown": (
                "### Formation\n"
                "- Auxiliaire au present + participe passe.\n"
                "- Participes reguliers: -er -> -e, -ir -> -i, -re -> -u.\n\n"
                "### Choix de l'auxiliaire\n"
                "- La majorite des verbes prennent **avoir**.\n"
                "- Verbes de mouvement frequents prennent **etre** (aller, venir, partir).\n\n"
                "### Irreguliers frequents\n"
                "- faire -> fait\n"
                "- prendre -> pris\n"
                "- voir -> vu\n"
                "- avoir -> eu\n"
                "- etre -> ete\n\n"
                "### Exemples\n"
                "- J'ai termine mes devoirs.\n"
                "- Elle est arrivee en avance.\n"
                "- Nous avons pris des notes."
            ),
            "tags": ["passe-compose", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Imparfait",
            "niveau": "A2",
            "resume": "Former l'imparfait et l'utiliser pour le contexte et l'habitude.",
            "contenu_markdown": (
                "### Formation\n"
                "Radical de **nous** au present + terminaisons: ais, ais, ait, ions, iez, aient.\n\n"
                "Exemple: nous parlons -> je parlais.\n\n"
                "### Irregulier majeur\n"
                "- etre -> j'etais, tu etais, il etait, nous etions...\n\n"
                "### Exemples\n"
                "- Quand j'etais petit, je lisais beaucoup.\n"
                "- Nous travaillions tous les soirs.\n"
                "- Il faisait froid en hiver."
            ),
            "tags": ["imparfait", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Imparfait vs passe compose",
            "niveau": "B1",
            "resume": "Distinguer action de fond et evenement ponctuel.",
            "contenu_markdown": (
                "### Regle pratique\n"
                "- Imparfait: description, habitude, action en cours.\n"
                "- Passe compose: action ponctuelle terminee.\n\n"
                "### Exemples\n"
                "- Il pleuvait quand je suis sorti.\n"
                "- Nous etudiions quand le professeur est arrive.\n"
                "- Je lisais, puis j'ai entendu un bruit.\n"
                "- Avant, je prenais le bus; hier, j'ai pris le train."
            ),
            "tags": ["imparfait", "passe-compose"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Futur simple",
            "niveau": "A2",
            "resume": "Former le futur simple des verbes reguliers et connaitre les radicaux irreguliers utiles.",
            "contenu_markdown": (
                "### Formation reguliere\n"
                "- Infinitif + terminaisons: ai, as, a, ons, ez, ont.\n"
                "- Verbes en -re: retirer le e final (vendre -> vendrai).\n\n"
                "### Radicaux irreguliers frequents\n"
                "- etre -> ser-\n"
                "- avoir -> aur-\n"
                "- aller -> ir-\n"
                "- faire -> fer-\n"
                "- venir -> viendr-\n"
                "- pouvoir -> pourr-\n\n"
                "### Exemples\n"
                "- Demain, je reviserai deux heures.\n"
                "- Nous irons a la bibliotheque.\n"
                "- Ils auront plus de temps."
            ),
            "tags": ["futur-simple", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Conditionnel present",
            "niveau": "B1",
            "resume": "Former le conditionnel et l'utiliser pour politesse et hypothese.",
            "contenu_markdown": (
                "### Formation\n"
                "Radical du futur + terminaisons de l'imparfait: ais, ais, ait, ions, iez, aient.\n\n"
                "### Irreguliers frequents\n"
                "- etre -> serais\n"
                "- avoir -> aurais\n"
                "- aller -> irais\n"
                "- faire -> ferais\n"
                "- pouvoir -> pourrais\n\n"
                "### Exemples\n"
                "- Je voudrais plus d'exemples.\n"
                "- Si j'avais du temps, je lirais davantage.\n"
                "- Nous pourrions revoir ce point."
            ),
            "tags": ["conditionnel", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Subjonctif present",
            "niveau": "B2",
            "resume": "Former et utiliser le subjonctif present en contexte frequent.",
            "contenu_markdown": (
                "### Formation generale\n"
                "Radical de ils/elles au present + e, es, e, ions, iez, ent.\n\n"
                "### Irreguliers a memoriser\n"
                "- etre: que je sois\n"
                "- avoir: que j'aie\n"
                "- aller: que j'aille\n"
                "- faire: que je fasse\n"
                "- pouvoir: que je puisse\n\n"
                "### Exemples\n"
                "- Il faut que tu finisses ce travail.\n"
                "- Bien qu'il soit tard, nous continuons.\n"
                "- Je veux que vous soyez attentifs."
            ),
            "tags": ["subjonctif", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Plus-que-parfait",
            "niveau": "B1",
            "resume": "Exprimer une anterieurite dans le passe.",
            "contenu_markdown": (
                "### Formation\n"
                "Auxiliaire a l'imparfait + participe passe.\n\n"
                "### Exemples\n"
                "- J'avais deja termine quand il est arrive.\n"
                "- Nous etions partis avant la pluie.\n"
                "- Elle avait pris des notes utiles.\n\n"
                "### Astuce\n"
                "Utilise-le pour clarifier la chronologie de deux actions passees."
            ),
            "tags": ["plus-que-parfait", "formation"],
        },
        {
            "category_slug": "temps-verbaux",
            "titre": "Gerondif",
            "niveau": "B1",
            "resume": "Exprimer simultaneite, maniere ou condition.",
            "contenu_markdown": (
                "### Formation\n"
                "**en + participe present** (radical de nous + ant).\n\n"
                "### Exemples\n"
                "- Il apprend en lisant.\n"
                "- Nous progressons en pratiquant chaque jour.\n"
                "- En etant organise, on reduit le stress.\n\n"
                "### Attention\n"
                "Le gerondif exprime souvent la maniere ou la condition."
            ),
            "tags": ["gerondif", "formation"],
        },
    ]
    for lesson in enriched:
        upsert_lesson(lessons, lesson)


def build_extra_vocabulary() -> list[dict[str, Any]]:
    words: list[tuple[str, str, str, str]] = [
        ("aisance", "ease", "B2", "Expression"),
        ("analyse", "analysis", "B1", "Etudes"),
        ("annonce", "announcement", "A2", "Travail"),
        ("apprenant", "learner", "A2", "Etudes"),
        ("argumentation", "argumentation", "B2", "Expression"),
        ("assurer", "to ensure", "B1", "Travail"),
        ("atelier", "workshop", "A2", "Etudes"),
        ("attitude", "attitude", "A2", "Societe"),
        ("auditoire", "audience", "B2", "Expression"),
        ("autocorrection", "self-correction", "B2", "Etudes"),
        ("autoevaluation", "self-assessment", "B2", "Examens"),
        ("brouillon", "draft", "A2", "Expression"),
        ("cadre", "framework", "B1", "Travail"),
        ("capacite", "ability", "A2", "Etudes"),
        ("carriere", "career", "A2", "Travail"),
        ("certification", "certification", "B1", "Examens"),
        ("citer", "to quote", "B1", "Expression"),
        ("classement", "ranking", "B2", "Examens"),
        ("collaborer", "to collaborate", "B1", "Travail"),
        ("commentaire", "comment", "A2", "Expression"),
        ("competence", "skill", "A2", "Etudes"),
        ("comprehensible", "understandable", "B1", "Expression"),
        ("concision", "conciseness", "B2", "Expression"),
        ("confiance", "confidence", "A2", "Societe"),
        ("conseiller", "to advise", "B1", "Travail"),
        ("consistant", "consistent", "B2", "Etudes"),
        ("conviction", "conviction", "B2", "Expression"),
        ("convocation", "summons", "B1", "Examens"),
        ("creativite", "creativity", "B1", "Expression"),
        ("critere", "criterion", "B1", "Examens"),
        ("debattre", "to debate", "B2", "Expression"),
        ("decrire", "to describe", "A2", "Expression"),
        ("demarche", "approach", "B2", "Etudes"),
        ("demonstration", "demonstration", "B2", "Expression"),
        ("detail", "detail", "A2", "Expression"),
        ("diplome", "degree", "A2", "Etudes"),
        ("discours", "speech", "B1", "Expression"),
        ("dissertation", "essay", "B2", "Expression"),
        ("documenter", "to document", "B2", "Travail"),
        ("domaine", "field", "A2", "Etudes"),
        ("durable", "sustainable", "B1", "Societe"),
        ("echanger", "to exchange", "A2", "Societe"),
        ("echeance", "due date", "B1", "Examens"),
        ("eclaircir", "to clarify", "B2", "Expression"),
        ("ecoute", "listening", "A2", "Etudes"),
        ("effort", "effort", "A2", "Etudes"),
        ("elargir", "to broaden", "B2", "Etudes"),
        ("employabilite", "employability", "B2", "Travail"),
        ("encadrement", "supervision", "B2", "Travail"),
        ("enchainement", "flow", "B2", "Expression"),
        ("encourager", "to encourage", "A2", "Societe"),
        ("energie", "energy", "A2", "Societe"),
        ("entretien", "interview", "B1", "Travail"),
        ("equilibre", "balance", "B1", "Societe"),
        ("erreur", "mistake", "A1", "Etudes"),
        ("essentiel", "essential", "A2", "Etudes"),
        ("estimation", "estimate", "B1", "Examens"),
        ("ethique", "ethics", "B2", "Societe"),
        ("evaluation", "evaluation", "A2", "Examens"),
        ("evidence", "evidence", "B2", "Expression"),
        ("evolution", "evolution", "A2", "Societe"),
        ("exactitude", "accuracy", "B2", "Expression"),
        ("exigence", "requirement", "B1", "Examens"),
        ("experience", "experience", "A2", "Societe"),
        ("explicite", "explicit", "B2", "Expression"),
        ("faciliter", "to facilitate", "B1", "Etudes"),
        ("fiabilite", "reliability", "B2", "Travail"),
        ("formuler", "to formulate", "B1", "Expression"),
        ("habitude", "habit", "A2", "Etudes"),
        ("hypothese", "hypothesis", "B2", "Expression"),
        ("impact", "impact", "A2", "Societe"),
        ("implication", "involvement", "B2", "Travail"),
        ("inciter", "to encourage", "B1", "Societe"),
        ("indicator", "indicator", "B2", "Examens"),
        ("initiative", "initiative", "B1", "Travail"),
        ("innovation", "innovation", "B2", "Societe"),
        ("inscription", "registration", "A2", "Examens"),
        ("intention", "intention", "A2", "Expression"),
        ("interpretation", "interpretation", "B2", "Expression"),
        ("intervenir", "to intervene", "B1", "Societe"),
        ("justification", "justification", "B2", "Expression"),
        ("lecture", "reading", "A2", "Etudes"),
        ("legitimite", "legitimacy", "B2", "Societe"),
        ("logique", "logic", "B1", "Expression"),
        ("maitrise", "mastery", "B2", "Etudes"),
        ("methode", "method", "A2", "Etudes"),
        ("mobilite", "mobility", "B1", "Societe"),
        ("module", "module", "A2", "Etudes"),
        ("niveau", "level", "A1", "Examens"),
        ("notion", "notion", "A2", "Etudes"),
        ("objectif", "objective", "A2", "Etudes"),
        ("obstacle", "obstacle", "B1", "Societe"),
        ("opinion", "opinion", "A2", "Expression"),
        ("oral", "oral", "A2", "Examens"),
        ("organisation", "organization", "A2", "Travail"),
        ("paragraphe", "paragraph", "A2", "Expression"),
        ("parcours", "pathway", "B1", "Etudes"),
        ("participation", "participation", "A2", "Societe"),
        ("pertinence", "relevance", "B2", "Expression"),
        ("planification", "planning", "B1", "Travail"),
        ("ponctualite", "punctuality", "A2", "Travail"),
        ("position", "position", "A2", "Expression"),
        ("precision", "precision", "B2", "Expression"),
        ("preparation", "preparation", "A2", "Examens"),
        ("prioriser", "to prioritize", "B1", "Etudes"),
        ("probleme", "problem", "A2", "Societe"),
        ("procedure", "procedure", "B1", "Travail"),
        ("progression", "progression", "A2", "Etudes"),
        ("proposition", "proposal", "B1", "Expression"),
        ("qualite", "quality", "A2", "Travail"),
        ("questionnaire", "questionnaire", "B1", "Examens"),
        ("raisonnement", "reasoning", "B2", "Expression"),
        ("realiste", "realistic", "B1", "Societe"),
        ("recherche", "research", "A2", "Etudes"),
        ("recommandation", "recommendation", "B1", "Expression"),
        ("redaction", "writing", "A2", "Expression"),
        ("reference", "reference", "B1", "Etudes"),
        ("regulier", "regular", "A2", "Etudes"),
        ("renforcer", "to strengthen", "B1", "Expression"),
        ("reponse", "answer", "A1", "Examens"),
        ("revision", "revision", "A2", "Etudes"),
        ("rigueur", "rigor", "B2", "Etudes"),
        ("risque", "risk", "B1", "Societe"),
        ("scolarite", "schooling", "A2", "Etudes"),
        ("selection", "selection", "B1", "Examens"),
        ("sens", "meaning", "A2", "Expression"),
        ("simulateur", "simulator", "B1", "Technologie"),
        ("strategie", "strategy", "B1", "Etudes"),
        ("synthese", "synthesis", "B2", "Expression"),
        ("systematique", "systematic", "B2", "Etudes"),
        ("technique", "technique", "A2", "Travail"),
        ("tendance", "trend", "B2", "Societe"),
        ("these", "thesis", "B2", "Expression"),
        ("tolerance", "tolerance", "B1", "Societe"),
        ("trace", "trace", "A2", "Etudes"),
        ("validation", "validation", "B1", "Examens"),
        ("vigilance", "vigilance", "B2", "Travail"),
        ("vision", "vision", "B1", "Societe"),
    ]
    out: list[dict[str, Any]] = []
    for mot, en, niveau, theme in words:
        out.append(
            {
                "mot": mot,
                "definition_fr": f"Terme utile pour parler de {theme.lower()} dans un contexte de preparation TCF.",
                "traduction_en": en,
                "exemple_fr": f"J'utilise le mot '{mot}' pour rendre mon expression plus precise.",
                "niveau": niveau,
                "theme": theme,
            }
        )
    return out


def build_extra_exercises() -> list[dict[str, Any]]:
    return [
        {
            "type": "qcm",
            "theme": "Subjonctif",
            "niveau": "B2",
            "question": "Il est important que vous ___ ce chapitre.",
            "options": ["lisez", "lisiez", "lirez", "avez lu"],
            "answer_index": 1,
            "explication": "Apres 'il est important que', on utilise le subjonctif.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Declencheurs du subjonctif",
        },
        {
            "type": "qcm",
            "theme": "Subjonctif",
            "niveau": "B2",
            "question": "Bien qu'il ___ tard, il continue de travailler.",
            "options": ["est", "sera", "soit", "etait"],
            "answer_index": 2,
            "explication": "Bien que est suivi du subjonctif.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Declencheurs du subjonctif",
        },
        {
            "type": "qcm",
            "theme": "Concordance",
            "niveau": "B2",
            "question": "Il a dit qu'il ___ le lendemain.",
            "options": ["vient", "viendra", "viendrait", "venait"],
            "answer_index": 2,
            "explication": "Discours rapporte au passe: conditionnel present.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Concordance des temps",
        },
        {
            "type": "qcm",
            "theme": "Concordance",
            "niveau": "B2",
            "question": "Je savais qu'elle ___ deja termine.",
            "options": ["avait", "a", "aura", "aurait"],
            "answer_index": 0,
            "explication": "Anterieurite dans le passe: plus-que-parfait.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Concordance des temps",
        },
        {
            "type": "qcm",
            "theme": "Participe passe",
            "niveau": "B2",
            "question": "Les lettres que j'ai ___ sont claires.",
            "options": ["ecrit", "ecrites", "ecrits", "ecrite"],
            "answer_index": 1,
            "explication": "COD place avant + feminin pluriel: ecrites.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Accord du participe passe",
        },
        {
            "type": "qcm",
            "theme": "Participe passe",
            "niveau": "B2",
            "question": "Elles se sont ___ hier soir.",
            "options": ["parlees", "parle", "parles", "parler"],
            "answer_index": 1,
            "explication": "Se parler = COI, donc pas d'accord.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Accord du participe passe",
        },
        {
            "type": "qcm",
            "theme": "Futur proche",
            "niveau": "B1",
            "question": "Je ___ commencer ma redaction.",
            "options": ["vais", "irai", "allais", "irais"],
            "answer_index": 0,
            "explication": "Futur proche: aller au present + infinitif.",
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
            "explication": "Hypothese non realisee: conditionnel passe.",
            "lesson_category_slug": "temps-verbaux",
            "lesson_titre": "Conditionnel passe",
        },
        {
            "type": "qcm",
            "theme": "Discours indirect",
            "niveau": "B2",
            "question": "Direct: Elle dit: \"Je suis prete.\" -> Indirect:",
            "options": [
                "Elle dit qu'elle est prete.",
                "Elle dit qu'elle soit prete.",
                "Elle dit que je suis prete.",
                "Elle dit qu'elle etait prete."
            ],
            "answer_index": 0,
            "explication": "Au present, on garde le present pour rapporter une parole actuelle.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Discours direct et indirect",
        },
        {
            "type": "qcm",
            "theme": "Negation",
            "niveau": "B1",
            "question": "Choisis la phrase avec une restriction.",
            "options": [
                "Je ne travaille que le matin.",
                "Je ne travaille jamais le matin.",
                "Je ne travaille plus le matin.",
                "Je ne travaille personne."
            ],
            "answer_index": 0,
            "explication": "Ne...que exprime la restriction.",
            "lesson_category_slug": "regles-grammaire",
            "lesson_titre": "Negation complexe",
        },
    ]


def build_extra_prompts() -> list[dict[str, Any]]:
    topics = [
        "teletravail et productivite",
        "intelligence artificielle et etudes",
        "sport et reussite scolaire",
        "voyages et ouverture culturelle",
        "reseaux sociaux et information",
        "lecture obligatoire a l'universite",
        "benevolat et insertion professionnelle",
        "ville durable et mobilite etudiante",
        "cours hybrides a l'universite",
        "evaluation continue ou examen final",
        "usage des smartphones en classe",
        "apprentissage des langues en ligne",
        "importance de la prise de notes",
        "uniforme scolaire: pour ou contre",
        "impact du cout de la vie etudiante",
        "gestion du stress avant les examens",
        "importance des stages",
        "plagiat et integrite academique",
    ]
    out: list[dict[str, Any]] = []
    for t in topics:
        out.append(
            {
                "titre": f"Debat: {t}",
                "tache_tcf": "Tache 3",
                "niveau": "B2",
                "consigne": f"Redigez un texte argumentatif sur le theme '{t}'. Presentez avantages, limites et position personnelle.",
                "min_mots": 180,
                "max_mots": 230,
            }
        )
    return out


def build_full_irregular_conjugations() -> list[dict[str, Any]]:
    return [
        {"infinitif": "etre", "temps": "present", "niveau": "A1", "formes": {"je": "suis", "tu": "es", "il/elle": "est", "nous": "sommes", "vous": "etes", "ils/elles": "sont"}},
        {"infinitif": "etre", "temps": "imparfait", "niveau": "A2", "formes": {"je": "etais", "tu": "etais", "il/elle": "etait", "nous": "etions", "vous": "etiez", "ils/elles": "etaient"}},
        {"infinitif": "etre", "temps": "futur simple", "niveau": "A2", "formes": {"je": "serai", "tu": "seras", "il/elle": "sera", "nous": "serons", "vous": "serez", "ils/elles": "seront"}},
        {"infinitif": "etre", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "serais", "tu": "serais", "il/elle": "serait", "nous": "serions", "vous": "seriez", "ils/elles": "seraient"}},
        {"infinitif": "etre", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "sois", "tu": "sois", "il/elle": "soit", "nous": "soyons", "vous": "soyez", "ils/elles": "soient"}},
        {"infinitif": "etre", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai ete", "tu": "as ete", "il/elle": "a ete", "nous": "avons ete", "vous": "avez ete", "ils/elles": "ont ete"}},
        {"infinitif": "avoir", "temps": "present", "niveau": "A1", "formes": {"je": "ai", "tu": "as", "il/elle": "a", "nous": "avons", "vous": "avez", "ils/elles": "ont"}},
        {"infinitif": "avoir", "temps": "imparfait", "niveau": "A2", "formes": {"je": "avais", "tu": "avais", "il/elle": "avait", "nous": "avions", "vous": "aviez", "ils/elles": "avaient"}},
        {"infinitif": "avoir", "temps": "futur simple", "niveau": "A2", "formes": {"je": "aurai", "tu": "auras", "il/elle": "aura", "nous": "aurons", "vous": "aurez", "ils/elles": "auront"}},
        {"infinitif": "avoir", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "aurais", "tu": "aurais", "il/elle": "aurait", "nous": "aurions", "vous": "auriez", "ils/elles": "auraient"}},
        {"infinitif": "avoir", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "aie", "tu": "aies", "il/elle": "ait", "nous": "ayons", "vous": "ayez", "ils/elles": "aient"}},
        {"infinitif": "avoir", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai eu", "tu": "as eu", "il/elle": "a eu", "nous": "avons eu", "vous": "avez eu", "ils/elles": "ont eu"}},
        {"infinitif": "aller", "temps": "present", "niveau": "A1", "formes": {"je": "vais", "tu": "vas", "il/elle": "va", "nous": "allons", "vous": "allez", "ils/elles": "vont"}},
        {"infinitif": "aller", "temps": "imparfait", "niveau": "A2", "formes": {"je": "allais", "tu": "allais", "il/elle": "allait", "nous": "allions", "vous": "alliez", "ils/elles": "allaient"}},
        {"infinitif": "aller", "temps": "futur simple", "niveau": "A2", "formes": {"je": "irai", "tu": "iras", "il/elle": "ira", "nous": "irons", "vous": "irez", "ils/elles": "iront"}},
        {"infinitif": "aller", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "irais", "tu": "irais", "il/elle": "irait", "nous": "irions", "vous": "iriez", "ils/elles": "iraient"}},
        {"infinitif": "aller", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "aille", "tu": "ailles", "il/elle": "aille", "nous": "allions", "vous": "alliez", "ils/elles": "aillent"}},
        {"infinitif": "aller", "temps": "passe compose", "niveau": "A2", "formes": {"je": "suis alle", "tu": "es alle", "il/elle": "est alle", "nous": "sommes alles", "vous": "etes alles", "ils/elles": "sont alles"}},
        {"infinitif": "faire", "temps": "present", "niveau": "A1", "formes": {"je": "fais", "tu": "fais", "il/elle": "fait", "nous": "faisons", "vous": "faites", "ils/elles": "font"}},
        {"infinitif": "faire", "temps": "imparfait", "niveau": "A2", "formes": {"je": "faisais", "tu": "faisais", "il/elle": "faisait", "nous": "faisions", "vous": "faisiez", "ils/elles": "faisaient"}},
        {"infinitif": "faire", "temps": "futur simple", "niveau": "A2", "formes": {"je": "ferai", "tu": "feras", "il/elle": "fera", "nous": "ferons", "vous": "ferez", "ils/elles": "feront"}},
        {"infinitif": "faire", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "ferais", "tu": "ferais", "il/elle": "ferait", "nous": "ferions", "vous": "feriez", "ils/elles": "feraient"}},
        {"infinitif": "faire", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "fasse", "tu": "fasses", "il/elle": "fasse", "nous": "fassions", "vous": "fassiez", "ils/elles": "fassent"}},
        {"infinitif": "faire", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai fait", "tu": "as fait", "il/elle": "a fait", "nous": "avons fait", "vous": "avez fait", "ils/elles": "ont fait"}},
        {"infinitif": "venir", "temps": "present", "niveau": "A2", "formes": {"je": "viens", "tu": "viens", "il/elle": "vient", "nous": "venons", "vous": "venez", "ils/elles": "viennent"}},
        {"infinitif": "venir", "temps": "imparfait", "niveau": "A2", "formes": {"je": "venais", "tu": "venais", "il/elle": "venait", "nous": "venions", "vous": "veniez", "ils/elles": "venaient"}},
        {"infinitif": "venir", "temps": "futur simple", "niveau": "B1", "formes": {"je": "viendrai", "tu": "viendras", "il/elle": "viendra", "nous": "viendrons", "vous": "viendrez", "ils/elles": "viendront"}},
        {"infinitif": "venir", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "viendrais", "tu": "viendrais", "il/elle": "viendrait", "nous": "viendrions", "vous": "viendriez", "ils/elles": "viendraient"}},
        {"infinitif": "venir", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "vienne", "tu": "viennes", "il/elle": "vienne", "nous": "venions", "vous": "veniez", "ils/elles": "viennent"}},
        {"infinitif": "venir", "temps": "passe compose", "niveau": "A2", "formes": {"je": "suis venu", "tu": "es venu", "il/elle": "est venu", "nous": "sommes venus", "vous": "etes venus", "ils/elles": "sont venus"}},
        {"infinitif": "pouvoir", "temps": "present", "niveau": "A2", "formes": {"je": "peux", "tu": "peux", "il/elle": "peut", "nous": "pouvons", "vous": "pouvez", "ils/elles": "peuvent"}},
        {"infinitif": "pouvoir", "temps": "imparfait", "niveau": "B1", "formes": {"je": "pouvais", "tu": "pouvais", "il/elle": "pouvait", "nous": "pouvions", "vous": "pouviez", "ils/elles": "pouvaient"}},
        {"infinitif": "pouvoir", "temps": "futur simple", "niveau": "B1", "formes": {"je": "pourrai", "tu": "pourras", "il/elle": "pourra", "nous": "pourrons", "vous": "pourrez", "ils/elles": "pourront"}},
        {"infinitif": "pouvoir", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "pourrais", "tu": "pourrais", "il/elle": "pourrait", "nous": "pourrions", "vous": "pourriez", "ils/elles": "pourraient"}},
        {"infinitif": "pouvoir", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "puisse", "tu": "puisses", "il/elle": "puisse", "nous": "puissions", "vous": "puissiez", "ils/elles": "puissent"}},
        {"infinitif": "pouvoir", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai pu", "tu": "as pu", "il/elle": "a pu", "nous": "avons pu", "vous": "avez pu", "ils/elles": "ont pu"}},
        {"infinitif": "devoir", "temps": "present", "niveau": "A2", "formes": {"je": "dois", "tu": "dois", "il/elle": "doit", "nous": "devons", "vous": "devez", "ils/elles": "doivent"}},
        {"infinitif": "devoir", "temps": "imparfait", "niveau": "B1", "formes": {"je": "devais", "tu": "devais", "il/elle": "devait", "nous": "devions", "vous": "deviez", "ils/elles": "devaient"}},
        {"infinitif": "devoir", "temps": "futur simple", "niveau": "B1", "formes": {"je": "devrai", "tu": "devras", "il/elle": "devra", "nous": "devrons", "vous": "devrez", "ils/elles": "devront"}},
        {"infinitif": "devoir", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "devrais", "tu": "devrais", "il/elle": "devrait", "nous": "devrions", "vous": "devriez", "ils/elles": "devraient"}},
        {"infinitif": "devoir", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "doive", "tu": "doives", "il/elle": "doive", "nous": "devions", "vous": "deviez", "ils/elles": "doivent"}},
        {"infinitif": "devoir", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai du", "tu": "as du", "il/elle": "a du", "nous": "avons du", "vous": "avez du", "ils/elles": "ont du"}},
        {"infinitif": "vouloir", "temps": "present", "niveau": "A2", "formes": {"je": "veux", "tu": "veux", "il/elle": "veut", "nous": "voulons", "vous": "voulez", "ils/elles": "veulent"}},
        {"infinitif": "vouloir", "temps": "imparfait", "niveau": "B1", "formes": {"je": "voulais", "tu": "voulais", "il/elle": "voulait", "nous": "voulions", "vous": "vouliez", "ils/elles": "voulaient"}},
        {"infinitif": "vouloir", "temps": "futur simple", "niveau": "B1", "formes": {"je": "voudrai", "tu": "voudras", "il/elle": "voudra", "nous": "voudrons", "vous": "voudrez", "ils/elles": "voudront"}},
        {"infinitif": "vouloir", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "voudrais", "tu": "voudrais", "il/elle": "voudrait", "nous": "voudrions", "vous": "voudriez", "ils/elles": "voudraient"}},
        {"infinitif": "vouloir", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "veuille", "tu": "veuilles", "il/elle": "veuille", "nous": "voulions", "vous": "vouliez", "ils/elles": "veuillent"}},
        {"infinitif": "vouloir", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai voulu", "tu": "as voulu", "il/elle": "a voulu", "nous": "avons voulu", "vous": "avez voulu", "ils/elles": "ont voulu"}},
        {"infinitif": "prendre", "temps": "present", "niveau": "A2", "formes": {"je": "prends", "tu": "prends", "il/elle": "prend", "nous": "prenons", "vous": "prenez", "ils/elles": "prennent"}},
        {"infinitif": "prendre", "temps": "imparfait", "niveau": "A2", "formes": {"je": "prenais", "tu": "prenais", "il/elle": "prenait", "nous": "prenions", "vous": "preniez", "ils/elles": "prenaient"}},
        {"infinitif": "prendre", "temps": "futur simple", "niveau": "B1", "formes": {"je": "prendrai", "tu": "prendras", "il/elle": "prendra", "nous": "prendrons", "vous": "prendrez", "ils/elles": "prendront"}},
        {"infinitif": "prendre", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "prendrais", "tu": "prendrais", "il/elle": "prendrait", "nous": "prendrions", "vous": "prendriez", "ils/elles": "prendraient"}},
        {"infinitif": "prendre", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "prenne", "tu": "prennes", "il/elle": "prenne", "nous": "prenions", "vous": "preniez", "ils/elles": "prennent"}},
        {"infinitif": "prendre", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai pris", "tu": "as pris", "il/elle": "a pris", "nous": "avons pris", "vous": "avez pris", "ils/elles": "ont pris"}},
        {"infinitif": "savoir", "temps": "present", "niveau": "A2", "formes": {"je": "sais", "tu": "sais", "il/elle": "sait", "nous": "savons", "vous": "savez", "ils/elles": "savent"}},
        {"infinitif": "savoir", "temps": "imparfait", "niveau": "B1", "formes": {"je": "savais", "tu": "savais", "il/elle": "savait", "nous": "savions", "vous": "saviez", "ils/elles": "savaient"}},
        {"infinitif": "savoir", "temps": "futur simple", "niveau": "B1", "formes": {"je": "saurai", "tu": "sauras", "il/elle": "saura", "nous": "saurons", "vous": "saurez", "ils/elles": "sauront"}},
        {"infinitif": "savoir", "temps": "conditionnel present", "niveau": "B1", "formes": {"je": "saurais", "tu": "saurais", "il/elle": "saurait", "nous": "saurions", "vous": "sauriez", "ils/elles": "sauraient"}},
        {"infinitif": "savoir", "temps": "subjonctif present", "niveau": "B2", "formes": {"je": "sache", "tu": "saches", "il/elle": "sache", "nous": "sachions", "vous": "sachiez", "ils/elles": "sachent"}},
        {"infinitif": "savoir", "temps": "passe compose", "niveau": "A2", "formes": {"je": "ai su", "tu": "as su", "il/elle": "a su", "nous": "avons su", "vous": "avez su", "ils/elles": "ont su"}},
    ]


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


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "content" / "packs" / "tcf_pack_v1.json"
    dst = root / "content" / "packs" / "tcf_pack_v2.json"

    data = json.loads(src.read_text(encoding="utf-8"))
    data["metadata"] = {
        "name": "tcf_pack_v2",
        "version": "2.0.0",
        "language": "fr",
        "description": "Pack enrichi: contenu massif pour grammaire, temps verbaux, conjugaison, QCM et expression ecrite.",
    }

    lessons = data.get("lessons", [])
    enrich_specific_lessons(lessons)
    for lesson in build_extra_lessons():
        upsert_lesson(lessons, lesson)
    data["lessons"] = dedupe_items(lessons, ("category_slug", "titre"))

    vocab = data.get("vocabulary", []) + build_extra_vocabulary()
    data["vocabulary"] = dedupe_items(vocab, ("mot",))

    conjugations = data.get("verb_conjugations", [])
    for row in build_full_irregular_conjugations():
        upsert_conjugation(conjugations, row)
    data["verb_conjugations"] = dedupe_items(conjugations, ("infinitif", "temps"))

    exercises = data.get("exercises", [])
    exercises.extend(build_extra_exercises())
    exercises.extend(generate_conjugation_qcm(data["verb_conjugations"], n=90))
    data["exercises"] = dedupe_items(exercises, ("question", "niveau"))

    prompts = data.get("writing_prompts", []) + build_extra_prompts()
    data["writing_prompts"] = dedupe_items(prompts, ("titre",))

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Pack genere: {dst}")
    for k in ["lessons", "vocabulary", "verb_conjugations", "exercises", "writing_prompts"]:
        print(f"- {k}: {len(data[k])}")


if __name__ == "__main__":
    main()
