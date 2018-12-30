from app.utils.utils import register_blueprint

from .game import mod as game_mod


def view_configure_blueprint(app):
    register_blueprint(app, game_mod, url_prefix='')

