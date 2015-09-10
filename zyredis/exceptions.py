#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: exceptions.py
创 建 者: WangLichao
创建日期: 2015-08-18
"""


class ZyRedisError(StandardError):

    """错误类统一处理
    """
    pass


class NotSupportCommandError(ZyRedisError):

    """命令不支持
    """
    pass


class ConfError(ZyRedisError):

    """获取配置失败
    """
    pass

if __name__ == '__main__':
    pass
