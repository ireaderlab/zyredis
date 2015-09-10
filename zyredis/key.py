#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014,掌阅科技
All rights reserved.

摘    要: key.py
创 建 者: WangLichao
创建日期: 2014-10-24
"""


class Key(unicode):

    """使用[]操作来拼接redis的key
    默认下划线分隔符
    """

    def __getitem__(self, key):
        if not isinstance(key, basestring):
            key = str(key)
        if not self:
            return Key(key)
        return Key(u"{}_{}".format(self, key))
