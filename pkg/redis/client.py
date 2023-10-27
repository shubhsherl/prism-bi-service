import os
import redis
import logging

logger = logging.getLogger('redis')

class RedisClient:
    def __init__(self):
        host = os.getenv('REDIS_HOST')
        password = os.getenv('REDIS_PASSWORD')
        port = os.getenv('REDIS_PORT')
        self.redis = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def set(self, key, value, ttl= 60 * 60 * 24):
        logger.info(f"Setting {key} in Redis...")
        if ttl is None:
            self.redis.set(key, value)
        else:
            self.redis.setex(key, ttl, value)

    def get(self, key):
        logger.info(f"Fetching {key} from Redis...")
        return self.redis.get(key)

    def delete(self, key):
        return self.redis.delete(key)

    def ttl(self, key):
        return self.redis.ttl(key)