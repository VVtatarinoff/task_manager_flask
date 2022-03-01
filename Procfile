init: python/task_manager/init_db_development.py
release: flask db upgrade --directory task_manager/migrations
web: gunicorn manager.py