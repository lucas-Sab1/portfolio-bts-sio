document.addEventListener("DOMContentLoaded", function () {

    const container = document.getElementById("veilles-container");

    if (!container) {
        return;
    }

    const theme = container.getAttribute("data-theme");

    fetch("./data/veilles.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("Erreur HTTP " + response.status);
            }

            return response.json();
        })

        .then(data => {

            const articles = data[theme];

            if (!Array.isArray(articles) || articles.length === 0) {
                container.innerHTML = "<p>Aucune veille disponible pour le moment.</p>";
                return;
            }

            container.innerHTML = "";

            articles.forEach(article => {

                const div = document.createElement("div");

                div.style.backgroundColor = "#ffffff";
                div.style.borderRadius = "8px";
                div.style.padding = "20px";
                div.style.marginBottom = "20px";
                div.style.boxShadow = "0 4px 6px rgba(0,0,0,0.05)";
                div.style.border = "1px solid #eaeaea";

                const titre = document.createElement("h3");
                titre.style.color = "#2c3e50";
                titre.style.fontSize = "1.2rem";
                titre.style.marginTop = "0";
                titre.textContent = article.titre;

                const informations = document.createElement("p");
                informations.style.color = "#7f8c8d";
                informations.style.fontSize = "0.9rem";
                informations.style.marginBottom = "15px";
                informations.textContent = "Publié le " + article.date + " | Source : " + article.source;

                const resume = document.createElement("p");
                resume.style.color = "#34495e";
                resume.style.lineHeight = "1.5";
                resume.style.marginBottom = "15px";
                resume.textContent = article.resume;

                const lien = document.createElement("a");
                lien.href = article.lien;
                lien.target = "_blank";
                lien.rel = "noopener noreferrer";
                lien.style.color = "#3498db";
                lien.style.fontWeight = "bold";
                lien.style.textDecoration = "none";
                lien.textContent = "Lire la source ➔";

                div.appendChild(titre);
                div.appendChild(informations);
                div.appendChild(resume);
                div.appendChild(lien);

                container.appendChild(div);
            });
        })

        .catch(error => {

            console.error("Erreur lors du chargement des veilles :", error);

            container.innerHTML =
                "<p>Impossible de charger les articles de veille.</p>";
        });

});