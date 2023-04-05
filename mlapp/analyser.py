import functools
import tensorflow as tf
from tensorflow import keras
import numpy as np


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash

from mlapp.db import get_db

bp = Blueprint('analyser', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/analyser')
def analyser():
    return render_template('analyser.html')

@bp.route("/predict/<string:comment>", methods=['GET','POST'])
def predict(comment):
    model = keras.models.load_model("model")
    comment_array = np.array(comment.numpy())
    prediction = model.predict(comment_array)
    return jsonify(prediction)

@bp.route("/predict", methods=['POST'])
def test():
    # test_comment = "test "+comment
    req = request.get_json()
    print(req)
    model = keras.models.load_model("model")
    comment_array = np.array([req['comment']])
    prediction_value = (model.predict(comment_array, verbose=0)[0][0]).item()
    print(type(prediction_value))
    prediction = get_classification(prediction_value)
    response = make_response(jsonify({"prediction": prediction,"comment":req['comment']}),200)
    return response
    
def get_classification(prediction: float) -> str:
    """Takes the models prediction value and returns the classification.

    If the prediction value is >=0.5 then it is classified as Misinformation, 
    otherwise it is neutral.    

    Args:
        prediction (float): The prediction value of the model.

    Returns:
        str: The binary classification of the comment; can be either "Misinformation 
        or neutral.
    """
    if(prediction>=0.5):
        return "Misinformation"
    else:
        return "Neutral"
