# init.py

import dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import get_root_path
from flask_login import LoginManager, login_required

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    server = Flask(__name__)

    server.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(server)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(server)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our server
    from .auth import auth as auth_blueprint
    server.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of server
    from .main import main as main_blueprint
    server.register_blueprint(main_blueprint)

    # Register dash app
    register_dashapps(server)

    return server


def register_dashapps(app):
    # from app.dashapp1.layout import layout
    from project.app.dashapp1.layout import layout
    from project.app.dashapp1.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp1 = dash.Dash(__name__,
                         server=app,
                         sharing=True,
                         url_base_pathname='/dashboard/',
                         assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                         meta_tags=[meta_viewport])

    with app.app_context():
        dashapp1.title = 'Dashapp 1'
        dashapp1.layout = layout
        register_callbacks(dashapp1)

    _protect_dashviews(dashapp1)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])
