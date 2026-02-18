from __future__ import annotations

import json
import os
import random
from typing import Any

import streamlit as st
from openai import OpenAI

import db


st.set_page_config(page_title="Coach TCF Francais", page_icon="🇫🇷", layout="wide")


ORDRE_TEMPS = [
    "present",
    "imparfait",
    "passe compose",
    "plus-que-parfait",
    "futur simple",
    "conditionnel present",
    "subjonctif present",
]


def extraire_json_depuis_texte(texte: str) -> dict[str, Any] | None:
    if not texte:
        return None

    propre = texte.strip()
    if propre.startswith("```"):
        propre = propre.strip("`")
        if "\n" in propre:
            propre = propre.split("\n", 1)[1]

    debut = propre.find("{")
    fin = propre.rfind("}")
    if debut == -1 or fin == -1 or fin <= debut:
        return None

    try:
        return json.loads(propre[debut : fin + 1])
    except json.JSONDecodeError:
        return None


def corriger_redaction_avec_openai(
    api_key: str, modele: str, tache: str, consigne: str, texte: str
) -> tuple[dict[str, Any] | None, str]:
    client = OpenAI(api_key=api_key)
    reponse = client.responses.create(
        model=modele,
        input=[
            {
                "role": "system",
                "content": (
                    "Tu es un correcteur expert du TCF. "
                    "Evalue selon: coherence, grammaire, lexique, orthographe, registre. "
                    "Retourne strictement un JSON valide avec ces cles: "
                    "note_globale_sur_20, criteres, points_forts, erreurs_prioritaires, "
                    "version_corrigee, conseil_methode."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Tache TCF: {tache}\n"
                    f"Consigne: {consigne}\n"
                    "Texte du candidat:\n"
                    f"{texte}"
                ),
            },
        ],
    )

    brut = (reponse.output_text or "").strip()
    return extraire_json_depuis_texte(brut), brut


def get_default_api_key() -> str:
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return str(st.secrets["OPENAI_API_KEY"])
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY", "")


def get_default_model() -> str:
    try:
        if "OPENAI_MODEL" in st.secrets:
            return str(st.secrets["OPENAI_MODEL"])
    except Exception:
        pass
    return os.getenv("OPENAI_MODEL", "gpt-5-mini")


def compter_mots(texte: str) -> int:
    return len([mot for mot in texte.strip().split() if mot])


def ordre_temps(temps: str) -> int:
    return ORDRE_TEMPS.index(temps) if temps in ORDRE_TEMPS else len(ORDRE_TEMPS) + 1


def normaliser_valeur_critere(valeur: Any) -> tuple[Any, str | None]:
    if isinstance(valeur, (int, float, str)):
        return valeur, None

    if isinstance(valeur, dict):
        note = valeur.get("note_sur_4")
        commentaire = valeur.get("commentaire")
        note_affichee = note if isinstance(note, (int, float, str)) else "N/A"
        commentaire_texte = commentaire if isinstance(commentaire, str) else None
        return note_affichee, commentaire_texte

    return "N/A", None


def evaluer_barreme_ce(score: int, total: int) -> dict[str, Any]:
    if total <= 0:
        return {"pourcentage": 0, "niveau": "N/A", "score_tcf_simule": 100}
    pourcentage = round((score / total) * 100, 1)
    score_tcf = round(100 + (pourcentage / 100) * 599)

    if pourcentage < 30:
        niveau = "A1"
    elif pourcentage < 45:
        niveau = "A2"
    elif pourcentage < 60:
        niveau = "B1"
    elif pourcentage < 75:
        niveau = "B2"
    elif pourcentage < 90:
        niveau = "C1"
    else:
        niveau = "C2"

    return {"pourcentage": pourcentage, "niveau": niveau, "score_tcf_simule": score_tcf}


def verifier_base() -> bool:
    if db.database_exists():
        return True

    st.error("Base SQLite absente.")
    st.code("python3 scripts/init_db.py")
    st.info("Initialise la base puis relance l'application.")
    return False


