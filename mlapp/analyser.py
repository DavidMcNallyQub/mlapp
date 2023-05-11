"""
This module contains view functions for the comment analyser and related functions.

Functions:
- index: The index view function.

"""
import functools
from tensorflow import keras
import numpy as np


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, make_response, Response
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
from mlapp.extensions import dbase
from mlapp.db import get_db
from mlapp.forms import IssueForm
from mlapp.models import Issue, User, Classification
from mlapp.auth import login_required
from sqlalchemy.exc import IntegrityError
from sqlite3 import Row
# for YouTube API
import os
import googleapiclient.discovery
from googleapiclient.errors import HttpError
# for type hints
from typing import List, Dict, Any
from numpy import ndarray
# import json
from deprecated import deprecated

# TODO this blueprint could be for logged in user pages! Could have another blueprint for general access purposes!
analyser_bp = Blueprint('analyser', __name__)

@analyser_bp.route('/')
def index():
    """The index view function.

    Renders the landing page with navigation to most other parts of the application.

    Returns
    -------
    str 
        A rendered template string for the index page.
    """
    return render_template('index.html')

@analyser_bp.route('/about')
def about():
    """The about view function.

    Renders the about page which has details about the application. 

    Returns
    -------
    str
        A rendered template string for the about page.
    """
    return render_template('about.html')

@analyser_bp.route('/issues', methods=["POST"])
def create_issue() -> str | Response:
    """Create an issue.

    Expects a comment, issue, and classification from a request alongside a user_id from the current session.
    An IssueForm will validate the issue data and flash any errors on the next request.
    The issue is then inserted into the database and the user is redirected to the analyser page.

    Returns
    -------
    str | Response
        If IssueForm validation errors occur, render the analyser template as a string; otherwise,
        return a redirect response to the analyser page.
    """
    author_id = g.user['user_id']
    errors = {}
    issue_form = IssueForm(request.form)

    if not issue_form.validate():
        errors = issue_form.errors

    if errors:
        for category, message_list in errors.items():
            for message in message_list:
                flash(message, category=category)
    else:
        try:
            db = get_db()
            db.execute(
                "INSERT INTO issue (comment, issue, author_id, classified_id) \
                VALUES (?, ?, ?, ?)",
                (issue_form.comment.data, issue_form.issue.data, author_id, issue_form.classification_id.data)
            )
            db.commit()
        except Exception as e:
            errors = {"error": e}

        return redirect(url_for('analyser.analyser'))
    # return to analyser page and display flashed messages
    return render_template('analyser.html')

def get_issue(issue_id, check_author=True) -> Row:
    """Return an issue given an issue_id.

    The sqlite3 database is queried for an issue with the primary key issue_id.
    If an issue exists with that issue_id, return the issue as a sqlite.Row object 
    containing the issue's: issue_id, comment, issue message, date created, author id and classification id.
    If no issue's exists with the issue_id provided abort and raise an HttpException with a 404 status code.
    If check_author=True and the current signed-in user is not the author of the issue with the issue_id argument,
    abort and raise an HttpException with a 403 status code.

    Parameters
    ----------
    issue_id : int
        The issue primary key id number in the database.
    check_author : bool, optional
        Whether to check if current user is the author, by default True

    Returns
    -------
    Row
        An issue as a sqlite.Row object.   
    """
    issue = get_db().execute(
        "SELECT i.issue_id, i.comment, i.issue, i.date_created, i.author_id, \
        c.classification_id \
        FROM issue i \
        INNER JOIN user u ON i.author_id = u.user_id \
        INNER JOIN classification c ON i.classified_id = c.classification_id \
        WHERE i.issue_id = ?",
        (issue_id,)
    ).fetchone()
    if issue is None:
        abort(404, f"Issue with the id '{issue_id}' doesn't exist.")

    if check_author and issue['author_id'] != g.user['user_id']:
        abort(403)

    return issue

