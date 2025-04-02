//  Fonction pour ajouter aux favoris
function createFavoriForm(mediaId) {
  const form = document.createElement("form");
  form.action = `/add_favori/${mediaId}`;
  form.method = "POST";

  const button = document.createElement("button");
  button.type = "submit";
  button.textContent = "Ajouter aux favoris";
  button.classList.add("favori-btn");

  form.appendChild(button);
  return form;
}


const API_KEY = "8b2f4ba709ce554aa633554c67097989";
const BASE_URL = "https://api.themoviedb.org/3";
const seriesContainer = document.getElementById("series-container");
const loadMoreBtn = document.createElement("button");
loadMoreBtn.textContent = "Charger plus de séries";
loadMoreBtn.style.margin = "20px auto";
loadMoreBtn.style.display = "block";

const pageIndicator = document.createElement("p");
pageIndicator.style.textAlign = "center";
pageIndicator.style.marginTop = "10px";

const loadingIndicator = document.createElement("p");
loadingIndicator.textContent = "Chargement des séries...";
loadingIndicator.style.textAlign = "center";
loadingIndicator.style.display = "none";

let currentPage = 1;
let maxPages = 5;

async function fetchPopularSeries(page = 1) {
  try {
    loadingIndicator.style.display = "block";
    const response = await fetch(`${BASE_URL}/tv/popular?api_key=${API_KEY}&language=fr-FR&page=${page}`);
    const data = await response.json();
    const seriesList = data.results;

    seriesList.forEach(serie => {
      const card = document.createElement("div");
      card.classList.add("media-card");

      const image = document.createElement("img");
      image.src = `https://image.tmdb.org/t/p/w300${serie.poster_path}`;
      image.alt = serie.name;

      const title = document.createElement("h3");
      title.textContent = serie.name;

      const rating = document.createElement("p");
      rating.textContent = `Note : ${serie.vote_average.toFixed(1)}/10`;

      const form = document.createElement("form");
      form.action = `/add_favori/${serie.id}`;
      form.method = "POST";

      const button = document.createElement("button");
      button.type = "submit";
      button.textContent = "Ajouter aux favoris";

      form.appendChild(button);

      card.appendChild(image);
      card.appendChild(title);
      card.appendChild(rating);
      card.appendChild(form);
      seriesContainer.appendChild(card);
    });
    loadingIndicator.style.display = "none";
  } catch (error) {
    console.error("Erreur lors de la récupération des séries :", error);
    loadingIndicator.style.display = "none";
  }
}

function loadMoreSeries() {
  if (currentPage < maxPages) {
    currentPage++;
    pageIndicator.textContent = `Page ${currentPage} sur ${maxPages}`;
    fetchPopularSeries(currentPage);
  } else {
    loadMoreBtn.disabled = true;
    loadMoreBtn.textContent = "Aucune page supplémentaire";
  }
}

// Initial load
pageIndicator.textContent = `Page ${currentPage} sur ${maxPages}`;
fetchPopularSeries(currentPage);

document.body.appendChild(loadingIndicator);
document.body.appendChild(loadMoreBtn);
document.body.appendChild(pageIndicator);
loadMoreBtn.addEventListener("click", loadMoreSeries);
