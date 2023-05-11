"""
This module is used to test retrieving a database connection, closing the database connection
and initilising the database.

Functions:
- test_get_close_db: Test for the database connection.
- test_init_db_command: Test for the init-db Click command. 

"""

import sqlite3
import pytest
from mlapp.db import get_db

def test_get_close_db(app):
    """Test the database connection.

    Test the same database connection is retrieved each time it is called and
    the connection closes after the context.

    Parameters
    ----------
    app : Flask
        An instance of the Flask application object with the current request context.
    """
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    """Test the init-db command.

    Test that the init-db command calls the init_db_command function and outputs a
    message that includes the word "Initialized".

    Parameters
    ----------
    runner : FlaskCliRunner
        A CliRunner for testing a Flask app’s CLI commands.
    monkeypatch : MonkeyPatch
        Helper to conveniently monkeypatch attributes/items/environment variables/syspath.
    """

    class Recorder(object):
        """A class used to record if the fake_init_db function has been called.

        Parameters
        ----------
        object : object
            The base class of the class hierarchy.
        """

        called = False

    def fake_init_db():
        """Records if this function is called instead of init_db.

        If this function is called, set Recorder.called = True.
        """
        Recorder.called = True

    # Instead of init_db being called within init_db_command, fake_init_db will be called instead.
    monkeypatch.setattr('mlapp.db.init_db', fake_init_db)
    # Use the runner fixture to call the init-db command by name.
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called