install:
	poetry install

tests:
	poetry run pytest -vv

db_init:
	flask db init --directory task_manager/migrations

migrate:
	flask db migrate --directory task_manager/migrations

upgrade:
	flask db upgrade --directory task_manager/migrations

test_fill_db:
	poetry run task_manager/database/init_db_development.py
coverage:
	poetry run pytest --cov=task_manager

build:
	poetry build
run:
	flask run

log:
	heroku logs --tail

lint:
	poetry run flake8

translate:
	django-admin compilemessages

command_prompt:
	export PS1="\W ($(git branch 2>/dev/null | grep '^*' | colrm 1 2)) $ "
.PHONY: install  build run tests log lint translate