def afficher_accueil() -> None:
    st.title("Coach TCF Francais")
    st.caption("Plateforme de preparation TCF, 100% en francais, avec contenu charge depuis SQLite.")

    resume = st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="distribute",
        vertical_alignment="center",
        gap="large",
    )
    with resume:
        st.metric("Fiches de cours", db.count_rows("lessons"))
        st.metric("Mots de vocabulaire", db.count_rows("vocabulary"))
        st.metric("Conjugaisons", db.count_rows("verb_conjugations"))
        st.metric("Questions QCM", db.count_rows("exercises"))
        st.metric("Textes CE", db.count_rows("reading_passages"))

    st.subheader("Parcours recommande")
    st.markdown("1. `Vocabulaire` pour enrichir le lexique.")
    st.markdown("2. `Grammaire` puis `Regles de grammaire` pour consolider la base.")
    st.markdown("3. `Temps verbaux` + `Conjugaison` pour la precision.")
    st.markdown("4. `Comprehension ecrite` pour s'entrainer au format TCF.")
    st.markdown("5. `QCM` pour evaluer le niveau.")
    st.markdown("6. `Expression ecrite` pour corriger et noter les productions.")


def afficher_lessons_par_categorie(category_slug: str, titre: str) -> None:
    st.title(titre)
    niveaux = ["Tous"] + db.list_levels_for_table("lessons")

    filtres = st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
        gap="small",
    )
    with filtres:
        recherche = st.text_input("Recherche", key=f"search-{category_slug}")
        niveau = st.selectbox("Niveau", niveaux, key=f"niveau-{category_slug}")

    fiches = db.search_lessons(category_slug=category_slug, search=recherche, level=niveau)
    st.write(f"{len(fiches)} fiche(s).")

    for fiche in fiches:
        with st.expander(f"{fiche['titre']} ({fiche['niveau']})", expanded=False):
            st.markdown(f"**Resume:** {fiche['resume']}")
            st.markdown(fiche["contenu_markdown"])
            tags = fiche.get("tags", [])
            if tags:
                st.caption("Tags: " + ", ".join(tags))


def afficher_vocabulaire() -> None:
    st.title("Vocabulaire")
    niveaux = ["Tous"] + db.list_levels_for_table("vocabulary")
    themes = ["Tous"] + db.list_themes_vocab()

    filtres = st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
        gap="small",
    )
    with filtres:
        recherche = st.text_input("Recherche mot ou definition", key="vocab-search")
        niveau = st.selectbox("Niveau", niveaux, key="vocab-level")
        theme = st.selectbox("Theme", themes, key="vocab-theme")

    resultats = db.search_vocabulary(recherche, niveau, theme)
    st.write(f"{len(resultats)} entree(s) trouvee(s).")

    for mot in resultats:
        carte = st.container(border=True)
        with carte:
            st.markdown(f"### {mot['mot']}")
            infos = st.container(horizontal=True, horizontal_alignment="left", gap="small")
            with infos:
                st.caption(f"Niveau: {mot['niveau']}")
                st.caption(f"Theme: {mot['theme']}")
            st.markdown(f"**Definition:** {mot['definition_fr']}")
            st.markdown(f"**Traduction EN:** {mot['traduction_en']}")
            st.markdown(f"**Exemple:** {mot['exemple_fr']}")


def afficher_conjugaison() -> None:
    st.title("Conjugaison")
    verbes = db.list_verbs()
    if not verbes:
        st.warning("Aucune conjugaison en base.")
        return

    select = st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
        gap="small",
    )
    with select:
        verbe = st.selectbox("Verbe", verbes, index=0)
    temps_disponibles = sorted(db.list_tenses_for_verb(verbe), key=ordre_temps)
    if not temps_disponibles:
        st.info("Aucun temps verbal disponible pour ce verbe.")
        return

    st.subheader(f"Conjugaisons completes: {verbe}")
    for temps in temps_disponibles:
        lignes = db.get_conjugations(verbe, temps)
        if not lignes:
            continue
        with st.container(border=True):
            st.markdown(f"### {temps}")
            for ligne in lignes:
                st.markdown(f"**{ligne['personne']} {ligne['forme']}**")
            st.caption(f"Niveau indicatif: {lignes[0]['niveau']}")


