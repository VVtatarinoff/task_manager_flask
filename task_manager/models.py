from task_manager.main import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from task_manager import db

#db = SQLAlchemy()
#db.init_app(app)

class Users(db.Model):
    __table_name__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(70))
    last_name = db.Column(db.String(70))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    password = db.Column(db.String(200), nullable=False)

