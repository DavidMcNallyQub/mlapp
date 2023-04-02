import os

from flask import Flask, render_template


def page_not_found(e):
  
    """Displays a custom Error page for a 404 status code.

        Paramters: 
            e (ANY): Exception 
        
            Returns:
                render_template('error/404.html'), 404: """
    return render_template('error/404.html'), 404

def internal_server_error(e):
  """Displays a custom Error page for a 500 status code."""
  return render_template('500.html'), 500

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # TODO: CHANGE SECRET_KEY WHEN DEPLOYING!
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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
    
    # relative imports from this directory
    from . import db
    db.init_app(app)

    # register Blueprints
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import analyser
    app.register_blueprint(analyser.bp)
    app.add_url_rule('/', endpoint='index')

    # register error handlers
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)


    return app
