#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: test_key.py
创 建 者: WangLichao
创建日期: 2015-08-18
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))
import unittest
from zyredis.key import Key


class TestKeyModel(unittest.TestCase):

    """测试key生成逻辑
    """

    def test_key_with_prefix(self):
        """测试带前缀情况
        """
        key = Key("prefix") # 有前缀
        mykey = key["abc"]["def"]["ddd"]
        assert mykey == "prefix_abc_def_ddd"

    def test_key_no_prefix(self):

        """测试没有前缀的情况
        """
        key = Key() # 无前缀
        key1 = Key("")
        mykey = key["abc"]["def"]
        mykey1 = key1["abc"]["def"]
        assert mykey == "abc_def"
        assert mykey1 == "abc_def"
        key2 = Key("")
        mykey2 = key2["ttt"]["xxx"]
        assert mykey2 == "ttt_xxx"

if __name__ == '__main__':
    unittest.main()
