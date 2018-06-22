# !usr/bin/python
# encoding=utf8

# 服务器 tracker
BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881),
]

# 双端队列容量
MAX_NODE_QSIZE = 10000
# UDP 报文 buffsize
UDP_RECV_BUFFSIZE = 65536
# 服务 host
SERVER_HOST = "0.0.0.0"
# 服务端口
SERVER_PORT = 9090
# 磁力链接前缀
MAGNET_PER = "magnet:?xt=urn:btih:{}"
# while 循环休眠时间
SLEEP_TIME = 0

# 每个节点长度
PER_NODE_LEN = 26
# 节点 id 长度
PER_NID_LEN = 20
# 节点 id 和 ip 长度
PER_NID_NIP_LEN = 24
# 构造邻居随机结点
NEIGHBOR_END = 10

# redis key
REDIS_KEY = "magnets"
# redis 地址
REDIS_HOST = "localhost"
# redis 端口
REDIS_PORT = 6379
# redis 密码
REDIS_PASSWORD = None
# redis 连接池最大连接量
REDIS_MAX_CONNECTION = 20
