import os

from flask import Flask, render_template
from flask_login import LoginManager, login_required
from dotenv import load_dotenv
from flask_wtf import CSRFProtect 

from .user import User

load_dotenv()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'hwdb.sqlite'),
    )
    csrf = CSRFProtect(app) 

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint)

    # a simple page that says hello
    @app.route('/')
    @login_required
    def home():
        return render_template('base.html')

    return app