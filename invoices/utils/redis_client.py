import redis
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    _instance = None

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            connection_params = {
                'host': settings.REDIS_HOST,
                'port': settings.REDIS_PORT,
                'db': settings.REDIS_DB,
                'password': settings.REDIS_PASSWORD,
                'decode_responses': True,
                'socket_connect_timeout': 5,
                'socket_timeout': 5,
            }
            
            cls._instance = redis.Redis(**connection_params)
            
            try:
                cls._instance.ping()
                logger.info("Successfully connected to Redis")
            except redis.AuthenticationError as e:
                logger.error(f"Redis authentication failed: {e}")
                raise Exception(f"Redis authentication failed: {e}")
            except redis.ConnectionError as e:
                logger.error(f"Could not connect to Redis server: {e}")
                raise Exception(f"Could not connect to Redis server: {e}")
                
        return cls._instance

def get_redis_client():
    return RedisClient.get_client()