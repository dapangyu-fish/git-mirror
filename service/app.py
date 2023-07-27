import json
import os
from flask import Flask, Response, request, jsonify, after_this_request

from pathlib import Path
from service.gitshark import GitShark
from service.redis_test import RedisShark, redis_obj


DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_data():
    data = {
        'code': '0'
    }
    return jsonify(data)


def add_git_extension(string):
    if not string.endswith('.git'):
        string += '.git'
    return string


@app.route('/<path:path_with_namespace>/info/refs', methods=['GET'])
def streaming_get(path_with_namespace):
    path_with_namespace = add_git_extension(path_with_namespace)
    # print(path_with_namespace)
    service = request.args.get('service', default=None, type=None)
    path = Path("/Users/dapangyu/github-mirror/gitserver/repo", add_git_extension(path_with_namespace))
    repo = GitShark(path) if path.exists() else GitShark.init(path)
    data = repo.inforefs(service)
    return Response(data, mimetype=f'application/x-{service}-advertisement')


@app.route('/<path:path_with_namespace>/info/lfs/objects/batch', methods=['POST'])
def lfs_post(path_with_namespace, service):
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
def streaming_post(path_with_namespace, service):
    path_with_namespace = add_git_extension(path_with_namespace)
    print(path_with_namespace)
    # r = RedisShark("/test_repo_lfs.git", redis_obj)
    #
    # @after_this_request
    # def after_request():
    #     r.end_read_repo()

    path = Path("/Users/dapangyu/github-mirror/gitserver/repo", path_with_namespace)
    repo = GitShark(path) if path.exists() else GitShark.init(path)
    data = request.data
    data = repo.service(service, data)
    return Response(data, mimetype=f'application/x-{service}-result')


if __name__ == '__main__':
    app.run(port=8001, host="127.0.0.1")
    # gunicorn gitserver:app -w 8
