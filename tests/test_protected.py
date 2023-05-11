"""
This module is used to test functionality of protected view functions and any related functions.  

Functions:
- test_analyser: Test the analyser view function.
- test_create_issue: Test the create_issue view function.
# TODO test_get_issue_existing: Test the get_issue function for an existing issue.
# TODO test_get_issue_nonexistent: Test the get_issue function for an non-existent issue.
- test_update_issue: Test the update_issue view function.
- test_create_update_validate: Test the form validators for the create_issue and update_issue view functions.
- test_delete_issue: Test the delete_issue view function.
- test_get_classification_valid: Test the get_classification function with a valid classification name.
- test_get_classification_invalid_classification_name: Test the get_classification function with an invalid classification name.
# TODO test_update_classification: Write and Test the update_classification function.
# TODO test_delete_classification: Write and Test the delete_classification function.
- test_analyse_comments_valid: Test the analyse_comments function with a valid comment source and a valid YouTube videoId.
- test_analyse_comments_invalid_source: Test the analyse_comments function with an invalid comment sources.
- test_analyse_comments_invalid_video_id: Test the analyse_comments function with an invalid YouTube videoId.
- test_get_youtube_video_comments_valid_videoId: Test the get_youtube_video_comments function with a valid YouTube videoId.
- test_get_youtube_video_comments_video_without_comments: Test the get_youtube_video_comments function on a YouTube video without comments.
- test_get_youtube_video_comments_invalid_videoId: Test the get_youtube_video_comments function with an invalid videoId.
- test_predict_comments_valid: Test the predict_comments function with a list of comments.
- test_predict_comments_invalid_model_path: Test the predict_comments function with an invalid model file path.
- test_predict_comments_invalid_comments: Test the predict_comments function with an empty comment list.
- test_combine_analysed_data_valid: Test the combine_analysed_data function with corresponding numbers of prediction values and comments.
- test_combine_analysed_data_invalid: Test the combine_analysed_data function with mismatched numbers of predictions values and comments.
- test_calculate_prediction_confidence_valid: Test the calculate_prediction_confidence with valid parameters.
- test_calculate_prediction_confidence_invalid: Test the calculate_prediction_confidence with invalid parameters.
- test_classify_prediction_misinformation: Test the classify_prediction function for misinformation prediction values.
- test_classify_prediction_neutral: Test the classify_prediction function for neutral prediction values.
- test_classify_prediction_outside_range: Test the classify_prediction function for outside the prediction value range.
- test_account: Test the account view function.
- test_login_required: Test the view functions that require a logged in user.
- test_issue_author_required: Tests the view functions that require logged in users to be issue authors.
- test_issue_exists_required: Test the view functions that require existing issues.
"""
import pytest
from flask import g, session, request
from werkzeug.exceptions import HTTPException
from mlapp.db import get_db
from mlapp.protected import get_issue, get_classification, analyse_comments, get_youtube_video_comments, predict_comments, combine_analysed_data, calculate_prediction_confidence, classify_prediction
from googleapiclient.errors import HttpError
import numpy as np
from numpy import ndarray
from typing import List

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
        An instance of the AuthActions class instantiated with FlaskClient instance.
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
        An instance of the AuthActions class instantiated with FlaskClient instance.
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

# TODO : def test_get_issue_existing(issue_id: int):
# TODO : def test_get_issue_nonexistent(issue_id: int)

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
        An instance of the AuthActions class instantiated with FlaskClient instance.
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
def test_create_update_validate_issue(client, auth, path):
    """Test the create_issue and update_issue view function validators.

    Test comment DataRequired IssueForm validator.
    Test user_id DataRequired IssueForm validator.
    Test classification_id DataRequired IssueForm validator.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instantiated with FlaskClient instance.
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
        An instance of the AuthActions class instantiated with FlaskClient instance.
    """
    auth.login()
    response = client.post('/issue/delete/1')
    assert response.headers["Location"] == "/analyser"

    with app.app_context():
        db = get_db()
        issue = db.execute('SELECT * FROM issue \
                           WHERE id = 1').fetchone()
        assert issue is None

@pytest.mark.parametrize("classification_name", [
        ("Misinformation"),
        ("Neutral")
])
def test_get_classification_valid(classification_name: str, app, client):
    """Test the get_classification function with valid classification names.

    Test the classification_id is returned as an integer.
    Test the classification is the correct classifcation name.

    Parameters
    ----------
    classification_name : str
        The binary classifcation name.
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    """
    with app.app_context():
       classification_id, classification = get_classification(classification_name)
       assert type(classification_id).__name__ == "int" 
       assert classification == classification_name

