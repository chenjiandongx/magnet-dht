#!usr/bin/python
# encoding=utf8


import subprocess
from threading import Thread

SAVE_PATH = r"D:\torrents"
STOP_TIMEOUT = 120
CMD = (
    r"aria2c -d {save_path} --bt-metadata-only=true "
    r"--bt-save-metadata=true --listen-port=6881 "
    r'--bt-stop-timeout={stop_timeout} "{magnet}"'
)


def get_magnets():
    with open("MAGNET.txt", "r") as f:
        for row in f.readlines():
            yield row.strip()


def exec_cmd(magnet):
    subprocess.call(
        CMD.format(
            save_path=SAVE_PATH, stop_timeout=STOP_TIMEOUT, magnet=magnet
        )
    )


if __name__ == "__main__":
    magnets = list(get_magnets())

    threads = []
    for magnet in magnets:
        th = Thread(target=exec_cmd, args=(magnet,))
        threads.append(th)

    for th in threads:
        th.start()

    for th in threads:
        th.join()
