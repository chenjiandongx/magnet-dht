#!usr/bin/python
# encoding=utf8

from http.client import HTTPConnection
import json

from .database import RedisClient

SAVE_PATH = ".\\torrents"
STOP_TIMEOUT = 60
MAX_CONCURRENT = 16
MAX_MAGNETS = 256

ARIA2RPC_ADDR = "127.0.0.1"
ARIA2RPC_PORT = 6800
ARIA2RPC_TOKEN = None

rd = RedisClient()


def get_magnets():
    """
    获取磁力链接
    """
    mgs = rd.get_magnets(MAX_MAGNETS)
    for m in mgs:
        # 解码成字符串
        yield m.decode()


def exec_rpc(magnet):
    """
    调用rpc
    """
    conn = HTTPConnection(ARIA2RPC_ADDR, ARIA2RPC_PORT)
    req = {
        'jsonrpc':
        '2.0',
        'id':
        "magnet",
        'method':
        "aria2.addUri",
        'params': [[magnet], {
            "bt-stop-timeout": "30",
            "max-concurrent-downloads": str(MAX_CONCURRENT),
            "listen-port": "6881",
            "bt-metadata-only": True,
            "bt-save-metadata": True,
            "dir": SAVE_PATH,
        }]
    }
    if ARIA2RPC_TOKEN:
        req['params'].insert(0, "token:" + ARIA2RPC_TOKEN)

    conn.request("POST", "/jsonrpc", json.dumps(req), {
        "Content-Type": "application/json",
    })

    res = json.loads(conn.getresponse().read())
    if "error" in res:
        print("Aria2c replied with an error:", res["error"])


def magnet2torrent():

    for magnet in get_magnets():
        exec_rpc(magnet)
