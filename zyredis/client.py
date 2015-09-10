#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014,掌阅科技
All rights reserved.

摘    要: client.py
创 建 者: WangLichao
创建日期: 2014-10-24
"""
# pylint: disable=invalid-name,superfluous-parens
import functools
# third
from redis import Redis as _RedisClient
from redis.exceptions import ResponseError
# self
from zyredis import types
from zyredis.utils import mkey
from zyredis.utils import LOG
from zyredis.serialization import JSON
from zyredis.exceptions import NotSupportCommandError

# codis不支持的命令
NOT_SUPPORT_COMMANDS = frozenset([
    'KEYS', 'MOVE', 'OBJECT', 'RENAME', 'RENAMENX', 'SORT', 'SCAN',
    'BITOP', 'MSETNX', 'BLPOP', 'BRPOP', 'BRPOPLPUSH', 'PSUBSCRIBE', 'PUBLISH',
    'PUNSUBSCRIBE', 'SUBSCRIBE', 'UNSUBSCRIBE', 'DISCARD', 'EXEC', 'MULTI',
    'UNWATCH', 'WATCH', 'AUTH', 'ECHO', 'SELECT', 'BGREWRITEAOF', 'BGSAVE',
    'DBSIZE', 'FLUSHALL', 'FLUSHDB', 'INFO', 'LASTSAVE', 'MONITOR', 'SAVE',
    'SHUTDOWN', 'SLAVEOF', 'SLOWLOG', 'SYNC', 'TIME'
])

class Client(object):

    """Redis Client
    Attributes:
        host: redis 服务器地址,默认localhost
        port: redis 端口,默认6379
        db: 数据库名称
        serializer: 使用的序列化方式
    """

    host = "localhost"
    port = 6379
    db = 0
    serializer = JSON()

    def __init__(self, host=None, port=None, db=0,
                 serializer=None, transaction=False, **kwargs):
        self.host = host or self.host
        self.port = port or self.port
        self.transaction = transaction # codis不支持事务机制
        self.serializer = serializer or self.serializer
        self.db = db or self.db
        # 将redis的超时设置统一处理
        socket_timeout = kwargs.get("socket_timeout", 1)
        socket_connect_timeout = kwargs.get("socket_connect_timeout", 1)
        # 使用长连接
        socket_keepalive = kwargs.get("socket_keepalive", True)
        retry_on_timeout = kwargs.get("retry_on_timeout", True)
        self.api = _RedisClient(self.host,
                                self.port,
                                self.db,
                                socket_timeout=socket_timeout,
                                socket_connect_timeout=socket_connect_timeout,
                                socket_keepalive=socket_keepalive,
                                retry_on_timeout=retry_on_timeout,
                                connection_pool=None,
                                **kwargs)

    def List(self, name, initial=None, auto_slice=True):
        """list 类型
        Args:
            name: redis key
            initial: 初始化值(list类型)
        Returns:
            返回支持Python list操作的对象
        """
        return types.List(name, self.api, initial=initial, auto_slice=auto_slice)

    def Set(self, name, initial=None):
        """set 类型
        Args:
            name: redis key
            initial: 初始化值(set类型)
        Returns:
            返回支持Python set操作的对象
        """
        return types.Set(name, self.api, initial)

    def SortedSet(self, name, initial=None, auto_slice=True):
        """sorted set类型
        Args:
            name: redis key
            initial: 初始化值(ZSet类型,自定义类型)
        Returns:
            返回SortedSet对象
        """
        return types.SortedSet(name, self.api, initial, auto_slice=auto_slice)

    def Dict(self, name, initial=None, auto_slice=True, **extra):
        """Hash 类型
        Args:
            name: redis key
            initial: 初始化值(dict类型,自定义类型)
        Returns:
            返回支持python dict操作的对象
        """
        return types.Dict(name, self.api, initial=initial, auto_slice=auto_slice, **extra)

    def Queue(self, name, initial=None, maxsize=None):
        """queue队列
        Args:
            name: The name of the queue.
            initial: Initial items in the queue.
        """
        return types.Queue(name, self.api, initial=initial, maxsize=maxsize)

    def LifoQueue(self, name, initial=None, maxsize=None):
        """后进先出队列类型，部分命令codis不支持
        Args:
            name: string The name of the queue.
            initial: Initial items in the queue.
        """
        return types.LifoQueue(name, self.api,
                               initial=initial, maxsize=maxsize)

    def prepare_value(self, value):
        """编码
        Args:
            value: 需要编码的值
        """
        return self.serializer.encode(value)

    def value_to_python(self, value):
        """解码"""
        return self.serializer.decode(value)

    def dbsize(self):
        """获取dbsize数量，改命令不支持codis
        """
        if self.transaction:
            return self.api.dbsize()
        LOG.warning("dbsize is not supported by codis")

    def info(self):
        """获取info信息，该命令不支持codis
        """
        if self.transaction:
            return self.api.info()
        LOG.warning("info is not supported by codis")

    def clear(self):
        """清理所有的key,该命令不支持codis
        """
        if self.transaction:
            return self.api.flushdb()
        LOG.warning("flushdb is not supported by codis")

    def update(self, mapping):
        """使用key/values批量更新"""
        return self.api.mset(dict((key, self.prepare_value(value))
                                  for key, value in mapping.items()))

    def rename(self, old_name, new_name):
        """重命名redis的key
        Args:
            old_name: 旧版本key
            new_name: 新key
        Returns:
            False: 如果key不存在
            True: key存在并且设置成功
        """
        try:
            self.api.rename(mkey(old_name), mkey(new_name))
            return True
        except ResponseError as exc:
            LOG.error("zyredis rename error, error info=%s", exc)
            return False

    def keys(self, pattern="*"):
        '''获取所有的key,不建议使用,codis本身也不支持
        Args:
            pattern: 正则
        Returns:
            list类型key的列表
        '''
        if self.transaction:
            return self.api.keys(pattern)
        LOG.warning("keys is not supported by codis")

    def iterkeys(self, pattern="*"):
        '''使用迭代器遍历key
        '''
        if self.transaction:
            return iter(self.keys(pattern))
        LOG.warning("keys is not supported by codis")

    def iteritems(self, pattern="*"):
        '''使用迭代器获取所有的key和value
        '''
        if self.transaction:
            for key in self.keys(pattern):
                yield (key, self[key])

    def items(self, pattern="*"):
        '''获取所有的key/value对
        '''
        if self.transaction:
            return list(self.iteritems(pattern))

    def itervalues(self, pattern="*"):
        '''获取所有的value
        '''
        if self.transaction:
            for key in self.keys(pattern):
                yield self[key]

    def values(self, pattern="*"):
        """values
        """
        if self.transaction:
            return list(self.itervalues(pattern))

    def pop(self, name):
        """Get and remove key from database (atomic)."""
        name = mkey(name)
        temp = mkey((name, "__poptmp__"))
        self.rename(name, temp)
        value = self[temp]
        del(self[temp])
        return value

    def get(self, key, default=None):
        """Returns the value at ``key`` if present, otherwise returns
        ``default`` (``None`` by default.)"""
        try:
            return self[key]
        except KeyError:
            return default

    def expire(self, key, time):
        """设置key的过期时间
        Args:
            time: int or timedelta object
            key: string
        """
        return self.api.expire(key, time)

    def expireat(self, key, when):
        """设置过期标记
        Args:
            key: string
            when: unixtime or datetime object
        """
        return self.api.expireat(key, when)

    def mget(self, keys):
        """批量获取redis的key
        Args:
            keys: list 输入多个key
        Returns:
            返回list,如果不存在则为None
            ['xxx', None, ...]
        """
        return self.api.mget(keys)

    def mset(self, mapping):
        """批量set
        Args:
            key_value_list: list 多个key,value的list
        Returns:
            True or False
        """
        return self.api.mset(dict((key, self.prepare_value(value))
                                  for key, value in mapping.items()))

    def getset(self, key, value):
        """如果key存在返回key的值并设置value
        如果key不存在返回空并设置value
        Args:
            key: string
            value: string
        """
        return self.api.getset(key, value)

    def exists(self, key):
        """验证key是否存在
        """
        return self.api.exists(key)

    def set(self, name, value):
        """x.set(name, value) <==> x[name] = value"""
        return self.api.set(mkey(name), self.prepare_value(value))

    def __getitem__(self, name):
        """``x.__getitem__(name) <==> x[name]``"""
        name = mkey(name)
        value = self.api.get(name)
        if value is None:
            return None
        return self.value_to_python(value)

    def __setitem__(self, name, value):
        """``x.__setitem(name, value) <==> x[name] = value``"""
        return self.api.set(mkey(name), self.prepare_value(value))

    def __delitem__(self, name):
        """``x.__delitem__(name) <==> del(x[name])``
        Returns:
            True: delete success
            False: key is not exists
        """
        name = mkey(name)
        if not self.api.delete(name):
            return False
        return True

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        if self.transaction:
            return self.api.dbsize()
        LOG.warning("dbsize is not supported by codis")

    def __contains__(self, name):
        """``x.__contains__(name) <==> name in x``"""
        return self.api.exists(mkey(name))

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return "<RedisClient: {}:{}/{}>".format(self.host,
                                                self.port,
                                                self.db or "")


    def _wrap(self, method, *args, **kwargs):
        """对执行的命令进行验证
        Args:
            method: redis的方法
        """
        LOG.debug("redis adapter execute method:%s, args=%s, kwargs=%s", method, args, kwargs)
        try:
            key = args[0]
        except IndexError:
            raise ValueError('method %s requires a key param as the first argument' % method)
        if method.upper() in NOT_SUPPORT_COMMANDS:
            LOG.error('%s is not supported by codis', method)
            raise NotSupportCommandError('method %s is not supported by codis, key=%s' % (method, key))
        codis_func = getattr(self.api, method)
        return codis_func(*args, **kwargs)


    def __getattr__(self, method):
        """用于适配未定义的redis client的函数
        """
        LOG.debug("in __getattr__ method")
        return functools.partial(self._wrap, method)

    def pipeline(self):
        '''转换为自定义pipeline
        '''
        return Pipeline(self, self.transaction)


class Pipeline(object):

    '''自定义pipeline
    '''

    def __init__(self, client, transaction=False):
        self.codis_pipeline = client.api.pipeline(transaction=transaction)

    def _wrap(self, method, *args, **kwargs):
        '''打包pipeline的方法
        Args:
            method: pipeline要执行的方法
            args: pipeline执行方法的参数
            kwargs: pipeline字典参数
        '''
        LOG.debug("pipeline execute method:%s, args=%s, kwargs=%s", method, args, kwargs)
        try:
            key = args[0]
        except:
            raise ValueError("'%s' requires a key param as the first argument" % method)
        if method.upper() in NOT_SUPPORT_COMMANDS:
            LOG.error('%s is not supported by codis', method)
            raise NotSupportCommandError('method %s is not supported by codis, key=%s' % (method, key))
        # 执行codis
        f = getattr(self.codis_pipeline, method)
        f(*args, **kwargs)

    def execute(self):
        '''提交pipeline执行
        '''
        LOG.debug("pipeline execute flag")
        return self.codis_pipeline.execute()

    def __getattr__(self, method):
        return functools.partial(self._wrap, method)
