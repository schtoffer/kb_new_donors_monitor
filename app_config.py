import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# App configuration
class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/donors.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    DEBUG = False
    TESTING = False
    
    # Azure specific configuration
    PORT = int(os.environ.get('PORT', 8000))
    HOST = '0.0.0.0'
    
    # Template configuration
    TEMPLATES_AUTO_RELOAD = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Choose configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'default')
    return config[env]
