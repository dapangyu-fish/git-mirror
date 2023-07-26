import json
import os
from flask import Flask, Response, request, jsonify

from pathlib import Path
from service.gitshark import GitShark

DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_data():
    data = {
        'code': '0'
    }
    return jsonify(data)


@app.route('/<path:path_with_namespace>/info/refs', methods=['GET'])
def streaming_get(path_with_namespace):
    service = request.args.get('service', default=None, type=None)
    path = Path("/root/repo", path_with_namespace)
    repo = GitShark(path) if path.exists() else GitShark.init(path)
    data = repo.inforefs(service)
    return Response(data, mimetype=f'application/x-{service}-advertisement')


@app.route('/<path:path_with_namespace>/<path:service>', methods=['POST'])
def streaming_post(path_with_namespace, service):
    if service == "info/lfs/objects/batch":
        # lfs请求
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
            url = get_file_url(oid, operation)
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
    else:
        path = Path("/root/repo", path_with_namespace)
        repo = GitShark(path) if path.exists() else GitShark.init(path)
        data = request.data
        data = repo.service(service, data)
        return Response(data, mimetype=f'application/x-{service}-result')
#
#
# if __name__ == '__main__':
#     app.run(port=8000, host="127.0.0.1")
#     # gunicorn gitserver:app -w 8
