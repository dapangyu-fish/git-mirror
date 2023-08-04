from service.redis_test import RedisShark, redis_obj, RepoStatus
from tasks.tasks import create_a_duplicate


create_a_duplicate.delay("github.com/moby/moby.git")
