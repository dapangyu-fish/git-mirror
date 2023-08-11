from service.redis_test import RedisShark, redis_obj, RepoStatus
from tasks.tasks import create_a_duplicate, updating_duplicated_repo, update_repo
from subprocess import run, Popen, PIPE


def is_latest_refs(repo_path):
    args = ['git', 'ls-remote', 'https://{0}'.format(repo_path)]
    result = run(args, check=True, capture_output=True)
    remote_refs = {}
    lines = result.stdout.decode("utf-8").strip().split('\n')
    for line in lines:
        parts = line.split()
        key = parts[1]
        value = parts[0]
        remote_refs[key] = value
    # git show-ref
    local_repo_path = '/root/repo/{0}'.format(repo_path)
    args = ['git', 'show-ref']
    result = run(args, check=True, capture_output=True, cwd=local_repo_path)
    local_refs = {}
    lines = result.stdout.decode("utf-8").strip().split('\n')
    for line in lines:
        parts = line.split()
        key = parts[1]
        value = parts[0]
        local_refs[key] = value
    # 需要判断远端和本地refs是否完全一致,一致则不需要更新
    for key in local_refs.keys():
        if key in remote_refs:
            if local_refs[key] == remote_refs[key]:
                pass
            else:
                if "refs/remotes/upstream" in key:
                    pass
                else:
                    return False
        else:
            if "refs/remotes/upstream" in key:
                pass
            else:
                return False
    return True


def update_1_repo(repo_path):
    if is_latest_refs(repo_path):
        print("repo:{0} is lasted now".format(repo_path))
    else:
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
        try:
            update_1_repo(repo)
        except:
            print("update {0} failed".format(repo))

# */3 * * * * /usr/local/bin/python3 -u /root/update.py >> /root/log/updater.log 2>> /root/log/updater.log