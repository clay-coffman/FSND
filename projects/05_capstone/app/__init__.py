from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):

    # creates flask object
    app = Flask(__name__)

    # set app config
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app


from app import models
