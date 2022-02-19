from datetime import date
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
            self.steps: list = []
        elif plan:
            self.extract_steps_from_plan()
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
            step_dict['actual_start'] = step.actual_start
            step_dict['planned_end'] = self.convert_date_to_string(
                step.planned_end)
            step_dict['actual_end_date'] = self.convert_date_to_string(
                step.actual_end_date)
            step_dict['executor_id'] = step.executor_id
            step_dict['executor_name'] = step.user_executor
            self.steps += [step_dict]

    def add_step_from_form(self, form, status_id: int, executor_id: int = None) -> None:
        """
        update session variable with new step
        Args:
            executor_id:
            status_id: pk in statuses to connect to
            form: the wtf form
        Returns:
            None
        """
        id = min(chain([0], map(lambda x: int(x['id']), self.steps))) - 1
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
             'start_date': self.convert_date_to_string(form.start_date.data),
             'actual_start': self.convert_date_to_string(form.actual_start.data),
             'planned_end': self.convert_date_to_string(form.planned_end.data),
             'actual_end_date': self.convert_date_to_string(form.actual_end_date.data),
             'executor_id': executor_id,
             'executor_name': executor_name
             }
        )
        self.save_to_session()

    def remove_step_from_session(self, plan_id: int) -> None:
        """
        removes step from plan stored in session
        plan_id should be vali id
        Args:
            plan_id: plan_id in self.steps dictionaryelement

        Returns:
            None
        """
        index = dict(map(lambda x: (x[1]['plan_id'], x[0]), enumerate(self.steps)))[plan_id]
        self.steps.pop(index)
        self.save_to_session()

    @staticmethod
    def convert_date_to_string(raw_date: date) -> str:
        return raw_date.strftime('%d-%m-%Y')

    @staticmethod
    def convert_string_to_date(date_string: str) -> date:
        day, month, year = tuple(map(int, date_string.split('-')))
        return date(year, month, day)
