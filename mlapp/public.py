"""
This module contains view functions for the public views and related functions.

Functions:
- index: Render the index page template as a string which Flask uses as the body of the response.
- about: Render the about page template as a string which Flask uses as the body of the response.

"""
from flask import (
    Blueprint, render_template
)
public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index() -> str:
    """The index view function.

    Renders the landing page with navigation to most other parts of the application.

    Returns
    -------
    str 
        A rendered template string for the index page.
    """
    return render_template('public/index.html')

@public_bp.route('/about')
def about() -> str:
    """The about view function.

    Renders the about page which has details about the application. 

    Returns
    -------
    str
        A rendered template string for the about page.
    """
    return render_template('public/about.html')