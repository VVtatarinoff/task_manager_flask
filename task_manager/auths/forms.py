from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField
from wtforms.validators import Email, EqualTo, Length, DataRequired, ValidationError, Regexp
from wtforms.widgets import HiddenInput

from task_manager.auths.models import User, Role


class CreateUser(FlaskForm):
    email = StringField('Email: ',
                        validators=[Email("Некорректный адрес"),
                                    Length(max=100),
                                    DataRequired()])
    name = StringField('Name: ',
                       validators=[Length(max=20),
                                   DataRequired(),
                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    first_name = StringField('First name: ',
                             validators=[Length(max=70)])
    last_name = StringField('Last name: ',
                            validators=[Length(max=70)])
    psw1 = PasswordField('Enter password: ',
                         validators=[Length(min=5, max=70),
                                     DataRequired(), ])
    psw2 = PasswordField(
        'Confirm password: ',
        validators=[
            Length(min=5, max=70),
            DataRequired(),
            EqualTo(
                'psw1',
                message='Passwords must match')])
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    @staticmethod
    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Username already in use.')


class SignInForm(FlaskForm):
    email = StringField('Email: ',
                        validators=[Email("Некорректный адрес"),
                                    Length(max=100),
                                    DataRequired()])
    psw = PasswordField('Enter password: ',
                        validators=[Length(min=5, max=70),
                                    DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in')


class EditProfileForm(FlaskForm):
    first_name = StringField('First nam: ',
                        validators=[Length(max=70)])
    last_name = StringField('Last name: ',
                            validators=[Length(max=70)])
    location = StringField('Location', validators=[Length(max=70)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_name.data = self.first_name.data or user.first_name
        self.last_name.data = self.last_name.data or user.last_name
        self.location.data = self.location.data or user.location
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class EditProfileFormAdmin(EditProfileForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    role = SelectField('Role', coerce=int)

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.role.data = self.role.data  or user.role_id
        self.email.data = self.email.data or user.email
