#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: 基础model类实现用于统一管理redis的Model
创 建 者: WangLichao
创建日期: 2015-08-19
"""
from zyredis.manager import RedisManager
from zyredis.key import Key


class Model(object):

    """redis所有model的基类
    Attributes:
        client_name: 选择redis
        db_num: 使用db编号
    """
    client_name = ""
    db_num = 0
    prefix = ""
    zk_path = ""
    redis_manager = None

    @property
    def db(self):
        """当前使用的redis,RedisManager使用前需要进行初始化
        """
        if self.redis_manager is None:
            self.redis_manager = RedisManager.instance().init(self.zk_path)
        return self.redis_manager.select_db(self.client_name, self.db_num)

    @property
    def key(self):
        """构造redis的key
        """
        return Key(self.prefix)