@analyser_bp.route('/issue/update/<int:issue_id>', methods=["GET","POST"])
@login_required
def update_issue(issue_id: int) -> Response:
    """Update an issue message in the SQLite database.

    For a POST request, form data containing the comment, issue, user_id and classification_id
    is passed to an IssueForm for validation.
    If no validation errors are present in the form data, the database is queried to update the issue message
    for the issue with the issue_id argument.
    If any errors occur they are flashed to the next request. 
    The user is then redirected to the analyser page.    

    Parameters
    ----------
    issue_id : int
        The issue primary key id number in the database.

    Returns
    -------
    Response
        A redirect Response to the analyser page.
    """
    # get_issue only checks if the issue exists and the author is a logged in user.
    get_issue(issue_id)
    if request.method == 'POST':
        issue_form = IssueForm(request.form)
        errors = {}
        
        if not issue_form.validate():
            errors = issue_form.errors
        else:
            try:
                db = get_db()
                db.execute("UPDATE issue \
                    SET issue = ? \
                    WHERE issue_id = ?",
                    (request.form['issue'], issue_id)
                )
                db.commit()
            except db.IntegrityError as e:
                print(e)
                errors = {"error": e}
            except Exception as e: 
                print(e)
                errors = {"error": "Error Updating issue in the database."}
    
        if errors:
            for category, message in errors.items():
                        flash(message, category=category)

    return redirect(url_for('analyser.analyser'))

@analyser_bp.route('/issue/delete/<int:issue_id>', methods=["POST"])
@login_required
def delete_issue(issue_id: int) -> Response:
    """Delete an issue from the SQLite3 database.

    For a POST request, form data containing the issue_id is passed to the view function.
    The database is queried to delete the issue with the passed issue_id.
    A success message will be flashed if no errors occur otherwise an error message is flashed to the 
    next request.
    The user is then redirected to the analyser page. 

    Parameters
    ----------
    issue_id : int
        The issue primary key id number in the database.

    Returns
    -------
    Response
        A redirect Response to the analyser page.
    """
     # get_issue only checks if the issue exists and the author is a logged in user.
    issue = get_issue(issue_id)
    issue_id = issue['issue_id']
    message = {"success": f"Issue number {issue_id} deleted."}
    try:
        db = get_db()
        db.execute('DELETE FROM issue \
                   WHERE issue_id = ?', 
                   (issue_id,))
        db.commit()
    except Exception as e:
        print(e)
        message = {"Error deleting issue from the database": f"Error deleting issue: {issue_id}"}
    
    flash(next(iter(message.values())), category=next(iter(message.keys())))
    return redirect(url_for('analyser.analyser'))

def get_classification(classification_name: str) -> tuple[int, str]:
    try:
        db = get_db()
        classification = db.execute("SELECT classification_id, classification \
            FROM classification \
            WHERE classification = ?",
            (classification_name,)).fetchone()
        if classification is None:
            abort(404,)
    except Exception as e:
        print(e)

    return classification['classification_id'], classification['classification']

def get_classification_id(classification_name: str) -> int:
    classification_id = None
    try:
        db = get_db()
        classification = db.execute("SELECT classification_id \
            FROM classification \
            WHERE classification = ?",
            (classification_name,)).fetchone()
        if classification is None:
            abort(404,)

    except Exception as e:
        print(e)
        flash("Error getting the classifcation", "")
    return classification['classification_id']

def update_classifcation(classification_id: int):
    raise NotImplementedError("update_classification has not been implemented!")

def delete_classifcation(classification_id: int):
    raise NotImplementedError("delete_classification has not been implemented!")

@analyser_bp.route('/analyser', methods=["GET","POST"])
@login_required
def analyser():
    """The analyser view function.

    Renders the analyser page which has the comment analysers and displays issues raised by users.

    Returns
    -------
    str
        A rendered template string for the analyser page.
    """
    db = get_db()
    issues = []
    errors = {}
    try:
        issues = db.execute("SELECT i.issue_id, i.comment, i.issue, i.date_created, \
            u.user_id, u.email, \
            c.classification_id, c.classification \
            FROM user AS u \
            INNER JOIN issue AS i \
            ON u.user_id = i.author_id \
            INNER JOIN classification as c \
            ON i.classified_id = c.classification_id \
            ORDER BY i.date_created DESC"
        ).fetchall()
    except Exception as e:
        errors = {"error_getting_issues": ["Issues could not be loaded!"]}
    if errors:
        for category, message_list in errors.items():
                for message in message_list:
                    flash(message, category=category)
    
    return render_template('analyser.html', issues=issues)

