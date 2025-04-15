CREATE DATABASE movie_serie;
USE movie_serie;

-- Table commune pour les Médias (Films et Séries)
CREATE TABLE media (
    media_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    overview TEXT,
    release_date DATE,
    vote_average DECIMAL(3, 1),
    poster_path VARCHAR(255),
    media_type ENUM('movie', 'tv') NOT NULL, -- Type du média : film ou série
    UNIQUE (title, release_date) -- Pour éviter les doublons
);



-- Table pour les Films
CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    media_id INT,
    FOREIGN KEY (media_id) REFERENCES media(media_id)
);

-- Table spécifique pour les Séries
CREATE TABLE series (
    series_id INT PRIMARY KEY,
    media_id INT,
    number_of_seasons INT,
    number_of_episodes INT,
    FOREIGN KEY (media_id) REFERENCES media(media_id)
);

-- Table pour les Saisons (exclusif aux Séries)
CREATE TABLE seasons (
    season_id INT PRIMARY KEY AUTO_INCREMENT,
    series_id INT,
    season_number INT NOT NULL,
    air_date DATE,
    episode_count INT,
    poster_path VARCHAR(255),
    FOREIGN KEY (series_id) REFERENCES series(series_id)
);

-- Table pour les Épisodes (exclusif aux Séries)
CREATE TABLE episodes (
    episode_id INT PRIMARY KEY AUTO_INCREMENT,
    season_id INT,
    episode_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    overview TEXT,
    air_date DATE,
    vote_average DECIMAL(3, 1),
    FOREIGN KEY (season_id) REFERENCES seasons(season_id)
);

-- Table pour les Genres
CREATE TABLE genres (
    genre_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Table de liaison Media-Genres (Many-to-Many)
CREATE TABLE media_to_genres (
    media_id INT,
    genre_id INT,
    PRIMARY KEY (media_id, genre_id),
    FOREIGN KEY (media_id) REFERENCES media(media_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Table pour le Casting
CREATE TABLE actors (
    cast_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    character_name VARCHAR(100),
    profile_path VARCHAR(255)
);


-- Table de liaison Media-Casting/actors (Many-to-Many)
CREATE TABLE media_to_cast (
    media_id INT,
    cast_id INT,
    PRIMARY KEY (media_id, cast_id),
    FOREIGN KEY (media_id) REFERENCES media(media_id),
    FOREIGN KEY (cast_id) REFERENCES actors(cast_id)
);

-- Table des Utilisateurs
CREATE TABLE users (
    user_id INTEGER AUTO_INCREMENT PRIMARY KEY ,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL CHECK (email LIKE '%@gmail.com'),
    password_hash VARCHAR(255) NOT NULL,
    CONSTRAINT check_password_length CHECK (LENGTH(password_hash) >= 8)
);

-- Table des Favoris (relation Many-to-Many)
CREATE TABLE favorites (
    user_id INT,
    media_id INT,
    PRIMARY KEY (user_id, media_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE NO ACTION,
    FOREIGN KEY (media_id) REFERENCES media(media_id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE TABLE genre_favorites (
    user_id INT,
    genre_id INT,
    PRIMARY KEY (user_id, genre_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE);


-- Indexation pour améliorer les performances:
#1 - Pour accélérer les jointures favorites/media
CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_media ON favorites(media_id);

#2 - Pour les jointures genre_favorites
CREATE INDEX idx_genre_fav_user ON genre_favorites(user_id);
CREATE INDEX idx_genre_fav_genre ON genre_favorites(genre_id);

#3 - Pour filtrer rapidement sur type de média
CREATE INDEX idx_media_type ON media(media_type);

#4 - Pour optimiser les filtres sur les notes
CREATE INDEX idx_vote_average ON media(vote_average);

#5 - Pour les tris/recherches par date
CREATE INDEX idx_release_date ON media(release_date);
#Test index :
SHOW INDEX FROM favorites;
SHOW INDEX FROM media;
SHOW INDEX FROM genre_favorites;

#Visualisation des tables
select * From favorites;
select * From users;
select * From genre_favorites;
select * From genres;
select * From media_to_genres;
select * From media;
select * From series;
select * From seasons;
select * From episodes;

#Requêtes SQL
#1- Liste des genres les plus populaires (selon les favoris des utilisateurs)
SELECT g.name AS genre, COUNT(*) AS total_favoris
FROM genre_favorites gf
JOIN genres g ON gf.genre_id = g.genre_id
GROUP BY g.genre_id
ORDER BY total_favoris DESC;

#2- Films ou séries les mieux notés par type
SELECT media_type, title, vote_average
FROM media
WHERE vote_average IS NOT NULL
ORDER BY vote_average DESC
LIMIT 10;

#3- Nombre de favoris par utilisateur
SELECT u.username, COUNT(f.media_id) AS total_favoris
FROM users u
LEFT JOIN favorites f ON u.user_id = f.user_id
GROUP BY u.user_id
ORDER BY total_favoris DESC;

#4- Utilisateurs n’ayant aucun favori
SELECT u.username
FROM users u
LEFT JOIN favorites f ON u.user_id = f.user_id
WHERE f.media_id IS NULL;

#Trigger :  Mettre à jour un champ last_favori_ad dans la table users quand un favori est ajouté
ALTER TABLE users ADD COLUMN last_favori_add DATETIME;

DELIMITER //
CREATE TRIGGER update_last_favori
AFTER INSERT ON favorites
FOR EACH ROW
BEGIN
    UPDATE users
    SET last_favori_add = NOW()
    WHERE user_id = NEW.user_id;
END;
//
DELIMITER ;

DELIMITER //

#Procédure stockée qui retourne tous les favoris d’un utilisateur
DELIMITER //
CREATE PROCEDURE NomDesFavorisUser(IN uid INT)
BEGIN
    SELECT m.media_id, m.title, m.vote_average, m.poster_path
    FROM favorites f
    JOIN media m ON f.media_id = m.media_id
    WHERE f.user_id = uid;
END;
//
DELIMITER ;
CALL NomDesFavorisUser(8); #utiliisation de la procédure

#Fonction qui calcule la note moyenne (vote_average) de tous les médias favoris d’un utilisateur
DELIMITER //

CREATE FUNCTION AverageRatingOfUserFavorites(uid INT)
RETURNS DECIMAL(3,1)
DETERMINISTIC
READS SQL DATA
BEGIN
  DECLARE avg_rating DECIMAL(3,1);

  SELECT AVG(m.vote_average)
  INTO avg_rating
  FROM favorites f
  JOIN media m ON f.media_id = m.media_id
  WHERE f.user_id = uid;

  RETURN avg_rating;
END;
//

DELIMITER ;
SELECT AverageRatingOfUserFavorites(8) AS moyenne_favoris;









