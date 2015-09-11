# zyredis 使用文档

zyredis 是一个提供redis 或redis proxy failover的python client端解决方案，它解决了codis 做为redis proxy时python的client pipeline命令不支持的问题，提供了友好的日志处理codis不支持的命令。
zyredis同时也是一个redis的client，zyredis同时支持原生redis client以及codis redis client两种模式，最大程度上让codis的使用者在迁移上不必花太多精力。

zyredis主要有以下几个文件构成：
* manager: 管理与QConf的共享内存
* client：提供redis client以及codis redis client两种版本的支持，codis版本主要解决pipeline事务机制异常问题。
* model: 提供redis model 的odm支持
* types：提供了pythonic 方式使用redis client
* serialization：提供了对redis数据的序列化与反序列化操作

## zyredis 依赖项说明

qconf_py.so： 该文件由QConf项目提供的python扩展包编译得到，如需升级请自行重新编译替换

## zyredis 各个接口的使用举例请参考test目录下的测试用例，里面有针对各个接口的详细测试以及说明


