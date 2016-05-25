# zyredis 使用文档

zyredis 是一个提供redis 或redis proxy failover的python client端解决方案，它解决了codis 做为redis proxy时python的client pipeline命令不支持的问题，提供了友好的日志处理codis不支持的命令。
zyredis同时也是一个redis的client，zyredis同时支持原生redis client以及codis redis client两种模式，最大程度上让codis的使用者在迁移上不必花太多精力。
zyredis另外一个亮点就是他是一个简化版本的redis orm，使用zyredis可以让所有的redis key不必散落到项目的各个地方，使用zyredis可以帮助管理redis的key，另外就是zyredis提供了对redis阻塞相关的命令的优化方案，
对于阻塞redis的操作zyredis会对其进行优化，使其在线上生产环境尽量不阻塞redis。

zyredis主要有以下几个文件构成：
* manager: 管理redis的连接和配置
* client：提供redis client以及codis redis client两种版本的支持，codis版本主要解决pipeline事务机制异常问题。
* model: 提供redis model 的odm支持
* types：提供了pythonic 方式使用redis client
* serialization：提供了对redis数据的序列化与反序列化操作

## zyredis 对qconf的使用说明

qconf_py.so： 该文件由QConf项目提供的python扩展包编译得到，如需升级请自行重新编译替换,该包仅仅提供了qconf的操作基础，可以不使用

## zyredis 各个接口的使用举例请参考test目录下的测试用例，里面有针对各个接口的详细测试以及说明

## 升级至1.0.0版本说明
RedisManager.instance().init函数移除，如果想从qconf配置中读取配置直接使用以下方法替换
RedisManager.instance().init_from_qconf("/test_group/service/codis")

RedisManager提供了对原生redis的支持，增加了对redis配置参数的传递,只需要定义BaseModel的时候将以下几个参数覆盖即可
```py
class BaseRedisModel(Model):

    client_name = "test_redis"
    db_num = 0
    init_from = "local"
    redis_conf = {
        0:"redis://localhost:6389/test_redis?weight=1&transaction=1&db=0",
        1:"redis://localhost:6389/test_redis2?weight=3&transaction=1&db=0",
    }
```
以上写法可以使用原生redis的配置，redis_conf配置项指定，并且init_from设置为local即可
