import requests
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv('security.env')

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


cnx = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME')
)
cursor = cnx.cursor()

# -------------------------------
# 1. Insérer les Médias (Films et Séries)
# -------------------------------
def fetch_and_insert_media(media_type):
    db_media_type = "tv" if media_type == "tv" else "movie"
    url = f"{BASE_URL}/{media_type}/popular?api_key={API_KEY}&language=fr-FR"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()['results']
        for item in data:
            media_id = item['id']
            title = item.get('title') or item.get('name')
            overview = item['overview']
            release_date = item.get('release_date') or item.get('first_air_date')
            vote_average = item['vote_average']
            poster_path = item['poster_path']

            query = """
            INSERT INTO media (media_id, title, overview, release_date, vote_average, poster_path, media_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=VALUES(title);
            """
            cursor.execute(query, (media_id, title, overview, release_date, vote_average, poster_path, media_type))

            # Insérer dans movies ou series
            if db_media_type == "movie":
                query_movie = """
                           INSERT INTO movies (movie_id, media_id)
                           VALUES (%s, %s)
                           ON DUPLICATE KEY UPDATE media_id=VALUES(media_id);
                           """
                cursor.execute(query_movie, (media_id, media_id))
            else:
                number_of_seasons = item.get('number_of_seasons', 0)
                number_of_episodes = item.get('number_of_episodes', 0)

                query_series = """
                           INSERT INTO series (series_id, media_id, number_of_seasons, number_of_episodes)
                           VALUES (%s, %s, %s, %s)
                           ON DUPLICATE KEY UPDATE media_id=VALUES(media_id);
                           """
                cursor.execute(query_series, (media_id, media_id, number_of_seasons, number_of_episodes))

    cnx.commit()


# -------------------------------
# 2. Insérer les Genres
# -------------------------------
def fetch_and_insert_genres():
    url_movie = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=fr-FR"
    response = requests.get(url_movie)

    if response.status_code == 200:
        genres = response.json()['genres']
        for genre in genres:
            query = "INSERT INTO genres (genre_id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name);"
            cursor.execute(query, (genre['id'], genre['name']))

    url_tv = f"{BASE_URL}/genre/tv/list?api_key={API_KEY}&language=fr-FR"
    response_tv = requests.get(url_tv)

    if response_tv.status_code == 200:
        genres = response_tv.json()['genres']
        for genre in genres:
            query = "INSERT INTO genres (genre_id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name);"
            cursor.execute(query, (genre['id'], genre['name']))

    cnx.commit()


# -------------------------------
# 3. Associer les Médias aux Genres (Many-to-Many)
# -------------------------------
def fetch_and_insert_media_genres(media_type):
    url = f"{BASE_URL}/{media_type}/popular?api_key={API_KEY}&language=fr-FR"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()['results']
        for item in data:
            media_id = item['id']
            genres = item['genre_ids']

            for genre_id in genres:
                # Vérifier si le genre existe avant de l'insérer dans la table de liaison
                cursor.execute("SELECT COUNT(*) FROM genres WHERE genre_id = %s", (genre_id,))
                genre_exists = cursor.fetchone()[0]

                if genre_exists:
                    query = """
                                INSERT INTO media_to_genres (media_id, genre_id) 
                                VALUES (%s, %s) 
                                ON DUPLICATE KEY UPDATE media_id=VALUES(media_id);
                                """
                    cursor.execute(query, (media_id, genre_id))
                else:
                    print(f"⚠️ Genre {genre_id} non trouvé dans `genres`. Vérifie l'insertion des genres.")

    cnx.commit()


# -------------------------------
# 4. Insérer les Acteurs
# -------------------------------
def fetch_and_insert_actors(media_type):
    url = f"{BASE_URL}/{media_type}/popular?api_key={API_KEY}&language=fr-FR"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()['results']
        for item in data:
            media_id = item['id']
            credits_url = f"{BASE_URL}/{media_type}/{media_id}/credits?api_key={API_KEY}&language=fr-FR"
            credits_response = requests.get(credits_url)

            if credits_response.status_code == 200:
                cast_data = credits_response.json().get('cast', [])
                for actor in cast_data[:10]:  # On prend seulement les 10 premiers acteurs
                    cast_id = actor['id']
                    name = actor['name']
                    character_name = actor.get('character', 'Inconnu')
                    profile_path = actor.get('profile_path', None)

                    query = """
                    INSERT INTO actors (cast_id, name, character_name, profile_path)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE name=VALUES(name);
                    """
                    cursor.execute(query, (cast_id, name, character_name, profile_path))

    cnx.commit()


