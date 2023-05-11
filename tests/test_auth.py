"""
This module is used to test registration, log-in, log-out,

Functions:
- test_register: Test successful registration of a user to the application.
- test_register_validate_input: Test unsuccessful registration of a user to the application. 
- test_login: Test successful log-in of a user. 
- test_login_validate_input: Test unsuccessful log-in of a user.
- test_logout: Test successful log-out of a user.
- test_logout_redirect: Test the log-out redirect.

"""
import pytest
from flask import g, session
from mlapp.db import get_db

def test_register(client, app):
    """Test successful registration of a user to the application using the register view function.

    Test that navigation to the register page returns an 200 OK status code.
    Test that valid form data on a POST request to the register view function
    redirects to the login URL and the user's data is successfully inserted into the database.    

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    app : Flask
        An instance of the Flask application object with the current request context. 
    """
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', 
        data={'email': 't@e.sttwo', 'password': 'a', 'confirm_password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE email = 't@e.sttwo'",
        ).fetchone() is not None


@pytest.mark.parametrize(('email', 'password', 'confirm_password', 'message'), (
    ('', '', '', b'Email address is required!'),
    ('t@e.s', '', '', b'Accepted email addresses are'),
    ('t@e.st', '', '', b'Password is required!'),
    ('te.st', '', '', b'Not a valid email address!'),
    ('t@est', '', '', b'Not a valid email address!'),
    ('t@e.st', 'a', 'b', b'Both passwords must match!'),
    ('t@e.st', 'test', '', b'Confirm password required!'),
    ('t@e.st', 'a', 'a', b'already registered'),
))
def test_register_validate_input(client, email, password, confirm_password, message):
    """Test unsuccessful registration of a user to the application using the register view function.

    Test email DataRequired RegistrationForm validator.
    Test email Length RegistrationForm validator.
    Test email Email RegistrationForm validator.
    Test password DataRequired RegistrationForm validator.
    Test password EqualTo RegistrationForm validator.
    Test confirm_password DataRequired RegistrationForm validator.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    email : str
        The test user's email address.
    password : str
        The test user's password.
    confirm_password : str
        The test user's confirmation password.
    message : str
        The messaged returned in the response data.
    """
    response = client.post(
        '/auth/register',
        data={'email': email, 'password': password, 'confirm_password': confirm_password}
    )
    assert message in response.data


def test_login(client, auth):
    """Test successful log-in of a user using the login view function. 

    Test that navigation to the login page returns an 200 OK status code.
    Test that valid form data on a POST request to the login view function
    redirects to the index URL.
    Test that the session object has been populated with the user_id.
    Test that the user's email is stored in g.user['email']. 

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['email'] == 't@e.st'
    

@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('t@e.stInv', 'test', b'Incorrect email.'),
    ('t@e.st', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, email, password, message):
    """Test unsuccessful log-in of a user to the application using the login view function.

    Test the error message is displayed for an email that does not exist in the database. 
    Test the error message is displayed for an incorrect password for a user email address. 

    Parameters
    ----------
    auth : AuthActions
        An instance of the AuthActions class instatiated with a FlaskClient instance.
    email : str
        The test user's email address. 
    password : str
        The test user's password
    message : str
        The message returned in the response data.
    """
    response = auth.login(email, password)
    assert message in response.data


def test_logout(client, auth):
    """Test successful log-out of a user using the logout view function.

    Test that the user_id is removed from the session object after the logout view
    function has been called.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with a FlaskClient instance.
    """
    auth.login()

    with client:
        auth.logout()
        # session is still accessible
        assert 'user_id' not in session
    # session is no longer accessible

def test_logout_redirect(client):
    """Test log-out redirect by the /auth/logout URL.

    Test that only one redirect response.
    Test the redirect path is to the / URL.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    """
    # Then try to log them out
    response = client.get("/auth/logout", follow_redirects=True)
    # Check that there was one redirect response.
    # TestResponse.history is a tuple of the responses that led up to the final
    # response. Each response has a request attribute which records the request that
    # produced that response.
    assert len(response.history) == 1
    # Check that the second request was to the index page.
    assert response.request.path == "/"



