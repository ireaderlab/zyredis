#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014,掌阅科技
All rights reserved.

摘    要: serialization.py
创 建 者: WangLichao
创建日期: 2014-10-24
"""

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import ujson as json
except ImportError:
    import json

from zyredis.utils import maybe_list


class Serializer(object):
    """序列化的基类
    序列化和反序列化一定要成对
    Attributes:
        encoding: 编码方式
    Example:
        >>> s = Pickler(encoding='zlib')
        >>> val = s.encode({"foo": "bar"})
        >>> s.decode(val)
    """

    def __init__(self, encoding=None):
        self.encoding = encoding

    def encode(self, value):
        """Encode value."""
        value = self.serialize(value)
        if self.encoding:
            value = value.encode(self.encoding)
        return value

    def decode(self, value):
        """Decode value."""
        if self.encoding:
            value = value.decode(self.encoding)
        return self.deserialize(value)

    def serialize(self, value):
        """序列化
        """
        raise NotImplementedError("Serializers must implement serialize()")

    def deserialize(self, value):
        """反序列化
        """
        raise NotImplementedError("Serializers must implement deserialize()")


class Plain(Serializer):
    """不做操作的方式
    """

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class Pickler(Serializer):
    """pickle序列化方式"""
    protocol = 2

    def serialize(self, value):
        return pickle.dumps(value, protocol=self.protocol)

    def deserialize(self, value):
        return pickle.loads(value)


class JSON(Serializer):
    '''JSON序列化方式'''
    def serialize(self, value):
        return json.dumps(value)

    def deserialize(self, value):
        try:
            return json.loads(value)
        except ValueError:
            return value
