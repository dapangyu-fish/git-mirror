import time

import redis
from pathlib import Path
from enum import Enum

time.sleep(2)

redis_obj = redis.Redis(host='redis', port=6379, db=0, retry_on_timeout=True)
redis_obj.flushdb()
redis_obj.flushall()


class RepoStatus(Enum):
    initialization = "initialization"         # 表示该仓库正在初次镜像,不可读
    readable = "readable"       # 表示该仓库可读
    unreadable = "unreadable"   # 表示该仓库不可读,但是仍有读取操作未完成,后续读请求需要夯住或者排队
    writing = "writing"         # 表示该仓库正在推送
    updating = "updating"       # 表示该仓库正在更新


class RedisShark(object):
    def __init__(self, path: str, r: redis.client.Redis):
        super(RedisShark, self).__init__()
        self.path = Path(path)
        self.counter_key = f"{self.path}_fetch_counter"
        self.requests_key = f"{self.path}_requests"
        self.status_key = f"{self.path}_status"
        self.r = r

    def update_counter(self, pipe, value):
        try:
            while True:
                try:
                    pipe.watch(self.counter_key)
                    current_value = pipe.get(self.counter_key)
                    if current_value is None:
                        current_value = 0
                    else:
                        current_value = int(current_value)
                    print(f"Old value: {current_value}")
                    next_value = int(current_value) + value
                    pipe.multi()
                    pipe.set(self.counter_key, next_value)
                    pipe.execute()
                    print(f"New value: {next_value}")
                    break
                except redis.WatchError:
                    # 如果键的值在事务中被其他客户端改变，重新开始事务
                    continue
        finally:
            # 无论事务是否成功，都要取消监视
            pipe.unwatch()

    def get_counter(self):
        pipe = self.r.pipeline()
        counter = 0
        try:
            while True:
                try:
                    pipe.watch(self.counter_key)
                    current_value = pipe.get(self.counter_key)
                    if current_value is None:
                        counter = 0
                    else:
                        counter = int(current_value)
                    break
                except redis.WatchError:
                    # 如果键的值在事务中被其他客户端改变，重新开始事务
                    continue
        finally:
            # 无论事务是否成功，都要取消监视
            pipe.unwatch()
        return counter

    def begin_read_repo(self):
        pipe = self.r.pipeline()
        self.update_counter(pipe, -1)

    def end_read_repo(self):
        pipe = self.r.pipeline()
        self.update_counter(pipe, -1)

    def update_repo_status(self, status: str):
        pipe = self.r.pipeline()
        try:
            while True:
                try:
                    pipe.watch(self.status_key)
                    old_status = pipe.get(self.status_key)
                    if old_status is None:
                        old_status = RepoStatus.initialization.value
                    else:
                        old_status = old_status.decode('utf-8')
                    print(f"Old status: {old_status}")
                    pipe.multi()
                    pipe.set(self.status_key, status)
                    pipe.execute()
                    print(f"New status: {status}")
                    break
                except redis.WatchError:
                    # 如果键的值在事务中被其他客户端改变，重新开始事务
                    continue
        finally:
            # 无论事务是否成功，都要取消监视
            pipe.unwatch()

    def get_repo_status(self):
        pipe = self.r.pipeline()
        status = None
        try:
            while True:
                try:
                    pipe.watch(self.status_key)
                    status = pipe.get(self.status_key)
                    if status is None:
                        pipe.multi()
                        pipe.set(self.status_key, RepoStatus.readable.value)
                        pipe.execute()
                        status = RepoStatus.readable.value
                    else:
                        status = status.decode('utf-8')
                    break
                except redis.WatchError:
                    # 如果键的值在事务中被其他客户端改变，重新开始事务
                    continue
        finally:
            # 无论事务是否成功，都要取消监视
            pipe.unwatch()
        return status


if __name__ == '__main__':
    sr = RedisShark("/test_repo_lfs.git", redis_obj)
    sr.begin_read_repo()
    sr.update_repo_status(RepoStatus.initialization.value)
