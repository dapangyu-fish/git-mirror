import json
import os
import time
import requests

from flask import Flask, Response, request, jsonify, after_this_request, render_template

from pathlib import Path
from service.gitshark import GitShark
from service.redis_test import RedisShark, redis_obj, RepoStatus

DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
app = Flask(__name__)


@app.route('/<path:path_with_namespace>/path', methods=['GET'])
def get_data(path_with_namespace):
    data = {
        'path': path_with_namespace
    }
    return jsonify(data)


def add_git_extension(string):
    if not string.endswith('.git'):
        string += '.git'
    return string


@app.route('/<path:path_with_namespace>/info/refs', methods=['GET'])
def streaming_get(path_with_namespace):
    service = request.args.get('service')
    print(service)
    print(path_with_namespace)
    path_with_namespace = add_git_extension(path_with_namespace)
    # print(path_with_namespace)
    service = request.args.get('service', default=None, type=None)
    path = Path("/root/repo", add_git_extension(path_with_namespace))
    repo = GitShark(path)
    if path.exists():
        r = RedisShark(path_with_namespace, redis_obj)
        status = r.get_repo_status()
        while status != str(RepoStatus.readable.value):
            time.sleep(1)
            status = r.get_repo_status()
            print("===status:{0}\n".format(status))
            print("===path_with_namespace:{0}\n".format(path_with_namespace))
    else:
        url = "https://{0}/info/refs?service=git-upload-pack".format(path_with_namespace)
        ex_response = requests.get(url)
        if ex_response.status_code == 200:
            r = RedisShark(path_with_namespace, redis_obj)
            r.update_repo_status(RepoStatus.initialization.value)
            repo.init(path)
            r.update_repo_status(RepoStatus.readable.value)
        else:
            return 'repo not found', 404

    data = repo.inforefs(service)
    return Response(data, mimetype=f'application/x-{service}-advertisement')


@app.route('/<path:path_with_namespace>/info/lfs/objects/batch', methods=['POST'])
def lfs_post(path_with_namespace):
    data = json.loads(request.data)
    operation = data.get('operation')
    objects = data.get('objects')

    def get_file_url(oid):
        return f'http://{DOMAIN_NAME}/lfs-object-file/{path_with_namespace}/lfs/objects/{oid[:2]}/{oid[2:4]}/{oid}'

    objects_response = []
    for obj in objects:
        oid = obj.get('oid')
        size = obj.get('size')
        # 获取文件的URL
        url = get_file_url(oid)
        # 添加到响应列表中
        objects_response.append({
            'oid': oid,
            'size': size,
            'authenticated': True,
            'actions': {
                operation: {
                    'href': url,
                    'header': {},
                    'expires_in': 86400
                }
            }
        })
    lfs_response = jsonify({
        'transfer': 'basic',
        'objects': objects_response
    })
    return lfs_response


@app.route('/<path:path_with_namespace>/git-upload-pack', methods=['POST'])
def streaming_post(path_with_namespace):
    path_with_namespace = add_git_extension(path_with_namespace)
    print(path_with_namespace)
    r = RedisShark(path_with_namespace, redis_obj)
    status = r.get_repo_status()
    while status != str(RepoStatus.readable.value):
        time.sleep(1)
        status = r.get_repo_status()
        print("===status:{0}\n".format(status))
        print("===path_with_namespace:{0}\n".format(path_with_namespace))

    r.begin_read_repo()

    @after_this_request
    def after_request(response):
        r.end_read_repo()
        return response

    path = Path("/root/repo", path_with_namespace)
    repo = GitShark(path) if path.exists() else GitShark.init(path)
    data = request.data
    data = repo.service("git-upload-pack", data)
    return Response(data, mimetype=f'application/x-"git-upload-pack"-result')


@app.route('/<path:path_with_namespace>/update_repo', methods=['POST'])
def update_repo(path_with_namespace):
    path_with_namespace = add_git_extension(path_with_namespace)
    pass


@app.errorhandler(404)
def handle_not_found_error(e):
    url = request.url
    index = url.find("/", url.find("/", url.find("/") + 1) + 1)
    path = url[index + 1:]
    EXTERNAL_URL = os.environ.get('EXTERNAL_URL')
    url = "{0}/{1}".format(EXTERNAL_URL, path)
    return render_template('400.html', url=url), 400


def find_git_directories(directory):
    git_dirs = []
    subdirectories = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            subdirectories.append(item)
    for subdir in subdirectories:
        if subdir.endswith('.git'):
            repo_dir = os.path.join(directory, subdir)
            git_dirs.append(repo_dir)
        else:
            dir = os.path.join(directory, subdir)
            git_dirs.extend(find_git_directories(dir))
    return git_dirs


@app.route('/')
def index():
    directories = find_git_directories("/root/repo")
    git_dir = []
    EXTERNAL_URL = os.environ.get('EXTERNAL_URL')
    for dir_t in directories:
        index = dir_t.find("/", dir_t.find("/", dir_t.find("/") + 1) + 1)
        repo_path = dir_t[index + 1:]
        git_dir.append(repo_path)
    return render_template('index.html', directories=git_dir, EXTERNAL_URL=EXTERNAL_URL)


if __name__ == '__main__':
    app.run(port=8001, host="127.0.0.1")
    # gunicorn gitserver:app -w 8
