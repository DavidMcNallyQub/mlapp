"""
This module is used to test functionality of the comment analyser view functions and related functions.  

Functions:
- test_index:

"""
import pytest
from flask import g, session
from mlapp.db import get_db

# TODO: MAKE TESTS FOR POSTS LIKE FLASKBLOG TUTORIAL!
# TODO: Finish tests for the analyser blueprint.

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

def test_create_issue(app, client, auth):
    """Test the create_issue view function.

    Test the create_issue view function by checking the number of issues 
    present in the database increments by one after calling create_issue.

    Parameters
    ----------
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    # creating issues requires a user to be logged in.
    auth.login()
    client.post('/issues',
                 data={'comment': 'created', 'issue': '', 'user_id': 1, 'classification_id': 1})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(issue_id) \
                            FROM issue').fetchone()[0]
        assert count == 2

# TODO : def test_get_issue():

def update_issue(app, client, auth):
    """Test the update_issue view function.

    Test a GET request to the update_issue view function
    returns a 200 OK status code for a logged in user.
    Test a POST request to the update_issue view function 
    sucessfully updates an issue message.

    Parameters
    ----------
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    # updating issues requires a user to be logged in.
    auth.login()
    assert client.get('/issue/update/1').status_code == 200
    client.post('/issue/update/1',
                data={"comment": "", 'issue': 'updated', "author_id": 1, "classification_id": 1}
                )

    with app.app_context():
        db = get_db()
        issue = db.execute('SELECT * \
                            FROM issue \
                            WHERE issue_id = 1').fetchone()
        assert issue['issue'] == 'updated'

@pytest.mark.parametrize('path', (
    '/issues',
    '/issue/update/1',
))
def test_create_update_validate(client, auth, path):
    """Test the create_issue and update_issue view function validators.

    Test comment DataRequired IssueForm validator.
    Test user_id DataRequired IssueForm validator.
    Test classification_id DataRequired IssueForm validator.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    path : str
        The view function's bound URL.
    """
    auth.login()
    response = client.post(path, data={"user_id": 1, "classification_id": 1}, follow_redirects=True)
    assert b"The issues&#39;s comment is required!" in response.data
    # an issue message is not compulsory
    response = client.post(path, data={"comment": "create_update", "classification_id": 1}, follow_redirects=True)
    assert b"A user_id is required!" in response.data
    response = client.post(path, data={"comment": "create_update", "user_id": 1}, follow_redirects=True)
    assert b"A classification_id is required!" in response.data

def delete_issue(app, client, auth):
    """Test the delete_issue view function.

    Test the delete_issue view function by checking the number of issues 
    present in the database decreases by one after calling delete_issue.

    Parameters
    ----------
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    auth.login()
    response = client.post('/issue/delete/1')
    assert response.headers["Location"] == "/analyser"

    with app.app_context():
        db = get_db()
        issue = db.execute('SELECT * FROM issue \
                           WHERE id = 1').fetchone()
        assert issue is None

# TODO : def test_get_classification():
# TODO : def test_get_classification_id():
# TODO : def test_update_classification():
# TODO : def test_delete_classification():

def test_analyser(client, auth):
    """Test the analyser view function.

    Test the Sign-Out link is displayed for a logged in user.
    Test the account link is displayed for a logged in user.
    Test issues' comment are displayed to the analyser page.
    Test issues' date created are displayed to the analyser page.
    Test issues' issue message are displayed to the analyser page.
    Test issues' classification are displayed to the analyser page.
    Test that the Update Issue button is displayed in the analyser page when the current user is the issue's author.
    Test that the Delete Issue button is displayed in the analyser page when the current user is the issue's author.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    # redirected from the analyser unless a user is logged in.
    auth.login()
    response = client.get('/analyser')
    assert b'Sign-Out' in response.data
    assert b't@e.st'in response.data
    # check the issues are present in the analyser page.
    assert b'test comment' in response.data
    assert b'2023-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'Misinformation' in response.data
    assert b'Update Issue' in response.data
    assert b'Delete Issue' in response.data

# TODO : def test_analyse_comments():
# TODO : def test_get_youtube_video_comments():
# TODO : @pytest.mark.parametrize("")
# TODO :def test_predict_comments(): 

# TODO : def test_combine_analysed_data():
# TODO : def test_calculate_prediction_confidence():
# TODO : def test_classify_prediction():
# TODO : def test_account():

@pytest.mark.parametrize('path', (
    "/analyser",
    "/account",
    "/issue/update/1",
    "/issue/delete/1",
))
def test_login_required(client, path):
    """Test the view functions that require log-in access.

    Test the analyser view function requires log-in.
    Test the account view function requires log-in.
    Test the update_issue view function requires log-in.
    Test the delete_issue view function requires log-in.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    path : str
        The view function's bound URL.
    """
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

def test_issue_author_required(app, client, auth):
    """Test view functions that require the logged in user to be the issue author.

    Test update_issue returns a 403 Forbidden status code if the current user tries to update another user's issue.
    Test delete_issue returns a 403 Forbidden status code is returned if the current user tries to delete another user's issue.
    Test that the Update Issue button is not displayed in the analyser page when the current user is not the issue's author.
    Test that the Delete Issue button is not displayed in the analyser page when the current user is not the issue's author.

    Parameters
    ----------
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    # change the issue author to another user.
    with app.app_context():
        db = get_db()
        db.execute('UPDATE issue \
                    SET author_id = 2 \
                    WHERE issue_id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's issues.
    assert client.post('/issue/update/1').status_code == 403
    assert client.post('/issue/delete/1').status_code == 403
    # current user doesn't see Update Issue and Delete Issue buttons.
    assert b'Update Issue' not in client.get('/analyser').data
    assert b'Delete Issue' not in client.get('/analyser').data

@pytest.mark.parametrize('path', (
    '/issue/update/2',
    '/issue/delete/2',
))
def test_issue_exists_required(client, auth, path):
    """Test view functions issue existing requirement.

    Test if the update_issue view function returns a 404 Not Found for an issue_id of a non-existent issue.
    Test if the delete_issue view function returns a 404 Not Found for an issue_id of a non-existent issue.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    path : str
        The view function's bound URL.
    """
    auth.login()
    assert client.post(path).status_code == 404