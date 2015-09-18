#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015,掌阅科技
All rights reserved.

摘    要: test_client.py
创 建 者: WangLichao
创建日期: 2015-08-19
"""
import sys
import os
import logging.config
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))
import unittest
import zyredis
from zyredis.serialization import JSON

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

CODIS_CLI = zyredis.Client('localhost', 6389, transaction=False)
CLI = zyredis.Client('localhost', 6389, transaction=True)


class TestClient(unittest.TestCase):

    """测试key生成逻辑
    """
    def setUp(self):
        """setup
        """
        self.db = zyredis.Client(host='localhost', port=6389, serializer=JSON(), transaction=True)
        self.codis_db = zyredis.Client(host='localhost', port=6389, serializer=JSON(), transaction=False)

    # string type
    def test_string(self):
        """test pyredis string type
        """
        # set
        self.db["foo"] = 'bar'

        # get
        self.failUnlessEqual(self.db['foo'], 'bar')
        self.failUnlessEqual(self.db.get('foo'), 'bar')

        # update
        self.db.update({'company': 'ZhangYue', 'product': 'iReader'})
        self.failUnlessEqual(self.db.get('company'), 'ZhangYue')
        self.failUnlessEqual(self.db.get('product'), 'iReader')

        # mset
        self.db.mset({'wanglichao': 1, 'wlc': 2})

        # mget
        data = self.db.mget(['wanglichao', 'wlc'])
        self.failUnlessEqual(self.db.get('wanglichao'), 1)
        self.failUnlessEqual(self.db.get('wlc'), 2)

    def test_range_by_score(self):
        """测试zrangebyscore问题
        """
        ss = self.db.SortedSet(name="test_sortedset_zrangebyscore",
                               initial=(('wlc', 1), ('ls', 2), ('wyf', 3)))
        assert ss.range_by_score(0, 10, 0, 1)[0] == 'wlc'
        assert ss.range_by_score(0, 10, 1, 1)[0] == 'ls'
        assert ss.range_by_score(0, 10, 2, 1)[0] == 'wyf'

    # db level
    def test_db_level(self):
        """pyredis db
        """
        self.db['color'] = 'white'
        self.db['animal'] = 'dog'

        # in
        self.failUnlessEqual('color' in self.db, True)

        # rename
        self.db.rename('color', 'a_color')
        self.failUnlessEqual('color' in self.db, False)
        self.failUnlessEqual('a_color' in self.db, True)

        # pop
        self.failUnlessEqual(self.db.pop('a_color'), 'white')
        self.failUnlessEqual('a_color' in self.db, False)

        # delete
        del(self.db['animal'])
        self.failUnlessEqual('animal' in self.db, False)


    # List type
    def test_List(self):
        """test pyredis List
        """
        try:
            del self.db['a_list']   # 先删除数据库中名为'a_list'的键，避免干扰。
        except KeyError:
            pass
        l = self.db.List("a_list")

        # append and pop
        l.append("one")
        l.append("two")
        self.failUnlessEqual(l.pop(), 'two')
        l.appendleft('33')
        self.failUnlessEqual(l.popleft(), '33')

        # len
        self.failUnlessEqual(len(l), 1)

        # extend
        l.extend(["11"])
        self.failUnlessEqual(l.pop(), '11')
        l.extendleft(["aa"])
        self.failUnlessEqual(l.popleft(), 'aa')

        # copy
        l.extend(['two', 'three'])
        self.failUnlessEqual(l.copy(), ['one', 'two', 'three'])

        # get and set
        self.failUnlessEqual(l[0], 'one')
        self.failUnlessEqual(l[-1], 'three')
        l[0] = 'abc'
        self.failUnlessEqual(l[0], 'abc')

        # slice
        self.failUnlessEqual(l[0:2], ['abc', 'two'])
        self.failUnlessEqual(l[:], ['abc', 'two', 'three'])

        # trim
        l.trim(0, 2)
        self.failUnlessEqual(l[:], ['abc', 'two'])

        # remove
        l.remove('abc')
        self.failUnlessEqual(l[:], ['two'])

    # Queue type
    def test_queue(self):
        """test pyredis Queue
        """
        try:
            del self.db['a_queue']   # 先删除数据库中名为'a_queue'的键，避免干扰。
        except KeyError:
            pass
        q = self.db.Queue('a_queue', maxsize=10)

        # empty
        self.failUnlessEqual(q.empty(), True)

        # full
        self.failUnlessEqual(q.full(), False)

        # put
        q.put('iReader')
        q.put('book')

        # get
        self.failUnlessEqual(q.get(block=False), 'iReader')

        # qsize
        self.failUnlessEqual(q.qsize(), 1)

    # LifoQueue type
    def test_lifoqueue(self):
        try:
            del self.db['a_lifoqueue']   # 先删除数据库中名为'a_lifoqueue'的键，避免干扰。
        except:
            pass
        lifoq = self.db.LifoQueue('a_lifoqueue', maxsize=10)

        # empty
        self.failUnlessEqual(lifoq.empty(), True)

        # full
        self.failUnlessEqual(lifoq.full(), False)

        # put
        lifoq.put('iReader')
        lifoq.put('book')

        # get
        self.failUnlessEqual(lifoq.get(block=False), 'book')

        # qsize
        self.failUnlessEqual(lifoq.qsize(), 1)

    # Set type
    def test_set_type(self):
        try:
            del self.db['a_set']   # 先删除数据库中名为'a_set'的键，避免干扰。
        except:
            pass
        s = self.db.Set('a_set', {'A', 'B'})

        # contains
        self.failUnlessEqual('A' in s, True)

        # len
        self.failUnlessEqual(len(s), 2)

        # copy
        self.failUnlessEqual(s.copy(), {'A', 'B'})

        # add
        s.add('C')
        self.failUnlessEqual('C' in s, True)

        # remove
        s.remove('A')
        self.failUnlessEqual('A' in s, False)

        # pop
        self.failUnlessEqual(s.pop() in {'B', 'C'}, True)

        # update
        new_s = self.db.Set('b_set', {'A', 'B', 'C'})
        new_s.update({'D', 'E'})
        self.failUnlessEqual('D' in new_s, True)
        self.failUnlessEqual('E' in new_s, True)

        # union
        s1 = self.db.Set('x_set', {'A', 'B', 'C'})
        s2 = self.db.Set('y_set', {'B', 'C', 'D'})
        self.failUnlessEqual(s1.union(s2), {'A', 'B', 'C', 'D'})

        # intersection
        self.failUnlessEqual(s1.intersection(s2), {'B', 'C'})

        # intersection_update
        s1.intersection_update(s2)
        self.failUnlessEqual(s1.copy(), {'B', 'C'})

        # difference
        s1 = self.db.Set('z_set', {'A', 'B', 'C'})
        self.failUnlessEqual(s1.difference(s2), {'A'})
        self.failUnlessEqual(s2.difference(s1), {'D'})

        # difference_update
        s1.difference_update(s2)
        self.failUnlessEqual(s1.copy(), {'A'})
        s2.difference_update(s1)
        self.failUnlessEqual(s2.copy(), {'B', 'C', 'D'})

    # SortedSet type
    def test_sortedset(self):
        try:
            del self.db['sortedset']   # 先删除数据库中名为'sortedset'的键，避免干扰。
        except:
            pass
        sts = self.db.SortedSet('sortedset')

        # add
        sts.add('A', 100)
        sts.add('B', 90)

        # get
        self.failUnlessEqual(sts[0], ['B'])
        self.failUnlessEqual(list(sts), ['B', 'A'])

        # len
        self.failUnlessEqual(len(sts), 2)

        # remove
        sts.remove('A')
        self.failUnlessEqual('A' in sts[:], False)

        # discard
        sts.discard('B')
        self.failUnlessEqual('B' in sts[:], False)

        # update
        sts.update([('C', 80), ('D', 70), ('E', 60)])
        self.failUnlessEqual(list(sts), ['E', 'D', 'C'])

        # copy
        self.failUnlessEqual(sts.copy(), ['E', 'D', 'C'])

        # revrange
        self.failUnlessEqual(sts.revrange(), ['C', 'D', 'E'])

        # score
        self.failUnlessEqual(sts.score('C'), 80)

        # increment
        sts.increment('C', 5)
        new_score = sts.score('C')
        self.failUnlessEqual(new_score, 85)

        # rank
        self.failUnlessEqual(sts.rank('C'), 2)
        self.failUnlessEqual(sts.rank('E'), 0)

        # revrank
        self.failUnlessEqual(sts.revrank('C'), 0)
        self.failUnlessEqual(sts.revrank('E'), 2)

        # range_by_score
        self.failUnlessEqual(sts.range_by_score(60, 85), ['E', 'D', 'C'])
        self.failUnlessEqual(sts.range_by_score(60, 70), ['E', 'D'])

        # items
        sts_items = sts.items()
        self.failUnlessEqual(sts_items, ['E', 'D', 'C'])
        sts_items_withscores = sts.items(withscores=True)
        self.failUnlessEqual(sts_items_withscores, [('E', 60.0), ('D', 70.0), ('C', 85.0)])

    # Dict type
    def test_dict(self):
        try:
            del self.db['a_dict']  # 先删除数据库中名为'a_dict'的键，避免干扰。
        except KeyError:
            pass
        d = self.db.Dict('a_dict')

        # set and get
        d['a'] = 'valueA'
        self.failUnlessEqual(d['a'], 'valueA')
        res = d.get('b', 'default')
        self.failUnlessEqual(res, 'default')

        # setdefault
        res_a = d.setdefault('a', 'valueB')
        self.failUnlessEqual(res_a, 'valueA')
        res_b = d.setdefault('b', 'valueB')
        self.failUnlessEqual(res_b, 'valueB')
        self.failUnlessEqual(d['b'], 'valueB')

        # len
        self.failUnlessEqual(len(d), 2)

        # in
        self.failUnlessEqual('a' in d, True)

        # has_key
        self.failUnlessEqual('b' in d, True)

        # copy
        self.failUnlessEqual(d.copy(), {'a': 'valueA', 'b': 'valueB'})

        # keys
        self.failUnlessEqual(d.keys(), ['a', 'b'])

        # values
        self.failUnlessEqual(d.values(), ['valueA', 'valueB'])

        # items
        d_items = d.items()
        self.failUnlessEqual(('a', 'valueA') in d_items, True)
        self.failUnlessEqual(('b', 'valueB') in d_items, True)

        # iter
        self.failUnlessEqual(('a', 'valueA') in d.iteritems(), True)
        self.failUnlessEqual('a' in d.iterkeys(), True)
        self.failUnlessEqual('valueA' in d.itervalues(), True)

        # update
        d.update({'c': 'valueC', 'd': 'valueD'})
        self.failUnlessEqual('c' in d, True)
        self.failUnlessEqual('d' in d, True)

        # pop
        self.failUnlessEqual(d.pop('c'), 'valueC')
        self.failUnlessEqual('c' in d, False)
        self.failUnlessEqual(d.pop('no_exist_key', 'no_exist'), 'no_exist')

        # del
        del d['b']
        self.failUnlessEqual('b' in d, False)

    def test_basic(self):
        """测试基本操作
        """
        CLI.set("wlc123", "www")
        assert CLI.get("wlc123") == "www"
        CLI.delete("wlc123")
        assert CLI.get("wlc123") is None
        assert CODIS_CLI.dbsize() is None
        assert CLI.dbsize() > 0
        pass

    def test_nodefine(self):
        """测试未实现的方法是否可用
        """
        CLI.hset("wlchset", 'key', 123)
        assert CLI.hget("wlchset", 'key') == "123"  # 注意数据类型发生变化

    def test_pipeline(self):
        """测试管道
        """
        pipe = CLI.pipeline()
        pipe.set('wlc333', 333)
        pipe.set('wlc332', 332)
        pipe.execute()
        assert CLI.get("wlc333") == 333
        pipe = CLI.pipeline()
        pipe.delete("wlc333")
        pipe.delete("wlc332")
        assert CLI.get("wlc333") == 333
        pipe.execute()
        assert CLI.get("wlc333") is None

    def test_pythonic(self):
        """测试pythonionc方法
        """
        dbsize = len(CLI)
        assert dbsize > 0
        del CLI["hello_world"]
        CLI["hello_world"] = "hello_world"
        assert "hello_world" in CLI


    def test_types_list(self):
        """测试列表类型List
        """
        del CLI["wlc_list"]
        list_struct = CLI.List("wlc_list")
        list_struct.append(1)
        list_struct.append(2)
        list_struct.append(3)
        assert list_struct[0] == "1"  # 注意数据类型不能保证,默认序列化方式为json导致
        assert list_struct[1] == "2"
        assert list_struct[2] == "3"
        assert len(list_struct) == 3
        del CLI["wlc_list"]
        assert "wlc_list" not in list_struct
        del(CLI['mylist'])  # 先删除，避免存在key的情况会extend操作
        l = CLI.List("mylist", ["Jerry", "George"])  # 注意如果key已经存在的话，默认使用extend操作扩展
        # 添加另外一个列表到列表尾
        l.extend(["Elaine", "Kramer"])
        assert l[0] == "Jerry"
        assert l[1] == "George"
        assert l[2] == "Elaine"
        assert l[3] == "Kramer"
        slice_test = l[2:4]
        assert slice_test[0] == "Elaine"
        assert slice_test[1] == "Kramer"
        assert l.popleft() == "Jerry"
        assert len(l) == 3
        # 验证迭代器部分逻辑
        it = iter(l)
        assert it.next() == "George"
        # 查找并删除
        l.remove("Elaine", count=1)
        assert "Elaine" not in l
        # 添加另外一个列表到列表头,遍历要添加的列表到l
        l.extendleft(["Args", "Soup-nazi", "Art"])
        # now ``l = ['Art', 'Soup-nazi', 'Args', 'George', 'Kramer']``
        assert l[0] == "Art"
        # 清理列表的某些字段
        l.trim(start=1, stop=2)
        # now ``l = ['Soup-nazi']``
        assert len(l) == 1
        assert l[0] == "Soup-nazi"
        assert l[:] == ["Soup-nazi"]

    def test_types_dict(self):
        """测试数据类型Dict
        """
        del CLI["test_dict"]
        d = CLI.Dict("test_dict", {'1': 1, '2': 2})
        rd = CLI.Dict("test_dict")
        assert rd.get('1') == '1'  # json序列化后类型变化
        assert rd['2'] == '2'
        rd['3'] = '3'
        assert len(rd) == 3
        assert rd['3'] == '3'
        del rd["2"]
        assert "2" not in rd
        for k, v in rd.iteritems():
            assert k == v

    def test_types_set(self):
        """测试集合类型Set
        """
        del CLI["test_set"]
        s = CLI.Set("test_set", {1, 3, 4, 4, 5})
        rs = CLI.Set("test_set")
        assert len(rs) == 4
        assert 1 in rs
        assert 4 in rs

if __name__ == '__main__':
    unittest.main()
