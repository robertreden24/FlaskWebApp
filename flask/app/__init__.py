from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_uploads import configure_uploads,IMAGES,UploadSet


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view= 'auth.login'
mail = Mail ()
images = UploadSet('images', IMAGES)

from app import models
from app.auth import routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db = SQLAlchemy(app)
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    configure_uploads(app,images)
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import models
