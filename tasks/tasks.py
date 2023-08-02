from __future__ import absolute_import

import os
from subprocess import run, Popen, PIPE
from tasks.celery import app

DUPLICATE_BASE = '/root/repo/tmp/duplicate'


@app.task
def create_a_duplicate(path: str):
    repo_path = '/root/repo/github.com/{0}'.format(path)
    duplicate_father_path = '{0}/github.com/{1}'.format(DUPLICATE_BASE, os.path.dirname(path))
    args = ['mkdir', '-p', duplicate_father_path]
    result = run(args, check=True, capture_output=True)
    print(result)
    args = ['rsync', '-aP', repo_path, duplicate_father_path]
    result = run(args, check=True, capture_output=True)
    data = {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    }
    print(data)
    return data


@app.task
def delete_a_duplicate(path):
    duplicate_path = '{0}/github.com/{1}'.format(DUPLICATE_BASE, path)
    args = ['rm', '-rf', duplicate_path]
    result = run(args, check=True, capture_output=True)
    data = {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    }
    print(data)
    return data


@app.task
def delete_all_duplicate():
    args = ['rm', '-rf', DUPLICATE_BASE]
    result = run(args, check=True, capture_output=True)
    data = {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    }
    print(data)
    return data


@app.task
def updating_duplicated_repo(path):
    duplicate_path = '{0}/{1}'.format(DUPLICATE_BASE, path)
    args = ['/usr/bin/sync_repo']
    result = run(args, check=True, cwd=duplicate_path)
    data = {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    }
    print(data)
    return data

@app.task
def add(x, y):
    return x + y