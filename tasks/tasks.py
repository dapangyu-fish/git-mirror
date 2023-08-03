from __future__ import absolute_import

import os
import time
from subprocess import run, Popen, PIPE
from tasks.celery import app
from service.redis_test import RedisShark, redis_obj, RepoStatus

DUPLICATE_BASE = '/root/repo/tmp/duplicate'


@app.task
def create_a_duplicate(path: str):
    repo_path = '/root/repo/{0}'.format(path)
    duplicate_father_path = '{0}/{1}'.format(DUPLICATE_BASE, os.path.dirname(path))
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
    duplicate_path = '{0}/{1}'.format(DUPLICATE_BASE, path)
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
def update_repo(path):
    path_with_namespace = path
    r = RedisShark(path_with_namespace, redis_obj)
    r.update_repo_status(str(RepoStatus.unreadable.value))
    time.sleep(20)
    while r.get_counter() != 0:
        time.sleep(1)
    r.update_repo_status(str(RepoStatus.updating.value))
    time.sleep(60)  # 模拟更新动作
    r.update_repo_status(str(RepoStatus.readable.value))
    data = {
        'status': "update success"
    }
    print(data)
    return data
