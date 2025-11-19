from flask import g
from pymongo import MongoClient
from config import Config

def get_db():
    if 'db' not in g:
        client = MongoClient(Config.MONGO_URI)
        g.db = client['library_db']  
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    pass

def init_app(app):
    app.teardown_appcontext(close_db)
