from datetime import datetime
from task_manager import db


class Status(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime,
                              default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(200))

    plans = db.relationship('Plan', backref='status', lazy='dynamic')
