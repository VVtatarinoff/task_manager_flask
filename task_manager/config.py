import os
from pathlib import Path

from dotenv import load_dotenv


current_dir = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = Path(__file__).resolve().parent.parent

env_path = Path(BASE_DIR) / '.env'
load_dotenv()
load_dotenv(dotenv_path=env_path)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    TASK_MANAGER_ADMIN = os.getenv('EMAIL_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    FLASK_ENV = 'development'
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL')


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL') or ('sqlite:///' + os.path.join(current_dir, 'data.sqlite'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
