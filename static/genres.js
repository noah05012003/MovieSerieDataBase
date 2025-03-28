const API_KEY = "8b2f4ba709ce554aa633554c67097989";
const BASE_URL = "https://api.themoviedb.org/3";
const genreContainer = document.getElementById("genres-container");

async function fetchGenres(mediaType) {
  try {
    const response = await fetch(`${BASE_URL}/genre/${mediaType}/list?api_key=${API_KEY}&language=fr-FR`);
    const data = await response.json();
    const genres = data.genres;

    genres.forEach(genre => {
      const card = document.createElement("div");
      card.classList.add("media-card");

      const title = document.createElement("h3");
      title.textContent = genre.name;

      const form = document.createElement("form");
      form.action = `/add_genre_favori/${genre.id}`;
      form.method = "POST";

      const button = document.createElement("button");
      button.type = "submit";
      button.textContent = "Ajouter aux favoris";

      form.appendChild(button);
      card.appendChild(title);
      card.appendChild(form);
      genreContainer.appendChild(card);
    });
  } catch (error) {
    console.error("Erreur lors de la récupération des genres :", error);
  }
}

// Charger genres films et series
fetchGenres("movie");
fetchGenres("tv");