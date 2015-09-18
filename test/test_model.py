#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: test_model.py
创 建 者: WangLichao
创建日期: 2015-08-21
"""
import sys
import os
import time
import logging.config
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))
import unittest
from zyredis.model import Model

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'zyredis': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

logging.config.dictConfig(LOGGING)


class BaseModel(Model):

    client_name = "test_codis"
    db_num = 0
    zk_path = "/test_group/service/codis"


class TestModel(BaseModel):

    prefix = "wlctest"

    def set_key(self, arg1, arg2, val):
        self.db[self.key[arg1][arg2]] = val

    def set_key1(self, arg1, val):
        self.db.set(self.key[arg1], val)

    def get_key(self, arg1, arg2):
        return self.db[self.key[arg1][arg2]]

    def get_key1(self, arg1):
        return self.db.get(self.key[arg1])


class TestNoPrefixModel(BaseModel):

    def set_key(self, arg1, arg2, val):
        self.db[self.key[arg1][arg2]] = val

    def set_key1(self, arg1, val):
        self.db.set(self.key[arg1], val)

    def get_key(self, arg1, arg2):
        return self.db[self.key[arg1][arg2]]

    def get_key1(self, arg1):
        return self.db.get(self.key[arg1])


class TestRedisModel(unittest.TestCase):

    """测试redis manager基本用法
    """

    def test_basic(self):
        """测试基本操作
        """
        i = 0
        tb = TestModel()
        while i < 1:
            tb.set_key("abc", "def", "value")
            assert tb.key["abc"]["def"] == "wlctest_abc_def"
            assert tb.get_key("abc", "def") == "value"
            i = i + 1
        tb.set_key1("ddd", "newvalue")
        assert tb.key["ddd"] == "wlctest_ddd"
        assert tb.get_key1("ddd") == "newvalue"
        # 无前缀key测试
        tb_noprefix = TestNoPrefixModel()
        tb_noprefix.set_key("abc", "def", "value")
        assert tb_noprefix.key["abc"]["def"] == "abc_def"
        assert tb_noprefix.get_key("abc", "def") == "value"
        tb_noprefix.set_key1("ddd", "newvalue")
        assert tb_noprefix.key["ddd"] == "ddd"
        assert tb_noprefix.get_key1("ddd") == "newvalue"

if __name__ == '__main__':
    unittest.main()
