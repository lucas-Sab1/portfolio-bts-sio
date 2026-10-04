// 1. On sélectionne le bouton burger et la liste des liens dans la page
const burger = document.querySelector('.burger');
const navLinks = document.querySelector('.nav-links');

// 2. On ajoute un "écouteur d'événement" qui réagit au clic sur le bouton
burger.addEventListener('click', () => {
    // 3. À chaque clic, on ajoute ou on enlève la classe "active" sur le menu
    navLinks.classList.toggle('active');
});