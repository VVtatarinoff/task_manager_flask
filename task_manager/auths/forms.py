from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Email, EqualTo, Length, DataRequired, ValidationError

from task_manager.models import User


class CreateUser(FlaskForm):
    email = StringField('Email: ',
                        validators=[Email("Некорректный адрес"),
                                    Length(max=100),
                                    DataRequired()])
    name = StringField('Name: ',
                       validators=[Length(max=20),
                                   DataRequired()])
    first_name = StringField('First name: ',
                             validators=[Length(max=70)])
    last_name = StringField('Last name: ',
                            validators=[Length(max=70)])
    psw1 = PasswordField('Enter password: ',
                         validators=[Length(min=5, max=70),
                                     DataRequired(),])
    psw2 = PasswordField(
        'Repeat password: ',
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
                        validators=[Email(),
                                    Length(max=100),
                                    DataRequired()])
    psw = PasswordField('Enter password: ',
                         validators=[Length(min=5, max=70),
                                     DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in')
