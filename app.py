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
        print("Mot de passe reçu :", password)

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

# Accueil
@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.id)



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
def favoris():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM favorites")
    favoris = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("favoris.html", favoris=favoris)

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



if __name__ == '__main__':
    app.run(debug=True)

