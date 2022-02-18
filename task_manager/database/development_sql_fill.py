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

TASK = [{'i': 1, 'name': 'first_task',
         'description': 'first task in database - testing',
         'manager_id': 2, 'executor_id': 1,
         'start_date': datetime.today(),
         'planned_end_date':
             datetime.today() + timedelta(days=15),
         'post_to_review': 0, 'actual_start': None,
         'actual_end': None},
        {'i': 2, 'name': 'second_task',
         'description': 'second task in database - testing',
         'manager_id': 2, 'executor_id': 1,
         'start_date': datetime.today() - timedelta(days=2),
         'planned_end_date':
             datetime.today() + timedelta(days=10),
         'post_to_review': 0, 'actual_start': f"'{str(datetime.today())}'",
         'actual_end': None},
        {'i': 3, 'name': 'third_task',
         'description': 'third task in database - testing',
         'manager_id': 2, 'executor_id': 2,
         'start_date': datetime.today() - timedelta(days=5),
         'planned_end_date':
             datetime.today() - timedelta(days=1),
         'post_to_review': 0,
         'actual_start': f"'{str(datetime.today() - timedelta(days=4))}'",
         'actual_end': None},
        {'i': 4, 'name': 'forth_task',
         'description': 'forth task in database - testing',
         'manager_id': 2, 'executor_id': 2,
         'start_date': datetime.today() - timedelta(days=15),
         'planned_end_date':
             datetime.today() - timedelta(days=4),
         'post_to_review': 0,
         'actual_start': f"'{str(datetime.today() - timedelta(days=10))}'",
         'actual_end': f"'{str(datetime.today() - timedelta(days=3))}'"}
        ]
comma = "'"
SQL_TASKS = []
for i in range(len(TASK)):
    SQL_TASKS += [
        "INSERT INTO tasks (id, name, description, creation_date,"
        " manager_id, executor_id, start_date, "
        "planned_end_date, post_to_review,"
        "actual_start_date, actual_end_date) "
        f"VALUES ({TASK[i]['i']}, '{TASK[i]['name']}', "
        f"'{TASK[i]['description']}', '{datetime.today()}' ,"
        f"{TASK[i]['manager_id']}, {TASK[i]['executor_id']}, "
        f"'{TASK[i]['start_date']}', '{TASK[i]['planned_end_date']}',"
        f" {TASK[i]['post_to_review']}, "
        f"{TASK[i]['actual_start'] if TASK[i]['actual_start'] else 'NULL'}, "
        f"{TASK[i]['actual_end'] if TASK[i]['actual_end'] else 'NULL'})"
    ]

PLAN = [{'i': 1, 'start_date': TASK[0]['start_date'],
         'planned_end': TASK[0]['planned_end_date'],
         'status_id': STATUSES[0]['i'],
         'executor_id': 1,
         'task_id': TASK[0]['i'],
         'actual_start': None, 'actual_end': None},
        {'i': 2, 'start_date': TASK[0]['start_date'],
         'planned_end': TASK[0]['planned_end_date'],
         'status_id': STATUSES[1]['i'],
         'executor_id': 1,
         'task_id': TASK[0]['i'],
         'actual_start': None, 'actual_end': None},
        {'i': 3, 'start_date': TASK[1]['start_date'],
         'planned_end': TASK[1]['planned_end_date'],
         'status_id': STATUSES[2]['i'],
         'executor_id': 1,
         'task_id': TASK[1]['i'],
         'actual_start': TASK[1]['actual_start'],
         'actual_end': None},
        {'i': 4, 'start_date': TASK[2]['start_date'],
         'planned_end': TASK[2]['planned_end_date'],
         'status_id': STATUSES[3]['i'],
         'executor_id': 2,
         'task_id': TASK[2]['i'],
         'actual_start': TASK[2]['actual_start'],
         'actual_end': None},
        {'i': 5, 'start_date': TASK[3]['start_date'],
         'planned_end': TASK[3]['planned_end_date'],
         'status_id': STATUSES[3]['i'],
         'executor_id': 2,
         'task_id': TASK[3]['i'],
         'actual_start': TASK[3]['actual_start'],
         'actual_end': TASK[3]['actual_end']}
        ]
SQL_PLANS = []
for i in range(len(PLAN)):
    SQL_PLANS += [
        "INSERT INTO plans (id, start_date, planned_end, status_id, "
        "executor_id, task_id, actual_start, actual_end_date) "
        f"VALUES ({PLAN[i]['i']}, '{PLAN[i]['start_date']}', "
        f"'{PLAN[i]['planned_end']}', "
        f"{PLAN[i]['status_id']}, {PLAN[i]['executor_id']}, "
        f"{PLAN[i]['task_id']}, "
        f"{PLAN[i]['actual_start'] if PLAN[i]['actual_start'] else 'NULL'}, "
        f"{PLAN[i]['actual_end'] if PLAN[i]['actual_end'] else 'NULL'})"
    ]

TASK_TAG = [{'i': 1,
             'task_id': TASK[0]['i'],
             'tag_id': TAGS[0]['i']},
            {'i': 2,
             'task_id': TASK[1]['i'],
             'tag_id': TAGS[1]['i']}
            ]
SQL_TASK_TAGS = []
for i in range(len(TASK_TAG)):
    SQL_TASK_TAGS += [
        "INSERT INTO intermediate_task_tags (id, task_id, tag_id) "
        f"VALUES ({TASK_TAG[i]['i']}, {TASK_TAG[i]['task_id']}, "
        f"{TASK_TAG[i]['tag_id']})"]

SQLS = SQL_CLEAR + SQL_ROLES + SQL_USERS + SQL_TAGS
SQLS += SQL_STATUSES + SQL_TASKS + SQL_PLANS + SQL_TASK_TAGS
