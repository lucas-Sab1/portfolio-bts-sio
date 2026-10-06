import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape


FEEDS = {
    "cybersecurite": [
        "https://www.cert.ssi.gouv.fr/actualite/feed/",
        "https://cyber.gouv.fr/actualites"
    ],
    "identite_numerique": [
        "https://www.cnil.fr/fr/rss.xml"
    ]
}

JSON_PATH = "data/veilles.json"

MAX_ARTICLES = 5


# ---------------------------------------------------------
# CHARGEMENT / SAUVEGARDE DU JSON
# ---------------------------------------------------------

def charger_json():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as fichier:
            data = json.load(fichier)
    else:
        data = {}

    data.setdefault("cybersecurite", [])
    data.setdefault("identite_numerique", [])

    return data


def sauvegarder_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as fichier:
        json.dump(data, fichier, ensure_ascii=False, indent=2)


# ---------------------------------------------------------
# NETTOYAGE DES TEXTES
# ---------------------------------------------------------

def nettoyer_texte(texte):
    if not texte:
        return ""

    texte = unescape(texte)
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()


# ---------------------------------------------------------
# REQUÊTE HTTP
# ---------------------------------------------------------

def telecharger(url):
    requete = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; VeillePortfolio/1.0)"
        }
    )

    with urllib.request.urlopen(requete, timeout=30) as reponse:
        return reponse.read()


# ---------------------------------------------------------
# EXTRACTION RSS / ATOM
# ---------------------------------------------------------

def recuperer_articles(url):
    contenu = telecharger(url)
    root = ET.fromstring(contenu)

    articles = []

    # Flux RSS classique
    items = root.findall(".//item")

    # Flux Atom
    if not items:
        items = root.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        )

    for item in items:
        titre = ""

        titre_element = item.find("title")

        if titre_element is None:
            titre_element = item.find(
                "{http://www.w3.org/2005/Atom}title"
            )

        if titre_element is not None and titre_element.text:
            titre = nettoyer_texte(titre_element.text)

        # -------------------------------------------------
        # LIEN
        # -------------------------------------------------

        lien = ""

        lien_element = item.find("link")

        if lien_element is not None:
            lien = (
                lien_element.text
                or lien_element.get("href", "")
                or ""
            )

        if not lien:
            lien_element = item.find(
                "{http://www.w3.org/2005/Atom}link"
            )

            if lien_element is not None:
                lien = (
                    lien_element.get("href", "")
                    or lien_element.text
                    or ""
                )

        lien = lien.strip()

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        date = ""

        for nom in [
            "pubDate",
            "published",
            "updated"
        ]:
            element = item.find(nom)

            if element is not None and element.text:
                date = element.text.strip()
                break

        if not date:
            for nom in [
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated"
            ]:
                element = item.find(nom)

                if element is not None and element.text:
                    date = element.text.strip()
                    break

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        description = ""

        for nom in [
            "description",
            "summary",
            "content"
        ]:
            element = item.find(nom)

            if element is not None and element.text:
                description = element.text
                break

        if not description:
            for nom in [
                "{http://www.w3.org/2005/Atom}summary",
                "{http://www.w3.org/2005/Atom}content"
            ]:
                element = item.find(nom)

                if element is not None and element.text:
                    description = element.text
                    break

        description = nettoyer_texte(description)

        if titre and lien:
            articles.append({
                "titre": titre,
                "date": date,
                "lien": lien,
                "description": description
            })

    return articles


# ---------------------------------------------------------
# FILTRAGE CYBERSÉCURITÉ
# ---------------------------------------------------------

MOTS_CLES_CYBER = [
    "cybersécurité",
    "cyberattaque",
    "cyberattaque",
    "cybermenace",
    "ransomware",
    "rançongiciel",
    "sécurité",
    "attaque",
    "incident",
    "piratage",
    "hameçonnage",
    "phishing",
    "intelligence artificielle",
    "ia",
    "cloud",
    "réseau",
    "infrastructure",
    "cryptographie",
    "post-quantique",
    "cyber resilience",
    "résilience",
    "cyber résilience",
    "sécurité informatique",
    "vulnérabilité"
]


MOTS_A_EXCLURE_CYBER = [
    "ordre du jour",
    "séance plénière",
    "avis de recrutement",
    "recrutement",
    "appel d'offres",
    "marché public",
    "vacance",
    "nomination"
]


# ---------------------------------------------------------
# FILTRAGE IDENTITÉ NUMÉRIQUE
# ---------------------------------------------------------

