import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'mms-birthday-app.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register blueprints
    from . import auth, home, birthday
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(birthday.bp)
    app.add_url_rule('/', endpoint='index')

    from . import db
    db.init_app(app)
    auth.init_app(app)

    return app
