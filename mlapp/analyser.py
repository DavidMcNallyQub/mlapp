import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
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
    