#! usr/bin/python
# encoding=utf8

import socket
import codecs
import time
from threading import Thread
from collections import deque

import bencoder

from .config import (
    BOOTSTRAP_NODES,
    MAX_NODE_QSIZE,
    UDP_RECV_BUFFSIZE,
    SERVER_HOST,
    SERVER_PORT,
    MAGNET_PER,
    PER_NID_LEN,
    SLEEP_TIME,
)
from .utils import get_logger, get_nodes_info, get_rand_id, get_neighbor
from .database import RedisClient

LOG = get_logger()


class HNode:
    """
    DHT 节点类
    """
    def __init__(self, nid, ip=None, port=None):
        self.nid = nid
        self.ip = ip
        self.port = port


class DHTClient(Thread):
    """
    DHT 客户端类，继承自 Thread 类，负责发送请求。
    """
    def __init__(self, bind_ip, bind_port):
        Thread.__init__(self)
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.nid = get_rand_id()
        # nodes 节点是一个双端队列
        self.nodes = deque(maxlen=MAX_NODE_QSIZE)
        # KRPC 协议是由 bencode 编码组成的一个简单的 RPC 结构，使用 UDP 报文发送。
        self.udp = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        # UDP 地址绑定
        self.udp.bind((self.bind_ip, self.bind_port))

    def send_find_node_forever(self):
        """
        循环发送 find_node 请求
        """
        LOG.info("Client Start Working...")
        while True:
            try:
                # 弹出一个节点
                node = self.nodes.popleft()
                self.send_find_node((node.ip, node.port), node.nid)
                time.sleep(SLEEP_TIME)
            except IndexError:
                # 一旦节点队列为空，则重新加入 DHT 网络
                self.join_dht()

    def send_krpc(self, msg, address):
        """
        发送 krpc 协议

        :param msg: 发送 UDP 报文信息
        :param address: 发送地址，(ip, port) 元组
        """
        try:
            # msg 要经过 bencode 编码
            self.udp.sendto(bencoder.bencode(msg), address)
        except:
            pass

    def send_find_node(self, address, nid=None):
        """
        发送 find_node 请求。

        `find_node 请求`
        find_node 被用来查找给定 ID 的节点的联系信息。这时 KPRC 协议中的
        "q" == "find_node"。find_node 请求包含 2 个参数，第一个参数是 id，
        包含了请求节点的 ID。第二个参数是 target，包含了请求者正在查找的
        节点的 ID。当一个节点接收到了 find_node 的请求，他应该给出对应的
        回复，回复中包含 2 个关键字 id 和 nodes，nodes 是字符串类型，
        包含了被请求节点的路由表中最接近目标节点的 K(8) 个最接近的节点的联系信息。

        `示例`
        参数: {"id" : "<querying nodes id>", "target" : "<id of target node>"}
        回复: {"id" : "<queried nodes id>", "nodes" : "<compact node info>"}

        :param address: 地址元组（ip, port)
        :param nid: 节点 id
        """
        nid = get_neighbor(nid) if nid else self.nid
        tid = get_rand_id()
        msg = dict(
            t=tid,
            y="q",
            q="find_node",  # 指定请求为 find_node
            a=dict(id=nid, target=get_rand_id()),
        )
        self.send_krpc(msg, address)

    def join_dht(self):
        """
        利用 tracker 服务器，伪装成 DHT 节点，加入 DHT 网络
        """
        for address in BOOTSTRAP_NODES:
            self.send_find_node(address)


