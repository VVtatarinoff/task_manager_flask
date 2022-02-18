from datetime import date

from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField,
                     SelectMultipleField, DateField)
from wtforms.validators import Length, DataRequired, Regexp, ValidationError, InputRequired

from task_manager.auths.models import User
from task_manager.statuses.models import Status
from task_manager.tags.models import Tag


def check_data_not_in_past():
    msg = 'The date could not be in the past'

    def _gt_today(form, field):
        today = date.today()
        if field.data and field.data < today:
            raise ValidationError(msg)

    return _gt_today


def check_selected(msg):
    def _not_none(form, field):
        if field.data == "None":
            raise ValidationError(msg)

    return _not_none


def check_not_empty(msg=''):

    def _is_empty(form, field):
        if not field.data:
            raise ValidationError(msg)

    return _is_empty


class StepTask(FlaskForm):
    step_name = SelectField('Step name', validators=[
        check_selected("Choose the step to include")])
    start_step_date = DateField('Start date',
                                validators=[
                                    check_data_not_in_past()])
    planned_step_end = DateField('Deadline',
                                 validators=[
                                             check_data_not_in_past()])
    add_step = SubmitField('Add step')
    del_step = SubmitField('X')
    del_option = SelectField('choice to delete')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        statuses = Status.query.all()
        choices = [(None, '   <------>     ')] + list(
            map(lambda x: (x.id, x.name), statuses))
        self.step_name.choices = choices
        self.del_option.choices = self.del_option.choices or []

    def check_adding_step_form(self):
        """
                Validates the form by calling `validate` on each field.
                Returns `True` if no errors occur.
                """
        success = True
        fields = [self.step_name, self.planned_step_end,
                  self.start_step_date]
        for field in fields:
            success = success and field.validate(self)
        if success and (
                self.planned_step_end.data < self.start_step_date.data):
            success = False
            self.start_step_date.errors = list(
                *self.start_step_date.errors) + [
                "Start date greater than deadline"]
        return success

    def clear_step_data(self):
        self.step_name.data=""
        self.start_step_date.data = self.start_step_date.raw_data = None
        self.planned_step_end.data = self.planned_step_end.raw_data = None


class TaskBody(FlaskForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        executors = User.query.filter(User.role_id.in_([1, 2])).all()
        self.executor.choices = [(None, '   <------>     ')] + list(
            map(lambda x: (x.id, f"{x.first_name} {x.last_name}"),
                executors))
        tags = Tag.query.all()
        self.tags.choices = [(None, '   <------>     ')] + list(
            map(lambda x: (x.id, x.name), tags))



class CreateTask(TaskBody, StepTask):
    pass


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
