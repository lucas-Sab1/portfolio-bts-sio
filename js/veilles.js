function chargerVeilles() {
    // 1. On cherche la zone où afficher les veilles
    const container = document.getElementById("veilles-container");
    if (!container) return; // Si on n'est pas sur une page de veille, on arrête le script

    // 2. On regarde quel thème est demandé sur la page (cybersecurite ou identite_numerique)
    const theme = container.getAttribute("data-theme");

    // 3. On va chercher le fichier de données
    fetch('./data/veilles.json')
        .then(response => {
            if (!response.ok) {
                throw new Error("Erreur lors du chargement du fichier JSON : " + response.status);
            }
            return response.json();
        })
        .then(data => {
            const articles = data[theme];
            container.innerHTML = ""; // On vide le message "Chargement..."

            if (!articles || articles.length === 0) {
                container.innerHTML = "<p>Aucune veille disponible pour le moment.</p>";
                return;
            }

            // 4. Pour chaque article dans le JSON, on crée un bloc HTML
            articles.forEach(article => {
                const div = document.createElement("div");
                div.style.backgroundColor = "#ffffff";
                div.style.borderRadius = "8px";
                div.style.padding = "20px";
                div.style.marginBottom = "20px";
                div.style.boxShadow = "0 4px 6px rgba(0,0,0,0.05)";
                div.style.border = "1px solid #eaeaea";

                div.innerHTML = `
                    <h3 style="color:#2c3e50; font-size: 1.2rem; margin-top:0;">${article.titre}</h3>
                    <p style="color:#7f8c8d; font-size: 0.9rem; margin-bottom: 15px;">
                        Publié le ${article.date} | Source : <strong>${article.source}</strong>
                    </p>
                    <p style="color:#34495e; line-height: 1.5; margin-bottom: 15px;">${article.resume}</p>
                    <a href="${article.lien}" target="_blank" rel="noopener noreferrer" style="color:#3498db; font-weight:bold; text-decoration:none;">Lire la source ➔</a>
                `;
                container.appendChild(div);
            });
        })
        .catch(error => {
            console.error("Erreur:", error);
            container.innerHTML = "<p style='color:red;'>Erreur lors du chargement des veilles. Vérifiez la console.</p>";
        });
}

// Exécution immédiate si le DOM est déjà prêt, sinon écoute de l'événement
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", chargerVeilles);
} else {
    chargerVeilles();
}