@analyser_bp.route('/analyser_sqlalchemy')
@login_required
def analyser_sqlalchemy():
    issues = dbase.session.execute(dbase.select(Issue)
                                   .join(User, Issue.user_id == User.user_id)
                                   .join(Classification, Issue.classification_id == Classification.classification_id)
                                   .order_by(Issue.date_created)
                                   ).scalars().fetchall()
    issue = Issue(comment = "Bill gates is lovely!", issue = "This was flagged as misinformation and clearly is not.",user_id = 1, classification_id = 1)
    # dbase.session.add(issue)
    # dbase.session.commit()
    return render_template('analyser.html', issues=issues)

@analyser_bp.route("/analyse_comments/<string:source>", methods=["POST"])
def analyse_comments(source: str) -> Response:
    """Analyse comments view function.

    
    If the source is "youtube_video" treat the request form data as a YouTube videoId and retireve all comments from the YouTube
    video with that VideoId.
    Otherwise, treat the request form data as a single string comment.
    Get the classification data from the retrieved comment(s) and Return a Response object that renders analysed comments 
    alongside a form to highlight issues with analysed comments. 

    Parameters
    ----------
    source : str
        How comment(s) are retieved during the request.
        Current options are from a YouTube video using the YouTube API or a manual text input.

    Returns
    -------
    Response
        A Response object to render analysed comments from the anaylsed_comments template.
    """
    try:
        if source == "youtube_video":
            comments = get_youtube_video_comments(request.form['input'])
            # TODO can display the number of comments using len(comments)
        elif source == "manually_entered":
            comments = [request.form['input']]
        predictions = predict_comments(comments)
        classification_data = combine_analysed_data(predictions, comments)
    except Exception as e:
        print(e)
    response = make_response(render_template('analyser/analysed_comments.html',
                                         classification_data = classification_data)
                            )
    return response

def get_youtube_video_comments(video_id: str) -> list[str]:
    """Returns a list of all comments from a YouTube video for a specified videoId.  

    Reponses for YouTube API commentThreads().list() requests are returned with the maximum of
    100 commentThreads per page.
    Each commentThread contains one top level comment which is added to the comment list; 
    replies to each top level comment are also added to the comment list.
    Comments are 
    The origional, raw text of the comment is retrieved using the snippet.textOrigional
    property of the YouTube comment resource.

    Parameters
    ----------
    video_id : str
        The YouTube video videoId.

    Returns
    -------
    list[str]
        A list of comments as strings.
    """
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyD5l-RDjjcUSjSaSqMGE2YrR6WqRgZzvAA"
    # build the YouTube API client.
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        part = "snippet, replies",
        videoId = video_id,
        maxResults = 100
    )
    try:
        response = request.execute()
        all_comments = []
        while response:
            comment_threads = response['items']
            for thread in comment_threads:
                top_level_comment = thread['snippet']['topLevelComment']['snippet']['textOriginal']
                all_comments.append(top_level_comment)
                # if top level comments have replies append them to the list of comments.
                if thread['snippet']['totalReplyCount'] > 0:
                    replies= thread['replies']['comments']
                    for reply in replies:
                        reply = reply['snippet']['textOriginal']
                        all_comments.append(reply)
            # check if there are more comments to retrieve on other comment pages.
            if 'nextPageToken' in response:
                next_page_token = response['nextPageToken']
                response = youtube.commentThreads().list(
                    part='snippet, replies',
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token
                ).execute()
            else:
                response = None
    except HttpError as e:
        if(e.error_details):
            error_dict = e.error_details[0]
            print(f"{e.status_code} : {error_dict['reason']} for the {error_dict['location']} : {video_id}")
    except Exception as e:
        print(e)
        
    return all_comments

def predict_comments(comments: List[str]) -> ndarray:
    """Return prediction values using the TensorFlow model for a list of comments.

    The TensorFlow model is loaded and using keras.Model.predict a NumPy array of predictions
    is returned for the list of comments.

    Parameters
    ----------
    comments : List[str]
        A list of comments as strings.

    Returns
    -------
    ndarray
        A NumPy array of prediction values for each comment in comments.
    """
    try:
        model = keras.models.load_model("model")
        comment_array = np.asarray(comments)
        predictions = model.predict(comment_array, verbose=0)
    except Exception as e:
        print(e)
    return predictions

