"""
This module is used to create fixtures that are setup functions to be used by tests. 

Functions:
- app: A pytest fixture function that configures the Flask application and database.
- client: A pytest fixture function that creates a FlaskClient.
- runner: A pytest fixture function that creates a FlaskCliRunner.
- auth: A pytest fixture function that creates a AuthActions instance instantiated with a FlaskClient instance.

Classes:
- AuthActions: A class representing authorisation actions.

"""

import os
import tempfile
import pytest
from mlapp import create_app
from mlapp.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    """Configure the application and database for testing.

    Creates and opens a temporary file returning the file descriptor and its filepath. 
    Then, a Flask application object is created where its DATABASE path is overwritten and points 
    to the temporary filepath instead of the instance folder. Test mode is also enabled
    by setting the applications TESTING config value to True.
    The database tables are created by calling init_db and is then populated with the test data.
    Once the tests have finished, the temporary file is closed and then removed. 

    Yields
    ------
    Flask
        An instance of the Flask application object with the current request context. 
    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Tests will use this client to make requests to the application without running
    the server.

    Parameters
    ----------
    app : Flask
        An instance of the Flask application object with the current request context.

    Returns
    -------
    FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts. 
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """Creates a runner that is able to call Click commands that have been registered to 
    the application.

    Parameters
    ----------
    app : Flask
        An instance of the Flask application object with the current request context.

    Returns
    -------
    FlaskCliRunner
        A CliRunner for testing a Flask app's CLI commands.
    """
    return app.test_cli_runner()

class AuthActions(object):
    """
    The class respresents Authentication actions for a test user.

    Methods
    -------
    login()
        Simulate a test user logging in. 
    logout()
        Simulate a test user logging out. 

    """

    def __init__(self, client):
        """
        Constructor for the AuthActions class.

        Parameters
        ----------
        client : FlaskClient
            Similar to a Werkzeug test client but has knowledge about Flask's contexts. 
        """
        self._client = client

    def login(self, email='t@e.st', password='test'):
        """Simulate the log-in of a test user.  

        Make's a POST request to the login view function with the FlaskClient.

        Parameters
        ----------
        email : str, optional
            The user's email address, by default 't@e.st'
        password : str, optional
            The user's password, by default 'test'

        Returns
        -------
        TestResponse
            werkzeug.wrappers.Response subclass that provides extra information about
            requests made with the test werkzeug.test.Client.
        """
        return self._client.post(
            '/auth/login',
            data={'email': email, 'password': password}
        )

    def logout(self):
        """Simulate the log-out of a test user.

        Make's a GET request to the logout view function with the FlaskClient.

        Returns
        -------
        TestResponse
            werkzeug.wrappers.Response subclass that provides extra information about
            requests made with the test werkzeug.test.Client.
        """
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """Creates an AuthActions instance with the client fixture function.

    Passes a FlaskClient instance, which has been setup in the client fixture to the AuthActions
    class constructor and returns an AuthActions instance.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.

    Returns
    -------
    AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    return AuthActions(client)