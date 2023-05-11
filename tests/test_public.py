"""
This module is used to test functionality of view functions that do not require authentication and any related functions.  

Functions:
- test_index: Test the index route.
- test_about: Test the about route.

"""

def test_index(client):
    """Test the index view function.

    Test the analyser page link is displayed.
    Test the about page link is displayed.
    Test the TensorFlow link is displayed.
    Test the Flask link is displayed.
    Test the GitHub respository link is displayed.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    """
    response = client.get("/")
    assert b'href="/analyser"' in response.data
    assert b'href="/about"' in response.data
    assert b'href="https://www.tensorflow.org/"' in response.data
    assert b'href="https://flask.palletsprojects.com/en/2.2.x/"' in response.data
    assert b'href="https://github.com/DavidMcNallyQub"' in response.data

def test_about(client, auth):
    """Test the about view function.

    Test the landing page link is displayed.
    Test the analyser page link is displayed.
    Test the about page link is displayed.
    Test the login page link is displayed.
    Test the register page link is displayed.
    Test the TensorFlow page link is displayed.
    Test the Flask page link is displayed.
    Test the Bootstrap page link is displayed.
    Test the GitHub respository link is displayed.
    Test the account link is displayed if a user is logged in.
    Test the logout link is displayed if a user is logged in.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    response = client.get("/about")
    assert b'href="/"' in response.data
    assert b'href="/analyser"' in response.data
    assert b'href="/about"' in response.data
    assert b'href="/auth/login"' in response.data
    assert b'href="/auth/register"' in response.data
    assert b'href="https://www.tensorflow.org/"' in response.data
    assert b'href="https://flask.palletsprojects.com/en/2.2.x/"' in response.data
    assert b'href="https://getbootstrap.com/"' in response.data
    assert b'href="https://github.com/DavidMcNallyQub/mlapp"' in response.data
    auth.login()
    response = client.get('/about')
    assert b'href="/account"' in response.data
    assert b'href="/auth/logout"' in response.data