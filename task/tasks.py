from __future__ import absolute_import

from task.celery import app


@app.task
def create_a_duplicate(path):
    pass


@app.task
def delete_a_duplicate(path):
    pass


@app.task
def delete_all_duplicate(path):
    pass


@app.task
def updating_duplicated_repo(path):
    pass
