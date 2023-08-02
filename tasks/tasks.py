from __future__ import absolute_import

from subprocess import run, Popen, PIPE
from tasks.celery import app

DUPLICATE_BASE = '/root/repo/tmp/duplicate'


@app.task
def create_a_duplicate(path: str):
    repo_path = '/root/repo/github/{0}'.format(path)
    duplicate_path = '{0}/{1}'.format(DUPLICATE_BASE, path)
    args = ['mkdir', '-p', duplicate_path]
    result = run(args, check=True, capture_output=True)
    print(result)
    args = ['rsync', '-aP', repo_path, duplicate_path]
    result = run(args, check=True, capture_output=True)
    print(result)
    return result


@app.task
def delete_a_duplicate(path):
    duplicate_path = '{0}/{1}'.format(DUPLICATE_BASE, path)
    args = ['rm', '-rf', duplicate_path]
    result = run(args, check=True, capture_output=True)
    print(result)
    return result


@app.task
def delete_all_duplicate():
    args = ['rm', '-rf', DUPLICATE_BASE]
    result = run(args, check=True, capture_output=True)
    print(result)
    return result


@app.task
def updating_duplicated_repo(path):
    duplicate_path = '{0}/{1}'.format(DUPLICATE_BASE, path)
    args = ['/usr/bin/sync_repo']
    result = run(args, check=True, cwd=duplicate_path)
    print(result)
    return result
