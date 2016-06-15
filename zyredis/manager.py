#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: 管理redis实例
创 建 者: WangLichao
创建日期: 2015-08-19
"""
import random
from zyredis.exceptions import ConfError
from zyredis.client import Client
from zyredis.utils.singleton import SingletonMixin
from zyredis.utils import tree
from zyredis.utils.parse_url import parse_from_url
from zyredis.utils import LOG
try:
    from zyredis.utils import qconf_py as qconf
except:
    pass


class RedisManager(SingletonMixin):

    """用于多个redis的ip:port的管理
    """
    redis_pool = tree.create_tree()
    redis_local_flag = True
    zk_path = None

    def init_from_local(self, redis_conf):
        """从配置中读取redis的配置"""
        self.redis_local_flag = True
        self.redis_conf = redis_conf
        if not self.redis_pool:
            self._init_from_conf()
        return self

    def init_from_qconf(self, zk_path):
        self.redis_local_flag = False
        if self.zk_path is None:
            self.zk_path = zk_path

        if not self.redis_pool:
            self._init_from_conf()
        return self

    def _get_conf(self):
        """使用qconf从zookeeper获取节点信息
        """
        try:
            # children = qconf.get_batch_conf(self.zk_path) # 官方qconf_so有内存泄露
            children = self._get_qconf_data()
        except qconf.Error as e:
            raise ConfError(e)

        if not children:
            raise ConfError("cant get conf from qconf, please check conf %s" % self.zk_path)
        return children

    def _get_qconf_data(self):
        """解决qconf get_batch_conf有内存泄露问题
        """
        qconf_data = {}
        data_keys = qconf.get_batch_keys(self.zk_path)
        for _key in data_keys:
            node_key = "{}/{}".format(self.zk_path, _key)
            qconf_data[_key] = qconf.get_conf(node_key)
        return qconf_data

    def _init_from_conf(self):
        """根据配置初始化redis客户端连接
        """
        self.redis_pool = tree.create_tree() # 重置redis_pool
        # qconf的话特殊对待
        if self.redis_local_flag is False:
            self.redis_conf = self._get_conf()
        LOG.info("init redis conf, redis_conf=%s", self.redis_conf)
        for url in self.redis_conf.itervalues():
            options = parse_from_url(url)  # 如果url不符合标准将会直接ValueError异常
            client_name = options["client_name"]
            db = options["db"]
            weight = options["weight"]
            if int(weight) == 0:
                continue
            client = Client(
                host=options["host"],
                port=options["port"],
                db=db,
                transaction=options.get("transaction", False),
            )
            if self.redis_pool[client_name][db]:
                self.redis_pool[client_name][db].extend([client] * weight)
            else:
                self.redis_pool[client_name][db] = [client] * weight

    def _do_check_conf(self):
        """检测配置是否更新,如果配置有变更则重新加载配置信息
        """
        new_conf = self._get_conf()
        for k, v in new_conf.iteritems():
            if self.redis_conf.get(k, None) != v:
                self._init_from_conf()
                LOG.info("run _do_check_conf, config has changed")
                break

    def select_db(self, client_name, db=0):
        """根据client和db选择redis,根据weight配比随机选择
        """
        if not self.redis_local_flag:
            self._do_check_conf()
        if not self.redis_pool[client_name][db]:
            raise ConfError('Redis db Conf Error')
        return random.choice(self.redis_pool[client_name][db])
