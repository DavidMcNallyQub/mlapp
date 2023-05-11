import os
from flask import Flask
from .views import register_api

def create_app(test_config: str=None) -> Flask:
    """The Flask factory function.

    This function uses Flask's application factory pattern to create an instance of the application object.
    # TODO write the rest of description... 

    Parameters
    ----------
    test_config : str, optional
        Path to the test configuration file, by default None

    Returns
    -------
    Flask
        _description_
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # TODO: CHANGE SECRET_KEY WHEN DEPLOYING!
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'mlapp.sqlite'),
        # SQLALCHEMY_DATABASE_URI='sqlite:////tmp/test.db'
        # SQLALCHEMY_DATABASE_URI='sqlite:///test.db'
    )

    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # initialise the app with the Flask tutorial SQLite database.
    from . import db
    db.init_app(app)

    # initialise the app with the Flask-SQLAlchemy extension
    # from .extensions import dbase as db
    # db.init_app(app)

    # register Blueprints
    from . import auth, protected, public
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(protected.protected_bp)
    app.register_blueprint(public.public_bp)
    # from . import analyser
    # app.register_blueprint(analyser.analyser_bp)
    # associates the endpoint name 'index' with the "/" url 
    # so that url_for('index') or url_for('public.index') will both work,
    # generating the same "/" URL either way.
    app.add_url_rule('/', endpoint='index')

    # register error handlers
    from . import error_handlers
    app.register_error_handler(404, error_handlers.page_not_found)
    app.register_error_handler(500, error_handlers.internal_server_error)

    # resister Class-based Views
    from . import models
    register_api(app, models.User, "users")
    register_api(app, models.Issue, "issues") 

    return app
