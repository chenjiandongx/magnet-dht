#! usr/bin/python
# encoding=utf8

from multiprocessing import Process, cpu_count
from magnet_dht.crawler import start_server


if __name__ == "__main__":
    # 利用多进程运行程序，提升总体效率
    processes = []
    for i in range(cpu_count()):
        processes.append(Process(target=start_server, args=(i,)))

    for p in processes:
        p.start()
