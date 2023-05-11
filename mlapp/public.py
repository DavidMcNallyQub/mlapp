"""
This module contains view functions that do no require authentication and their related functions.

Functions:
- index: View function used to render the index page.
- about: View function used to render the about page. 

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
        A rendered template string for the index page which Flask uses as the body of the response. 
    """
    return render_template('public/index.html')

@public_bp.route('/about')
def about() -> str:
    """The about view function.

    Renders the about page which has details about the application. 

    Returns
    -------
    str
        A rendered template string for the about page which Flask uses as the body of the response.
    """
    return render_template('public/about.html')