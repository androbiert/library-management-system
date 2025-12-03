import os
from urllib.parse import urlparse, parse_qs

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_very_secret'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/library_db'
    
    # Babel Configuration
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'ar']
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    
    @staticmethod
    def get_db_name():
        """Extract database name from MongoDB URI"""
        uri = Config.MONGO_URI
        
        # For MongoDB Atlas (mongodb+srv://) or standard (mongodb://)
        if '/' in uri:
            # Parse the URI
            parsed = urlparse(uri)
            # Get the path (database name)
            db_name = parsed.path.lstrip('/')
            
            # Remove query parameters if present
            if '?' in db_name:
                db_name = db_name.split('?')[0]
            
            # Return db name or default
            return db_name if db_name else 'library_db'
        
        return 'library_db'
