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

# Connexion à la base de données
cnx = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME')
)

cursor = cnx.cursor()

#Faire les @app.route...





if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1',port=5000)
