from flask import Flask
from os import path


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'NEVER GONNA GIVE YOU UP NEVER GONNA LET YOU DOWN' # Clé secret global

    # Import des fichiers auth et views pour la gestion des url
    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
