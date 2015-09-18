#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014,掌阅科技
All rights reserved.

摘    要: types.py
创 建 者: WangLichao
创建日期: 2014-10-24
"""
import sys
import bisect
from Queue import Empty, Full

from redis.exceptions import ResponseError
from zyredis.utils import mkey
from zyredis.utils import sublist

MAX_INT = sys.maxint


class Type(object):

    """Base-class for Redis datatypes."""

    def __init__(self, name, client):
        self.name = mkey(name)
        self.client = client

    def __getindex__(self, i, j, step, length):
        if i is None:
            i = 0 if step > 0 else length - 1
        elif i < 0:
            i = length + i
        if j is None or j == MAX_INT:
            j = length if step > 0 else -1
        elif j < 0:
            j = length + j
        if step < 0:
            i, j = j + 1, i + 1
        return i, j


class List(Type):

    """list"""

    def __init__(self, name, client, initial=None, auto_slice=True, max_slice_size=50):
        super(List, self).__init__(name, client)
        self.extend(initial or [])
        self.auto_slice = auto_slice
        self.max_slice_size = max_slice_size

    def __getitem__(self, index):
        """``x.__getitem__(index) <==> x[index]``"""
        if isinstance(index, slice):
            li_len = self.__len__()
            i, j = self.__getindex__(index.start, index.stop, index.step, li_len)
            return self.__getslice__(i, j, index.step)
        item = self.client.lindex(self.name, index)
        if item:
            return item
        raise IndexError("list index out of range")

    def __setitem__(self, index, value):
        """``x.__setitem__(index, value) <==> x[index] = value``"""
        try:
            self.client.lset(self.name, index, value)
        except ResponseError, exc:
            if "index out of range" in exc.args:
                raise IndexError("list assignment index out of range")
            raise

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.llen(self.name)

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_list())

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_list())

    def __getslice__(self, i, j, step=1):
        """``x.__getslice__(start, stop) <==> x[start:stop]``"""
        # Redis indices are zero-based, while Python indices are 1-based.
        if i >= j:
            return []
        result = self._slice(i, j)
        return result[::step]

    def _as_list(self):
        """as list
        """
        slice_len = self.__len__()
        return self._slice(0, slice_len)

    def _slice(self, i, j):
        """执行List切片操作,i < j
        """
        if self.auto_slice:
            result = []
            slice_len = self.__len__()
            if j > slice_len:
                j = slice_len
            keys = range(i, j)
            slice_li = sublist(keys, self.max_slice_size)
            for sli in slice_li:
                start = sli[0]
                end = sli[-1]
                slice_li = self.client.lrange(self.name, start, end)
                result.extend(slice_li)
            return result
        else:
            return self.client.lrange(self.name, i, j - 1)

    def copy(self):
        """copy
        """
        return self._as_list()

    def append(self, value):
        """Add ``value`` to the end of the list."""
        return self.client.rpush(self.name, value)

    def appendleft(self, value):
        """Add ``value`` to the head of the list."""
        return self.client.lpush(self.name, value)

    def trim(self, start, stop):
        """Trim the list to the specified range of elements."""
        return self.client.ltrim(self.name, start, stop - 1)

    def pop(self):
        """Remove and return the last element of the list."""
        return self.client.rpop(self.name)

    def popleft(self):
        """Remove and return the first element of the list."""
        return self.client.lpop(self.name)

    def remove(self, value, count=1):
        """Remove occurences of ``value`` from the list.
        Args:
            count: Number of matching values to remove.
                   Default is to remove a single value.
        """
        count = self.client.lrem(self.name, value, num=count)
        if not count:
            raise ValueError("%s not in list" % value)
        return count

    def extend(self, iterable):
        """Append the values in ``iterable`` to this list."""
        for value in iterable:
            self.append(value)

    def extendleft(self, iterable):
        """Add the values in ``iterable`` to the head of this list."""
        for value in iterable:
            self.appendleft(value)


class Set(Type):

    """set"""

    def __init__(self, name, client, initial=None):
        super(Set, self).__init__(name, client)
        if initial:
            self.update(initial)

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_set())

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return "<Set: %s>" % (repr(list(self._as_set())), )

    def __contains__(self, member):
        """``x.__contains__(member) <==> member in x``"""
        return self.client.sismember(self.name, member)

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.scard(self.name)

    def _as_set(self):
        """as set
        """
        return self.client.smembers(self.name)

    def copy(self):
        """copy
        """
        return self._as_set()

    def add(self, member):
        """Add element to set.
        """
        return self.client.sadd(self.name, member)

    def remove(self, member):
        """Remove element from set; it must be a member.
        Exceptions:
            KeyError: if the element is not a member.
        """
        if not self.client.srem(self.name, member):
            raise KeyError(member)

    def pop(self):
        """Remove and return an arbitrary set element.
        Exceptions:
            KeyError: if the set is empty.
        """
        member = self.client.spop(self.name)
        if member is not None:
            return member
        raise KeyError()

    def union(self, other):
        """Return the union of sets as a new set.
        """
        if isinstance(other, self.__class__):
            return self.client.sunion([self.name, other.name])
        else:
            return self._as_set().union(other)

    def update(self, other):
        """Update this set with the union of itself and others."""
        if isinstance(other, self.__class__):
            return self.client.sunionstore(self.name, [self.name, other.name])
        else:
            for member in other:
                self.add(member)
            # return map(self.add, other) # bad-buildin

    def intersection(self, other):
        """Return the intersection of two sets as a new set.
        """
        if isinstance(other, self.__class__):
            return self.client.sinter([self.name, other.name])
        else:
            return self._as_set().intersection(other)

    def intersection_update(self, other):
        """Update the set with the intersection of itself and another."""
        return self.client.sinterstore(self.name, [self.name, other.name])

    def difference(self, *others):
        """Return the difference of two or more sets as a new :class:`set`.
        """
        if all([isinstance(a, self.__class__) for a in others]):
            return self.client.sdiff([self.name] + [other.name for other in others])
        else:
            othersets = [x for x in others if isinstance(x, set)]
            # othersets = filter(lambda x: isinstance(x, set), others) # bad-buildin
            othertypes = [x for x in others if isinstance(x, self.__class__)]
            # othertypes = filter(lambda x: isinstance(x, self.__class__), others) # bad-buildin
            return self.client.sdiff([self.name] + [other.name for other in othertypes]).difference(*othersets)

    def difference_update(self, other):
        """Remove all elements of another set from this set."""
        return self.client.sdiffstore(self.name, [self.name, other.name])


class SortedSet(Type):

    """A sorted set.
    Args:
        initial: Initial data to populate the set with,
                 must be an iterable of ``(element, score)`` tuples.
    """
    class _itemsview(object):

        """视图类
        """

        def __init__(self, zset, start=0, end=-1, desc=False,
                     withscores=False):
            self.zset = zset
            self.start = start
            self.end = end
            self.desc = desc
            self.withscores = withscores

        def _items(self, start, end, desc, withscores):
            """get all items
            """
            return self.zset.items(start, end, desc=desc,
                                   withscores=withscores)

        def __iter__(self):
            """for iter
            """
            return iter(self._items(self.start, self.end, self.desc,
                                    self.withscores))

        def __reversed__(self):
            """for reverse
            """
            return self._items(self.start, self.end, True, self.withscores)

        def __getitem__(self, key):
            if isinstance(key, slice):
                i = key.start or 0
                j = key.stop or -1
                j = j - 1
                return self._items(i, j, False, self.withscores)
            else:
                return self._items(key, key, False, self.withscores)[0]

    def __init__(self, name, client, initial=None, auto_slice=True, max_slice_size=50):
        super(SortedSet, self).__init__(name, client)
        if initial:
            self.update(initial)
        self.auto_slice = auto_slice
        self.max_slice_size = max_slice_size

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_set())

    def __getitem__(self, index):
        """``x.__getitem__(index) <==> x[index]``"""
        if isinstance(index, slice):
            set_len = self.__len__()
            i, j = self.__getindex__(index.start, index.stop, index.step, set_len)
            return self.__getslice__(i, j, index.step)
        item = self.client.zrange(self.name, index, index)
        if item:
            return item
        raise IndexError("sortedset index out of range")

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.zcard(self.name)

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return "<SortedSet: %s>" % (repr(list(self._as_set())), )

    def add(self, member, score):
        """Add the specified member to the sorted set, or update the score
        if it already exist.
        """
        return self.client.zadd(self.name, member, score)

    def remove(self, member):
        """Remove member."""
        if not self.client.zrem(self.name, member):
            raise KeyError(member)

    def revrange(self, start=0, stop=-1):
        """revrange
        """
        stop = stop is None and -1 or stop
        return self.client.zrevrange(self.name, start, stop)

    def discard(self, member):
        """Discard member."""
        self.client.zrem(self.name, member)

    def increment(self, member, amount=1):
        """Increment the score of ``member`` by ``amount``."""
        return self.client.zincrby(self.name, member, amount)

    def rank(self, member):
        """Rank the set with scores being ordered from low to high."""
        return self.client.zrank(self.name, member)

    def revrank(self, member):
        """Rank the set with scores being ordered from high to low."""
        return self.client.zrevrank(self.name, member)

    def score(self, member):
        """Return the score associated with the specified member."""
        return self.client.zscore(self.name, member)

    def range_by_score(self, min_, max_, start=None, num=None, withscores=False, score_cast_func=float):
        """Return all the elements with score >= min and score <= max
        (a range query) from the sorted set.
        """
        return self.client.zrangebyscore(self.name, min_, max_, start=start, num=num,
                                         withscores=withscores, score_cast_func=score_cast_func)

    def update(self, iterable):
        """update
        """
        # support dict type
        if isinstance(iterable, dict):
            iterable = iterable.iteritems()
        for member, score in iterable:
            self.add(member, score)

    def __getslice__(self, i, j, step=1):
        """``x.__getslice__(start, stop) <==> x[start:stop]``"""
        if i >= j:
            return []
        result = self.zrange_slice(i, j)
        return result[::step]

    def _as_set(self):
        """使用zrange
        """
        slice_len = self.__len__()
        return self.zrange_slice(0, slice_len)

    def items(self, start=0, end=-1, desc=False, withscores=False):
        """items
        """
        return self.zrange_slice(start, end, desc=desc, withscores=withscores)

    def zrange_slice(self, start=0, end=-1, desc=False, withscores=False):
        """切片后使用zrange
        """
        if self.auto_slice:
            result = []
            set_len = self.__len__()
            if end < 0:
                end = set_len + end + 1
            if end > set_len:
                end = set_len
            keys = range(start, end)
            slice_li = sublist(keys, self.max_slice_size)
            for sli in slice_li:
                i = sli[0]
                j = sli[-1]
                slice_li = self.client.zrange(self.name, i, j, desc=desc, withscores=withscores)
                result.extend(slice_li)
            return result
        else:
            return self.client.zrange(self.name, start, end - 1, desc=desc, withscores=withscores)

    def itemsview(self, start=0, end=-1, desc=False):
        """itemsview
        """
        return self._itemsview(self, start, end, desc, withscores=True)

    def keysview(self, start=0, end=-1, desc=False):
        """keysview
        """
        return self._itemsview(self, start, end, desc, withscores=False)

    def copy(self):
        """复制
        """
        return self._as_set()

    def count(self, minnum, maxnum):
        """获取指定分数范围内的key个数（包含界定分数）
        minnum可以指定为'-inf'表示最小分数
        maxnum可以指定为'+inf'表示最大分数
        """
        return self.client.zcount(self.name, minnum, maxnum)


class Dict(Type):

    """A dictionary."""

    def __init__(self, name, client, initial=None, auto_slice=True, max_slice_size=50, **extra):
        super(Dict, self).__init__(name, client)
        initial = dict(initial or {}, **extra)
        if initial:
            self.update(initial)
        self.auto_slice = auto_slice
        self.max_slice_size = max_slice_size

    def __getitem__(self, key):
        """``x.__getitem__(key) <==> x[key]``"""
        value = self.client.hget(self.name, key)
        if value is not None:
            return value
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        """``x.__setitem__(key, value) <==> x[key] = value``"""
        return self.client.hset(self.name, key, value)

    def __delitem__(self, key):
        """``x.__delitem__(key) <==> del(x[key])``"""
        if not self.client.hdel(self.name, key):
            raise KeyError(key)

    def __contains__(self, key):
        """``x.__contains__(key) <==> key in x``"""
        return self.client.hexists(self.name, key)

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.hlen(self.name)

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return self.iteritems()

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_dict())

    def keys(self):
        """Returns the list of keys present in this dictionary."""
        return self.client.hkeys(self.name)

    def values(self):
        """Returns the list of values present in this dictionary."""
        return self.client.hvals(self.name)

    def items(self):
        """This dictionary as a list of ``(key, value)`` pairs, as
        2-tuples.
        """
        return self._as_dict().items()

    def iteritems(self):
        """Returns an iterator over the ``(key, value)`` items present in this
        dictionary.
        """
        return iter(self.items())

    def iterkeys(self):
        """Returns an iterator over the keys present in this dictionary."""
        return iter(self.keys())

    def itervalues(self):
        """Returns an iterator over the values present in this dictionary."""
        return iter(self.values())

    def has_key(self, key):
        """Returns ``True`` if ``key`` is present in this dictionary,
        ``False`` otherwise.
        """
        return key in self

    def get(self, key, default=None):
        """Returns the value at ``key`` if present, otherwise returns
        ``default`` (``None`` by default.)
        """
        try:
            return self[key]
        except KeyError:
            return default

    def mget(self, keys):
        """返回一个或多个给定域的值
        Args:
            keys: list 需获取值的key列表
        Returns:
            值的列表,顺序与传入参数顺序一致
        """
        if self.auto_slice and isinstance(keys, list):
            result = []
            slice_list = sublist(keys, self.max_slice_size)
            for sli in slice_list:
                slice_li = self.client.hmget(self.name, sli)
                result.extend(slice_li)
            return result
        else:
            return self.client.hmget(self.name, keys)

    def setdefault(self, key, default=None):
        """Returns the value at ``key`` if present, otherwise
        stores ``default`` value at ``key``.
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def pop(self, key, *args, **kwargs):
        """Remove specified key and return the corresponding value.
        Args:
            default: If key is not found, ``default`` is returned if given,
                     otherwise :exc:`KeyError` is raised.
        """
        try:
            val = self[key]
        except KeyError:
            if len(args):
                return args[0]
            if "default" in kwargs:
                return kwargs["default"]
            raise

        try:
            del self[key]
        except KeyError:
            pass

        return val

    def update(self, other):
        """Update this dictionary with another."""
        return self.client.hmset(self.name, other)

    def _as_dict(self):
        """使用hgetall
        """
        return self.client.hgetall(self.name)

    def copy(self):
        """复制
        """
        return self._as_dict()


