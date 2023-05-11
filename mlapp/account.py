import functools
import tensorflow as tf
from tensorflow import keras
import numpy as np


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.exceptions import abort

from mlapp.db import get_db
from mlapp.auth import login_required

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route("/account")
@login_required
def account():
    user_id = session['user_id']
    db = get_db()
    user_issues = db.execute(
        'SELECT i.id, title, body, created, author_id, email'
        ' FROM issue i JOIN user u ON i.author_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC',
        (user_id)
    ).fetchall()
    return render_template("protected/account.html", user_issues=user_issues)

@bp.route("/update")
@login_required
def update_issue():

    return render_template("")