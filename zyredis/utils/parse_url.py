#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: parse_url.py
创 建 者: WangLichao
创建日期: 2015-08-21
"""
from urlparse import urlparse, parse_qs

def parse_from_url(url):
    """从url解析配置信息
    Example:
        url = "redis://host:port/client_name?db=0&weight=1"
        url = "redis://localhsot:6379/myredis?db=0&weight=1"
    Args:
        url: string
    """
    url_string = url
    url = urlparse(url)
    qs = ''

    # in python2.6, custom URL schemes don't recognize querystring values
    # they're left as part of the url.path.
    if '?' in url.path and not url.query:
        # chop the querystring including the ? off the end of the url
        # and reparse it.
        qs = url.path.split('?', 1)[1]
        url = urlparse(url_string[:-(len(qs) + 1)])
    else:
        qs = url.query
    if url.scheme != "redis" or not url.path:
        raise ValueError("url conf error, url must be redis protocol")

    url_options = {}

    for name, value in parse_qs(qs).iteritems():
        if value and len(value) > 0:
            url_options[name] = value[0]
    url_options['db'] = int(url_options.get('db', 0))
    url_options['weight'] = int(url_options.get('weight', 1))
    url_options['client_name'] = url.path.lstrip("/")
    host, port = url.netloc.split(":") # 如果不符合规则抛出ValueError异常
    url_options['host'] = host
    url_options['port'] = port
    return url_options
