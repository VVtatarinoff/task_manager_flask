init: python task_manager/database/init_db_development.py
release: flask db upgrade --directory task_manager/migrations
web: gunicorn task_manager.manager:app