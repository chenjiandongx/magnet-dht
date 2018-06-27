#!usr/bin/python
# encoding=utf8

import subprocess
from threading import Thread

from .database import RedisClient

SAVE_PATH = ".\\torrents"
STOP_TIMEOUT = 60
MAX_CONCURRENT = 16
MAX_MAGNETS = 256

CMD = (
    "aria2c -d {save_path} "
    "--bt-metadata-only=true "
    "--bt-save-metadata=true "
    "--listen-port=6881 "
    "--max-concurrent-downloads={max_concurrent} "
    '--bt-stop-timeout={stop_timeout} "{magnet}"'
)

rd = RedisClient()


def get_magnets():
    """
    获取磁力链接
    """
    mgs = rd.get_magnets(MAX_MAGNETS)
    for m in mgs:
        # 解码成字符串
        yield m.decode()


def exec_cmd(magnet):
    """
    执行命令行操作
    """
    subprocess.call(
        CMD.format(
            save_path=SAVE_PATH,
            stop_timeout=STOP_TIMEOUT,
            max_concurrent=MAX_CONCURRENT,
            magnet=magnet,
        )
    )


def magnet2torrent():
    threads = []
    for magnet in get_magnets():
        th = Thread(target=exec_cmd, args=(magnet,))
        threads.append(th)

    for th in threads:
        th.start()
