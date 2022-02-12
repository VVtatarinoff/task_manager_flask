from pathlib import Path
import sqlite3
from task_manager.auths.models import Role, Permission
#from task_manager.manage import db

DATABASE = Path(__file__).resolve().parent / 'tm.db'
print('database: ', DATABASE, type(DATABASE))
print(type(Path(__file__).resolve().parent))


db = sqlite3.connect(DATABASE)


def execute_script(script):
    with sqlite3.connect(DATABASE) as db:
        db.cursor().executescript(script)
        db.commit()
        db.close


def create_user_db():
    script = 'CREATE TABLE IF NOT EXISTS users ' \
             '(id INTEGER PRIMARY KEY, ' \
             'name VARCHAR(20) NOT NULL UNIQUE, ' \
             'email VARCHAR(100) NOT NULL UNIQUE, ' \
             'first_name VARCHAR(70), ' \
             'last_name VARCHAR(70), ' \
             'location VARCHAR(70), '\
             'creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
             'last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
             'password_hash VARCHAR(200) NOT NULL, ' \
             'role_id INTEGER, ' \
             'FOREIGN KEY (role_id) REFERENCES roles(id))'
    print(script)
    execute_script(script)


def create_roles_db():
    script = """CREATE TABLE IF NOT EXISTS roles
     (id INTEGER PRIMARY KEY,
      name VARCHAR(64) NOT NULL UNIQUE,
       default_flag BOOLEAN DEFAULT FALSE,
        permissions INTEGER)"""
    print(script)
    execute_script(script)


def insert_roles():
    roles = {
        'Executor': (Permission.REVIEW | Permission.EXECUTE, True),
        'Manager': (
            Permission.REVIEW | Permission.EXECUTE | Permission.MANAGE, False),
        'Administrator': (0xff, False)
    }

    for r in roles:
        # role = Role.query.filter_by(name=r).first()
        # if role is None:
        #     role = Role(name=r)
        permissions = roles[r][0]
        default_flag = roles[r][1]
        # with db.session as ds:
        #     ds.add(role)
        #     ds.commit()
        script= f"INSERT INTO roles (name, default_flag, permissions) "\
         f"VALUES ('{r}','{default_flag}','{permissions}')"
        print(script)
        execute_script(script)

create_roles_db()
create_user_db()
insert_roles()
