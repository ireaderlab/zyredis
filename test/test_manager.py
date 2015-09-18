#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: test_manager.py
创 建 者: WangLichao
创建日期: 2015-08-21
"""
import sys
import os
import time
import logging.config
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))
import unittest
from zyredis.manager import RedisManager

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


class TestRedisManager(unittest.TestCase):

    """测试redis manager基本用法
    """

    def test_singleton(self):
        """测试基本操作
        """
        r1, r2 = RedisManager.instance(), RedisManager.instance()
        assert r1 is r2

    def test_init(self):
        """测试初始化方法,以及配置变更后是否自动识别
        """
        count = 0
        while True:
            rm = RedisManager.instance().init("/test_group/service/test")
            db = rm.select_db("test")
            db.set("wlctest", "wlctest")
            assert db.get("wlctest") == "wlctest"
            time.sleep(1)
            count += 1
            if count > 1:
                break


if __name__ == '__main__':
    unittest.main()
