#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (c) 2014,掌阅科技
All rights reserved.

摘    要: tree.py
创 建 者: WangLichao
创建日期: 2014-10-25
'''
from collections import defaultdict

class DefaultDict(defaultdict):
    '''为defaultdict添加属性操作
    '''
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, val):
        self[attr] = val

def create_tree():
    '''使用字典表示树的节点，非字典类型表示叶子节点
    具体使用请参考测试数据
    '''
    return DefaultDict(create_tree)

def dicts(t):
    '''获取树的叶子节点
    '''
    if isinstance(t, dict):
        return {k: dicts(t[k]) for k in t}
    return t

if __name__ == '__main__':
    a = create_tree()
    a['x']['z'] = 6
    a['x']['d'] = [4, 6, 9]
    a['x']['y']['dd'] = 1
    a['x']['y']['xd'] = 1
    if a.z.y:
        print 'xxx'
    a.x.y.z = 248
    import ujson
    print ujson.dumps(a)
    print dicts(a)