@pytest.mark.parametrize("classification_name", [
        ("invalid_classfication_name")
])
def test_get_classification_invalid_classfication_name(classification_name: str, app, client):
    """Test the get_classification function with invalid classification names.

    Test that the get_classification function raises a HTTPException.
    Test that the HTTPException status code is 404 NotFound.

    Parameters
    ----------
    classification_name : str
        The binary classifcation name.
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    """
    with app.app_context():
        with pytest.raises(HTTPException) as e:
            get_classification(classification_name)
        assert e.value.code == 404

# TODO : def test_update_classification():
# TODO : def test_delete_classification():

@pytest.mark.parametrize("source, input", [
        ("youtube_video", "rdwz7QiG0lk"),
        ("manually_entered", "test comment")
])
def test_analyse_comments_valid(source: str, input: str, app, client, auth):
    """Test analyse_comments with valid comment sources and inputs.

    Test that valid comment sources return a response with a 200 OK status code.
    Test that classification data is present in the response data.
    Test that options to raise issues for classified comments is present in the response data.

    Parameters
    ----------
    source : str
        How comment(s) are retieved during the request.
        Current options are from a YouTube video using the YouTube API or a manual text input.
    input : str
        Data that represents the input from the comment source.
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instantiated with FlaskClient instance.
    """
    with app.app_context():
        auth.login()
        response = client.post(f"/analyse_comments/{source}", data={'input': input})
        assert response.status_code == 200
        # Classification data.
        assert b"classification" in response.data
        assert b"Confidence Score" in response.data
        # Options to raise an issue.
        assert b"Raise an Issue" in response.data
        assert b"Classification" in response.data
        assert b"Comment" in response.data
        assert b"Issue Details" in response.data
        assert b"Submit Issue" in response.data

@pytest.mark.parametrize("source, input", [
        ("invalid_source", "test_input"),
])
def test_analyse_comments_invalid_source(source: str, input: str, app, client, auth):
    """Test analyse_comments with invalid comment sources.

    Test that an invalid comment source raises a ValueError and displays the correct message.

    Parameters
    ----------
    source : str
        How comment(s) are retieved during the request.
        Current options are from a YouTube video using the YouTube API or a manual text input.
    input : str
        Data that represents the input from the comment source.
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instantiated with FlaskClient instance.
    """
    with app.app_context():
        auth.login()
        response = client.post(f"/analyse_comments/{source}", data={'input': input})
        assert b"Comments could not be returned from an unknown source!" in response.data

@pytest.mark.parametrize("source, input", [
        ("youtube_video", "invalid_video_id"),
])
def test_analyse_comments_invalid_video_id(source: str, input: str, app, client, auth):
    """Test analyse_comments for an invalid YouTube videoId. 

    Test that an invalid YouTube videoId raises a HttpError and displays the correct message.

    Parameters
    ----------
    source : str
        How comment(s) are retieved during the request.
        Current options are from a YouTube video using the YouTube API or a manual text input.
    input : str
        Data that represents the input from the comment source.
    app : Flask
        An instance of the Flask application object with the current request context. 
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    auth : AuthActions
        An instance of the AuthActions class instatiated with FlaskClient instance.
    """
    with app.app_context():
        auth.login()
        response = client.post(f"/analyse_comments/{source}", data={'input': input})
        assert b"An error occured while retrieving YouTube comments:" in response.data

# NOTE: test for the base Exception handler in analyse_comments is dependent on unkown unhandled exceptions and hence not tested.

@pytest.mark.parametrize('video_id', [
        "rdwz7QiG0lk"
])
def test_get_youtube_video_comments_valid_videoId(video_id: str):
    """Test the get_youtube_video_comments function with valid a YouTube videoId.

    Test that a list returned by get_youtube_video_comments.
    Test that the list returned by get_youtube_video_comments has one or more elements.

    Parameters
    ----------
    video_id : str
        The YouTube videoId.
    """
    comments = get_youtube_video_comments(video_id)
    assert type(comments).__name__ == "list"
    assert len(comments) > 0 

@pytest.mark.parametrize('video_id', [
        "8rZP8ef7fps"
])
def test_get_youtube_video_comments_video_without_comments(video_id: str):
    """Test the get_youtube_video_comments function raises a ValueError exception where
    the YouTube video, specified by its videoId, doesn't have any comments.

    Test that if get_youtube_video_comments is passed a videoId of a video without comments, the function raises a ValueError exception.
    Test the ValueError exception displays the correct message. This test is entirely 
    dependent on the YouTube video's comments remaining disabled for this video.

    Parameters
    ----------
    video_id : str
        The YouTube videoId.
    """
    with pytest.raises(ValueError) as e:
        get_youtube_video_comments(video_id)
    assert str(e.value) == f"No comments were found for the YouTube video with videoId: {video_id}"
    
