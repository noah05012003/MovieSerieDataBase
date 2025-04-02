document.addEventListener("DOMContentLoaded", () => {
  const favorisContainer = document.getElementById("favoris-container");

  function createRemoveFavoriForm(mediaId) {
    const form = document.createElement("form");
    form.action = `/remove_favori/${mediaId}`;
    form.method = "POST";

    const button = document.createElement("button");
    button.type = "submit";
    button.textContent = "Retirer des favoris";
    button.classList.add("favori-btn");

    form.appendChild(button);
    return form;
  }

  async function fetchFavoris() {
    try {
      const response = await fetch("/api/favoris");
      const data = await response.json();

      if (data.length === 0) {
        const emptyMsg = document.createElement("p");
        emptyMsg.textContent = "Vous n'avez encore ajouté aucun favori.";
        emptyMsg.style.textAlign = "center";
        emptyMsg.style.fontSize = "1.2rem";
        emptyMsg.style.color = "#ccc";
        favorisContainer.appendChild(emptyMsg);
        return;
      }

      data.forEach(media => {
        if (!media.title || !media.poster_path) return; // ⛔️ Skip si info manquante

        const card = document.createElement("div");
        card.classList.add("media-card");

        const image = document.createElement("img");
        image.src = `https://image.tmdb.org/t/p/w300${media.poster_path}`;
        image.alt = media.title;

        const title = document.createElement("h3");
        title.textContent = media.title;

        const rating = document.createElement("p");
        const note = typeof media.vote_average === "number"
          ? media.vote_average.toFixed(1)
          : "N/A";
        rating.textContent = `Note : ${note}/10`;

        const form = createRemoveFavoriForm(media.media_id);

        card.appendChild(image);
        card.appendChild(title);
        card.appendChild(rating);
        card.appendChild(form);
        favorisContainer.appendChild(card);
      });
    } catch (error) {
      console.error("Erreur lors du chargement des favoris:", error);
      const errorMsg = document.createElement("p");
      errorMsg.textContent = "Erreur lors du chargement des favoris.";
      errorMsg.style.color = "red";
      favorisContainer.appendChild(errorMsg);
    }
  }

  fetchFavoris();
});
