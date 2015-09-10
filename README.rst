=======
zyredis yet another redis client that support failover and codis 
=======
掌阅科技python接入redis客户端

项目描述
--------
- 实现redis接入以及redis的failover机制
- 实现redis客户端级别的负载均衡
- 解决长连接失效后需要重启服务问题
- 提供redis的基础model层
- 支持codis

项目当前状态
---------
- 服务线上所有redis的接入，日请求量大于5亿
- failover机制可以灵活切换redis proxy，并配置不同不服务器的负载

项目依赖
--------
- [QConf](https://github.com/Qihoo360/QConf)
- QConf python client目前已经集成到本目录代码中，zyredis/utils/qconf_py.so是通过QConf项目编译的python客户端
- [redis client](https://github.com/andymccurdy/redis-py)
- [Codis](https://github.com/wandoulabs/codis)

当前版本
--------
- v0.1.3 完全支持redis failover机制，兼容redis所有原生命令，python版本codis客户端，额外提供pythonic的数据结构