@pytest.mark.parametrize('video_id', [
        "invalid"
])
def test_get_youtube_video_comments_invalid_videoId(video_id: str):
    """Test the get_youtube_video_comments function with an invalid YouTube videoId.

    Test that get_youtube_video_comments raises a HttpError for an invalid videoId.
    Test the HttpError exception's status returned is 404.
    Test the HttpError exception displays the "videoNotFound" reason.

    Parameters
    ----------
    video_id : str
        The YouTube videoId.
    """
    with pytest.raises(HttpError) as e:
        get_youtube_video_comments(video_id)
    assert e.value.status_code == 404
    assert str(e.value.error_details[0]['reason']) == "videoNotFound"

@pytest.mark.parametrize("comments", [
        (["test comment", "list"])
])
def test_predict_comments_valid(comments: List[str]):
    """Test the predict_comments function with a valid list of comments. 

    Test that predict_comments returns a NumPy array.
    Test the returned NumPy array from predict_comments has the same number of elements as the comments list.

    Parameters
    ----------
    comments : List[str]
        A list of test string comments.
    """
    assert type(predict_comments(comments)).__name__ == "ndarray"
    assert predict_comments(comments).size == len(comments)

@pytest.mark.parametrize("comments, invalid_model_path", [
        (["Test", "comments"], "invalid_path")
])
def test_predict_comments_invalid_model_path(comments: List[str], invalid_model_path: str):
    """Test the predict_comments function with an invalid model file_path.

    Test that an invalid file path for the model raises a OSError exception.
    Test that the OSError exception displays the correct message.  

    Parameters
    ----------
    comments : List[str]
        A list of test comments.
    invalid_model_path : str
        An invalid model file path.
    """
    with pytest.raises(OSError) as e:
        predict_comments(comments, model_path=invalid_model_path)
    assert str(e.value) == "The file for the Neural Network Model could not be found!"

@pytest.mark.parametrize("invalid_comments", [
        []
])
def test_predict_comments_invalid_comments(invalid_comments: List[str]):
    """Test the predict_comments function with an empty list of comments.

    Test that an empty comment list raises a ValueError exception.
    Test that the ValueError exception displays the correct message.

    Parameters
    ----------
    invalid_comments : List[str]
        An empty test list of comments.
    """
    with pytest.raises(ValueError) as e:
        predict_comments(invalid_comments)
    assert str(e.value) == "There is an error with the input comment data during predictions!"

@pytest.mark.parametrize("predictions, comments", [
    (np.random.rand(3,1),["test","comment","list"])
])
def test_combine_analysed_data_valid(predictions: ndarray, comments: List[str], app):
    """Test combine_analysed_data with valid prediction arrays and comment lists.

    Test that combine_analysed_data returns a dictionary with the "comment" key. 
    Test that combine_analysed_data returns a dictionary with the "classification_id" key. 
    Test that combine_analysed_data returns a dictionary with the "classification" key.
    Test that combine_analysed_data returns a dictionary with the "prediction_value" key. 
    Test that combine_analysed_data returns a dictionary with the "prediction_confidence" key.

    Parameters
    ----------
    predictions : ndarray
        A NumPy array of comment predictions.
    comments : List[str]
        A list of comments as strings.
    """
    with app.app_context():
        combined_analysed_data = combine_analysed_data(predictions, comments)
        for analysed_data in combined_analysed_data.values():
            assert "comment" in analysed_data
            assert "classification_id" in analysed_data
            assert "classification" in analysed_data
            assert "prediction_value" in analysed_data
            assert "prediction_confidence" in analysed_data

@pytest.mark.parametrize("predictions, comments", [
    (np.random.rand(4,1),["test","comment","list"])
])
def test_combine_analysed_data_invalid(predictions: ndarray, comments: List[str], app):
    """Test combine_analysed_data with invalid prediction and comment data.

    Test that differing number of elements within predictions and comments passed into combine_analysed_data
    raises a ValueError exception.
    Test that the ValueError exception displays the correct message.
    Parameters
    ----------
    predictions : ndarray
        A NumPy array of comment predictions.
    comments : List[str]
        A list of comments as strings.
    app : Flask
#         An instance of the Flask application object with the current request context. 
    """
    with app.app_context():
        with pytest.raises(ValueError) as e:
            combine_analysed_data(predictions, comments)
        assert str(e.value) == "The number of prediction values does not match the number of comments!" 

