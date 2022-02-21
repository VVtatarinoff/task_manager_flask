from datetime import date
from operator import and_

from flask import session
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField,
                     SelectMultipleField, DateField)
from wtforms.validators import (Length, DataRequired,
                                Regexp, ValidationError)

from task_manager.auths.models import User
from task_manager.statuses.models import Status
from task_manager.tags.models import Tag
from task_manager.tasks.models import Task
from task_manager.tasks.session import SessionPlan


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
    status_name = SelectField('Step name', validators=[
        check_selected("Choose the step to include")])
    start_date = DateField('Start date',
                           validators=[
                               check_data_not_in_past()])
    planned_end = DateField(
        'Deadline',
        validators=[check_data_not_in_past()])
    add_step = SubmitField('Add step')
    del_step = SubmitField('X')
    del_option = SelectField('choice to delete')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        statuses = Status.query.all()
        choices = [(None, '   <------>     ')] + list(
            map(lambda x: (x.id, x.name), statuses))
        self.status_name.choices = choices
        self.del_option.choices = self.del_option.choices or []

    def check_adding_step_form(self):
        """
                Validates the form by calling `validate` on each field.
                Returns `True` if no errors occur.
                """
        success = True
        fields = [self.status_name, self.planned_end,
                  self.start_date]
        for field in fields:
            success = success and field.validate(self)
        if success and (
                self.planned_end.data < self.start_date.data):
            success = False
            self.start_date.errors = list(
                *self.start_date.errors
            ) + ["Start date greater than deadline"]
        return success

    def clear_step_data(self):
        self.status_name.data = ""
        self.start_date.data = self.start_date.raw_data = None
        self.planned_end.data = self.planned_end.raw_data = None


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
    executor = SelectField('Executor ', validators=[
        check_selected("Nominate an executor")])
    tags = SelectMultipleField('Tags ', validate_choice=False)
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

    def check_create_task_form(self):
        fields = [self.tags, self.task_name, self.description, self.executor]
        success = True
        for field in fields:
            success = success and field.validate(self)
        if success and list(
                Task.query.filter_by(name=self.task_name.data).all()):
            self.task_name.errors = [
                "Task with such name exists in database"]
            success = False
        return success


class EditTaskForm(TaskBody, StepTask):

    def __init__(self, task, request_form, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task
        self.task_name.data = self.task_name.data or task.name
        self.description.data = self.description.data or task.description
        self.executor.data = self.executor.data or str(task.executor_id)
        self.submit.label.text = "Change"
        if not (tags := session.get('tags', None)):
            tags = list(map(lambda x: str(x.id), task.tags))
            session['tags'] = tags
        self.tags.data = self.tags.data or tags
        self.set_steps_from_session(request_form)

    def set_steps_from_session(self, form):

        def set_bound_date_field(name):
            field = DateField(name,
                              validators=[
                                  check_data_not_in_past()])
            bound_field = field.bind(self, f'{name}_{step["plan_id"]}')
            bound_field.data = step[name]
            setattr(self, f'{name}_{step["plan_id"]}', bound_field)

        steps = SessionPlan(form, plan=self.task.plan.all())
        for step in steps.plan:
            set_bound_date_field('start_date')
            set_bound_date_field('planned_end')

    def check_update_task_form(self):
        fields = [self.tags, self.task_name, self.description, self.executor]
        success = True
        for field in fields:
            success = success and field.validate(self)
        tasks_with_same_name = list(
            Task.query.filter(and_(Task.name == self.task_name.data,
                                   Task.id != self.task.id)).all())
        if success and tasks_with_same_name:
            self.task_name.errors = [
                "Task with such name exists in database"]
            success = False
        return success
