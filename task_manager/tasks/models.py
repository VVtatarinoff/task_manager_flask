from sqlalchemy import ForeignKey, Table
from datetime import datetime, date
from task_manager import db
from task_manager.tags.models import Tag  # noqa 401
from task_manager.statuses.models import Status  # noqa 401


class Plan(db.Model):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    actual_start = db.Column(db.Date)
    planned_end = db.Column(db.Date, nullable=False)
    actual_end_date = db.Column(db.Date)
    status_id = db.Column(db.Integer, ForeignKey('statuses.id'))
    task_id = db.Column(db.Integer, ForeignKey('tasks.id'))
    executor_id = db.Column(db.Integer, ForeignKey('users.id'))


class IntermediateTaskTag(db.Model):
    __tablename__ = 'intermediate_task_tags'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, ForeignKey('tasks.id'))
    tag_id = db.Column(db.Integer, ForeignKey('tags.id'))


association_table = Table('intermediate_task_tags', db.metadata)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    creation_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(200))
    manager_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    executor_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    planned_end_date = db.Column(db.Date, nullable=False)
    actual_end_date = db.Column(db.Date)
    post_to_review = db.Column(db.Boolean, default=False, nullable=False)

    tags = db.relationship('Tag', backref='task', secondary=association_table)
    plan = db.relationship('Plan', backref='task', lazy='dynamic')
