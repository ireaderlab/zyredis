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
    init_from = "local"
    redis_manager = None
    redis_conf = {
        0: "redis://localhost:6371/myclient?weight=1&db=0&transaction=1",
        1:"redis://localhost:6371/myclient?weight=1&db=1&transaction=0"
    }

    @property
    def db(self):
        """当前使用的redis,RedisManager使用前需要进行初始化
        """
        if self.redis_manager is None:
            if self.init_from == "qconf":
                self.redis_manager = RedisManager.instance().init_from_qconf(self.zk_path)
            else:
                self.redis_manager = RedisManager.instance().init_from_local(self.redis_conf)
        return self.redis_manager.select_db(self.client_name, self.db_num)

    @property
    def key(self):
        """构造redis的key
        """
        return Key(self.prefix)
