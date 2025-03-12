from flask import Flask, render_template, jsonify, flash, request, session, redirect, url_for
from flask_session import Session
import mysql.connector
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import os

load_dotenv('security.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
bcrypt = Bcrypt(app)

# Connexion à la base de données
cnx = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME')
)

cursor = cnx.cursor()


# ---------------------------
# Routes pour les utilisateurs
# ---------------------------

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data['username']
    email = data['email']
    password = data['password']

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
    values = (username, email, hashed_password)

    cursor.execute(query, values)
    cnx.commit()

    flash("Compte créé avec succès !", "success")
    return redirect(url_for('login'))


@app.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data['email']
    password = data['password']

    cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[1], password):
        session['user_id'] = user[0]
        flash("Connexion réussie !", "success")
        return redirect(url_for('favorites'))
    else:
        flash("Échec de la connexion", "danger")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Déconnexion réussie.", "success")
    return redirect(url_for('login'))


# ---------------------------
# Routes pour gérer les favoris
# ---------------------------

@app.route('/favorites')
@login_required
def favorites():
    user_id = session.get('user_id')

    cursor.execute(""" 
    SELECT media.media_id, media.title, media.media_type
        FROM favorites
        JOIN media ON favorites.media_id = media.media_id
        WHERE favorites.user_id = %s
    """, (user_id,))

    favorites = cursor.fetchall()

    return jsonify(favorites)


@app.route('/add_favorite/<int:media_id>', methods=['POST'])
@login_required
def add_favorite(media_id):
    user_id = session.get('user_id')

    query = "INSERT IGNORE INTO favorites (user_id, media_id) VALUES (%s, %s)"
    values = (user_id, media_id)

    cursor.execute(query, values)
    cnx.commit()

    flash("Ajouté aux favoris.", "success")
    return redirect(url_for('favorites'))


@app.route('/remove_favorite/<int:media_id>', methods=['POST'])
@login_required
def remove_favorite(media_id):
    user_id = session.get('user_id')

    query = "DELETE FROM favorites WHERE user_id = %s AND media_id = %s"
    values = (user_id, media_id)

    cursor.execute(query, values)
    cnx.commit()

    flash("Retiré des favoris.", "success")
    return redirect(url_for('favorites'))


# ---------------------------
# Routes pour gérer les médias
# ---------------------------

@app.route('/media')
def get_all_media():
    cursor.execute("SELECT * FROM media")
    media_list = cursor.fetchall()
    return jsonify(media_list)


@app.route('/media/<int:media_id>')
def get_media(media_id):
    cursor.execute("SELECT * FROM media WHERE media_id = %s", (media_id,))
    media = cursor.fetchone()
    return jsonify(media)


@app.route('/genres')
def get_all_genres():
    cursor.execute("SELECT * FROM genres")
    genres = cursor.fetchall()
    return jsonify(genres)


@app.route('/media/<int:media_id>/actors')
def get_media_actors(media_id):
    cursor.execute("""
        SELECT actors.name, actors.character_name
        FROM media_to_cast
        JOIN actors ON media_to_cast.cast_id = actors.cast_id
        WHERE media_to_cast.media_id = %s
    """, (media_id,))

    actors = cursor.fetchall()
    return jsonify(actors)





if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1',port=5000)
