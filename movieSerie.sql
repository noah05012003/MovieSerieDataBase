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
    media_type ENUM('movie', 'series') NOT NULL, -- Type du média : film ou série
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


-- Indexation pour améliorer les performances:

-- Fonction à faire :



