INSERT INTO roles (name, default_flag, permissions) VALUES ('Executor','True','3');
INSERT INTO roles (name, default_flag, permissions) VALUES ('Manager','False','7');
INSERT INTO roles (name, default_flag, permissions) VALUES ('Administrator','False','255');
INSERT INTO users (email, name, first_name, last_name, password_hash, role_id)
VALUES
    ('test1@mail.ru', 'test1', 'TEST1', 'TESTOFF1', 'pbkdf2:sha256:260000$pugOZEsHPB06srps$4c024bba3436fcadc66e60fbf3a55a721d89d7076b625e5b7945ac17b8fd9cd1',1);
INSERT INTO users (email, name, first_name, last_name, password_hash, role_id)
VALUES
    ('test2@mail.ru', 'test2', 'TEST2', 'TESTOFF2', 'pbkdf2:sha256:260000$pugOZEsHPB06srps$4c024bba3436fcadc66e60fbf3a55a721d89d7076b625e5b7945ac17b8fd9cd1',2);
INSERT INTO users (email, name, first_name, last_name, password_hash, role_id)
VALUES
    ('test3@mail.ru', 'test3', 'TEST3', 'TESTOFF3', 'pbkdf2:sha256:260000$pugOZEsHPB06srps$4c024bba3436fcadc66e60fbf3a55a721d89d7076b625e5b7945ac17b8fd9cd1',3);