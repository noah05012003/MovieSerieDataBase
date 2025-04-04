const API_KEY = "8b2f4ba709ce554aa633554c67097989";
const BASE_URL = "https://api.themoviedb.org/3";
const genreContainer = document.getElementById("genres-container");

async function fetchGenres(mediaType) {
  try {
    const response = await fetch(`${BASE_URL}/genre/${mediaType}/list?api_key=${API_KEY}&language=fr-FR`);
    const data = await response.json();
    const genres = data.genres;

    genres.forEach(genre => {
      // Création de la carte
      const card = document.createElement("div");
      card.classList.add("genre-card", "media-card");

      // Titre du genre
      const title = document.createElement("h3");
      title.textContent = genre.name;

      // Création du formulaire pour la logique "favori"
      const form = document.createElement("form");
      form.action = `/add_genre_favori/${genre.id}`;
      form.method = "POST";

      // Création de l'icône cœur
      const heart = document.createElement("span");
      heart.innerHTML = "&#9825;"; // Cœur vide (♡)
      heart.classList.add("like-button");
      heart.dataset.liked = "false";

      // Logique de basculement du cœur
      heart.addEventListener("click", function(e) {
        e.preventDefault();
        const liked = heart.dataset.liked === "true";
        heart.innerHTML = liked ? "&#9825;" : "&#10084;"; // Passe de ♡ à ❤️
        heart.style.color = liked ? "#fff" : "red";
        heart.dataset.liked = liked ? "false" : "true";
        // Pour soumettre réellement le formulaire, décommente la ligne suivante :
        // form.submit();
      });

      form.appendChild(heart);
      card.appendChild(title);
      card.appendChild(form);
      genreContainer.appendChild(card);
    });
  } catch (error) {
    console.error("Erreur lors de la récupération des genres :", error);
  }
}

// Charger les genres pour "movie" et "tv"
fetchGenres("movie");
fetchGenres("tv");
