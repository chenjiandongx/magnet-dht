#!usr/bin/python
# encoding=utf-8

import os
import logging
from struct import unpack
from socket import inet_ntoa

# 每个节点长度
PER_NODE_LEN = 26
# 节点 id 长度
PER_NID_LEN = 20
# 节点 id 和 ip 长度
PER_NID_NIP_LEN = 24
# 构造邻居随机结点
NEIGHBOR_END = 14
# 日志等级
LOG_LEVEL = logging.INFO


def get_rand_id():
    """
    生成随机的节点 id，长度为 20 位
    """
    return os.urandom(PER_NID_LEN)


def get_neighbor(target):
    """
    生成随机 target 周边节点 id，在 Kademlia 网络中，距离是通过异或(XOR)计算的，
    结果为无符号整数。distance(A, B) = |A xor B|，值越小表示越近。

    :param target: 节点 id
    """
    return target[:NEIGHBOR_END] + get_rand_id()[NEIGHBOR_END:]


def get_nodes_info(nodes):
    """
    解析 find_node 回复中 nodes 节点的信息

    :param nodes: 节点薪资
    """
    length = len(nodes)
    # 每个节点单位长度为 26 为，node = node_id(20位) + node_ip(4位) + node_port(2位)
    if (length % PER_NODE_LEN) != 0:
        return []

    for i in range(0, length, PER_NODE_LEN):
        nid = nodes[i : i + PER_NID_LEN]
        # 利用 inet_ntoa 可以返回节点 ip
        ip = inet_ntoa(nodes[i + PER_NID_LEN : i + PER_NID_NIP_LEN])
        # 解包返回节点端口
        port = unpack("!H", nodes[i + PER_NID_NIP_LEN : i + PER_NODE_LEN])[0]
        yield (nid, ip, port)


def get_logger(logger_name):
    """
    返回日志实例
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)
    fh = logging.StreamHandler()
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)
    return logger
