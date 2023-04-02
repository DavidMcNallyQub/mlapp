import pytest
from flask import g, session
from mlapp.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        # session is still accessible
        assert 'user_id' not in session
    # session is no longer accessible


def test_logout_redirect(client):
    """TestResponse.history is a tuple of the responses that led up to the final
    response. Each response has a request attribute which records the request that
    produced that response.
    
    From (https://flask.palletsprojects.com/en/2.2.x/testing/#following-redirects)"""
    response = client.get("/logout")
    # Check that there was one redirect response.
    assert len(response.history) == 1
    # Check that the second request was to the index page.
    assert response.request.path == "/index"


def test_modify_session(client):
    """If you want to access or set a value in the session before making a request,
    use the client’s session_transaction() method in a with statement. It returns a
    session object, and will save the session once the block ends.
    
    From ()"""
    with client.session_transaction() as session:
        # set a user id without going through the login route
        session["user_id"] = 1

    # session is saved now

    response = client.get("/users/me")
    assert response.json["username"] == "flask"

# NO TESTS FOR POSTS LIKE FLASKBLOG TUTORIAL YET!
