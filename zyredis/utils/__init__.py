#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014,掌阅科技
All rights reserved.

摘    要: client.py
创 建 者: WangLichao
创建日期: 2014-10-24
"""
import logging
import time
from datetime import datetime

LOG = logging.getLogger("zyredis")

def sublist(lst, slice_size):
    """列表切片
    """
    if not slice_size:
        return lst
    sub = []
    result = []
    for i in lst:
        sub += [i]
        if len(sub) == slice_size:
            result += [sub]
            sub = []
    if sub:
        result += [sub]
    return result


def maybe_list(value):
    """maybe list
    """
    if hasattr(value, "__iter__"):
        return value
    if value is None:
        return []
    return [value]


def mkey(names, flag="_"):
    """mkey
    """
    return flag.join(maybe_list(names))


def dt_to_timestamp(datetime_):
    """Convert :class:`datetime` to UNIX timestamp."""
    return time.mktime(datetime_.timetuple())


def maybe_datetime(timestamp):
    """Convert datetime to timestamp, only if timestamp
    is a datetime object."""
    if isinstance(timestamp, datetime):
        return dt_to_timestamp(timestamp)
    return timestamp
