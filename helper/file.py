import json
import logging

from pkg.s3.client import S3Client
from pkg.redis.client import RedisClient

logger = logging.getLogger('helper')

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        return None
    
def fetch_from_s3(key, cache=True):
    redis_client = RedisClient()
    data_str = redis_client.get(key)
    if data_str is not None:
        data = json.loads(data_str)
        return data

    s3_client = S3Client()
    data_str = s3_client.get_object(key)
    data = json.loads(data_str)
    if data is None:
        return data
    
    redis_client.set(key, data_str)
    return data

def store_in_s3(key, data, invalidate_cache=True):
    s3_client = S3Client()
    s3_client.put_object(key, json.dumps(data))
    if invalidate_cache:
        redis_client = RedisClient()
        redis_client.delete(key)
