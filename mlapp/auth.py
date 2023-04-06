import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from mlapp.db import get_db

from typing import Union

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register() -> Union[Response, str]:
    """The register view function.           

    Process a request to the register URL.
    For a POST request retrieve the user's email and password and register the user. 
    After registration, redirect the user to the login page. 
    If an email or a password is not provided, or the user is already registered in the database, 
    render the register page and Flash corresponding error. 
    For a GET request, render the register page.

    Returns:
        Union[Response, str]: For a successful POST request return a Redirect Reponse. 
        For a GET request or a error on a POST request, return a Rendered template string.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not email:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (email, password) VALUES (?, ?)",
                    (email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login() -> Union[Response, str]:
    """The login view function.

    Process a request to the login URL.
    For a POST request, retrieve the user's email and password and log the user in.
    After log-in, redirect the user to the homepage. 
    If the user's email does not exist in the database or their password does not match,
    render the login page and Flash any error.
    For a GET request, render the login page. 

    Returns:
        Union[Response, str]: For a successful POST request return a Redirect Reponse. 
        For a GET request or a error on a POST request, return a Rendered template string.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """Check if a user_id is stored in the session, gets that users data from the database 
    and store it on g.user. 

    For any requested URL load_logged_in_user will be run. This allows a logged in user's
    information to be made available to other view functions. If there is no user_id, g.user
    will be None. 
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout() -> Response:
    """Remove the current user_id from the session. 

    A user's will not be loaded on subsequent requests (See load_logged_in_user()). 

    Returns:
        Response: _description_
    """
    session.clear()
    return redirect(url_for('index'))


def login_required(view) -> Union[Response, str]:
    """A decorator that wraps the origional view it is applied to and returns an new view function.

    The new view function checks if a user is logged in. 
    If a user is not logged in, the user is directed to the login page. 
    Otherwise, the original view function is returned and continues normally.
    
    Args:
        view (_type_): _description_

    Returns:
        Union[Response, str]: _description_
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
