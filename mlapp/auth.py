"""
This module contains a Blueprint to register view functions for authorisation.

Functions:
- 
"""
import functools
from typing import Union
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from werkzeug.security import check_password_hash, generate_password_hash
from mlapp.db import get_db
from mlapp.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=('GET', 'POST'))
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
        reg_form = RegistrationForm(request.form)
        errors = {}
        # reg_form.validate populates reg_form.errors
        # reg_form.errors returns a dictionary of field keys and lists of field errors values.
        if not reg_form.validate():
            errors = reg_form.errors
        print(errors)
        if not errors:
            try:
                email = reg_form.email.data
                password = reg_form.password.data
                db = get_db()
                db.execute(
                    "INSERT INTO user (email, password) VALUES (?, ?)",
                    (email, generate_password_hash(password)),
                )
                db.commit()
                # errors are mirrored in the style of the wtform Form.errors output.
            except db.IntegrityError as e:
                errors.update({"Registraition": [f"User {email} is already registered."]})
            except Exception:
                errors.update({"Unexpected": ["An unxpected error has occured during registration."]})
            else:
                flash("Account created!", category="success")
                return redirect(url_for("auth.login"))
        
        for category, message_list in errors.items():
            for message in message_list:
                flash(message, category=category)

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=('GET', 'POST'))
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
        login_form = LoginForm(request.form)
        errors = {}
        # login_form.validate populates reg_form.errors
        # login_form.errors returns a dictionary of field keys and lists of field errors values.
        if not login_form.validate():
            errors = login_form.errors
        
        if not errors:
            email = login_form.email.data
            password = login_form.password.data
            db = get_db()
            user = db.execute(
                'SELECT * FROM user WHERE email = ?', (email,)
            ).fetchone()
            # errors are mirrored in the style of the wtform Form.errors output.
            if user is None:
                errors.update({"email": ["Incorrect email."]})
            elif not check_password_hash(user['password'], password):
                errors.update({"password": ["Incorrect password."]})

            if not errors:
                session.clear()
                session['user_id'] = user['user_id']
                return redirect(url_for('index'))
            
            for category, message_list in errors.items():
                for message in message_list:
                    flash(message, category=category)

    return render_template('auth/login.html')

@auth_bp.before_app_request
def load_logged_in_user():
    """Check if a user_id is stored in the session, gets that user's data from the database 
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
            'SELECT * FROM user WHERE user_id = ?', 
            (user_id,)
        ).fetchone()

@auth_bp.route('/logout')
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
