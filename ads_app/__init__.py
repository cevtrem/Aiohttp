from flask import Flask
from ads_app.database.session import db
from ads_app.views import ads_bp
from ads_app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(ads_bp)

    return app
