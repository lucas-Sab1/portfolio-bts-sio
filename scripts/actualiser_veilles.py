import json
import os
import xml.etree.ElementTree as ET
import urllib.request

# Flux RSS officiels sélectionnés
FEEDS = {
    "cybersecurite": "https://www.cert.ssi.gouv.fr/feed/",  # CERT-FR (ANSSI)
    "identite_numerique": "https://www.cnil.fr/fr/rss.xml"   # CNIL
}

JSON_PATH = "data/veilles.json"

def charger_json():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"cybersecurite": [], "identite_numerique": []}

def sauvegarder_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def recuperer_rss(url, theme):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        xml_data = response.read()
    
    root = ET.fromstring(xml_data)
    articles = []
    
    # Parcours des 5 derniers articles du flux RSS
    for item in root.findall(".//item")[:5]:
        titre = item.find("title").text if item.find("title") is not None else "Sans titre"
        lien = item.find("link").text if item.find("link") is not None else "#"
        date = item.find("pubDate").text if item.find("pubDate") is not None else ""
        description = item.find("description").text if item.find("description") is not None else "Pas de résumé disponible."
        
        # Nettoyage sommaire des balises HTML dans les descriptions
        clean_desc = description.replace("<p>", "").replace("</p>", "").strip()
        
        articles.append({
            "titre": titre.strip(),
            "date": date.strip()[:16] if date else "2026",
            "source": "CERT-FR (ANSSI)" if theme == "cybersecurite" else "CNIL",
            "lien": lien.strip(),
            "resume": clean_desc[:250] + "..." if len(clean_desc) > 250 else clean_desc
        })
    return articles

def main():
    data = charger_json()
    
    for theme, url in FEEDS.items():
        try:
            nouveaux = recuperer_rss(url, theme)
            liens_existants = {a["lien"] for a in data.get(theme, [])}
            
            for art in nouveaux:
                if art["lien"] not in liens_existants:
                    data[theme].insert(0, art)  # Ajoute l'article en haut de liste
        except Exception as e:
            print(f"Erreur lors de la récupération du flux {theme}: {e}")

    sauvegarder_json(data)

if __name__ == "__main__":
    main()