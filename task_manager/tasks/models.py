from sqlalchemy import ForeignKey   # noqa 401
from datetime import datetime, date
from task_manager import db


class Plan(db.Model):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    planned_end = db.Column(db.Date, nullable=False)
    actual_end_date = db.Column(db.Date)
    status_id = db.Column(db.Integer, ForeignKey('statuses.id'))
    task_id = db.Column(db.Integer, ForeignKey('tasks.id'))


class IntermediateTaskPlan(db.Model):
    __tablename__ = 'intermediate_task_tags'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, ForeignKey('tasks.id'))
    tag_id = db.Column(db.Integer, ForeignKey('tags.id'))

class Task(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(200))
    manager_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    executor_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, default=date.utcnow, nullable=False)
    planned_end_date= db.Column(db.Date, nullable=False)
    actual_end_date = db.Column(db.Date, nullable=False)
    post_to_review = db.Column(db.Boolean, default=False, nullable=False)
