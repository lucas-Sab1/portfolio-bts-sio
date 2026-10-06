import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET


FEEDS = {
    "cybersecurite": "https://www.cert.ssi.gouv.fr/feed/",
    "identite_numerique": "https://www.cnil.fr/fr/rss.xml"
}

JSON_PATH = "data/veilles.json"


def charger_json():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "cybersecurite": [],
        "identite_numerique": []
    }


def sauvegarder_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def nettoyer_texte(texte):
    if not texte:
        return ""

    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()


def recuperer_rss(url, theme):
    requete = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(requete, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    items = root.findall(".//item")

    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    if not items:
        raise ValueError("Aucun article trouvé dans le flux RSS/Atom.")

    articles = []

    for item in items[:5]:

        titre_element = item.find("title")

        if titre_element is None:
            titre_element = item.find("{http://www.w3.org/2005/Atom}title")

        titre = (
            titre_element.text.strip()
            if titre_element is not None and titre_element.text
            else "Sans titre"
        )

        lien = ""

        lien_element = item.find("link")

        if lien_element is not None:
            lien = lien_element.text or lien_element.get("href", "")

        if not lien:
            lien_element = item.find("{http://www.w3.org/2005/Atom}link")

            if lien_element is not None:
                lien = lien_element.get("href", "") or lien_element.text or ""

        date_element = item.find("pubDate")

        if date_element is None:
            date_element = item.find("published")

        if date_element is None:
            date_element = item.find("updated")

        if date_element is None:
            date_element = item.find("{http://www.w3.org/2005/Atom}published")

        if date_element is None:
            date_element = item.find("{http://www.w3.org/2005/Atom}updated")

        date = (
            date_element.text.strip()
            if date_element is not None and date_element.text
            else ""
        )

        description_element = item.find("description")

        if description_element is None:
            description_element = item.find("summary")

        if description_element is None:
            description_element = item.find("{http://www.w3.org/2005/Atom}summary")

        description = (
            description_element.text
            if description_element is not None
            else "Pas de résumé disponible."
        )

        description = nettoyer_texte(description)

        if len(description) > 250:
            description = description[:250] + "..."

        source = (
            "CERT-FR (ANSSI)"
            if theme == "cybersecurite"
            else "CNIL"
        )

        articles.append({
            "titre": titre,
            "date": date,
            "source": source,
            "lien": lien.strip(),
            "resume": description
        })

    return articles


def main():
    data = charger_json()

    erreurs = []

    for theme, url in FEEDS.items():

        try:
            nouveaux_articles = recuperer_rss(url, theme)

            if theme not in data:
                data[theme] = []

            liens_existants = {
                article.get("lien")
                for article in data[theme]
            }

            for article in nouveaux_articles:

                if article["lien"] and article["lien"] not in liens_existants:
                    data[theme].insert(0, article)

        except Exception as erreur:
            erreurs.append(
                f"{theme} : {erreur}"
            )

    sauvegarder_json(data)

    if erreurs:
        for erreur in erreurs:
            print(erreur)

        raise RuntimeError(
            "La récupération d'au moins un flux a échoué."
        )


if __name__ == "__main__":
    main()