def afficher_qcm() -> None:
    st.title("QCM")
    themes = ["Tous"] + db.list_themes_qcm()
    niveaux = ["Tous"] + db.list_levels_for_table("exercises")

    filtres = st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
        gap="small",
    )
    with filtres:
        theme = st.selectbox("Theme", themes, index=0)
        niveau = st.selectbox("Niveau", niveaux, index=0)
        taille = st.slider("Nombre de questions", min_value=3, max_value=20, value=5, step=1)
        melanger = st.toggle("Melanger", value=True)
        generer = st.button("Nouvelle serie", type="primary")

    signature = (theme, niveau, taille, melanger)
    if generer or st.session_state.get("signature-qcm-db") != signature:
        questions = db.get_qcm(theme, niveau)
        if melanger:
            random.shuffle(questions)
        st.session_state["serie-qcm-db"] = questions[: min(taille, len(questions))]
        st.session_state["signature-qcm-db"] = signature

    serie = st.session_state.get("serie-qcm-db", [])
    if not serie:
        st.warning("Aucune question disponible pour ces filtres.")
        return

    with st.form("form-qcm-db"):
        for i, q in enumerate(serie, start=1):
            st.markdown(f"**{i}. {q['question']}**")
            st.radio(
                "Choix",
                options=list(range(len(q["options"]))),
                format_func=lambda idx, opts=q["options"]: opts[idx],
                key=f"reponse-{q['id']}",
                index=None,
                label_visibility="collapsed",
            )
        corriger = st.form_submit_button("Corriger")

    if corriger:
        bonnes = 0
        for q in serie:
            rep = st.session_state.get(f"reponse-{q['id']}")
            if rep == q["answer_index"]:
                bonnes += 1
        score = round((bonnes / len(serie)) * 100)
        st.metric("Score", f"{score}% ({bonnes}/{len(serie)})")

        st.subheader("Corrige")
        for q in serie:
            rep = st.session_state.get(f"reponse-{q['id']}")
            correcte = q["answer_index"]
            ok = rep == correcte
            st.markdown(f"**{'✅' if ok else '❌'} {q['question']}**")
            st.markdown(f"- Bonne reponse: {q['options'][correcte]}")
            st.markdown(f"- Explication: {q['explication']}")


