import faker
from werkzeug.security import generate_password_hash
from datetime import datetime

fake = faker.Faker()
ADMINISTRATOR = {
    'email': fake.ascii_email(),
    'name': fake.first_name(),
    'first_name': fake.first_name(),
    'last_name': fake.last_name(),
    'password': "".join(fake.random_letters(length=10))}
EXECUTOR = {
    'email': fake.ascii_email(),
    'name': fake.first_name(),
    'first_name': fake.first_name(),
    'last_name': fake.last_name(),
    'password': "".join(fake.random_letters(length=10))}
MANAGER = {
    'email': fake.ascii_email(),
    'name': fake.first_name(),
    'first_name': fake.first_name(),
    'last_name': fake.last_name(),
    'password': "".join(fake.random_letters(length=10))}
NEW_USER = {
    'email': fake.ascii_email(),
    'name': fake.first_name(),
    'first_name': fake.first_name(),
    'last_name': fake.last_name(),
    'password': "".join(fake.random_letters(length=10))}

SQLS = [
    "INSERT INTO roles (name, default_flag, permissions) "
    "VALUES ('Executor','True','3')",
    "INSERT INTO roles (name, default_flag, permissions) "
    "VALUES ('Manager','False','7')",
    "INSERT INTO roles (name, default_flag, permissions) "
    "VALUES ('Administrator','False','255')",
    "INSERT INTO users (email, name, first_name, last_name, "
    "password_hash, role_id, 'creation_date')"
    f"VALUES ('{EXECUTOR['email']}', '{EXECUTOR['name']}', "
    f"'{EXECUTOR['first_name']}', '{EXECUTOR['last_name']}', "
    f"'{generate_password_hash(EXECUTOR['password'])}',1,"
    f"'{datetime.utcnow()}');",
    "INSERT INTO users (email, name, first_name, last_name, "
    "password_hash, role_id,'creation_date')"
    f"VALUES ('{MANAGER['email']}', '{MANAGER['name']}', "
    f"'{MANAGER['first_name']}', '{MANAGER['last_name']}', "
    f"'{generate_password_hash(MANAGER['password'])}',2, "
    f"'{datetime.utcnow()}');",
    "INSERT INTO users (email, name, first_name, last_name, "
    "password_hash, role_id,'creation_date')"
    f"VALUES ('{ADMINISTRATOR['email']}', '{ADMINISTRATOR['name']}', "
    f"'{ADMINISTRATOR['first_name']}', '{ADMINISTRATOR['last_name']}', "
    f"'{generate_password_hash(ADMINISTRATOR['password'])}', 3, "
    f"'{datetime.utcnow()}');"
]
