
import sqlite3
from flask import g

DATABASE = "app.db"

def get_db():
    """
    Returns a SQLite3 connection tied to the Flask request context.
    """
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db

def close_db(e=None):
    """
    Closes the SQLite3 connection at the end of the request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    """
    Registers teardown cleanup with Flask.
    """
    app.teardown_appcontext(close_db)