def combine_analysed_data(predictions: ndarray, comments: List[str]) -> Dict:
    """Return analysed data about comments and their predictions.

    For each comment prediction, a dictionary key value pair is stored. 
    The key being the comment number and the value being a dictionary of comment classification data.
    The comment classification data contains the comment, the comment's classification, 
    the comment's classification id, the comment's prediction value and the comment's prediction confidence.

    Parameters
    ----------
    predictions : ndarray
        A NumPy array of the TensorFlow model's predictions for the comments.
    comments : List[str]
        A list of comments as strings.

    Returns
    -------
    Dict
        A dictionary of data for analysed comments.
    """
    classification_data = {}
    # TODO this may be better to do, by combining NumPy arrays.
    for prediction_number, prediction in enumerate(predictions):
        # TensorFlow's Model.predict method returns an ndarray 
        # where each predicion is a list of prediction value(s)
        # this model only has one prediction output at index 0.
        prediction_value = round(prediction[0].item(), 3)
        prediction_confidence = calculate_prediction_confidence(prediction_value)
        comment = comments[prediction_number]
        classification_id, classification = classify_prediction(prediction_value)
        # classification_id, classifcation = get_classification(classification)
        # classification_id = get_classification_id(classification)
        classification_data[prediction_number+1] = {"comment": comment,
                                                  "classification": classification,
                                                  "classfication_id": classification_id,
                                                  "prediction_value": prediction_value,
                                                  "prediction_confidence":prediction_confidence
                                                  }
    return classification_data

def calculate_prediction_confidence(prediction_value: float, prediction_threshold: float = 0.5) -> int:
    """Return the confidence percentage of the prediction.

    Each prediction value is a Float ranging from (0-1). 
    Prediction values below the prediction_threshold are comments classified as "Neutral" whereas
    prediction values of prediction_threshold and above are comments classified as "Misinformation".
    Therefore, prediction values closer to the prediction_threshold show more uncertainty of the models predictions,
    regardless of classification.
    The prediction confidence is a measure of how certain the TensorFlow's model's prediction for the comment is.

    Parameters
    ----------
    prediction_value : float
        The TensorFlow model's prediction value of a comment ranging (0-1).  
    prediction_threshold: float
        Any TensorFlow model prediction values equal to or greater than the prediction_threshold 
        are classified as "Misinformation", by default 0.5.

    Returns
    -------
    int
        The confidence percentage rounded to two decimal places.
    """
    confidence_percentage = None
    if(prediction_value >= prediction_threshold):
        confidence_percentage = int(round((prediction_value - prediction_threshold)/prediction_threshold, 2)*100)
    else:
        confidence_percentage = int(round((prediction_threshold - prediction_value)/prediction_threshold, 2)*100)
    return confidence_percentage

def classify_prediction(prediction: float, prediction_threshold: float=0.5) -> tuple(int, str):
    """Takes the models prediction value and returns the classification.

    If the prediction value is >=0.5 then it is classified and returned as "Misinformation", 
    otherwise it is "Neutral".  

    Parameters
    ----------
    prediction : float
        The prediction value of the model.
    prediction_threshold : float, optional
        Any TensorFlow model prediction values equal to or greater than the prediction_threshold 
        are classified as "Misinformation", by default 0.5.

    Returns
    -------
    str
        The binary classification of the comment; the classification will be either "Misinformation 
        or "Neutral".
    """
    if(prediction>=prediction_threshold):
        return get_classification("Misinformation")
    else:
        return get_classification("Neutral")
    


@analyser_bp.route("/account", methods=["GET", "POST"])
@login_required
def account() -> str:
    """The account view function.

    Renders the account page which has account information for a specified user.

    Returns
    -------
    str
        A rendered template string for the account page.
    """
    db = get_db()
    user_issues = {}
    user_id = g.user['user_id']
    try:
        user_issues = db.execute("SELECT i.issue_id, i.comment, i.issue, i.date_created, i.author_id, \
                                c.classification \
                                FROM issue AS i \
                                INNER JOIN classification AS c \
                                ON i.classified_id = c.classification_id \
                                WHERE author_id = ? \
                                ORDER BY i.date_created DESC",
                                (user_id, )
                                ).fetchall()
    except Exception as e:
        print(e)
        print("Error getting user's issues!")
    
    return render_template("user/account.html", 
                           user_issues=user_issues)

