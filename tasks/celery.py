from __future__ import absolute_import
from celery import Celery

app = Celery('tasks', include=['tasks.tasks'])
app.config_from_object('tasks.celeryconfig')

if __name__ == '__main__':
    app.start()