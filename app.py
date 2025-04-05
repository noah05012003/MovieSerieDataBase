from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_session import Session
import mysql.connector
from dotenv import load_dotenv
import os

# Initialisation
load_dotenv("security.env")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

bcrypt = Bcrypt(app)

# Connexion base de données
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Page de connexion
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print("Email reçu :", email)


        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            user_obj = User(user['user_id'])
            login_user(user_obj)
            flash("Connexion réussie !", "success")
            return redirect(url_for('home'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")
            return redirect(url_for('login'))


    return render_template('login.html')



# Inscription
@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']

        if password != passwordconfirm:
            flash("Les mots de passe ne correspondent pas", "warning")
            return redirect(url_for('sign_up'))

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, hashed)
            )
            conn.commit()
            flash("Compte créé avec succès !", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            flash("Erreur lors de la création du compte : " + str(e), "danger")
            return redirect(url_for('sign_up'))
        finally:
            cursor.close()
            conn.close()
    return render_template("signUp.html")


#Acceuil
@app.route('/home')
@login_required
def home():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username FROM users WHERE user_id = %s", (current_user.id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('home.html', username=user['username'])



# Affichage des films
@app.route('/movies')
def movies():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM media WHERE media_type = 'movie'")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("films.html", movies=movies)

# Affichage des séries
@app.route('/series')
def series():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM media WHERE media_type = 'tv'")
    series = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("series.html", series=series)

# Affichage des genres

@app.route('/genres')
def genres():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM genres")
    genres = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("genres.html", genres=genres)

# Favoris de l'utilisateur
@app.route('/favoris')
@login_required
def favoris():
    return render_template("favoris.html")


# Ajouter un favori
@app.route('/add_favori/<int:media_id>', methods=['POST'])
@login_required
def add_favori(media_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO favorites (user_id, media_id) VALUES (%s, %s)", (current_user.id, media_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Ajouté aux favoris", "success")
    return redirect(url_for('favoris'))

# Retirer un favori
@app.route('/remove_favori/<int:media_id>', methods=['POST'])
@login_required
def remove_favori(media_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE user_id = %s AND media_id = %s", (current_user.id, media_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Retiré des favoris", "info")
    return redirect(url_for('favoris'))

# Déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for('login'))

@app.route('/api/favoris')
@login_required
def api_favoris():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.media_id, m.title, m.poster_path, m.vote_average
        FROM favorites f
        JOIN media m ON f.media_id = m.media_id
        WHERE f.user_id = %s
    """, (current_user.id,))
    favoris = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(favoris)

# Favoris de genres
@app.route('/add_genre_favori/<int:genre_id>', methods=['POST'])
@login_required
def add_genre_favori(genre_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO genre_favorites (user_id, genre_id) VALUES (%s, %s)", (current_user.id, genre_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Genre ajouté aux favoris", "success")
    return redirect(url_for('genres'))

@app.route('/api/genres')
@login_required
def api_genres():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT genre_id, name FROM genres")
    genres = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(genres)

@app.route('/remove_genre_favori/<int:genre_id>', methods=['POST'])
@login_required
def remove_genre_favori(genre_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM genre_favorites WHERE user_id = %s AND genre_id = %s", (current_user.id, genre_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Genre retiré des favoris", "info")
    return redirect(url_for('genres'))

@app.route('/api/genres_favoris')
@login_required
def api_genres_favoris():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT g.genre_id, g.name
        FROM genre_favorites gf
        JOIN genres g ON gf.genre_id = g.genre_id
        WHERE gf.user_id = %s
    """, (current_user.id,))
    favoris = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(favoris)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

