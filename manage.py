import time
import json
import hashlib
import decimal
import datetime

from flask_script import Server, Manager, prompt, prompt_bool
from app import create_app
from app.ext import *


def make_app(app_type):
    if not app_type:
        return create_app()


manager = Manager(make_app)
manager.add_option('-a', '--app_type', dest='app_type',
                   default='', required=False)

manager.add_command("runserver", Server(host="0.0.0.0", port=9988))


@manager.command
def create_table():
    db.create_all()


if __name__ == "__main__":
    manager.run()
