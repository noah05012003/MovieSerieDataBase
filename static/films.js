const API_KEY = "8b2f4ba709ce554aa633554c67097989";
const BASE_URL = "https://api.themoviedb.org/3";
const filmsContainer = document.getElementById("films-container");
// Use the pagination container already in your HTML
const paginationControls = document.getElementById("pagination-controls");

const loadMoreBtn = document.createElement("button");
loadMoreBtn.textContent = "Charger plus de films";
loadMoreBtn.classList.add("load-more-btn");

const pageIndicator = document.createElement("p");
pageIndicator.classList.add("page-info");

const loadingIndicator = document.createElement("p");
loadingIndicator.textContent = "Chargement des films...";
loadingIndicator.style.textAlign = "center";
loadingIndicator.style.display = "none";

let currentPage = 1;
let maxPages = 5;

async function fetchPopularMovies(page = 1) {
  try {
    loadingIndicator.style.display = "block";
    const response = await fetch(`${BASE_URL}/movie/popular?api_key=${API_KEY}&language=fr-FR&page=${page}`);
    const data = await response.json();
    const movies = data.results;

    movies.forEach(movie => {
      const card = document.createElement("div");
      card.classList.add("media-card");

      const image = document.createElement("img");
      image.src = `https://image.tmdb.org/t/p/w300${movie.poster_path}`;
      image.alt = movie.title;

      const title = document.createElement("h3");
      title.textContent = movie.title;

      const rating = document.createElement("p");
      rating.textContent = `Note (Film) : ${movie.vote_average.toFixed(1)}/10`;

      // Create the favori form using the favori-btn class for styling
      const form = document.createElement("form");
      form.action = `/add_favori/${movie.id}`;
      form.method = "POST";

      const button = document.createElement("button");
      button.type = "submit";
      button.textContent = "Ajouter aux favoris";
      button.classList.add("favori-btn");

      form.appendChild(button);

      card.appendChild(image);
      card.appendChild(title);
      card.appendChild(rating);
      card.appendChild(form);
      filmsContainer.appendChild(card);
    });
    loadingIndicator.style.display = "none";
  } catch (error) {
    console.error("Erreur lors de la récupération des films :", error);
    loadingIndicator.style.display = "none";
  }
}

function loadMoreMovies() {
  if (currentPage < maxPages) {
    currentPage++;
    pageIndicator.textContent = `Page ${currentPage} sur ${maxPages}`;
    fetchPopularMovies(currentPage);
  } else {
    loadMoreBtn.disabled = true;
    loadMoreBtn.textContent = "Aucune page supplémentaire";
  }
}

// Initial load
pageIndicator.textContent = `Page ${currentPage} sur ${maxPages}`;
fetchPopularMovies(currentPage);

// Append the controls to the pagination container (inside <main>)
paginationControls.appendChild(loadingIndicator);
paginationControls.appendChild(loadMoreBtn);
paginationControls.appendChild(pageIndicator);

loadMoreBtn.addEventListener("click", loadMoreMovies);
