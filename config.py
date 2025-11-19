import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_very_secret'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/library_db'

