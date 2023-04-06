import sqlite3
from sqlite3 import Connection
import click
from flask import current_app, g

def get_db() -> Connection:
    """Return the SQLite3 database connection.

    The connection to the SQLite database is stored in the g object. g is unique for 
    all requests and can store data that can be accessed by multiple functions during requests.
    get_db() will be called when the application has been created and is handling a request, 
    so current_app() can be used. 
    sqlite3.connect() establishes a connection to the file pointed at by the DATABASE
    configuration key.
    Columns can be accessed by name as sqlite3.Row tells the connection to return rows that
    act similarly to dictionaries.

    Returns:
        Connection: A SQLite3 Connection object.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close a database connection if it exists.

    Checks if g.db was set, if so, db is removed from the g object and closed() is called
    on db.

    Args:
        e (_type_, optional): _description_. Defaults to None.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialise the SQLite3 database.
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables.
    """
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register the close_db() and init_db_command() with the application instance. 


    close_db() will be called after a response and init_db_command() will add a new command
    that can be called with the 'flask' command

    Args:
        app (Flask): A Flask application instance.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)