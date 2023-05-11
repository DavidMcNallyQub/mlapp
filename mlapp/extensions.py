"""
A module that contains extensions to the Flask application.
"""
from flask_sqlalchemy import SQLAlchemy
# create SQLAlchemy database abstraction layer extension
dbase = SQLAlchemy()