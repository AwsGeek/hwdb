import os

from flask import Flask
from flask_login import LoginManager, login_required
from .user import User


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        OAUTH1_PROVIDER_ENFORCE_SSL=False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
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
    from . import auth
    app.register_blueprint(auth.bp)

    # apply the blueprints to the app
    from . import casting
    app.register_blueprint(casting.bp)

    # apply the blueprints to the app
    from . import store
    app.register_blueprint(store.bp)

    # apply the blueprints to the app
    from . import api
    app.register_blueprint(api.bp)


    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="casting.index")

    return app