from sqlalchemy import ForeignKey
from datetime import datetime
from task_manager import db


class Status(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)