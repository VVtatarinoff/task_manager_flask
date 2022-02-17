from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField,
                     SelectMultipleField, DateField)
from wtforms.validators import Length, DataRequired, Regexp


class CreateTask(FlaskForm):
    task_name = StringField('Name: ',
                            validators=[Length(min=4, max=20),
                                        DataRequired(),
                                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                               'Name must have only letters, '
                                               'numbers, dots or underscores')])
    description = StringField('Description: ',
                              validators=[Length(max=200),
                                          DataRequired(), ])
    executor = SelectField('Executor ', validators=[DataRequired()])
    tags = SelectMultipleField('Tags ')
    submit = SubmitField('Create')
    step_name = SelectField('Step name')
    start_step_date = DateField('Start date')
    planned_step_end = DateField('Deadline')
    add_step = SubmitField('Add step')
    del_step = SubmitField('X')
    del_option = SelectField('choice to delete')

    def __init__(self, executors=[], tags=[], step_names=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor.choices = executors
        self.tags.choices = tags
        self.step_name.choices = step_names


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
