from flask import g
from pymongo import MongoClient
from config import Config

def get_db():
    if 'db' not in g:
        client = MongoClient(Config.MONGO_URI)
        g.db = client['library_db']  # Explicitly use library_db database
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    # MongoClient manages its own connection pool, so strictly closing isn't always necessary per request,
    # but it's good practice if we were creating new clients.
    # Here we just clear the reference.
    pass

def init_app(app):
    app.teardown_appcontext(close_db)