def afficher_expression_ecrite() -> None:
    st.title("Expression ecrite")
    st.caption("Correction et notation avec API OpenAI.")

    niveaux = ["Tous"] + db.list_levels_for_table("writing_prompts")
    niveau = st.selectbox("Niveau de sujet", niveaux, index=0)
    sujets = db.get_writing_prompts(niveau)
    if not sujets:
        st.warning("Aucun sujet disponible.")
        return

    sujet_labels = [f"{s['titre']} ({s['tache_tcf']} - {s['niveau']})" for s in sujets]
    idx = st.selectbox("Sujet", list(range(len(sujet_labels))), format_func=lambda i: sujet_labels[i], index=0)
    sujet = sujets[idx]

    config = st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
        gap="small",
    )
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = get_default_model()

    api_key_serveur = get_default_api_key().strip()
    with config:
        utiliser_cle_personnelle = st.toggle("Utiliser ma cle API personnelle", value=False)
        api_key = ""
        if utiliser_cle_personnelle:
            api_key = st.text_input("Cle API OpenAI", type="password", key="openai_api_key_user")
        elif api_key_serveur:
            st.success("Cle API serveur detectee (masquee).")
        else:
            st.warning("Aucune cle API serveur configuree.")
        modele = st.text_input("Modele", key="openai_model")

    st.markdown(f"**Consigne:** {sujet['consigne']}")
    st.caption(f"Longueur cible: {sujet['min_mots']} a {sujet['max_mots']} mots.")
    texte = st.text_area("Ton texte", height=260)
    nb_mots = compter_mots(texte)
    statut_longueur = "Dans la plage"
    if nb_mots < sujet["min_mots"]:
        statut_longueur = "Trop court"
    elif nb_mots > sujet["max_mots"]:
        statut_longueur = "Trop long"

    ligne_compteur = st.container(horizontal=True, horizontal_alignment="left", gap="small")
    with ligne_compteur:
        st.metric("Nombre de mots", nb_mots)
        st.metric("Cible", f"{sujet['min_mots']}-{sujet['max_mots']}")
        st.metric("Statut", statut_longueur)

    if st.button("Corriger et noter", type="primary"):
        api_key_effective = api_key.strip() if utiliser_cle_personnelle else api_key_serveur
        if not api_key_effective:
            st.error("Renseigne une cle API OpenAI ou configure OPENAI_API_KEY sur le serveur.")
            return
        if not texte.strip():
            st.error("Ajoute un texte a corriger.")
            return

        with st.spinner("Correction en cours..."):
            try:
                evaluation, brut = corriger_redaction_avec_openai(
                    api_key=api_key_effective,
                    modele=modele.strip(),
                    tache=sujet["tache_tcf"],
                    consigne=sujet["consigne"],
                    texte=texte.strip(),
                )
            except Exception as err:
                st.error(f"Erreur API: {err}")
                return

        if not evaluation:
            st.warning("Format JSON non detecte. Reponse brute affichee.")
            st.code(brut)
            return

        st.metric("Note globale", f"{evaluation.get('note_globale_sur_20', 'N/A')}/20")
        criteres = evaluation.get("criteres", {})
        if isinstance(criteres, dict):
            ligne = st.container(horizontal=True, horizontal_alignment="left", gap="small")
            commentaires_criteres: list[tuple[str, str]] = []
            with ligne:
                for cle in ["coherence", "grammaire", "lexique", "orthographe", "registre"]:
                    valeur, commentaire = normaliser_valeur_critere(criteres.get(cle, "N/A"))
                    st.metric(cle.capitalize(), valeur)
                    if commentaire:
                        commentaires_criteres.append((cle, commentaire))
            if commentaires_criteres:
                st.subheader("Commentaires par critere")
                for critere, commentaire in commentaires_criteres:
                    st.markdown(f"**{critere.capitalize()}**: {commentaire}")

        st.subheader("Points forts")
        for point in evaluation.get("points_forts", []):
            st.markdown(f"- {point}")

        st.subheader("Erreurs prioritaires")
        erreurs = evaluation.get("erreurs_prioritaires", [])
        if not erreurs:
            st.info("Aucune erreur prioritaire.")
        for err in erreurs:
            if isinstance(err, dict):
                st.markdown(f"**Erreur:** {err.get('erreur', 'N/A')}")
                st.markdown(f"- Correction: {err.get('correction', 'N/A')}")
                st.markdown(f"- Explication: {err.get('explication', 'N/A')}")

        st.subheader("Version corrigee proposee")
        st.write(evaluation.get("version_corrigee", "Non fournie."))

        st.subheader("Conseil methode")
        st.info(evaluation.get("conseil_methode", "Non fourni."))


