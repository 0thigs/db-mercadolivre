import redis


class RedisConnection:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = redis.Redis(
                host="redis-13698.c74.us-east-1-4.ec2.redns.redis-cloud.com",
                port=13698,
                db=0,
                username="default",
                password="jSh1y3NuRhMpgrxhl0NDBw3rpjNzJNp7",
                decode_responses=True,
            )
        return cls._client 