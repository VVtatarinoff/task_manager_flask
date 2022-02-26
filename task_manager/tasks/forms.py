import re
from datetime import date

from flask import request
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField,
                     SelectMultipleField, DateField)
from wtforms.validators import (Length, DataRequired,
                                Regexp, ValidationError)

from task_manager.auths.models import User
from task_manager.statuses.models import Status
from task_manager.tags.models import Tag
from task_manager.tasks.models import Task, Plan


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
    def _is_empty(_, field):
        if not field.data:
            raise ValidationError(msg)

    return _is_empty


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
        self.executor_choices = [(None, '   <------>     ')] + list(
            map(lambda x: (x.id, f"{x.first_name} {x.last_name}"),
                executors))
        self.executor.choices = self.executor_choices
        tags = Tag.query.all()
        self.tags.choices = [(None, '   <------>     ')] + list(
            map(lambda x: (x.id, x.name), tags))


class CreateTask(TaskBody):
    STATUS_ID = 'status_id'
    add_step_button = SubmitField('Add step')
    del_step_button = SubmitField('Delete selected')
    del_option = SelectField('choice to delete', validate_choice=False)

    def __init__(self, task: Task = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        statuses = Status.query.all()
        self.step_choices = [(None, '   <------>     ')] + list(
            map(lambda x: (x.id, x.name), statuses))
        self.del_option.choices = self.del_option.choices or []
        if task:
            self.init_from_task(task)
            return
        if request.form:
            self.init_from_form()
        else:
            self.ids = [-1]
            self.add_step(-1)

    def set_ids(self, args):
        reg_exp = f'(?<={self.STATUS_ID}_)' + r'(-)?\d+'
        self.ids = list(map(lambda y: y[0],
                            filter(
                                bool,
                                (map(lambda x: re.search(reg_exp, x), args)))))
        self.ids = list(map(int, self.ids))

    def init_from_task(self, task: Task):
        pass

    def get_names_step_fields(self, id):
        return [f'{self.STATUS_ID}_{id}', f'start_date_{id}',
                f'actual_start_{id}', f'planned_end_{id}',
                f'actual_end_date_{id}', f'executor_id_{id}',
                f'actual_start_{id}', f'actual_end_date_{id}']

    def init_from_form(self):
        fields = request.form
        self.set_ids(list(fields.keys()))

        for id in self.ids:
            step_fields = self.get_names_step_fields(id)
            kwargs = dict(map(
                lambda x: (
                    x, request.form[x] if (x in request.form.keys()) else None),
                step_fields))
            self.add_step(id, **kwargs)

    @staticmethod
    def convert_string_to_date(date_string: str) -> date:
        if not date_string or date_string == 'None':
            return
        if isinstance(date_string, date):
            return date_string
        year, month, day = tuple(map(int, date_string.split('-')))
        return date(year, month, day)

    def set_bound_field(self, name='default',
                        field_type=StringField, data=None, **kwargs):
        field = field_type(name, **kwargs)
        bound_field = field.bind(self, name)
        bound_field.data = data
        setattr(self, name, bound_field)

    def set_step_fields(self, id, **kwargs):
        names = self.get_names_step_fields(id)
        for name in names:
            data = kwargs.get(name, None)
            if self.STATUS_ID in name:
                self.set_bound_field(name=name,
                                     field_type=SelectField,
                                     data=str(data),
                                     choices=self.step_choices)
            elif 'executor_id' in name:
                self.set_bound_field(name=name,
                                     data=str(data),
                                     field_type=SelectField,
                                     choices=self.executor_choices
                                     )
            else:
                self.set_bound_field(name=name,
                                     data=self.convert_string_to_date(data),
                                     field_type=DateField,
                                     )


    def add_step(self, id, new=False, **kwargs):

        def get_next_id():
            if self.STATUS_ID in kwargs:
                id = kwargs[self.STATUS_ID] - 1
            else:
                id = min([0] + self.ids) - 1
            return id

        if new:
            id = get_next_id()
            self.ids.append(id)
            kwargs[f'executor_id_{id}']=self.executor.data
        self.set_step_fields(id, **kwargs)

    def delete_step(self):
        for id in self.del_option.raw_data:
            names = self.get_names_step_fields(id)
            for name in names:
                delattr(self, name)
        ids = set(self.ids)
        ids.difference_update(set(map(int, self.del_option.raw_data)))
        self.ids = list(ids)
        self.del_option.choices = []

    def check_create_task_form(self):  # noqa 901
        success = super().validate_on_submit()
        if not success:
            return success
        statuses = list(
            map(lambda x: x.id, Status.query.all()))
        for id in self.ids:
            end = f'planned_end_{id}'
            start = f'start_date_{id}'
            step = f'{self.STATUS_ID}_{id}'
            if (self.__dict__[step].data == 'None') or (
                    int(self.__dict__[step].data) not in statuses):
                self.__dict__[step].errors = list(
                    *self.__dict__[step].errors
                ) + ["Choose the step"]
                return False
            if not self.__dict__[end].data:
                self.__dict__[end].errors = list(
                    *self.__dict__[end].errors
                ) + ["Choose the planned deadline"]
                return False
            if not self.__dict__[start].data:
                self.__dict__[start].errors = list(
                    *self.__dict__[start].errors
                ) + ["Choose thee planned start date"]
                return False
            if (self.__dict__[end].data < self.__dict__[start].data):
                self.__dict__[start].errors = list(
                    *self.__dict__[start].errors
                ) + ["Start date greater than deadline"]
                return False
        return success


class UpdateTask(CreateTask):
    submit = SubmitField('Update')

    def init_from_task(self, task: Task):
        self.task_name.data = task.name
        self.description.data = task.description
        self.executor.data = str(task.executor_id)
        tags = list(map(lambda x: str(x.id), task.tags))
        self.tags.data = tags
        self.ids = list(map(lambda x: x.id, task.plan))
        for id in self.ids:
            step = Plan.query.filter_by(id=id).one()
            kwargs = dict(
                map(lambda x: (f'{x}_{id}', step.__dict__[x]),
                    step.__dict__))
            self.set_step_fields(id, **kwargs)