def afficher_comprehension_ecrite() -> None:
    st.title("Comprehension ecrite (simulation TCF)")
    st.caption("Format QCM progressif proche du TCF: questions explicites, inferentielles et lexicales.")

    niveaux = ["Tous"] + db.list_reading_levels()
    filtres = st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
        gap="small",
    )
    with filtres:
        niveau = st.selectbox("Niveau", niveaux, index=0)

    passages = db.get_reading_passages(niveau)
    if not passages:
        st.warning("Aucun texte de comprehension ecrite disponible.")
        return

    labels = [
        f"{p['titre']} ({p['niveau']} · {p['type_document']} · {p['nb_questions']} questions)"
        for p in passages
    ]
    idx = st.selectbox("Texte", list(range(len(labels))), format_func=lambda i: labels[i], index=0)
    passage = passages[idx]
    questions = db.get_reading_questions(int(passage["id"]))

    if not questions:
        st.warning("Ce texte n'a pas encore de questions associees.")
        return

    infos = st.container(horizontal=True, horizontal_alignment="left", gap="small")
    with infos:
        st.metric("Niveau", passage["niveau"])
        st.metric("Type", passage["type_document"])
        st.metric("Questions", len(questions))
        st.metric("Temps conseille", f"{passage['duree_recommandee_min']} min")

    st.markdown(f"**Contexte:** {passage['contexte']}")
    with st.container(border=True):
        st.markdown("### Texte")
        st.write(passage["texte"])

    st.subheader("Questions")
    form_key = f"form-ce-{passage['id']}"
    with st.form(form_key):
        for q in questions:
            st.markdown(f"**{q['ordre']}. {q['question']}**")
            st.caption(f"Difficulte: {q['difficulte']} · Competence: {q['competence']}")
            st.radio(
                "Choix",
                options=list(range(len(q["options"]))),
                format_func=lambda i, opts=q["options"]: opts[i],
                key=f"ce-rep-{passage['id']}-{q['id']}",
                index=None,
                label_visibility="collapsed",
            )
        corriger = st.form_submit_button("Corriger cette epreuve")

    if corriger:
        bonnes = 0
        non_repondues = 0
        for q in questions:
            rep = st.session_state.get(f"ce-rep-{passage['id']}-{q['id']}")
            if rep is None:
                non_repondues += 1
                continue
            if rep == q["answer_index"]:
                bonnes += 1

        total = len(questions)
        barreme = evaluer_barreme_ce(bonnes, total)

        st.subheader("Resultat")
        bloc = st.container(horizontal=True, horizontal_alignment="left", gap="small")
        with bloc:
            st.metric("Score brut", f"{bonnes}/{total}")
            st.metric("Pourcentage", f"{barreme['pourcentage']}%")
            st.metric("Niveau estime", barreme["niveau"])
            st.metric("Score TCF simule", f"{barreme['score_tcf_simule']}/699")

        if non_repondues:
            st.warning(f"{non_repondues} question(s) sans reponse, comptees comme fausses.")

        st.subheader("Correction detaillee")
        for q in questions:
            rep = st.session_state.get(f"ce-rep-{passage['id']}-{q['id']}")
            ok = rep == q["answer_index"]
            st.markdown(f"**{'✅' if ok else '❌'} {q['ordre']}. {q['question']}**")
            st.markdown(f"- Bonne reponse: {q['options'][q['answer_index']]}")
            if rep is None:
                st.markdown("- Ta reponse: (aucune)")
            else:
                st.markdown(f"- Ta reponse: {q['options'][rep]}")
            st.markdown(f"- Explication: {q['explication']}")


def main() -> None:
    if not verifier_base():
        return

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Section",
            [
                "Accueil",
                "Vocabulaire",
                "Grammaire",
                "Regles de grammaire",
                "Temps verbaux",
                "Conjugaison",
                "Comprehension ecrite",
                "QCM",
                "Expression ecrite",
            ],
            index=0,
        )
        st.caption("Interface en francais pour immersion TCF.")

    if page == "Accueil":
        afficher_accueil()
    elif page == "Vocabulaire":
        afficher_vocabulaire()
    elif page == "Grammaire":
        afficher_lessons_par_categorie("grammaire", "Grammaire")
    elif page == "Regles de grammaire":
        afficher_lessons_par_categorie("regles-grammaire", "Regles de grammaire")
    elif page == "Temps verbaux":
        afficher_lessons_par_categorie("temps-verbaux", "Temps verbaux")
    elif page == "Conjugaison":
        afficher_conjugaison()
    elif page == "Comprehension ecrite":
        afficher_comprehension_ecrite()
    elif page == "QCM":
        afficher_qcm()
    else:
        afficher_expression_ecrite()


if __name__ == "__main__":
    main()
