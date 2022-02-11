INSERT INTO roles (id, name, default_flag, permissions)
VALUES
    (1, 'Administrator', 0, 255),
    (2, 'Executor', 1, 3),
    (3, 'Manager', 0, 7)

INSERT INTO users (email, name, first_name, last_name, password_hash, role_id)
VALUES
    ('test1@mail.ru', 'test1', 'TEST1', 'TESTOFF1', 'pbkdf2:sha256:260000$pugOZEsHPB06srps$4c024bba3436fcadc66e60fbf3a55a721d89d7076b625e5b7945ac17b8fd9cd1',1),
    ('test2@mail.ru', 'test2', 'TEST2', 'TESTOFF2', 'pbkdf2:sha256:260000$pugOZEsHPB06srps$4c024bba3436fcadc66e60fbf3a55a721d89d7076b625e5b7945ac17b8fd9cd1',2),
    ('test3@mail.ru', 'test3', 'TEST3', 'TESTOFF3', 'pbkdf2:sha256:260000$pugOZEsHPB06srps$4c024bba3436fcadc66e60fbf3a55a721d89d7076b625e5b7945ac17b8fd9cd1',3);