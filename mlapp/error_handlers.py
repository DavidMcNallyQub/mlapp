"""
A module that contains error handling functions that return a reponse when a type of error is raised.

Functions:
- page_not_found:
- internal_server_error:
"""
from flask import render_template

def page_not_found(e) -> tuple[str, int]:
    """Displays a custom Error page for a 404 status code.

    _extended_summary_

    Parameters
    ----------
    e : _type_
        _description_

    Returns
    -------
    tuple(str, int)
        A tuple with the error template rendered as a string and the status code as an integer.
    """
    print(e)
    return render_template('error_handlers/404.html'), 404


def internal_server_error(e) -> tuple[str, int]:
    """Displays a custom Error page for a 500 status code.

    _extended_summary_

    Parameters
    ----------
    e : _type_
        _description_

    Returns
    -------
    tuple(str, int)
        A tuple with the error template rendered as a string and the status code as an integer."""
    return render_template('500.html'), 500