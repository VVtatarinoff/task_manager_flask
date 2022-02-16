from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired, Regexp


class CreateTask(FlaskForm):
    name = StringField('Name: #',
                       validators=[Length(max=20),
                                   DataRequired(),
                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Name must have only letters, '
                                          'numbers, dots or underscores')])
    description = StringField('Description: ',
                              validators=[Length(max=200)])
    submit = SubmitField('Create')


class EditTaskForm(FlaskForm):
    name = StringField('Name: #',
                       validators=[Length(max=20),
                                   DataRequired(),
                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Name must have only letters, '
                                          'numbers, dots or underscores')])
    description = StringField('Description: ',
                              validators=[Length(max=200)])
    submit = SubmitField('Submit')

    def __init__(self, task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name.data = self.name.data or task.name
        self.description.data = self.description.data or task.description
        self.task = task