class DHTServer(DHTClient):
    """
    DHT 服务端类，继承自 DHTClient 类
    """
    def __init__(self, bind_ip, bind_port):
        DHTClient.__init__(self, bind_ip, bind_port)
        self.rd = RedisClient()

    def send_error(self, tid, address):
        """
        发送错误回复
        """
        msg = dict(t=tid, y="e", e=[202, "Server Error"])
        self.send_krpc(msg, address)

    def save_magnet(self, info_hash):
        """
        将磁力链接保存到数据库

        :param info_hash:  磁力链接的 info_hash
        """
        # 使用 codecs 解码 info_hash
        hex_info_hash = codecs.getencoder("hex")(info_hash)[0].decode()
        self.rd.add_magnet(MAGNET_PER.format(hex_info_hash))

    def on_find_node_response(self, msg):
        """
        解码 nodes 节点信息，并存储在双端队列

        :param msg: 节点报文信息
        """
        nodes = get_nodes_info(msg[b"r"][b"nodes"])
        for node in nodes:
            nid, ip, port = node
            # 进行节点有效性判断
            if len(nid) != PER_NID_LEN or ip == self.bind_ip:
                continue
            # 将节点加入双端队列
            self.nodes.append(HNode(nid, ip, port))

    def on_get_peers_request(self, msg, address):
        """
        处理 get_peers 请求，获取 info hash

        :param msg: 节点报文信息
        :param address: 节点地址
        """
        tid = msg[b"t"]
        try:
            info_hash = msg[b"a"][b"info_hash"]
            self.save_magnet(info_hash)
        except KeyError:
            # 没有对应的 info hash，发送错误回复
            self.send_error(tid, address)

    def on_announce_peer_request(self, msg, address):
        """
        处理 get_peers 请求，获取 info hash

        :param msg: 节点报文信息
        :param address: 节点地址
        """
        tid = msg[b"t"]
        try:
            info_hash = msg[b"a"][b"info_hash"]
            self.save_magnet(info_hash)
        except KeyError:
            # 没有对应的 info hash，发送错误回复
            self.send_error(tid, address)

    def on_message(self, msg, address):
        """
        负责返回信息的处理

        :param msg: 报文信息
        :param address: 报文地址
        """
        try:
            # `回复`
            # 对应于 KPRC 消息字典中的 y 关键字的值是 r，包含了一个附加的关键字 r。
            # 关键字 r 是字典类型，包含了返回的值。发送回复消息是在正确解析了请求消息的
            # 基础上完成的。
            if msg[b"y"] == b"r":
                # nodes 是字符串类型，包含了被请求节点的路由表中最接近目标节点
                # 的 K个最接近的节点的联系信息。
                if msg[b"r"].get(b"nodes", None):
                    self.on_find_node_response(msg)
            # `请求`
            # 对应于 KPRC 消息字典中的 y 关键字的值是 q，它包含 2 个附加的关键字
            # q 和 a。关键字 q 是字符串类型，包含了请求的方法名字。关键字 a 一个字典
            # 类型包含了请求所附加的参数。
            # 而实际上我们只需要获取这两者中的 info hash，用于构造磁力链接进而获取种子。
            elif msg[b"y"] == b"q":
                # get_peers 与 torrent 文件的 info_hash 有关。这时 KPRC 协议中的
                # "q" = "get_peers"。get_peers 请求包含 2 个参数。第一个参数是 id，
                # 包含了请求节点的 ID。第二个参数是 info_hash，它代表 torrent 文件的 info_hash
                if msg[b"q"] == b"get_peers":
                    self.on_get_peers_request(msg, address)
                # announce_peer 表明请求的节点正在某个端口下载 torrent
                # 文件。announce_peer 包含 4 个参数。第一个参数是 id，包含了请求节点的 ID；
                # 第二个参数是 info_hash，包含了 torrent 文件的 info_hash；第三个参数是 port
                # 包含了整型的端口号，表明 peer 在哪个端口下载；第四个参数数是 token，
                # 这是在之前的 get_peers 请求中收到的回复中包含的。
                elif msg[b"q"] == b"announce_peer":
                    self.on_announce_peer_request(msg, address)
        except KeyError:
            pass

    def run(self):
        """
        启动服务端
        """
        LOG.info("Start Server {}:{}".format(self.bind_ip, self.bind_port))
        # 首先加入到 DHT 网络
        self.join_dht()
        while True:
            try:
                # 接受返回报文
                data, address = self.udp.recvfrom(UDP_RECV_BUFFSIZE)
                # 使用 bdecode 解码返回数据
                msg = bencoder.bdecode(data)
                # 处理返回信息
                self.on_message(msg, address)
                time.sleep(SLEEP_TIME)
            except Exception as e:
                LOG.warning(e)


def start_server(port_offset):
    """
    新开线程启动程序

    :param port_offset: 端口位移值
    """
    dht = DHTServer(SERVER_HOST, SERVER_PORT + port_offset)
    # 启动服务端
    dht.start()
    # 启动客户端
    dht.send_find_node_forever()
    dht.join()
