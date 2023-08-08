from service.redis_test import RedisShark, redis_obj, RepoStatus
from tasks.tasks import create_a_duplicate, updating_duplicated_repo, update_repo


def is_latest_refs():
    remotes_refs = []
    local_refs = []
    # 需要判断远端和本地refs是否完全一致,一致则不需要更新
    return True


def update_1_repo(repo_path):
    if is_latest_refs():
        print("repo:{0} is lasted now".format(repo_path))
        return
    step1 = create_a_duplicate.delay(repo_path)
    r = step1.get()
    print("step1 result:{0}".format(r))

    step2 = updating_duplicated_repo.delay(repo_path)
    r = step2.get()
    print("step2 result:{0}".format(r))

    step3 = update_repo.delay(repo_path)
    r = step3.get()
    print("step3 result:{0}".format(r))


if __name__ == '__main__':
    repo_list = []
    keys = redis_obj.keys('*')
    for key in keys:
        key_name = key.decode('utf-8')
        if ".git_status" in key_name:
            repo_list.append(key_name.replace(".git_status", ".git"))
    for repo in repo_list:
        update_1_repo(repo)

# */3 * * * * /usr/local/bin/python3 -u /root/update.py >> /root/log/updater.log 2>> /root/log/updater.log