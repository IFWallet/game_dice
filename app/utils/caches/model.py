#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from app.ext import redis_store
conn = None


class RedisDBMixin(object):
    @property
    def redis(self):
        global conn
        if conn is None:
            conn = redis_store

        return conn


class Base(RedisDBMixin):
    def __init__(self, key, is_load, is_lock=False):
        self._key = key
        self._value = None
        self._has_load = False
        self._is_lock = is_lock
        if is_load:
            self.load()

    @property
    def key(self):
        return self._key

    @property
    def has_load(self):
        return self._has_load

    @property
    def value(self):
        return self._value

    def save_value(self, value):
        self._value = value
        self.save()

    def load(self):
        """将REDIS数据写入对象"""
        self._value = self.read()
        self._has_load = True

    def read(self):
        """读REDIS，返回REDIS数据"""
        return None

    def format(self):
        """格式化数据，一般从数据库中读出"""
        return None

    def lock(self):
        key = ':'.join(('cache', 'model', self.key, 'lock'))
        while True:
            ret = self.redis.setex(key, 3600, "locking")
            if ret:
                return True
            time.sleep(10)

    def unlock(self):
        key = ':'.join(('cache', 'model', self.key, 'lock'))
        self.redis.delete(key)

    def is_lock(self):
        key = ':'.join(('cache', 'model', self.key, 'lock'))
        return self.redis.exists(key)

    def save(self):
        """写REDIS"""
        self._has_load = True

    def resave(self):
        """重新写REDIS，数据库中的数据发生了变化"""
        self._value = self.format()
        self._has_load = True

        if self._is_lock:
            self.lock()

        self.delete()
        self.save()

        if self._is_lock:
            self.unlock()

    def delete(self):
        """删除REDIS"""
        self.redis.delete(self.key)

    def exists(self):
        return self.redis.exists(self.key)


class StringModel(Base):
    def __init__(self, key, is_load, is_lock=False):
        super(StringModel, self).__init__(key, is_load, is_lock)
        if self._value is None:
            self._value = ''

    def read(self):
        return self.redis.get(self.key)

    def save_value(self, value, **kwargs):
        self._value = value
        self.save(**kwargs)

    def save(self, **kwargs):
        if self._value:
            self.redis.set(self.key, self._value, **kwargs)
        else:
            self.delete()
        super(StringModel, self).save()


class ListModel(Base):
    def __init__(self, key, is_load, is_lock=False):
        super(ListModel, self).__init__(key, is_load, is_lock)
        if self._value is None:
            self._value = []

    def read(self, start=0, end=-1):
        return self.redis.lrange(self.key, start, end)

    def save(self):
        if self._value:
            self.redis.rpush(self.key, *self._value)
        else:
            self.delete()
        super(ListModel, self).save()

    def lindex(self, index):
        return self.redis.lindex(self.key, index)

    def llen(self):
        return self.redis.llen(self.key)

    def rpush(self, *values):
        if not values:
            return 0
        self._value.extend(values)
        return self.redis.rpush(self.key, *values)

    def lpush(self, *values):
        if not values:
            return 0
        value_list = list(values)
        value_list.extend(self._value)
        self._value = value_list
        return self.redis.lpush(self.key, *values)

    def lrem(self, value):
        if self._value and value in self._value:
            self._value.remove(value)
        return self.redis.lrem(self.key, 0, value)

    def lexists(self, value):
        self.load()
        if not self._value:
            return False
        return str(value) in self._value


class HashModel(Base):
    def __init__(self, key, is_load, is_lock=False):
        super(HashModel, self).__init__(key, is_load, is_lock)
        if self._value is None:
            self._value = {}

    def read(self):
        return self.redis.hgetall(self.key)

    def save(self):
        if self._value:
            self.redis.hmset(self.key, self._value)
        else:
            self.delete()
        super(HashModel, self).save()

    def hset(self, key, value):
        self._value[key] = value
        return self.redis.hset(self.key, key, value)

    def hmset(self, mapping):
        self._value.update(mapping)
        return self.redis.hmset(self.key, mapping)

    def hget(self, key):
        self._value[key] = self.redis.hget(self.key, key)
        return self._value[key]

    def hdel(self, *keys):
        for key in keys:
            if key in self._value.keys():
                self._value.pop(key)
        return self.redis.hdel(self.key, *keys)

    def hincrby(self, key, amount):
        if key in self._value:
            self._value[key] = int(self._value[key])
            self._value[key] += amount
        return self.redis.hincrby(self.key, key, amount)

    def hkeys(self):
        return self.redis.hkeys(self.key)


class SetModel(Base):
    def __init__(self, key, is_load, is_lock=False):
        super(SetModel, self).__init__(key, is_load, is_lock)
        if self._value is None:
            self._value = set()

    def read(self):
        return self.redis.smembers(self.key)

    def save(self):
        if self._value:
            self.redis.sadd(self.key, *self._value)
        else:
            self.delete()
        super(SetModel, self).save()

    def sadd(self, value):
        if self._value is None:
            self._value = set()
        self._value.add(value)
        return self.redis.sadd(self.key, value)

    def srem(self, value):
        if value in self._value:
            self._value.remove(value)
        return self.redis.srem(self.key, value)

    def scard(self):
        return self.redis.scard(self.key)

    def smembers(self):
        return self.redis.smembers(self.key)


class SortSetModel(Base):
    def __init__(self, key, is_load, is_lock=False):
        super(SortSetModel, self).__init__(key, is_load, is_lock)
        if self._value is None:
            self._value = set()

    def read(self):
        return self.redis.zrange(self.key, 0, -1, withscores=True)

    def save(self):
        if self._value:
            value = []
            for data, score in self._value:
                value.append(score)
                value.append(data)
            self.redis.zadd(self.key, *value)
        else:
            self.delete()
        super(SortSetModel, self).save()

    def zadd(self, data, score):
        self._value.add((data, score))
        self.redis.zadd(self.key, score, data)

    def zrem(self, data):
        for v in self._value:
            if v[0] == data:
                self._value.remove(v)
        self.redis.zrem(self.key, data)

    def zcard(self):
        return self.redis.zcard(self.key)

    def zrange(self, start=0, stop=-1, withscores=True):
        return self.redis.zrange(self.key, start, stop, withscores)

    def zscore(self, data):
        return self.redis.zscore(self.key, data)