class Queue(Type):

    """FIFO Queue."""

    Empty = Empty
    Full = Full

    def __init__(self, name, client, initial=None, maxsize=0):
        super(Queue, self).__init__(name, client)
        self.list = List(name, client, initial)
        self.maxsize = maxsize
        self._pop = self.list.pop
        self._bpop = self.client.brpop
        self._append = self.list.appendleft

    def empty(self):
        """Return ``True`` if the queue is empty, or ``False``
        otherwise (not reliable!)."""
        return not len(self.list)

    def full(self):
        """Return ``True`` if the queue is full, ``False``
        otherwise (not reliable!).

        Only applicable if :attr:`maxsize` is set.

        """
        return self.maxsize and len(self.list) >= self.maxsize or False

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args ``block`` is ``True`` and ``timeout`` is
        ``None`` (the default), block if necessary until an item is
        available.  If ``timeout`` is a positive number, it blocks at
        most ``timeout`` seconds and raises the :exc:`Queue.Empty` exception
        if no item was available within that time. Otherwise (``block`` is
        ``False``), return an item if one is immediately available, else
        raise the :exc:`Queue.Empty` exception (``timeout`` is ignored
        in that case).
        """
        if not block:
            return self.get_nowait()
        item = self._bpop([self.name], timeout=timeout)
        if item is not None:
            return item
        raise Empty

    def get_nowait(self):
        """Remove and return an item from the queue without blocking.
        Exceptions:
            Queue.Empty: if an item is not immediately available.
        """
        item = self._pop()
        if item is not None:
            return item
        raise Empty()

    def put(self, item):
        """Put an item into the queue."""
        if self.full():
            raise Full()
        self._append(item)

    def qsize(self):
        """Returns the current size of the queue."""
        return len(self.list)


class LifoQueue(Queue):

    """Variant of :class:`Queue` that retrieves most recently added
    entries first."""

    def __init__(self, name, client, initial=None, maxsize=0):
        super(LifoQueue, self).__init__(name, client, initial, maxsize)
        self._pop = self.list.popleft
        self._bpop = self.client.blpop


class Int(Type):

    """实现对int类型的基础操作
    """

    def __add__(self, other):
        return type(other).__radd__(other, self.__int__())

    def __sub__(self, other):
        return type(other).__rsub__(other, self.__int__())

    def __cmp__(self, other):
        return cmp(self.__int__(), other)

    def __mul__(self, other):
        return type(other).__rmul__(other, self.__int__())

    def __div__(self, other):
        return type(other).__rdiv__(other, self.__int__())

    def __truediv__(self, other):
        return type(other).__rtruediv__(other, self.__int__())

    def __floordiv__(self, other):
        return type(other).__rfloordiv__(other, self.__int__())

    def __mod__(self, other):
        return type(other).__rmod__(other, self.__int__())

    def __divmod__(self, other):
        return type(other).__rdivmod__(other, self.__int__())

    def __pow__(self, other):
        return type(other).__rpow__(other, self.__int__())

    def __lshift__(self, other):
        return type(other).__rlshift__(other, self.__int__())

    def __rshift__(self, other):
        return type(other).__rrshift__(other, self.__int__())

    def __and__(self, other):
        return type(other).__rand__(other, self.__int__())

    def __or__(self, other):
        return type(other).__ror__(other, self.__int__())

    def __xor__(self, other):
        return type(other).__rxor__(other, self.__int__())

    def __radd__(self, other):
        return type(other).__add__(other, self.__int__())

    def __rsub__(self, other):
        return type(other).__sub__(other, self.__int__())

    def __rmul__(self, other):
        return type(other).__mul__(other, self.__int__())

    def __rdiv__(self, other):
        return type(other).__div__(other, self.__int__())

    def __rtruediv__(self, other):
        return type(other).__truediv__(other, self.__int__())

    def __rfloordiv__(self, other):
        return type(other).__floordiv__(other, self.__int__())

    def __rmod__(self, other):
        return type(other).__mod__(other, self.__int__())

    def __rdivmod__(self, other):
        return type(other).__divmod__(other, self.__int__())

    def __rpow__(self, other):
        return type(other).__pow__(other, self.__int__())

    def __rlshift__(self, other):
        return type(other).__lshift__(other, self.__int__())

    def __rrshift__(self, other):
        return type(other).__shift__(other, self.__int__())

    def __rand__(self, other):
        return type(other).__and__(other, self.__int__())

    def __ror__(self, other):
        return type(other).__or__(other, self.__int__())

    def __rxor__(self, other):
        return type(other).__xor__(other, self.__int__())

    def __iadd__(self, other):
        self.client.incr(self.name, other)
        return self

    def __isub__(self, other):
        self.client.decr(self.name, other)
        return self

    def __imul__(self, other):
        self.client.set(self.name, int.__mul__(self.__int__(), other))
        return self

    def __idiv__(self, other):
        self.client.set(self.name, int.__div__(self.__int__(), other))
        return self

    def __itruediv__(self, other):
        self.client.set(self.name, int.__truediv__(self.__int__(), other))
        return self

    def __ifloordiv__(self, other):
        self.client.set(self.name, int.__floordiv__(self.__int__(), other))
        return self

    def __imod__(self, other):
        self.client.set(self.name, int.__mod__(self.__int__(), other))
        return self

    def __ipow__(self, other):
        self.client.set(self.name, int.__pow__(self.__int__(), other))
        return self

    def __iand__(self, other):
        self.client.set(self.name, int.__and__(self.__int__(), other))
        return self

    def __ior__(self, other):
        self.client.set(self.name, int.__or__(self.__int__(), other))
        return self

    def __ixor__(self, other):
        self.client.set(self.name, int.__xor__(self.__int__(), other))
        return self

    def __ilshift__(self, other):
        self.client.set(self.name, int.__lshift__(self.__int__(), other))
        return self

    def __irshift__(self, other):
        self.client.set(self.name, int.__rshift__(self.__int__(), other))
        return self

    def __neg__(self):
        return int.__neg__(self.__int__())

    def __pos__(self):
        return int.__pos__(self.__int__())

    def __abs__(self):
        return int.__abs__(self.__int__())

    def __invert__(self):
        return int.__invert__(self.__int__())

    def __long__(self):
        return int.__long__(self.__int__())

    def __float__(self):
        return int.__float__(self.__int__())

    def __complex__(self):
        return int.__complex__(self.__int__())

    def __int__(self):
        return int(self.client.get(self.name))

    def __repr__(self):
        return repr(int(self))

    def copy(self):
        """get real item
        """
        return self.__int__()


class ZSet(object):

    """The simplest local implementation to Redis's Sorted Set imaginable.
    Little thought given to performance, simply get the basic implementation
    right."""

    def __init__(self, initial=None):
        if not self.is_zsettable(initial):
            raise ValueError(initial)
        self._dict = initial

    @staticmethod
    def is_zsettable(initial):
        """quick check that all values in a dict are reals"""
        return all([x for x in initial.values() if isinstance(x, (int, float, long))])
        # return all(map(lambda x: isinstance(x, (int, float, long)), initial.values())) # bad-buildin

    def items(self):
        """items
        """
        return sorted(self._dict.items(), key=lambda x: (x[1], x[0]))

    def __getitem__(self, key):
        """``x.__getitem__('key') <==> x['key'] ``
        """
        return self._as_set()[key]

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return len(self._dict)

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_set())

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_set())

    def add(self, member, score):
        """Add the specified member to the sorted set, or update the score
        if it already exist."""
        self._dict[member] = score

    def remove(self, member):
        """Remove member."""
        del self._dict[member]

    def discard(self, member):
        """discard
        """
        if member in self._dict:
            del self._dict[member]

    def increment(self, member, amount=1):
        """Increment the score of ``member`` by ``amount``."""
        self._dict[member] += amount
        return self._dict[member]

    def rank(self, member):
        """Rank the set with scores being ordered from low to high."""
        return self._as_set().index(member)

    def revrank(self, member):
        """Rank the set with scores being ordered from high to low."""
        return self.__len__() - self.rank(member) - 1

    def score(self, member):
        """Return the score associated with the specified member."""
        return self._dict[member]

    def range_by_score(self, min_, max_):
        """Return all the elements with score >= min and score <= max
        (a range query) from the sorted set."""
        data = self.items()
        keys = [r[1] for r in data]
        start = bisect.bisect_left(keys, min_)
        end = bisect.bisect_right(keys, max_, start)
        return self._as_set()[start:end]

    def _as_set(self):
        """_as_set
        """
        return [x[0] for x in self.items()]
        # return map(lambda x: x[0], self.items()) # bad-buildin