# -------------------------------
# 5. Associer les Acteurs aux Médias (Many-to-Many)
# -------------------------------
def fetch_and_insert_media(media_type, max_pages=5):  # ← Ajoute un paramètre pour paginer
    db_media_type = "tv" if media_type == "tv" else "movie"

    for page in range(1, max_pages + 1):  # ← Boucle sur plusieurs pages
        url = f"{BASE_URL}/{media_type}/popular?api_key={API_KEY}&language=fr-FR&page={page}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()['results']
            for item in data:
                media_id = item['id']
                title = item.get('title') or item.get('name')
                overview = item.get('overview')
                release_date = item.get('release_date') or item.get('first_air_date')
                vote_average = item.get('vote_average', 0)
                poster_path = item.get('poster_path')

                query = """
                INSERT INTO media (media_id, title, overview, release_date, vote_average, poster_path, media_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=VALUES(title);
                """
                cursor.execute(query, (media_id, title, overview, release_date, vote_average, poster_path, media_type))

                if db_media_type == "movie":
                    query_movie = """
                        INSERT INTO movies (movie_id, media_id)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE media_id=VALUES(media_id);
                    """
                    cursor.execute(query_movie, (media_id, media_id))
                else:
                    number_of_seasons = item.get('number_of_seasons', 0)
                    number_of_episodes = item.get('number_of_episodes', 0)

                    query_series = """
                        INSERT INTO series (series_id, media_id, number_of_seasons, number_of_episodes)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE media_id=VALUES(media_id);
                    """
                    cursor.execute(query_series, (media_id, media_id, number_of_seasons, number_of_episodes))

    cnx.commit()

def fetch_and_insert_seasons(series_id):
    url = f"{BASE_URL}/tv/{series_id}?api_key={API_KEY}&language=fr-FR"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        seasons = data.get("seasons", [])

        for season in seasons:
            season_id = season['id']
            season_number = season['season_number']
            air_date = season.get('air_date')
            episode_count = season.get('episode_count', 0)
            poster_path = season.get('poster_path')

            query = """
            INSERT INTO seasons (season_id, series_id, season_number, air_date, episode_count, poster_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE season_number=VALUES(season_number);
            """
            cursor.execute(query, (season_id, series_id, season_number, air_date, episode_count, poster_path))

    cnx.commit()

def fetch_and_insert_episodes(series_id, season_number):
    url = f"{BASE_URL}/tv/{series_id}/season/{season_number}?api_key={API_KEY}&language=fr-FR"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        episodes = data.get("episodes", [])

        for episode in episodes:
            episode_id = episode['id']
            title = episode['name']
            overview = episode['overview']
            air_date = episode.get('air_date')
            episode_number = episode['episode_number']
            vote_average = episode.get('vote_average', 0)

            query = """
            INSERT INTO episodes (episode_id, season_id, episode_number, title, overview, air_date, vote_average)
            VALUES (%s, (SELECT season_id FROM seasons WHERE series_id=%s AND season_number=%s), %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=VALUES(title);
            """
            cursor.execute(query, (episode_id, series_id, season_number, episode_number, title, overview, air_date, vote_average))

    cnx.commit()

# -------------------------------
# 6. Exécution du script
# -------------------------------
print("Insertion des genres...")
fetch_and_insert_genres()

print("Insertion des films et séries...")
fetch_and_insert_media("movie")
fetch_and_insert_media("tv")

print("Insertion des films et séries...")
fetch_and_insert_media("movie", max_pages=5)  # ← par exemple 5 pages = 100 films
fetch_and_insert_media("tv", max_pages=5)     # ← idem pour les séries

print("Insertion des genres associés aux médias...")
fetch_and_insert_media_genres("movie")
fetch_and_insert_media_genres("tv")

print("Insertion des acteurs...")
fetch_and_insert_actors("movie")
fetch_and_insert_actors("tv")


print("Insertion des saisons et épisodes...")
cursor.execute("SELECT series_id FROM series")
series_list = cursor.fetchall()

for series in series_list:
    series_id = series[0]
    fetch_and_insert_seasons(series_id)

    cursor.execute("SELECT season_number FROM seasons WHERE series_id=%s", (series_id,))
    season_numbers = cursor.fetchall()

    for season_number in season_numbers:
        fetch_and_insert_episodes(series_id, season_number[0])

print("job is done")


cursor.close()
cnx.close()
