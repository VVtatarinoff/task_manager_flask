import copy
from datetime import date, datetime
from itertools import chain

from flask import session

from task_manager.auths.models import User
from task_manager.statuses.models import Status
from task_manager.tasks.models import Plan


class SessionPlan(object):
    """
    the class helping to deal with editing the plan
    for specific task in template
    the session object - list of dictionaries
    each dictionary has the following keys:
        'plan_id' - pk in table 'plans' in DB if positive
            if negative - temporarily id in memory
        'status_id' - pk in table 'statuses' in DB
        'status_name' - name corresponding to status_id
        'start_date' - planned start of step
        'actual_start' - actual start of step
        'planned_end' - planned deadline
        'actual_end_date' - actual end of step
        'executor_id' - pk of 'users' table
        'executor_name' - username, corresponding to executor_id
    """

    def __init__(self, new: bool = False, plan: Plan = None) -> None:
        if new:
            session['steps'] = []
        if plan:
            self.extract_steps_from_plan(plan)
        else:
            self.steps = session['steps']
        self.save_to_session()

    def save_to_session(self):
        session['steps'] = self.steps

    def extract_steps_from_plan(self, plan: Plan):
        """

        Args:
            plan: the orm query object from Plan

        Returns:
            list containing dictionaries of steps in plan
            to upload in session
        """
        self.steps = []
        for step in plan:
            step_dict = dict()
            step_dict['plan_id'] = step.id
            step_dict['status_id'] = step.status.id
            step_dict['status_name'] = step.status.name
            step_dict['start_date'] = self.convert_date_to_string(
                step.start_date)
            step_dict['actual_start'] = self.convert_date_to_string(
                step.actual_start)
            step_dict['planned_end'] = self.convert_date_to_string(
                step.planned_end)
            step_dict['actual_end_date'] = self.convert_date_to_string(
                step.actual_end_date)
            step_dict['executor_id'] = step.executor_id
            step_dict['executor_name'] = step.executor.name
            self.steps += [step_dict]
        self._sort_steps()

    def add_step_from_form(self, form, status_id: int,
                           executor_id: int = None) -> None:
        """
        update session variable with new step
        Args:
            executor_id:
            status_id: pk in statuses to connect to
            form: the wtf form
        Returns:
            None
        """

        def get_str_date_from_field(field_name):
            if field_name in form:
                return self.convert_date_to_string(form[field_name].data)
            else:
                return None

        id = min(chain([0], map(lambda x: int(x['plan_id']), self.steps))) - 1
        status = Status.query.filter_by(id=status_id).one()
        if executor_id:
            executor = User.query.filter_by(id=executor_id).one()
            executor_name = executor.name
        else:
            executor_name = ''
        self.steps.append(
            {'plan_id': id,
             'status_id': status.id,
             'status_name': status.name,
             'start_date': get_str_date_from_field('start_date'),
             'actual_start': get_str_date_from_field('actual_start'),
             'planned_end': get_str_date_from_field('planned_end'),
             'actual_end_date': get_str_date_from_field('actual_end_date'),
             'executor_id': executor_id,
             'executor_name': executor_name
             }
        )
        self._sort_steps()
        self.save_to_session()

    def remove_step_from_session(self, plan_ids: list) -> None:
        """
        removes steps from plan stored in session
        numbers in plan_ids should be valiid
        Args:
            plan_ids: list of plan_id in self.steps dictionary element to remove

        Returns:
            None
        """
        for id in plan_ids:
            index = dict(map(lambda x: (x[1]['plan_id'],
                                        x[0]), enumerate(self.steps)))[int(id)]
            self.steps.pop(index)
        self._sort_steps()
        self.save_to_session()

    def _sort_steps(self) -> None:
        self.steps.sort(
            key=lambda k: self.convert_string_to_date(k['start_date']))

    @property
    def plan(self):
        steps_copy = copy.deepcopy(self.steps)
        for step in steps_copy:
            step['start_date'] = self.convert_string_to_date(
                step['start_date'])
            step['actual_start'] = self.convert_string_to_date(
                step['actual_start'])
            step['planned_end'] = self.convert_string_to_date(
                step['planned_end'])
            step['actual_end_date'] = self.convert_string_to_date(
                step['actual_end_date'])
        return steps_copy

    @property
    def raw_steps(self):
        return self.steps

    @staticmethod
    def convert_date_to_string(raw_date: date) -> str:
        if isinstance(raw_date, (date, datetime)):
            return raw_date.strftime('%d-%m-%Y')
        return ''

    @staticmethod
    def convert_string_to_date(date_string: str) -> date:
        if not date_string or date_string == 'None':
            return
        day, month, year = tuple(map(int, date_string.split('-')))
        return date(year, month, day)
