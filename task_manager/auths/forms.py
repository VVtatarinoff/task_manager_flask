from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Email, EqualTo, Length, DataRequired


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
                                     DataRequired()])
    psw2 = PasswordField(
        'Repeat password: ',
        validators=[
            Length(min=5, max=70),
            DataRequired(),
            EqualTo(
                'psw1',
                message='Пароли не совпадают')])
    submit = SubmitField('Register')


class SignInForm(FlaskForm):
    email = StringField('Email: ',
                        validators=[Email(),
                                    Length(max=100),
                                    DataRequired()])
    psw1 = PasswordField('Enter password: ',
                         validators=[Length(min=5, max=70),
                                     DataRequired()])
