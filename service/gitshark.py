from __future__ import annotations

import io
import os
import stat
from typing import IO
from subprocess import run, Popen, PIPE
from pathlib import Path
import gzip


def decompress_if_needed(data):
    try:
        return gzip.decompress(data).decode("utf-8").encode()
    except OSError:
        return data


class GitShark(object):
    def __init__(self, path: str):
        super(GitShark, self).__init__()
        self.path = Path(path)

    @staticmethod
    def init(path: str) -> GitShark:
        directory, filename = os.path.split(path)
        args = ['mkdir', '-p', directory]
        run(args, check=True)
        args = ['git', 'clone', '--bare',
                "https://github.com/{0}/{1}".format(directory.replace("/root/repo/github.com/", ""), filename), path]
        run(args, check=True)
        args = ['cd', path, '&&', 'git', 'lfs', 'fetch', '--all']
        run(args, check=True)
        return GitShark(path)

    def add_hook(self, name: str, hook: str) -> str:
        path = Path(self.path, 'hooks', name)
        path.write_text(hook)
        st = path.stat()
        path.chmod(st.st_mode | stat.S_IEXEC)
        return str(path)

    def inforefs(self, service: str) -> IO:
        args = [service, '--stateless-rpc', '--advertise-refs', str(self.path)]
        result = run(args, check=True, capture_output=True)

        # Adapted from:
        #   https://github.com/schacon/grack/blob/master/lib/grack.rb
        data = b'# service=' + service.encode()
        datalen = len(data) + 4
        datalen = b'%04x' % datalen
        data = datalen + data + b'0000' + result.stdout

        return io.BytesIO(data)

    def service(self, service: str, data: bytes) -> IO:
        args = [service, '--stateless-rpc', str(self.path)]
        proc = Popen(args, stdin=PIPE, stdout=PIPE)
        try:
            data = decompress_if_needed(data)
            data, _ = proc.communicate(data)
        finally:
            proc.wait()

        return io.BytesIO(data)
