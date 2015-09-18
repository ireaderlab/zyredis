#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: test_qconf.py
创 建 者: WangLichao
创建日期: 2015-08-20
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))
import unittest
from zyredis.utils import qconf_py as qconf


def get_qconf_data(zk_path):
    """解决qconf get_batch_conf有内存泄露问题
    """
    qconf_data = {}
    data_keys = qconf.get_batch_keys(zk_path)
    for _key in data_keys:
        node_key = "{}/{}".format(zk_path, _key)
        qconf_data[_key] = qconf.get_conf(node_key)
    return qconf_data


class TestQconf(unittest.TestCase):

    """测试qconf读取配置
    """

    def test_api(self):
        """测试基本api
        """
        key = "/test_group/service/codis"
        value = qconf.get_conf(key)
        keys = qconf.get_batch_keys(key)
        assert isinstance(keys, list)
        children = qconf.get_batch_conf(key)
        assert isinstance(children, dict)

    def test_memleak_get_conf(self):
        """测试get_conf是否有内存泄露
        """
        key = "/test_group/service/codis"
        i = 0
        while i < 1:
            qconf.get_conf(key)
            i = i + 1

    def test_memleak_get_batch_keys(self):
        """测试get_batch_keys是否有内存泄露
        """
        key = "/test_group/service/codis"
        i = 0
        while i < 1:
            qconf.get_batch_keys(key)
            i = i + 1

    def test_memleak_get_batch_conf(self):
        """测试get_batch_conf是否有内存泄露
        """
        key = "/test_group/service/codis"
        i = 0
        while i < 1:
            qconf.get_batch_conf(key)
            i = i + 1

    def test_diff_get_batch_conf(self):
        """批量获取对比接口测试
        """
        key = "/test_group/service/codis"
        children1 = qconf.get_batch_conf(key)
        children2 = get_qconf_data(key)
        assert len(children1) == len(children2)
        assert children1['0'] == children2["0"]
        assert children1['1'] == children2["1"]

if __name__ == '__main__':
    unittest.main()
