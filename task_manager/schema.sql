DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    default_flag BOOLEAN DEFAULT FALSE,
    permissions INTEGER
    );

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(70),
    last_name VARCHAR(70),
    location VARCHAR(70),
    creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    password_hash VARCHAR(200) NOT NULL,
    role_id INTEGER,
    FOREIGN KEY (role_id) REFERENCES roles(id)
    );

INSERT INTO roles (name, default_flag, permissions) VALUES ('Executor','True','3')
INSERT INTO roles (name, default_flag, permissions) VALUES ('Manager','False','7')
INSERT INTO roles (name, default_flag, permissions) VALUES ('Administrator','False','255')