@pytest.mark.parametrize("prediction_value, confidence_percentage",  [
    (0, 100),
    (0.25, 50),
    (0.49, 2),
    (0.5, 0),
    (0.51, 2),
    (0.75, 50),
    (1, 100)
])
def test_calculate_prediction_confidence_valid(prediction_value, confidence_percentage):
    """Test calculating the prediction confidence of a prediction valid values.

    Edge cases for the prediction values have been selected as paramters for these tests.

    Parameters
    ----------
    prediction_value : float
        The TensorFlow model's prediction value of a comment ranging (0-1).  
    confidence_percentage : int
        A measure of how certain the TensorFlow's model's prediction is for a comment.
    """
    assert calculate_prediction_confidence(prediction_value) == confidence_percentage

@pytest.mark.parametrize("prediction_value", (
    -0.1, 
    1.1
))
def test_calculate_prediction_confidence_invalid_value(prediction_value):
    """Test the calculate_prediction_confidence function with invalid prediction_values.
    
    Test that prediction values outside their expected range raises a ValueError.
    Test that the ValueError exception displays the correct message. 

    Parameters
    ----------
    prediction_value : float
        The TensorFlow model's prediction value of a comment ranging (0-1). 
    """
    with pytest.raises(ValueError) as e:
        calculate_prediction_confidence(prediction_value)
    assert str(e.value) == "The prediction value of a comment is not within the (0-1) range."

@pytest.mark.parametrize("prediction_value", (
    0,
    0.25,
    0.49,
    0.5,
    0.51,
    0.75,
    1
))
def test_calculate_prediction_confidence_invalid_threshold(prediction_value):
    """Test the calculate_prediction_confidence function with an invalid prediction_threshold.
    
    Test that a prediction_threshold of 0 raises a ZeroDivisionError. 
    Test that the ZeroDivsionError exception displays the correct message. 

    Parameters
    ----------
    prediction_value : float
        The TensorFlow model's prediction value of a comment ranging (0-1). 
    """
    with pytest.raises(ZeroDivisionError) as e:
        calculate_prediction_confidence(prediction_value, prediction_threshold=0)
    assert str(e.value) == "A zero-division error has occurred as the prediction threshold has been set to 0!"

@pytest.mark.parametrize("prediction", (
    0.5,
    0.51,
    0.75,
    1
))
def test_classify_prediction_misinformation(prediction: float, app):
    """Test the classify_prediction function misinformation prediction values.

    Test predictions >= 0.5 are classified as "Misinformation". 

    Parameters
    ----------
    prediction : float
        A TensorFlow model's prediction value.
    app : Flask
        An instance of the Flask application object with the current request context. 
    """
    with app.app_context():
        classification_id, classification = classify_prediction(prediction)
        assert classification_id == 1
        assert classification == "Misinformation"

@pytest.mark.parametrize("prediction", [
    0,
    0.25,
    0.49,
])
def test_classify_prediction_neutral(prediction: float, app):
    """Test the classify_prediction function neutral prediction values.

    Test predictions < 0.5 are classified as "Neutral". 

    Parameters
    ----------
    prediction : float
        A TensorFlow model's prediction value.
    app : Flask
        An instance of the Flask application object with the current request context. 
    """
    with app.app_context():
        classification_id, classification = classify_prediction(prediction) 
        assert classification == "Neutral"
        assert classification_id == 2

@pytest.mark.parametrize("prediction", (
    -0.1,
    1.1,
))
def test_classify_prediction_outside_range(prediction: float):
    """Test the classify_prediction function for predictions outside of the prediction value range.

    Test that predictions not within the range (0-1) raise an ValueError exception.
    Test that the ValueError exception  displays the correct message.

    Parameters
    ----------
    prediction : float
        A TensorFlow model's prediction value.
    """
    with pytest.raises(ValueError) as e:
        classify_prediction(prediction)
    assert str(e.value) == "A prediction value outside the range (0-1) cannot be classified!"

def test_account(client, auth):
    """Test the account view function.

    Test the response from the account endpoint hass a 200 OK status code.

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    """
    auth.login()
    response = client.get("/account")
    assert response.status_code == 200
    # TODO : Test more conponets of the webpage.

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
        An instance of the AuthActions class instantiated with FlaskClient instance.
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
        An instance of the AuthActions class instantiated with FlaskClient instance.
    path : str
        The view function's bound URL.
    """
    auth.login()
    assert client.post(path).status_code == 404