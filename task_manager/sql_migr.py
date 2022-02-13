from pathlib import Path
import sqlite3
from task_manager.auths.models import Permission


def execute_script(script, database):
    with sqlite3.connect(database) as db:
        cursor = db.cursor()
        cursor.execute(script)
        records = cursor.fetchall()
        db.commit()
        db.close
    return records


def create_user_db(db):
    script = 'CREATE TABLE IF NOT EXISTS users ' \
             '(id INTEGER PRIMARY KEY, ' \
             'name VARCHAR(20) NOT NULL UNIQUE, ' \
             'email VARCHAR(100) NOT NULL UNIQUE, ' \
             'first_name VARCHAR(70), ' \
             'last_name VARCHAR(70), ' \
             'location VARCHAR(70), ' \
             'creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
             'last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
             'password_hash VARCHAR(200) NOT NULL, ' \
             'role_id INTEGER, ' \
             'FOREIGN KEY (role_id) REFERENCES roles(id))'
    execute_script(script, db)


def create_roles_db(db):
    script = """CREATE TABLE IF NOT EXISTS roles
     (id INTEGER PRIMARY KEY,
      name VARCHAR(64) NOT NULL UNIQUE,
       default_flag BOOLEAN DEFAULT FALSE,
        permissions INTEGER)"""
    execute_script(script, db)


def insert_roles(db):
    roles = {
        'Executor': (Permission.REVIEW | Permission.EXECUTE, True),
        'Manager': (
            Permission.REVIEW | Permission.EXECUTE | Permission.MANAGE, False),
        'Administrator': (0xff, False)
    }
    script = "SELECT * FROM roles"
    selection = execute_script(script, db)
    if len(selection) == len(roles):
        return
    script = "DELETE FROM roles"
    execute_script(script, db)

    for r in roles:
        permissions = roles[r][0]
        default_flag = roles[r][1]
        script = f"INSERT INTO roles (name, default_flag, permissions) " \
                 f"VALUES ('{r}','{default_flag}','{permissions}')"
        print(script)
        execute_script(script, db)


def migrate(name):
    db = Path(__file__).resolve().parent / name
    create_roles_db(db)
    create_user_db(db)
    insert_roles(db)


if __name__ == '__main__':
    migrate('tm.db')
