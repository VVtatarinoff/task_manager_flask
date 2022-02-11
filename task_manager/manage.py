#!/usr/bin/env python
import os
from task_manager import create_app, db
from task_manager.auths.models import User, Role
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


if __name__ == '__main__':
    app.run()
