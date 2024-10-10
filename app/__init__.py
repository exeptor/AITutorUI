from flask import Flask
from configurations.config import Config
from app.models import db, User, Article
from flask_login import LoginManager
from app.utils import create_admin

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        create_admin()

    from .routes import main
    app.register_blueprint(main)

    return app
