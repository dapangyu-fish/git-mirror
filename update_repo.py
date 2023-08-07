from service.redis_test import RedisShark, redis_obj, RepoStatus
from tasks.tasks import create_a_duplicate, updating_duplicated_repo, update_repo


def update_1_repo(repo_path):
    step1 = create_a_duplicate.delay(test_repo)
    r = step1.get()
    print("step1 result:{0}".format(r))

    step2 = updating_duplicated_repo.delay(test_repo)
    r = step2.get()
    print("step2 result:{0}".format(r))

    step3 = update_repo.delay(test_repo)
    r = step3.get()
    print("step3 result:{0}".format(r))


if __name__ == '__main__':
    repo_list = []
    keys = redis_obj.keys('*')
    for key in keys:
        key_name = key.decode('utf-8')
        if ".git_status" in key_name:
            repo_list.append(key_name.replace(".git_status", ".git"))
    test_repo = "github.com/moby/moby.git"
    update_1_repo(test_repo)
