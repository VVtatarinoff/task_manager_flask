from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from task_manager import db
from task_manager import login_manager


class User(UserMixin, db.Model):
    """User account."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(70))
    last_name = db.Column(db.String(70))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    password_hash = db.Column(db.String(200), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    role_id = db.Column(db.Integer, ForeignKey('roles.id'))

    @property
    def password(self):
        pass

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return "<User %r>" % self.name


class AnonymousUser(AnonymousUserMixin):

    @staticmethod
    def can(self, permissions):
        return False

    @staticmethod
    def is_administrator(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    REVIEW = 0x01
    EXECUTE = 0x02
    MANAGE = 0x04
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default_flag = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Executor': (Permission.REVIEW |
                     Permission.EXECUTE, True),
            'Manager': (Permission.REVIEW |
                          Permission.EXECUTE |
                          Permission.MANAGE, False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
        if role is None:
            role = Role(name=r)
        role.permissions = roles[r][0]
        role.default_flag = roles[r][1]
        try:
            db.session.add(role)
            db.session.commit()
        except:
            db.session.rollback()
