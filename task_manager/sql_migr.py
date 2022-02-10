import os.path
from pathlib import Path
import sqlite3

DATABASE = Path(__file__).resolve().parent / 'tm.db'
print('database: ', DATABASE, type(DATABASE))
print(type(Path(__file__).resolve().parent))
# db = sqlite3.connect(DATABASE)
# SCRIPT = 'ALTER TABLE users ADD COLUMN password varchar(200)'


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
             'creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
             'last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
             'password_hash VARCHAR(200) NOT NULL, ' \
             'role_id INTEGER, '\
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


create_roles_db()
create_user_db()
