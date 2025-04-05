document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("genres-container");

  try {
    const resGenres = await fetch("/api/genres");
    const resFavoris = await fetch("/api/genres_favoris");

    const genres = await resGenres.json();
    const favoris = await resFavoris.json();

    const favorisIds = new Set(favoris.map(g => g.genre_id));

    genres.forEach(genre => {
      const card = document.createElement("div");
      card.classList.add("genre-card");

      const title = document.createElement("h3");
      title.textContent = genre.name;

      const form = document.createElement("form");
      form.method = "POST";
      form.action = favorisIds.has(genre.genre_id)
        ? `/remove_genre_favori/${genre.genre_id}`
        : `/add_genre_favori/${genre.genre_id}`;

      const heart = document.createElement("button");
      heart.type = "submit";
      heart.innerHTML = favorisIds.has(genre.genre_id) ? "❤️" : "♡";
      heart.classList.add("like-button");
      heart.style.fontSize = "1.8rem";
      heart.style.border = "none";
      heart.style.background = "transparent";
      heart.style.cursor = "pointer";

      form.appendChild(heart);
      card.appendChild(title);
      card.appendChild(form);
      container.appendChild(card);
    });
  } catch (error) {
    console.error("❌ Impossible de charger les genres :", error);
    const msg = document.createElement("p");
    msg.textContent = "Erreur lors du chargement des genres.";
    msg.style.color = "red";
    container.appendChild(msg);
  }
});
