document.addEventListener("DOMContentLoaded", function () {

    // Zone où afficher les veilles
    const container = document.getElementById("veilles-container");

    // Si la page ne contient pas de zone de veille, on arrête le script.
    if (!container) {
        return;
    }

    // Thème demandé par la page :
    // cybersecurite ou identite_numerique
    const theme = container.getAttribute("data-theme");

    // Chargement du fichier JSON
    fetch("./data/veilles.json")
        .then(function (response) {

            if (!response.ok) {
                throw new Error(
                    "Impossible de charger data/veilles.json"
                );
            }

            return response.json();
        })

        .then(function (data) {

            const articles = data[theme];

            // On vide le message "Chargement..."
            container.innerHTML = "";

            if (!articles || articles.length === 0) {

                container.innerHTML =
                    "<p>Aucune veille disponible pour le moment.</p>";

                return;
            }

            // Création de chaque article
            articles.forEach(function (article) {

                const div = document.createElement("div");

                div.style.backgroundColor = "#ffffff";
                div.style.borderRadius = "8px";
                div.style.padding = "20px";
                div.style.marginBottom = "20px";
                div.style.boxShadow =
                    "0 4px 6px rgba(0,0,0,0.05)";
                div.style.border = "1px solid #eaeaea";

                // Création du titre
                const titre = document.createElement("h3");

                titre.style.color = "#2c3e50";
                titre.style.fontSize = "1.2rem";
                titre.style.marginTop = "0";
                titre.textContent = article.titre;

                // Informations de publication
                const informations = document.createElement("p");

                informations.style.color = "#7f8c8d";
                informations.style.fontSize = "0.9rem";
                informations.style.marginBottom = "15px";

                informations.textContent =
                    "Publié le " +
                    article.date +
                    " | Source : " +
                    article.source;

                // Résumé
                const resume = document.createElement("p");

                resume.style.color = "#34495e";
                resume.style.lineHeight = "1.5";
                resume.style.marginBottom = "15px";
                resume.textContent = article.resume;

                // Analyse
                const analyse = document.createElement("p");

                analyse.style.color = "#34495e";
                analyse.style.lineHeight = "1.5";
                analyse.style.marginBottom = "15px";

                if (article.analyse) {

                    const titreAnalyse =
                        document.createElement("strong");

                    titreAnalyse.textContent = "Mon analyse : ";

                    analyse.appendChild(titreAnalyse);

                    analyse.appendChild(
                        document.createTextNode(article.analyse)
                    );
                }

                // Lien vers la source
                const lien = document.createElement("a");

                lien.href = article.lien;
                lien.target = "_blank";
                lien.rel = "noopener noreferrer";

                lien.style.color = "#3498db";
                lien.style.fontWeight = "bold";
                lien.style.textDecoration = "none";

                lien.textContent = "Lire la source ➔";

                // Assemblage
                div.appendChild(titre);
                div.appendChild(informations);
                div.appendChild(resume);

                if (article.analyse) {
                    div.appendChild(analyse);
                }

                div.appendChild(lien);

                container.appendChild(div);
            });
        })

        .catch(function (error) {

            console.error(
                "Erreur lors du chargement des veilles :",
                error
            );

            container.innerHTML =
                "<p style='color:red;'>" +
                "Erreur lors du chargement des veilles. " +
                "Vérifiez la console du navigateur." +
                "</p>";
        });
});