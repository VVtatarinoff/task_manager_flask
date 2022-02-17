from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

ADMINISTRATOR = {
    'email': 'vova@mail.ru',
    'name': 'vova',
    'first_name': 'Vladimir',
    'last_name': 'Kirov',
    'password': '123456'}
EXECUTOR = {
    'email': 'ivan@mail.ru',
    'name': 'ivan',
    'first_name': 'Ivan',
    'last_name': 'Executor',
    'password': '123456'}
MANAGER = {
    'email': 'anna@mail.ru',
    'name': 'anna',
    'first_name': 'Anna',
    'last_name': 'Manager',
    'password': '123456'}

SQL_CLEAR = ["DELETE FROM intermediate_task_tags",
             "DELETE FROM plans",
             "DELETE FROM tasks",
             "DELETE FROM tags",
             "DELETE FROM statuses",
             "DELETE FROM roles",
             "DELETE FROM users",
             ]
SQL_ROLES = [
    "INSERT INTO roles (name, default_flag, permissions) "
    "VALUES ('Executor','True','3')",
    "INSERT INTO roles (name, default_flag, permissions) "
    "VALUES ('Manager','False','7')",
    "INSERT INTO roles (name, default_flag, permissions) "
    "VALUES ('Administrator','False','255')", ]
SQL_USERS = [
    "INSERT INTO users (id, email, name, first_name, last_name, "
    "password_hash, role_id, 'creation_date')"
    f"VALUES (1, '{EXECUTOR['email']}', '{EXECUTOR['name']}', "
    f"'{EXECUTOR['first_name']}', '{EXECUTOR['last_name']}', "
    f"'{generate_password_hash(EXECUTOR['password'])}',1,"
    f"'{datetime.utcnow()}');",
    "INSERT INTO users (id, email, name, first_name, last_name, "
    "password_hash, role_id,'creation_date')"
    f"VALUES (2, '{MANAGER['email']}', '{MANAGER['name']}', "
    f"'{MANAGER['first_name']}', '{MANAGER['last_name']}', "
    f"'{generate_password_hash(MANAGER['password'])}',2, "
    f"'{datetime.utcnow()}');",
    "INSERT INTO users (id, email, name, first_name, last_name, "
    "password_hash, role_id,'creation_date')"
    f"VALUES (3, '{ADMINISTRATOR['email']}', '{ADMINISTRATOR['name']}', "
    f"'{ADMINISTRATOR['first_name']}', '{ADMINISTRATOR['last_name']}', "
    f"'{generate_password_hash(ADMINISTRATOR['password'])}', 3, "
    f"'{datetime.utcnow()}');"
]

TAGS = [{'i': 1, 'name': 'average', 'description': 'average'},
        {'i': 2, 'name': 'simple', 'description': 'simple'},
        {'i': 3, 'name': 'important', 'description': 'average'},
        {'i': 4, 'name': 'urgent', 'description': 'urgent'}]

SQL_TAGS = []
for i in range(len(TAGS)):
    SQL_TAGS += [
        "INSERT INTO tags (id, name, description, creation_date) "
        f"VALUES ({TAGS[i]['i']}, '{TAGS[i]['name']}', "
        f"'{TAGS[i]['description']}', '{datetime.utcnow()}')"
    ]

STATUSES = [{'i': 1, 'name': 'planning', 'description': 'planning phase'},
            {'i': 2, 'name': 'designing', 'description': 'designing phase'},
            {'i': 3, 'name': 'coding', 'description': 'coding phase'},
            {'i': 4, 'name': 'testing', 'description': 'testing phase'}]
SQL_STATUSES = []
for i in range(len(STATUSES)):
    SQL_STATUSES += [
        "INSERT INTO statuses (id, name, description, creation_date) "
        f"VALUES ({STATUSES[i]['i']}, '{STATUSES[i]['name']}', "
        f"'{STATUSES[i]['description']}', '{datetime.utcnow()}')"
    ]

TASK = [{'i':1, 'name': 'first_task',
         'description': 'first task in database - testing',
          'manager_id': 2, 'executor_id': 1,
          'start_date':datetime.utcnow(),
          'planned_end_date':
              datetime.utcnow() + timedelta(days=15),
         'post_to_review': 0}]

SQL_TASKS = []
for i in range(len(TASK)):
    SQL_TASKS += [
        "INSERT INTO tasks (id, name, description, creation_date,"
        " manager_id, executor_id, start_date, planned_end_date, post_to_review) "
        f"VALUES ({TASK[i]['i']}, '{TASK[i]['name']}', "
        f"'{TASK[i]['description']}', '{datetime.utcnow()}' ,"
        f"{TASK[i]['manager_id']}, {TASK[i]['executor_id']}, "
        f"'{TASK[i]['start_date']}', '{TASK[i]['planned_end_date']}',"
        f" {TASK[i]['post_to_review']})"
    ]


PLAN =[{'i':1, 'start_date': TASK[0]['start_date'],
        'planned_end': TASK[0]['planned_end_date'],
        'status_id': STATUSES[0]['i'],
        'executor_id': 1,
        'task_id': TASK[0]['i']},
        {'i':2, 'start_date': TASK[0]['start_date'],
        'planned_end': TASK[0]['planned_end_date'],
        'status_id': STATUSES[1]['i'],
        'executor_id': 1,
        'task_id': TASK[0]['i']}
       ]
SQL_PLANS = []
for i in range(len(PLAN)):
    SQL_PLANS += [
        "INSERT INTO plans (id, start_date, planned_end, status_id, executor_id, task_id) "
        f"VALUES ({PLAN[i]['i']}, '{PLAN[i]['start_date']}', "
        f"'{PLAN[i]['planned_end']}', "
        f"{PLAN[i]['status_id']}, {PLAN[i]['executor_id']}, "
        f"{PLAN[i]['task_id']})"
    ]

TASK_TAG =[{'i': 1,
            'task_id': TASK[0]['i'],
            'tag_id': TAGS[0]['i']}]
SQL_TASK_TAGS = []
for i in range(len(TASK_TAG)):
    SQL_TASK_TAGS += [
        "INSERT INTO intermediate_task_tags (id, task_id, tag_id) "
        f"VALUES ({TASK_TAG[i]['i']}, {TASK_TAG[i]['task_id']}, "
        f"{TASK_TAG[i]['tag_id']})"]


SQLS = SQL_CLEAR + SQL_ROLES + SQL_USERS + SQL_TAGS
SQLS += SQL_STATUSES + SQL_TASKS + SQL_PLANS + SQL_TASK_TAGS
