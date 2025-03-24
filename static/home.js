const API_KEY = "8b2f4ba709ce554aa633554c67097989";
const BASE_URL = "https://api.themoviedb.org/3";
const mediaContainer = document.getElementById("media-container");
const loadMoreBtn = document.createElement("button");
loadMoreBtn.textContent = "Charger plus";
loadMoreBtn.style.margin = "20px auto";
loadMoreBtn.style.display = "block";

const pageIndicator = document.createElement("p");
pageIndicator.style.textAlign = "center";
pageIndicator.style.marginTop = "10px";

const loadingIndicator = document.createElement("p");
loadingIndicator.textContent = "Chargement...";
loadingIndicator.style.textAlign = "center";
loadingIndicator.style.display = "none";

let currentPage = 1;
let maxPages = 5;

async function fetchPopularMedia(mediaType, page = 1) {
  try {
    loadingIndicator.style.display = "block";
    const response = await fetch(`${BASE_URL}/${mediaType}/popular?api_key=${API_KEY}&language=fr-FR&page=${page}`);
    const data = await response.json();
    const mediaList = data.results;

    mediaList.forEach(media => {
      const card = document.createElement("div");
      card.classList.add("media-card");

      const image = document.createElement("img");
      image.src = `https://image.tmdb.org/t/p/w300${media.poster_path}`;
      image.alt = media.title || media.name;

      const title = document.createElement("h3");
      title.textContent = media.title || media.name;

      const rating = document.createElement("p");
      rating.textContent = `Note (${mediaType === 'movie' ? 'Film' : 'Série'}) : ${media.vote_average.toFixed(1)}/10`;

      const form = document.createElement("form");
      form.action = `/add_favori/${media.id}`;
      form.method = "POST";

      const button = document.createElement("button");
      button.type = "submit";
      button.textContent = "Ajouter aux favoris";

      form.appendChild(button);

      card.appendChild(image);
      card.appendChild(title);
      card.appendChild(rating);
      card.appendChild(form);
      mediaContainer.appendChild(card);
    });
    loadingIndicator.style.display = "none";
  } catch (error) {
    console.error("Erreur lors de la récupération des médias :", error);
    loadingIndicator.style.display = "none";
  }
}

function loadMore() {
  if (currentPage < maxPages) {
    currentPage++;
    pageIndicator.textContent = `Page ${currentPage} sur ${maxPages}`;
    fetchPopularMedia("movie", currentPage);
    fetchPopularMedia("tv", currentPage);
  } else {
    loadMoreBtn.disabled = true;
    loadMoreBtn.textContent = "Aucune page supplémentaire";
  }
}

// Initial load
pageIndicator.textContent = `Page ${currentPage} sur ${maxPages}`;
fetchPopularMedia("movie", currentPage);
fetchPopularMedia("tv", currentPage);

document.body.appendChild(loadingIndicator);
document.body.appendChild(loadMoreBtn);
document.body.appendChild(pageIndicator);
loadMoreBtn.addEventListener("click", loadMore);
