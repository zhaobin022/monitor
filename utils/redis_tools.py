__author__ = 'zhaobin022'

import django
import redis
from monitor import settings

def redis_conn():
    pool = redis.ConnectionPool(host=settings.REDIS_CONN['HOST'], port=settings.REDIS_CONN['PORT'])
    r = redis.Redis(connection_pool=pool)
    return  r

if __name__ == '__main__':
    r = redis_conn()
    r.exists()