MOTS_CLES_IDENTITE = [
    "identité numérique",
    "identite numérique",
    "identification",
    "authentification",
    "authentification multifacteur",
    "multi-facteur",
    "multifacteur",
    "france identité",
    "franceidentité",
    "identité européenne",
    "portefeuille européen",
    "eidas",
    "eidas 2",
    "usurpation d'identité",
    "usurpation",
    "données personnelles",
    "protection des données",
    "biométrie",
    "reconnaissance faciale",
    "compte utilisateur",
    "mot de passe",
    "double authentification",
    "rgpd",
    "traçage",
    "cookies",
    "vie privée",
    "cybersécurité"
]


MOTS_A_EXCLURE_IDENTITE = [
    "ordre du jour",
    "séance plénière",
    "délibération",
    "délibérations",
    "avis de recrutement",
    "recrutement",
    "appel d'offres",
    "marché public",
    "vacance",
    "nomination"
]


# ---------------------------------------------------------
# CALCUL DE PERTINENCE
# ---------------------------------------------------------

def calculer_score(article, theme):
    texte = (
        article["titre"]
        + " "
        + article["description"]
    ).lower()

    if theme == "cybersecurite":
        mots_cles = MOTS_CLES_CYBER
        mots_exclus = MOTS_A_EXCLURE_CYBER

    else:
        mots_cles = MOTS_CLES_IDENTITE
        mots_exclus = MOTS_A_EXCLURE_IDENTITE

    score = 0

    # Les mots présents dans le titre comptent davantage.
    titre = article["titre"].lower()

    for mot in mots_cles:
        if mot in titre:
            score += 5
        elif mot in texte:
            score += 2

    # On pénalise fortement les contenus administratifs.
    for mot in mots_exclus:
        if mot in texte:
            score -= 10

    return score


# ---------------------------------------------------------
# CRÉATION D'UNE VEILLE
# ---------------------------------------------------------

def transformer_article(article, theme):
    if theme == "cybersecurite":
        source = "CERT-FR / ANSSI"
        analyse = (
            "Cette actualité est intéressante dans le cadre de ma veille "
            "car elle permet de suivre l'évolution des menaces, des "
            "techniques d'attaque et des moyens de protection des "
            "systèmes d'information."
        )
    else:
        source = "CNIL"
        analyse = (
            "Cette actualité est intéressante dans le cadre de ma veille "
            "car elle permet de suivre les évolutions liées à l'identité "
            "numérique, à l'authentification et à la protection des "
            "données personnelles."
        )

    resume = article["description"]

    if not resume:
        resume = (
            "Cette publication présente une actualité récente en lien "
            "avec le thème de cette veille technologique."
        )

    # On évite les résumés excessivement longs.
    if len(resume) > 400:
        resume = resume[:400].rsplit(" ", 1)[0] + "..."

    return {
        "titre": article["titre"],
        "date": article["date"],
        "source": source,
        "lien": article["lien"],
        "resume": resume,
        "analyse": analyse
    }


# ---------------------------------------------------------
# TRAITEMENT D'UN THÈME
# ---------------------------------------------------------

def traiter_theme(theme, urls, data):
    candidats = []

    for url in urls:
        try:
            articles = recuperer_articles(url)

            for article in articles:
                score = calculer_score(article, theme)

                if score > 0:
                    article["score"] = score
                    candidats.append(article)

        except Exception as erreur:
            print(
                f"Impossible de récupérer le flux {url} : {erreur}"
            )

    # Tri par pertinence
    candidats.sort(
        key=lambda article: article.get("score", 0),
        reverse=True
    )

    # Suppression des doublons
    articles_uniques = []
    liens = set()

    for article in candidats:
        if article["lien"] not in liens:
            liens.add(article["lien"])
            articles_uniques.append(article)

    # On conserve les plus pertinents.
    nouveaux = articles_uniques[:MAX_ARTICLES]

    # On conserve également les anciennes veilles déjà présentes.
    anciennes = data.get(theme, [])

    liens_existants = {
        article.get("lien")
        for article in anciennes
    }

    for article in reversed(nouveaux):
        if article["lien"] not in liens_existants:
            anciennes.insert(
                0,
                transformer_article(article, theme)
            )

    # On limite la quantité affichée dans le JSON.
    data[theme] = anciennes[:MAX_ARTICLES]


# ---------------------------------------------------------
# PROGRAMME PRINCIPAL
# ---------------------------------------------------------

def main():
    data = charger_json()

    erreurs = []

    for theme, urls in FEEDS.items():
        try:
            traiter_theme(theme, urls, data)

        except Exception as erreur:
            erreurs.append(
                f"{theme} : {erreur}"
            )

    sauvegarder_json(data)

    if erreurs:
        for erreur in erreurs:
            print(erreur)

        raise RuntimeError(
            "La mise à jour d'au moins une veille a échoué."
        )


if __name__ == "__main__":
    main()