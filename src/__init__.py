import os
import random
import string
import urllib.request

import requests
from flask import Flask
from flask_login import LoginManager

import src.db as database

from src.main import main_bp

scriptdir = os.path.dirname(os.path.abspath(__file__))
dbfile = os.path.join(scriptdir, "db.sqlite3")

def _setup_db(app: Flask):
    with app.app_context():
        database.db.init_app(app)
        if (os.getenv("RELOAD_DB") == "True"):
            print("Reloading DB...\n")
            database.db.drop_all()
            database.db.create_all()
            print("DB Reloaded\n")
        else:
            database.db.create_all()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SECRET_KEY'] = 'NotDefault'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.register_blueprint(main_bp)

    _setup_db(app)

    return app
