#!/usr/bin/env python
# coding=utf-8

import redis

from magnet_dht.config import (
    REDIS_KEY,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_HOST,
    REDIS_MAX_CONNECTION,
)


class RedisClient:

    def __init__(
        self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD
    ):
        conn_pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            max_connections=REDIS_MAX_CONNECTION,
        )
        self.redis = redis.Redis(connection_pool=conn_pool)

    def add_magnet(self, magnet):
        """
        新增磁力链接
        """
        self.redis.sadd(REDIS_KEY, magnet)

    def get_magnets(self, count=128):
        """
        返回指定数量的磁力链接
        """
        return self.redis.srandmember(REDIS_KEY, count)
